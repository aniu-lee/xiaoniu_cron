#!/usr/bin/python3 
# -*- coding:utf-8 -*-
import fcntl
import os
import uuid
from datetime import datetime, timedelta
from threading import TIMEOUT_MAX

import records
import redis
import six
from apscheduler.events import JobSubmissionEvent, EVENT_JOB_MAX_INSTANCES, EVENT_JOB_SUBMITTED
from apscheduler.executors.base import MaxInstancesReachedError
from apscheduler.schedulers.base import STATE_PAUSED
from apscheduler.schedulers.gevent import GeventScheduler
from apscheduler.util import timedelta_seconds

from configs import configs


class CuGeventScheduler(GeventScheduler):

    def _dbs(self):
        url = configs('cron_job_log_db_url')
        db = records.Database(url)
        db = db.get_connection()  # 新加
        return db

    def update_cron_info(self,cron_id):
        try:
            cron_id = cron_id.split('_')[-1]
            self._dbs().query("update cron_infos set status=-1 where id='%s'" % cron_id)
        except:
            pass

    def _process_jobs(self):
        """
        Iterates through jobs in every jobstore, starts jobs that are due and figures out how long
        to wait for the next round.

        If the ``get_due_jobs()`` call raises an exception, a new wakeup is scheduled in at least
        ``jobstore_retry_interval`` seconds.

        """
        f = open("scheduler.lock", "wb")
        wait_seconds = None
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except Exception as exc:
            f.close()
        else:
            if self.state == STATE_PAUSED:
                self._logger.debug('Scheduler is paused -- not processing jobs')
                return None

            self._logger.debug('Looking for jobs to run and os.pid is {%s}' % os.getpid())
            now = datetime.now(self.timezone)
            next_wakeup_time = None
            events = []

            uuids = str(uuid.uuid1())

            config = configs()

            is_single = config.get('is_single')

            if is_single and is_single != '1':
                if config.get('redis_pwd'):
                    pool = redis.ConnectionPool(host=config.get('redis_host'), port=config.get('redis_port') or 6379,
                                                db=config.get('redis_db') or 0, password=config.get('redis_pwd'))
                else:
                    pool = redis.ConnectionPool(host=config.get('redis_host'), port=config.get('redis_port') or 6379,
                                                db=config.get('redis_db') or 0)

                r = redis.Redis(connection_pool=pool)

                _result = r.get("SCHEDU_FLAG")

                if _result:
                    if _result.decode() == uuids[0:2]:
                        return

                r.setnx("SCHEDU_FLAG", uuids[0:2])
                r.expire("SCHEDU_FLAG", 60 * 10)

            with self._jobstores_lock:
                for jobstore_alias, jobstore in six.iteritems(self._jobstores):
                    try:
                        due_jobs = jobstore.get_due_jobs(now)
                        self._logger.info("due_jobs:%s     os.pid: %s\n" % (len(due_jobs), os.getpid()))
                    except Exception as e:
                        # Schedule a wakeup at least in jobstore_retry_interval seconds
                        self._logger.warning('Error getting due jobs from job store %r: %s',
                                             jobstore_alias, e)
                        retry_wakeup_time = now + timedelta(seconds=self.jobstore_retry_interval)
                        if not next_wakeup_time or next_wakeup_time > retry_wakeup_time:
                            next_wakeup_time = retry_wakeup_time

                        continue

                    for job in due_jobs:
                        # Look up the job's executor
                        try:
                            executor = self._lookup_executor(job.executor)
                        except BaseException:
                            self._logger.error(
                                'Executor lookup ("%s") failed for job "%s" -- removing it from the '
                                'job store', job.executor, job)
                            self.update_cron_info(job.id)
                            self.remove_job(job.id, jobstore_alias)
                            continue

                        run_times = job._get_run_times(now)
                        run_times = run_times[-1:] if run_times and job.coalesce else run_times
                        if run_times:
                            try:
                                executor.submit_job(job, run_times)
                            except MaxInstancesReachedError:
                                self._logger.warning(
                                    'Execution of job "%s" skipped: maximum number of running '
                                    'instances reached (%d)', job, job.max_instances)
                                event = JobSubmissionEvent(EVENT_JOB_MAX_INSTANCES, job.id,
                                                           jobstore_alias, run_times)
                                events.append(event)
                            except BaseException:
                                self._logger.exception('Error submitting job "%s" to executor "%s"',
                                                       job, job.executor)
                            else:
                                event = JobSubmissionEvent(EVENT_JOB_SUBMITTED, job.id, jobstore_alias,
                                                           run_times)
                                events.append(event)

                            # Update the job if it has a next execution time.
                            # Otherwise remove it from the job store.
                            job_next_run = job.trigger.get_next_fire_time(run_times[-1], now)
                            if job_next_run:
                                job._modify(next_run_time=job_next_run)
                                jobstore.update_job(job)
                            else:
                                try:
                                    self.update_cron_info(job.id)
                                    self.remove_job(job.id, jobstore_alias)
                                except:
                                    self._logger.error('Error remove job "%s" to executor "%s"',
                                                       job, job.executor)

                    # Set a new next wakeup time if there isn't one yet or
                    # the jobstore has an even earlier one
                    jobstore_next_run_time = jobstore.get_next_run_time()
                    if jobstore_next_run_time and (next_wakeup_time is None or
                                                   jobstore_next_run_time < next_wakeup_time):
                        next_wakeup_time = jobstore_next_run_time.astimezone(self.timezone)

            # Dispatch collected events
            for event in events:
                self._dispatch_event(event)

            # Determine the delay until this method should be called again
            if self.state == STATE_PAUSED:
                self._logger.debug('Scheduler is paused; waiting until resume() is called')
            elif next_wakeup_time is None:
                self._logger.debug('No jobs; waiting until a job is added')
            else:
                wait_seconds = min(max(timedelta_seconds(next_wakeup_time - now), 0), TIMEOUT_MAX)
                self._logger.debug('Next wakeup is due at %s (in %f seconds)', next_wakeup_time,
                                   wait_seconds)

            if is_single and is_single != '1':
                r.delete("SCHEDU_FLAG")

            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()

        return wait_seconds