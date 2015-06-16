function sohu_pvinsight_engine(){
    var spv_random_str = escape((new Date().getTime()) * 1000 + Math.round(Math.random() * 1000));
    var spv_screen_w = window.screen.width;
    var spv_screen_h = window.screen.height;
    var spv_referrer = (typeof(encodeURI) == 'function') ? encodeURI(document.referrer) : document.referrer;
    var spv_id = false;
    /*
     * 其他频道调用pv.js的时候，可以直接在url后面加入参数
     * 例如：<script type="text/javascript" src="http://js.sohu.com/mail/pv/pv.js?tv"></script>
     * update by fjc (2010-03-01)
     */
    var key_string = 'ifr';
    var spv_channel_flag = false;
    var sct = document.getElementsByTagName('script');
    (function() {
    	var _c_s = sct[sct.length-1], _c_src = _c_s && _c_s.src;
    	if(!_c_src) return false;
    	var _p = _c_src.split('?')[1];
    	if(!_p) return false;
    	if(_p.toLowerCase().indexOf(key_string) != -1) spv_channel_flag = true;
    })();
    if (typeof _focus_pv_id != "undefined") {
        spv_id = _focus_pv_id
    } else if (typeof _pvinsight_id != "undefined") {
        spv_id = _pvinsight_id
    }
    var spv_dhead = document.getElementsByTagName("head")[0],
	spv_dbody = document.body,
	d = spv_dhead || spv_dbody,
    suv_server = "//pv.sohu.com/suv",
    spv_server = "//pv.sohu.com";
    if (document.cookie.indexOf("SUV=") < 0 || document.cookie.indexOf("IPLOC=") < 0) {
        var suv_server_src = suv_server + "/" + spv_random_str;
		if (d) {
			var _script1 = document.createElement('script');
			_script1.src = suv_server_src;
			d.appendChild(_script1);
		} else {
			document.write("<script type='text/javascript' src='" + suv_server_src + "'></script>");
		}
    }
    if (spv_channel_flag || top.location == self.location || document.domain.indexOf(".go2map.com") >= 0) {
        if (spv_id) {
            var spv_server_src = spv_server + '/pv.gif?t?=_' + spv_random_str + '_' + spv_screen_w + '_' + spv_screen_h + '_' + spv_id + '?r?=' + spv_referrer;
			if (d) {
				var _script2 = document.createElement('script');
				_script2.src = spv_server_src;
                d.appendChild(_script2);
            } else {
                document.write("<script src='" + spv_server_src + "'></script>");
            }
        } else {
            var spv_server_src = spv_server + '/pv.gif?t?=' + spv_random_str + '_' + spv_screen_w + '_' + spv_screen_h + '?r?=' + spv_referrer;
            if (d) {
				var _script3 = document.createElement('script');
				_script3.src = spv_server_src;
                d.appendChild(_script3);
            } else {
                document.write("<script src='" + spv_server_src + "'></script>");
            }
        }
    }
}

var spv_flag;
if (!spv_flag) {
    sohu_pvinsight_engine();
}
spv_flag = 1;
