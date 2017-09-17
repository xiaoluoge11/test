if (typeof MUSICKING == "undefined") var MUSICKING = {};
MUSICKING.core = true;
(function($){
	Function.prototype.method = function(name,fn){
		if(typeof this.prototype[name] == 'undefined') 
			this.prototype[name] = fn;
		return this
	};
	
	String.method("encode",
	function(noCom) {
		return noCom ? encodeURI(this) : encodeURIComponent(this)
	}).method("decode",
	function(noCom) {
		return noCom ? decodeURI(this) : decodeURIComponent(this)
	});
	
	MUSICKING.isMobile = "createTouch" in document && !("onmousemove" in document.documentElement) || /(iPhone|iPad|iPod)/i.test(navigator.userAgent);
	
	MUSICKING.isIE6 = navigator.appVersion.indexOf("MSIE 6") > -1;
	
	/*tab切换*/
	MUSICKING.setTab = function(name,cursel,n){
		for(i=1;i<=n;i++){
			var menu=$("#"+name+i);
			var con=$("#tabCon_"+name+"_"+i);
			if(i==cursel){
				$("#"+name+i).addClass("curr");
				$("#tabCon_"+name+"_"+i).css({"display":'block'});
				$("#"+name+"Curr").attr('class','curr'+i);
			}else{
				$("#"+name+i).removeClass("curr");
				$("#tabCon_"+name+"_"+i).css({"display":'none'});
			}
		}
	}
	/*判断是否IE6或者IE7*/
	MUSICKING.isIE6orIE7 = function(){
		if(navigator.appName == "Microsoft Internet Explorer"){
			if(navigator.appVersion .split(";")[1].replace(/[ ]/g,"")=="MSIE6.0" || navigator.appVersion .split(";")[1].replace(/[ ]/g,"")=="MSIE7.0"){
				$("body").prepend('<div class="icon_v browserSug">温馨提示：您当前使用的浏览器版本过低，兼容性和安全性较差，劲歌王建议您升级: <a class="red" href="http://windows.microsoft.com/zh-cn/windows/upgrade-your-browser">IE8浏览器</a></div>');
			}
		}
	}	
})(jQuery)

function toTop() {
    var scrolltoTop = $("#toTop");
    $(scrolltoTop).hide();
    $(window).scroll(function () {
        if ($(window).scrollTop() == "0") {
            $(scrolltoTop).fadeOut("slow");
        } else {
            $(scrolltoTop).fadeIn("slow");
        }
    });
    $(scrolltoTop).click(function () {
        $('html, body').animate({
            scrollTop: 0
        },
            700);
    });
}



