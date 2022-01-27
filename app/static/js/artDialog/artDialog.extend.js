/***
 * 支持artDialog4.1.7
 * JS基本封装
 * 常用的js代码
 */

/****窗口抖动*****/
artDialog.fn.shake = function (){
    var style = this.DOM.wrap[0].style,
        p = [4, 8, 4, 0, -4, -8, -4, 0],
        fx = function () {
            style.marginLeft = p.shift() + 'px';
            if (p.length <= 0) {
                style.marginLeft = 0;
                clearInterval(timerId);
            };
        };
    p = p.concat(p.concat(p));
    timerId = setInterval(fx, 13);
    return this;
};

/********
 * 提示窗  可关闭
 * 			art.dialog.notice({
			    title: '万象网管',
			    width: 220,// 必须指定一个像素宽度值或者百分比，否则浏览器窗口改变可能导致artDialog收缩
			    content: '<font color=red>尊敬的顾客朋友，您IQ卡余额不足10元，请及时充值</font>',
			    icon: 'face-sad',
			    time: 3,
			    close:false
			});
 * **********/
artDialog.notice = function (options) {
    var opt = options || {},
        api, aConfig, hide, wrap, top,left,
        duration = 1000;
    var config = {
        id: 'Notice',
        left: opt.left==undefined ? '100%':opt.left,
        top: opt.top==undefined ? '100%':opt.top,
        fixed: true,
        drag: false,
        resize: false,
        follow: null,
        lock: false,
        init: function(here){
            api = this;
            aConfig = api.config;
            wrap = api.DOM.wrap;
            top = parseInt(wrap[0].style.top);
            hide = top + wrap[0].offsetHeight;

            wrap.css('top', hide + 'px')
                .animate({top: top + 'px'}, duration, function () {
                    opt.init && opt.init.call(api, here);
                });
        },
        close: function(here){
            wrap.animate({top: hide + 'px'}, duration, function () {
                opt.close && opt.close.call(this, here);
                aConfig.close = $.noop;
                api.close();
            });

            return false;
        }
    };

    for (var i in opt) {
        if (config[i] === undefined) config[i] = opt[i];
    };

    return artDialog(config);
};