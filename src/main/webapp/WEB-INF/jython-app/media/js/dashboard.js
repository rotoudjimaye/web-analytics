

// disable jquery ajax caching
jQuery.ajaxSetup({ cache: false });
var dashBoardParams = {"a": "basic", "frequency": "minutely", init: true};

function toQueryString (params){
    var queryString = "";
    for(var key in params){
	queryString += "&" + key + "="+ encodeURIComponent(params[key]);
    }
    return queryString.length? queryString.substr(1) : ""; 
}

var WEEKLY_GRAPH_OPTS = {
    "PAGEVIEW_STATS": [
	{vizBoxPanel:'div.VISITORS', selectColumns:[0, 1]},
	{vizBoxPanel:'div.AVG-DURATIONS', selectColumns:[0, 3]},
	{vizBoxPanel:'div.AVG-PAGEVIEWS', selectColumns:[0, 4]}
    ],
    "ENTRY-EXIT_STATS": [
	{vizBoxPanel:'div.TOP-ENTRY-PAGES', cmpOptions:{dataColIndex:3, cmpEntities:'items', cmpLabelProp:'pathname', cmpDataFrameProp:'history'}},
	{vizBoxPanel:'div.TOP-EXIT-PAGES', cmpOptions:{dataColIndex:4, cmpEntities:'items', cmpLabelProp:'pathname', cmpDataFrameProp:'history'}}
    ],
    "GEOLOCATION_STATS-A": [
	{vizBoxPanel:'div.TOP-VISITOR-COUNTRIES', cmpOptions:{dataColIndex:1, cmpEntities:'items', cmpLabelProp:'name', cmpDataFrameProp:'history'}}
    ],
    "GEOLOCATION_STATS-B": [
	{vizBoxPanel:'div.TOP-VISITOR-CITIES', cmpOptions:{dataColIndex:1, cmpEntities:'items', cmpLabelProp:'name', cmpDataFrameProp:'history'}}
    ]
};


function showBasicDashboard(domain, frequency){

    var dashboard = $("#dashboard-content-area");
    function doRefresh(){return running == 1 && dashboard.find("#PAGEVIEW_STATS").length; }
    
    // load dashboard area html snippet
    $.ajax(
    	{url: "/snippets/basic-dashboard/",
    	 type: "GET",
    	 success: function(s){
	     var result = $(s);
	     var frequencies = result.find(".data-frequency").remove();
	     $(".data-frequency-holder").empty().append(frequencies.html());
	     dashboard.empty().append(result);
	     dashboard.find('a.download').on('click', function(){
		 window.location.href = "/download-csv/pageview/"+dashBoardParams.frequency+"/?"+ toQueryString({domain: dashBoardParams.domain});
		 return false;
	     });
	     fetchPageViewStats();
	     $(".dashboard-navigation li").off().on("click", function(){$(this).addClass("selected").siblings().removeClass("selected");});
	 },
	 error: function(e){/* alert("error"+e); */} }
    );

    function showLiveSummary(live){
	var area = $(".page-views-summary");
	for(var k in live){
	    area.find("tr."+k)
		.find("td:nth(0)").text(live[k].visitors).end()
		.find("td:nth(1)").text(live[k].avg_pageviews_per_visit).end()
		.find("td:nth(2)").text(live[k].pageviews).end()
		.find("td:nth(3)").text(live[k].avg_visit_duration).end();
	}
    }

    var drawer;
    var running = 0;
    function fetchPageViewStats(_latest){
	var latest = _latest;
	running += 1 ;
	var xhr = $.ajax({
    	    url : "/pageview/"+dashBoardParams.frequency+"/?"+ toQueryString({domain: dashBoardParams.domain, latest: (latest? latest : "")}), 
    	    dataType: "json",
	    complete: function(){
		// loadingIcon.hide("slow");
		if(doRefresh()) { dashboard.oneTime(3000,  function(){ fetchPageViewStats(latest); }); }
		running -= 1;
	    },
            success: function(json) {
		if(!latest){
		    if(drawer) drawer.clear();
		    dashboard.find('a.download').hide();
		    drawer = new DrawReports(dashboard.find("#PAGEVIEW_STATS"), WEEKLY_GRAPH_OPTS['PAGEVIEW_STATS'], "history");
		}
		if(json.history["$RECORDS$"].length){	
		    dashboard.find('a.download').show();
		    drawer.draw(json, dashBoardParams.frequency);
		}
		latest = json.latest;
		showLiveSummary(json.live);
            }
	});
    }

    fetchPageViewStats.dashboard = dashboard;
    return fetchPageViewStats;
}



function showEntryExitPageDashboard(){


    var dashboard = $("#dashboard-content-area");
    function doRefresh(){return dashboard.find("#ENTRY-EXIT_STATS").length; }

    // load dashboard area html snippet
    $.ajax(
    	{url: "/snippets/entry-exit-pages-dashboard/",
    	 type: "GET",
    	 success: function(s){
	     var result = $(s);
	     var frequencies = result.find(".data-frequency").remove();
	     $(".data-frequency-holder").empty().append(frequencies.html());

	     dashboard.empty().append(result);
	     fetchJsonData();
	     $(".dashboard-navigation li").off().on("click", function(){$(this).addClass("selected").siblings().removeClass("selected");});
	 },
	 error: function(e){/* alert("error"+e); */} }
    );

    var drawer0;
    var running0 = 0;
    function fetchEntryPageJsonData(_latest){
	var latest = _latest;
	running0 += 1;
	var xhr = $.ajax({
    	    url : "/top-entry-pages/"+dashBoardParams.frequency+"/?"+ toQueryString({domain: dashBoardParams.domain, latest: (latest? latest : "")}), 
    	    dataType: "json",
	    complete: function(){
		if(doRefresh() && running0 == 1) { dashboard.oneTime(60000, function(){ fetchEntryPageJsonData(latest); });}
		running0 -= 1;
	    },
            success: function(json) {
		if(!latest){
		    if(drawer0) drawer0.clear();
		    drawer0 = new DrawReports(dashboard.find("#ENTRY-EXIT_STATS"), [WEEKLY_GRAPH_OPTS['ENTRY-EXIT_STATS'][0]]);
		}
		if(json.items.length && json.items[0].history["$RECORDS$"].length){		    
		    drawer0.draw(json, dashBoardParams.frequency);//, "ColumnChart"
		}
		latest = json.latest;
            }
	});
    }

    var drawer1;
    var running1 = 0;
    function fetchExitPageJsonData(_latest){
	var latest = _latest;
	running1 += 1;
	var xhr = $.ajax({
    	    url : "/top-exit-pages/"+dashBoardParams.frequency+"/?"+ toQueryString({domain: dashBoardParams.domain, latest: (latest? latest : "")}), 
    	    dataType: "json",
	    complete: function(){
		if(doRefresh() && running1 == 1) { dashboard.oneTime(60000, function(){ fetchExitPageJsonData(latest); });}
		running1 -= 1;
	    },
            success: function(json) {
		if(!latest){
		    if(drawer1) drawer1.clear();
		    drawer1 = new DrawReports(dashboard.find("#ENTRY-EXIT_STATS"), [WEEKLY_GRAPH_OPTS['ENTRY-EXIT_STATS'][1]]);
		}
		if(json.items.length && json.items[0].history["$RECORDS$"].length){		    
		    drawer1.draw(json, dashBoardParams.frequency);//, "ColumnChart"
		}
		latest = json.latest;
            }
	});
    }
   
   function fetchJsonData(){
	fetchEntryPageJsonData();
	fetchExitPageJsonData();
    };

    fetchJsonData.dashboard = dashboard;
    return fetchJsonData;
}



function showGeolocationDashboard(){

    var dashboard = $("#dashboard-content-area");
    function doRefresh(){return dashboard.find("#GEOLOCATION_STATS").length; }

    // load dashboard area html snippet
    $.ajax(
    	{url: "/snippets/geolocation-dashboard/",
    	 type: "GET",
    	 success: function(s){
	     var result = $(s);
	     var frequencies = result.find(".data-frequency").remove();
	     $(".data-frequency-holder").empty().append(frequencies.html());

	     dashboard.empty().append(result);
	     fetchJsonData();
	     $(".dashboard-navigation li").off().on("click", function(){$(this).addClass("selected").siblings().removeClass("selected");});
	 },
	 error: function(e){/* alert("error"+e); */} }
    );

    var drawer0;
    var running0 = 0;
    function fetchCountriesJsonData(_latest){
	var latest = _latest;
	running0 += 1;
	var xhr = $.ajax({
    	    url : "/top-countries/"+dashBoardParams.frequency+"/?"+ toQueryString({domain: dashBoardParams.domain, latest: (latest? latest : "")}), 
    	    dataType: "json",
	    complete: function(){
		if(doRefresh() && running0 == 1) { dashboard.oneTime(60000, function(){ fetchCountriesJsonData(latest); });}
		running0 -= 1;
	    },
            success: function(json) {
		if(!latest){
		    if(drawer0) drawer0.clear();
		    drawer0 = new DrawReports(dashboard.find("#GEOLOCATION_STATS-A"), WEEKLY_GRAPH_OPTS['GEOLOCATION_STATS-A']);
		}
		if(json.items.length && json.items[0].history["$RECORDS$"].length){		    
		    drawer0.draw(json, dashBoardParams.frequency);//, "ColumnChart"
		}
		latest = json.latest;
            }
	});
    }

    var drawer1;
    var running1 = 0;
    function fetchCitiesJsonData(_latest){
	var latest = _latest;
	running1 += 1;
	var xhr = $.ajax({
    	    url : "/top-cities/"+dashBoardParams.frequency+"/?"+ toQueryString({domain: dashBoardParams.domain, latest: (latest? latest : "")}), 
    	    dataType: "json",
	    complete: function(){
		if(doRefresh() && running1 == 1) { dashboard.oneTime(60000, function(){ fetchCitiesJsonData(latest); });}
		running1 -= 1;
	    },
            success: function(json) {
		if(!latest){
		    if(drawer1) drawer1.clear();
		    drawer1 = new DrawReports(dashboard.find("#GEOLOCATION_STATS-B"), WEEKLY_GRAPH_OPTS['GEOLOCATION_STATS-B']);
		}
		if(json.items.length && json.items[0].history["$RECORDS$"].length){		    
		    drawer1.draw(json, dashBoardParams.frequency);//, "ColumnChart"
		}
		latest = json.latest;
            }
	});
    }
   
   function fetchJsonData(){
	fetchCountriesJsonData();
	fetchCitiesJsonData();
    };

    fetchJsonData.dashboard = dashboard;
    return fetchJsonData;
}


var dashBoardUpdater;
$(document).ready(function(){
    
    addHistoryHandler('/switch/', function(path, queryString){

	var params = {};
	_.each(queryString.split("&"), function(item){
	    var kv = item.split("=");
	    params[kv[0]] = kv[1];
	});

	
	if(dashBoardUpdater)dashBoardUpdater.dashboard.stopTime();

	if((params.a && params.a != dashBoardParams.a) || dashBoardParams.init){   
	    _.extend(dashBoardParams, params);
	    if(dashBoardParams.a == "basic"){
		_.extend(dashBoardParams, {"frequency": "minutely"});
		dashBoardUpdater = showBasicDashboard(dashBoardParams.domain, dashBoardParams.frequency);
	    }
	    else if(dashBoardParams.a == "entry-exit"){
		_.extend(dashBoardParams, {"frequency": "hourly"});
		dashBoardUpdater = showEntryExitPageDashboard(dashBoardParams.domain, dashBoardParams.frequency);
	    }
	    else if(dashBoardParams.a == "geolocation"){
		_.extend(dashBoardParams, {"frequency": "hourly"});
		dashBoardUpdater = showGeolocationDashboard(dashBoardParams.domain, dashBoardParams.frequency);
	    }
	    delete dashBoardParams.init;
	}else{
	    _.extend(dashBoardParams, params);
	    dashBoardUpdater();
	}	
    });

    $(".dashboard-navigation li").off().on("click", function(){$(this).addClass("selected").siblings().removeClass("selected");});
    
    if(!window.location.hash){
	var defaultDomain =  $(".dashboard-navigation ul.my-domains li:first").click().find("a").attr('href');
	dashBoardParams['domain'] = defaultDomain.substr(defaultDomain.indexOf("=")+1);
	if(defaultDomain){
	    window.location.href = defaultDomain;
	}
    }
});