#!/usr/bin/python3 
# -*- coding:utf-8 -*-
from app import db


class JobLogItems(db.Model):
    __tablename__='job_log_items'
    id = db.Column(db.Integer,primary_key=True)
    log_id = db.Column(db.String(65),index=True,nullable=False)
    content = db.Column(db.TEXT,nullable=False,default='')