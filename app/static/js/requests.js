/**
 * author aniulee
 */
function requests(setting) {
    var defaultSetting={
        url:null,//url
        type:'GET',//method
        data:{},//data
        success:null,//success
        error:null,//error
        debug:true, //true or false
        beforeSend:null,
        complete:null,
        hash:'this,is,hard,guess'
    };
    var settings = $.extend(defaultSetting,setting);
    $.ajax({
        url:settings.url,
        data:settings.data,
        type:settings.type,
        headers: {
            sign: signs(settings.data,settings.hash)
        },
        beforeSend:settings.beforeSend || null,
        //contentType: "application/json; charset=utf-8",
        success:function (data) {
            console.log(data)
            if (data.errcode == '0'){
                if(typeof settings.successs !=null)
                settings.success(data.errmsg,data.result,data.url);
            }else {
                if(typeof settings.error !=null)
                settings.error(data.errcode,data.errmsg,data.result,data.url);
            }
            if(settings.debug){
                // console.log(data)
            }

        },
        //dataType:'json',
        error:function (data) {

            if(settings.debug){
                console.log(data)
            }
            if(typeof settings.error !=null){
                data = JSON.parse(data.responseText)
                settings.error(data.errcode,data.errmsg,data.result,data.url);
            }
        },
        complete:settings.complete || null
    })
}