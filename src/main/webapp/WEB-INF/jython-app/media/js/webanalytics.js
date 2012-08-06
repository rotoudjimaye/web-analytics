/* ******************************************************************
 * This is the main WebAnalytics js file which is referenced from third party websites.
 * Its role is to collect the web site visitors' browser information upon each page view 
 * ************************ ****************************************/

// var __webanalytics_account = 'adsbb3j388909d0d';
//(function() {var wa = document.createElement('script'); wa.type = 'text/javascript'; wa.async = true; wa.src = document.location.protocol+'//webanalytics-747.rhcloud.com/static/js/webanalytics.js'; var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(wa, s);})();

(function (){
    function toQueryString (params){
	var queryString = "";
	for(var key in params){
	    queryString += "&" + key + "="+ encodeURIComponent(params[key]);
	}
	return queryString.length? queryString.substr(1) : ""; 
    }

    var data = {
	'browser_host': window.location.host,
	'browser_hostname': window.location.hostname,
	'browser_href': window.location.href,
	'browser_hash': window.location.hash,
	'browser_pathname': window.location.pathname,
	'browser_port': window.location.port,
	'browser_protocol': window.location.protocol,
	'browser_search': window.location.search,
	'account_id': __webanalytics_account
    };

    var img = document.createElement('img'); 
    img.src = document.location.protocol+"//webanalytics-747.rhcloud.com/webanalytics.gif?"+toQueryString(data); 
    img.alt = "";
    var s = document.getElementsByTagName('div')[0]; 
    s.parentNode.insertBefore(img, s);
    img.style.display = "none";
})();



