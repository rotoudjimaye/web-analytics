
var STATUS_CLASSES = "UP WARNING DOWN";

function TimeLineDate(input, dateFormat) {
    return new Date(input);
}

function AreaChartDate(input) {
    // return new Date(input).format(this.dateFormat2);
    return new Date(input).toString(this.dateFormat2).toLowerCase();
}

try{
    google.load("visualization", "1", {packages:["corechart", 'annotatedtimeline', 'columnchart']});
}catch(e){}

function removeTrailingColon(text) {
    var colonIndex = text.lastIndexOf(":");
    return colonIndex != -1 ? text.substring(0, colonIndex) : text;
}

function getColumnType(colType, vizType){
    return colType.indexOf('date') != -1 && (vizType == 'AreaChart' ||  vizType == "ColumnChart"||  vizType == "BarChart") ? "string" : colType;
}

function getColumnFormater(colType, vizType){
    if(colType.indexOf('date') != -1 ){
	return (vizType == 'AreaChart' ||  vizType == "ColumnChart"||  vizType == "BarChart")? AreaChartDate :  TimeLineDate;
    }
    else{
	return function(e){return e;};
    }
}

function createDataTable(bulkCoumns, selectColumns, graphicPlace, graphicOptions, graphTitlePlace, vizType) {

    if (! graphicPlace) {
	throw "Graphic Place not Avaliable";
    }
    if (selectColumns[selectColumns.length - 1] >= bulkCoumns.length) {
	alert("selectColumns[selectColumns.length-1] >= bulkCoumns.length");
	return null;
    }

    var dataTable = new google.visualization.DataTable();

    dataTable.my_selectColumnsIndexes = selectColumns;
    dataTable.my_selectColumnsTypes = [];

    var allValuesSuffix = graphicOptions.allValuesSuffix;
    var selectColumsEntries = {};

    for (var i = 0; i < selectColumns.length; i++) {

	var colIndex = selectColumns[i];
	var colType = bulkCoumns[colIndex]['type'];
	var colLabel = bulkCoumns[colIndex]['label'];
	
	dataTable.addColumn(getColumnType(colType, vizType), colLabel);
	dataTable.my_selectColumnsTypes.push(getColumnFormater(colType, vizType));

        if (! allValuesSuffix && bulkCoumns[colIndex]['$suffix'])             allValuesSuffix = bulkCoumns[colIndex]['$suffix'];
    }

    //
    dataTable.my_graph_ctor = function() {
    	return ! vizType ? new google.visualization.AnnotatedTimeLine(graphicPlace) : new google.visualization[vizType](graphicPlace);
    };
    dataTable.my_graph = null; // the graph should be lazy loaded
    dataTable.my_options = graphicOptions;
    graphicPlace.dataTable = dataTable;

    //
    if (allValuesSuffix != undefined && allValuesSuffix != graphicOptions.allValuesSuffix) graphicOptions.allValuesSuffix = allValuesSuffix;

    //
    dataTable.populated = false;
    //
    return dataTable;
}


function appendDataRow(dataTable, bulkRow) {

    if (!dataTable) return;

    function getDataRow(dataTable, bulkRow) {
	var dataRow = [];

	for (var i = 0; i < dataTable.my_selectColumnsIndexes.length; i++) {

	    var colIndex = dataTable.my_selectColumnsIndexes[i];
	    var dataItem = bulkRow[colIndex];
            if (dataItem == null) dataItem = 0;// to fix a bug in google visualization: null values not left blank in the annoted timeline
            dataRow.push(dataTable.my_selectColumnsTypes[i].call(dataTable.my_options, dataItem));
        }
        return dataRow;
    }

    dataTable.addRow(getDataRow(dataTable, bulkRow));
}

function appendDataRows(dataTable, dataRows) {

    if (!dataTable) return;

    for (var i = 0; i < dataRows.length; i++) {
        //
        var bulkRow = dataRows[i];
        appendDataRow(dataTable, bulkRow);
    }
}

function appendDataRowsMaintConstLength(dataTable, dataRows) {

    appendDataRows(dataTable, dataRows);
    if (dataTable.populated) {
	dataTable.removeRows(0, dataRows.length);
    }
    else {
	dataTable.populated = true;
    }
}


var redrawGraphic = function (dataTable) {

    if (!dataTable) return;

    try {
	if (! dataTable.my_graph) {
	    dataTable.my_graph = dataTable.my_graph_ctor();
	}
	dataTable.my_graph.draw(dataTable, dataTable.my_options);
    } catch(e) {
	alert(e);
    }
};

var performGraphicRedraw = function (graphicPlace, context) {

    if (context.statsLatest == null) return;

    try {
	if (! graphicPlace.dataTable.my_graph) {
	    graphicPlace.dataTable.my_graph = graphicPlace.dataTable.my_graph_ctor();
	}
	graphicPlace.dataTable.my_graph.draw(graphicPlace.dataTable, graphicPlace.dataTable.my_options);
    } catch(e) {
        // alert(e);
    }
};


function setSPANpropertyValues(source, target) {
    for (var prop in source) {
	$(target).find("." + prop.replace(".", "_")).each(function() {
	    $(this).html(source[prop] != null ? source[prop] : '--');
	});
    }
}

function setSPANpropertyValuesAndShow(source, target) {
    setSPANpropertyValues(source, target);
    $(target).show().children().show();
}

var OnVisualizationPanelVisibility = function (panelVisible) {

    var panelContent = this;

    if (panelVisible) {
	$(panelContent).find(".graph-wrapper:visible").trigger("wrapper-visible");
    }
};


//
//
//
//
function createCmpDataTable(dateColIndex, dataColIndex, cmpEntities, cmpLabelProp, cmpDataFrameProp, graphicPlace, graphicOptions, graphTitlePlace, graphType) {
    //if(! graphicOptions.colors) graphicOptions.colors = null;
    if (! graphicPlace) return null;

    var dataTable = new google.visualization.DataTable();

    dataTable.my_dateColIndex = dateColIndex;
    dataTable.my_dataColIndex = dataColIndex;
    dataTable.my_cmpDataFrameProp = cmpDataFrameProp;

    dataTable.my_dataColIndexumnsTypes = [];
    dataTable.my_selectColumnsTypes = [];

    var allValuesSuffix = graphicOptions.allValuesSuffix;
    var dataColIndexumsEntries = {};

    //
    var dateColType = cmpEntities[0][cmpDataFrameProp]["$COLUMNS$"][dateColIndex]['type'];
    var dateColLabel = cmpEntities[0][cmpDataFrameProp]["$COLUMNS$"][dateColIndex]['label'];
    dataTable.addColumn(getColumnType(dateColType, graphType, dateColLabel));
    dataTable.my_selectColumnsTypes.push(getColumnFormater(dateColType, graphType));

    for (var i = 0; i < cmpEntities.length; i++) {

 	var entity = cmpEntities[i];

 	var entityDataFrame = entity[cmpDataFrameProp];
 	var entityBulkColumns = entityDataFrame["$COLUMNS$"];

 	var cmpColType = entityBulkColumns[dataColIndex]['type'];

 	var labelPrefix = (i == 0 ? entityBulkColumns[dataColIndex]['label'] : "");
 	var entityCmpLabel = entity[cmpLabelProp]; // ! graphTitlePlace ? (labelPrefix + entity[cmpLabelProp]) : entity[cmpLabelProp];

 	if (graphTitlePlace && labelPrefix) {
 	    $(graphTitlePlace).html("&nbsp;" + removeTrailingColon(labelPrefix) + "&nbsp;");
 	}

	dataTable.addColumn(getColumnType(cmpColType, graphType), entityCmpLabel);
	dataTable.my_selectColumnsTypes.push(getColumnFormater(cmpColType, graphType));

 	if (! allValuesSuffix && entityBulkColumns[dataColIndex]['$suffix'])             allValuesSuffix = entityBulkColumns[dataColIndex]['$suffix'];
    }

    //
    dataTable.my_graph_ctor = function() {
    	return new google.visualization[graphType](graphicPlace);
    };
    dataTable.my_graph = null; // the graph should be lazy loaded
    dataTable.my_options = graphicOptions;
    graphicPlace.dataTable = dataTable;

    //
    if (allValuesSuffix != undefined && allValuesSuffix != graphicOptions.allValuesSuffix) graphicOptions.allValuesSuffix = allValuesSuffix;

    //
    dataTable.populated = false;
    //
    return dataTable;
}

function appendCmpDataRows(dataTable, cmpEntities, numberOfRows) {

    if (!dataTable) return null;

    if (numberOfRows == undefined) {
	numberOfRows = cmpEntities[0][dataTable.my_cmpDataFrameProp]["$RECORDS$"].length;
    }

    var dateColLabel = cmpEntities[0][dataTable.my_cmpDataFrameProp]["$COLUMNS$"][dataTable.my_dateColIndex]['label'];

    for (var rowIdx = 0; rowIdx < numberOfRows; rowIdx++) {

	var cmpDataRow = [];
	var firstRowData = cmpEntities[0][dataTable.my_cmpDataFrameProp]["$RECORDS$"][rowIdx][dataTable.my_dateColIndex];
	cmpDataRow.push(dataTable.my_selectColumnsTypes[0].call(dataTable.my_options, firstRowData));

	for (var j = 0; j < cmpEntities.length; j++) {

	    var entity = cmpEntities[j];

	    var entityDataRecors = entity[dataTable.my_cmpDataFrameProp]["$RECORDS$"];
	    var entityBulkRow = rowIdx < entityDataRecors.length ? entityDataRecors[rowIdx] : [];
	    var dataItem = entityBulkRow[dataTable.my_dataColIndex];
	    var colType = dataTable.my_selectColumnsTypes[j];
	    if (dataItem == null) dataItem = 0;// to fix a bug in google visualization: null values not left blank in the annoted timeline
	    cmpDataRow.push(dataTable.my_selectColumnsTypes[j+1].call(dataTable.my_options, dataItem));
        }

        dataTable.addRow(cmpDataRow);
    }
    return numberOfRows;
}


function appendCmpDataRowsMaintConstLength(dataTable, cmpEntities) {

    var numberOfRows = appendCmpDataRows(dataTable, cmpEntities);

    if (dataTable.populated) {
	dataTable.removeRows(0, numberOfRows);
    }
    else {
	dataTable.populated = true;
    }
}

//
function createGenericTimestampGraphicsOptions(options) {

    options = $.extend({

	displayExactValues:true,
	dateFormat: "HH:mm EEE d MMM yyyy",
	dateFormat: "HH:mm d MMM yyyy",
	colors:['blue', 'green'],
	displayZoomButtons:false,
	displayRangeSelector: false,
	thickness:1,
	allowRedraw: true

    }, options);
    return options;
}


function createGenericDateGraphicsOptions(options) {

    options = $.extend({

	displayExactValues:true,
	dateFormat: "EEE d MMM yyyy",
	dateFormat2: "d MMM yyyy",
	colors:['blue', 'green'],
	displayZoomButtons:false,
	displayRangeSelector: false,
	thickness:1,
	allowRedraw: true

    }, options);
    return options;
}

function createGenericMonthGraphicsOptions(options) {

    options = $.extend({

	displayExactValues:true,
	dateFormat: "MMM yyyy",
	dateFormat2: "MMM yyyy",
	colors:['blue', 'green'],
	displayZoomButtons:false,
	displayRangeSelector: false,
	thickness:1,
	allowRedraw: true

    }, options);
    return options;
}


//
//
function createGenericDateCmpGraphicsOptions(options) {
    options = $.extend({

	displayExactValues:true,
	colors:['blue', 'green'],
	dateFormat: "EEE d MMM yyyy",
	dateFormat2: "d MMM yyyy",
	displayZoomButtons:false,
	displayRangeSelector: false,
	thickness:1,
	allowRedraw: true

    }, options);
    return options;
}

function createGenericMonthCmpGraphicsOptions(options) {

    options = $.extend({

	displayExactValues:true,
	colors:['blue', 'green'],
	dateFormat: "MMM yyyy",
	dateFormat2: "MMM yyyy",
	displayZoomButtons:false,
	displayRangeSelector: false,
	thickness:1,
	allowRedraw: true

    }, options);
    return options;
}

//
//
//
///
//
//
jQuery.loadJSON = function(uri, onSuccess) {
    var xhr = $.ajax({
	url : uri, dataType: "json",
	beforeSend: function() {
            // loadingIcon.show("slow");
        },
        complete: function() {
            // loadingIcon.hide("slow");
        },
        success: function(json) {
            if (onSuccess) {
        	onSuccess(json);
            }
        }
    });
};

function DrawReports(panels, _options, recordsPath) {
    this.$panels = $(panels);
    this.options = _options;
    this.recordsPath = recordsPath;
    this.dataTables = {};
    this.initialized = {};
    this.vizBoxIndexes = {};
    this.vizBoxColumns = {};
    this._vizTypes = {};
    this.vizOptions = {};
    this.clear();
    return true;
}

DrawReports.prototype.initializeOneTable = function(vizBoxPanelId, json, frequency, graphType, reinit){
    var _this = this;

    var currentOptions = _this.vizOptions[vizBoxPanelId];
    graphType = graphType || "AnnotatedTimeLine";
    _this._vizTypes[vizBoxPanelId] = graphType;

    var vizBoxPanel = _this.$panels.find(currentOptions.vizBoxPanel);
    var vizBox = vizBoxPanel.find('.graph-wrapper') [0];

    if (!vizBox) {
        // alert("Unknown '" + currentOptions.vizBoxPanel + "'");
        return;
    }


    var fquency = frequency || _this.options.frequency;
    var graphOptions = (fquency == "daily" || fquency == "weekly") ? createGenericDateGraphicsOptions() : 
	    (fquency == "monthly") ? createGenericMonthGraphicsOptions() : createGenericTimestampGraphicsOptions();

    if (currentOptions.cmpOptions) {
        _this.dataTables[currentOptions.vizBoxPanel] = createCmpDataTable(0, currentOptions.cmpOptions.dataColIndex, json[currentOptions.cmpOptions.cmpEntities], 
									  currentOptions.cmpOptions.cmpLabelProp, currentOptions.cmpOptions.cmpDataFrameProp, vizBox, 
									  graphOptions, $(vizBox).siblings(".viz-box-title2")[0], graphType);
    } else {
	var columns = json[_this.recordsPath]["$COLUMNS$"];
        if(!_this.vizBoxColumns[vizBoxPanelId]){
            _this.vizBoxColumns[vizBoxPanelId] = _.clone(currentOptions.selectColumns);
        }
        var selectColumns = _this.vizBoxColumns[vizBoxPanelId];
        _this.dataTables[currentOptions.vizBoxPanel] = createDataTable(columns, selectColumns, vizBox, graphOptions, vizBoxPanel.find(".viz-box-title .left .text")[0], graphType);
    }

    _this.$panels.find(currentOptions.vizBoxPanel).each(function() {
        $(this).find('.graph-wrapper').empty();
        this.populated = false;
    });
};

DrawReports.prototype.addColumn = function(vizBoxPanelId, colIndx){
    var _this = this;
    _this.vizBoxColumns[vizBoxPanelId].push(colIndx);	
};

DrawReports.prototype.removeColumn = function(vizBoxPanelId, colIndx){
    var _this = this;
    _this.vizBoxColumns[vizBoxPanelId] = _.without(_this.vizBoxColumns[vizBoxPanelId], colIndx);
};

DrawReports.prototype.drawOne = function(vizBoxPanelId, json, frequency, graphType, reinit){
    var _this = this;
  
    if (!_this.initialized[vizBoxPanelId] || reinit) {
    	this.initializeOneTable(vizBoxPanelId, json, frequency, graphType, reinit);
	_this.initialized[vizBoxPanelId] = true;
    }
    var currentOptions = _this.vizOptions[vizBoxPanelId];		
    var dataTable = _this.dataTables[currentOptions.vizBoxPanel];

    if (dataTable) {

    	if (currentOptions.cmpOptions) {
    	    appendCmpDataRows(dataTable, json[currentOptions.cmpOptions.cmpEntities]);
    	} else {
    	    appendDataRowsMaintConstLength(dataTable, json[_this.recordsPath]["$RECORDS$"]);
    	}
	redrawGraphic(dataTable);
    }

    if (_this.options.ajaxStatus) {
    	$(_this.options.ajaxStatus).text("ready");
    }
};

DrawReports.prototype.draw = function(json, frequency, graphType, reinit) {
    var _this = this;

    _.each(_this.options, function(currentOptions, i) {

	var vizBoxPanel = _this.$panels.find(currentOptions.vizBoxPanel);
	var vixBox = vizBoxPanel.find('.graph-wrapper') [0];

	if (!vixBox) {
	    alert("Unknown '" + currentOptions.vizBoxPanel + "'");
            return;
        }

        var vizBoxPanelId = vizBoxPanel[0].id;
        _this.vizOptions[vizBoxPanelId] = currentOptions;
        _this.vizBoxIndexes[vizBoxPanel[0].id] = i;
	_this.drawOne(vizBoxPanelId, json, frequency, graphType, reinit);
    });      
};

DrawReports.prototype.getVizBoxIndexes = function(json) {
    var _this = this;
    return _this.vizBoxIndexes;
};

DrawReports.prototype.clear = function(json) {
    var _this = this;
    _.each(_this.options, function(currentOptions, i) {

	var vizBoxPanel = _this.$panels.find(currentOptions.vizBoxPanel);
	var vixBox = vizBoxPanel.find('.graph-wrapper').html("<div>No data available</div>");
	_this.initialized[vizBoxPanel.id] = false;

	if (!vixBox) {
	    alert("Unknown '" + currentOptions.vizBoxPanel + "'");
            return;
        }
    }); 
};