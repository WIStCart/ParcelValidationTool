"use strict";

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Tooltip = reactTippy.Tooltip;
var _window$Recharts = window.Recharts,
    ResponsiveContainer = _window$Recharts.ResponsiveContainer,
    BarChart = _window$Recharts.BarChart,
    Bar = _window$Recharts.Bar,
    ReferenceLine = _window$Recharts.ReferenceLine,
    XAxis = _window$Recharts.XAxis,
    YAxis = _window$Recharts.YAxis,
    CartesianGrid = _window$Recharts.CartesianGrid,
    Legend = _window$Recharts.Legend,
    Cell = _window$Recharts.Cell;

var TooltipChart = window.Recharts.Tooltip;

// simple function for getting percent change negative or positive.
function getPcnt(oldNumber, newNumber) {
  if (newNumber == null) {
    return 0;
  } else {
    newNumber = Number(newNumber);
    var percentDifference = newNumber / oldNumber * 100;
    return percentDifference.toLocaleString(navigator.language, { minimumFractionDigits: 0, maximumFractionDigits: 2 });
  }
};

//three variables declared for sorting the data into three categories.
var address = ["SUFFIX", "STREETTYPE", "STREETNAME", "PREFIX", "ADDNUMPREFIX", "ADDNUM", "ADDNUMSUFFIX", "SITEADRESS", "PSTLADRESS", "OWNERNME1", "OWNERNME2", "TAXROLLYEAR", "PARCELDATE", "TAXPARCELID", "PARCELID", "STATEID"];
var general = ["LANDMARKNAME", "PLACENAME", "UNITTYPE", "UNITID", "ZIPCODE", "ZIP4", "STATE", "SCHOOLDIST", "SCHOOLDISTNO"];
var tax = ["LONGITUDE", "LOADDATE", "GISACRES", "LATITUDE", "AUXCLASS", "GRSPRPTA", "IMPVALUE", "ASSDACRES", "LNDVALUE", "NETPRPTA", "CONAME", "PARCELSRC", "DEEDACRES", "IMPROVED", "FORESTVALUE", "CNTASSDVALUE", "PARCELFIPS", "ESTFMKVALUE", "PROPCLASS"];
// Variable declared for the colors for each category
var catColors = {
  tax: "#004282",
  general: "#002549",
  address: "#003466"

  // This is the main App component
};
var App = function (_React$Component) {
  _inherits(App, _React$Component);

  function App(props) {
    _classCallCheck(this, App);

    var _this = _possibleConstructorReturn(this, (App.__proto__ || Object.getPrototypeOf(App)).call(this, props));

    _this.startHelp = function () {
      if (_this.state.helpName == 'Stop!') {
        _this.setState({ helpName: "Start Tutorial" });
        administerTutorial("stop");
      } else {
        _this.setState({ helpName: "Stop!" });
        administerTutorial("start");
      }
    };

    _this.state = {
      selectedBar: {},
      error: null,
      isLoaded: false,
      items: [],
      validation: [],
      explanations: [],
      helpName: "Start Tutorial"
    };
    return _this;
  }
  // when the component mounts we set the state to contain the values from the output JSON, they are in the console in a callback funtion.


  _createClass(App, [{
    key: "componentWillMount",
    value: function componentWillMount() {
      var _this2 = this;

      this.setState({
        validation: testValues,
        explanations: explain
      }, function () {
        return console.log("State: ", _this2.state.validation, _this2.state.explanations);
      });
    }
    //this function creates the data we want to work with for the chart out of the raw output JSON

  }, {
    key: "data",
    value: function data() {
      var data = [];

      for (var i in testValues.County_Info.Legacy) {
        // if change is zero don't display if old value is zero and new is X explain.
        if (testValues.County_Info.Legacy[i] === 0 && !(testValues.Fields_Diffs[i] === "0")) {
          data.push({
            name: i,
            'Percentage of Last Years Value': 100,
            cat: general.indexOf(i) > -1 ? "general" : tax.indexOf(i) > -1 ? 'tax' : 'address',
            tell: "There are: " + testValues.Fields_Diffs[i] + " new values since last submission."
          });
        }
        // if neither field is null push the record.
        if (!(testValues.County_Info.Legacy[i] === null) && !(testValues.Fields_Diffs[i] === null)) {
          //console.log("Field: ", i, "LEGACY: ", testValues.County_Info.Legacy[i], "New Value: ", testValues.Fields_Diffs[i])
          data.push({
            name: i,
            'Percentage of Last Years Value': getPcnt(testValues.County_Info.Legacy[i], testValues.Fields_Diffs[i]),
            cat: general.indexOf(i) > -1 ? "general" : tax.indexOf(i) > -1 ? 'tax' : 'address',
            tell: "Last submission: " + testValues.County_Info.Legacy[i].toLocaleString(navigator.language, { minimumFractionDigits: 0 }) + "; This submission: " + (Number(testValues.Fields_Diffs[i]) + testValues.County_Info.Legacy[i]).toLocaleString(navigator.language, { minimumFractionDigits: 0 })
          });
        }
      }
      // filter the records for NaN percentages.
      data = data.filter(function (x) {
        return !isNaN(x['Percentage of Last Years Value']) && !(x['Percentage of Last Years Value'] === 0);
      });
      //sort the data by category so that each category is clumped on the graph.
      data = data.sort(function (a, b) {
        var categoryA = a.cat.toLowerCase(),
            categoryB = b.cat.toLowerCase();
        if (categoryA > categoryB) {
          return -1;
        }
        if (categoryA < categoryB) {
          return 1;
        }
      });
      //console.log(data)
      return data;
    }
    // the selected bar state is changed when this function fires

  }, {
    key: "onBarClick",
    value: function onBarClick(bar) {
      this.setState({ selectedBar: bar });
    }
    // this function updates the chart info panel beside the chart whenever the selected bar changes

  }, {
    key: "renderSelectedBar",
    value: function renderSelectedBar(bar) {
      // the following code generates the unique messages for each of the breakpoints >2.5%, <2.5% and if there were new values added with no previous existing values in the legacy data.
      var n = testValues.Fields_Diffs[bar.name];
      var o = testValues.County_Info.Legacy[bar.name];
      var t = testValues.County_Info.Total_Records;
      var pct = getPcnt(o, n);
      var less = "<u><b id='less'>fewer</u></b>";
      var more = "<u><b id='more'>more</b></u>";
      var newV = "<u><b id='more'>new</b></u>";
      var refName = bar.name ? "https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf#nameddest=" + bar.name.toString().toLowerCase() : "blank"
      var target = "_blank"

      var total = pct.toString().replace("-", "") + "%  (" + Math.abs(Number(n)).toLocaleString(navigator.language, { minimumFractionDigits: 0 }) + " of " + Number(o).toLocaleString(navigator.language, { minimumFractionDigits: 0 }) + " records)";
      if (pct > 2.5) {
        var sub = pct + "% " + more + " non-null values than V4 data.<br><br>";
        var text = "There are " + pct + "% " + more + " " + `<a href=${refName} target=${target}>` + bar.name + "</a>" + " values than the number present in the final V4 data. This condition suggests there may be a problem within the " + bar.name + " field, please examine this field. This condition may also be the result of new parcels or new values added to the data (in which case they can be left as is.)";
      } else if (pct < -2.5) {
        pct = pct.toString().replace("-", "");
        var sub = pct + "% " + less + "  non-null values than V4 data.<br><br>";
        var text = "There are " + pct + "% " + less + " " + bar.name + " values than the number present in the final V4 data. This condition suggests there may be a problem within the " + bar.name + " field, please examine this field.";
      } else if (pct > -2.5 && pct < 2.5) {
        if (pct < 2.5 && pct > 0) {
          var sub = pct + "% " + more + " non-null values than V4 data.<br><br>";
          var text = "There are " + pct + "% " + more + " " + bar.name + " values than the number present in the final V4 data.";
        } else if (pct > -2.5 && pct < 0) {
          pct = pct.toString().replace("-", "");
          var sub = pct + "% " + less + " non-null values than V4 data.<br><br>";
          var text = "There are " + pct + "% " + less + " " + bar.name + " values than the number present in the final V4 data.";
        }
      } else if (bar.name && isNaN(pct)) {
        var sub = n + " " + newV + " non-null values added since V4 data submission. <br><br>";
        var text = "Keep up the good work!";
      }
      return React.createElement(
        "div",
        { className: "infoPanel" },
        React.createElement(
          "div",
          { id: "tooltip" },
          React.createElement(
            "strong",
            { id: "infoTitle" },
            bar.name
          ),
          sub ? React.createElement("div", { dangerouslySetInnerHTML: { __html: "<br>" + sub } }) : React.createElement(
            "strong",
            null,
            "Click on a bar to display info."
          ),
          React.createElement("div", { dangerouslySetInnerHTML: { __html: text } }),
          isFinite(pct) ? React.createElement("footer", { dangerouslySetInnerHTML: { __html: total } }) : " "
        )
      );
    }
    // Function to add % signs to the Yaxis

  }, {
    key: "formatY",
    value: function formatY(tickitem) {
      return tickitem + "%";
    }
  }, {
    key: "render",

    //main render function of the App component
    value: function render() {
      var _this3 = this;

      var mr = this.state.validation.Records_Missing;
      var mrExplained = this.state.explanations.Records_Missing;

      var tr = this.state.validation.Tax_Roll_Years_Pcnt;
      var trExplained = this.state.explanations.Tax_Roll_Years_Pcnt;

      var fd = this.state.validation.Fields_Diffs;
      var fdExplained = this.state.explanations.Fields_Diffs;

      var inL = this.state.validation.inLineErrors;
      var inLExplained = this.state.explanations.inLineErrors;

      var bLL = this.state.validation.broadLevelErrors;
      var bLLExplained = this.state.explanations.broadLevelErrors;

      var coInfo = this.state.validation.County_Info;
      return React.createElement(
        "div",
        null,
        React.createElement(
          "button",
          { id: "helpButton", onClick: this.startHelp },
          this.state.helpName
        ),
        React.createElement(
          "div",
          { id: "summary", className: "bricks" },
          React.createElement(
            "h1",
            null,
            " ",
            coInfo.CO_NAME.charAt(0) + coInfo.CO_NAME.slice(1).toLowerCase(),
            " Parcel Validation Summary ",
            React.createElement("img", { className: "img-responsive", src: "withumb.png", alt: "", height: "30", width: "30" })
          ),
          React.createElement("hr", null),
          React.createElement(
            "p",
            null,
            "This validation summary page contains an overview of ",
            React.createElement(
              "i",
              null,
              "possible"
            ),
            " errors found by the Parcel Validation Tool. Please review the contents of this file and make changes to your parcel dataset as necessary."
          )
        ),
        React.createElement(
          "div",
          { id: "row" },
          React.createElement(
            "div",
            { id: "inline", className: "bricks" },
            React.createElement(InLineErrors, { inline: inL, inlineexp: inLExplained })
          ),
          React.createElement(
            "div",
            { id: "broad", className: "bricks" },
            React.createElement(BroadLevelErrors, { broadLevel: bLL, broadLevelexp: bLLExplained }),
            React.createElement("hr", null),
            React.createElement(TaxRoll, { taxroll: tr, taxrollexp: trExplained }),
            React.createElement(MissingRecords, { missing: mr, missingexp: mrExplained })
          )
        ),
        React.createElement(
          "div",
          { id: "comparison", className: "bricks" },
          React.createElement(
            "h2",
            null,
            "Submission Comparison"
          ),
          React.createElement(
            "p",
            null,
            "BELOW IS A COMPARISON OF COMPLETENESS VALUES FROM YOUR PREVIOUS PARCEL SUBMISSION AND THIS CURRENT SUBMISSION. ",
            React.createElement(
              "text",
              { "class": "attention" },
              "If the value shown is a seemingly large negative number, please verify that all data was joined correctly and no data was lost during processing"
            ),
            ". Note: This does not necessarily mean your data is incorrect, we just want to highlight large discrepancies that could indicate missing or incorrect data. ",
            React.createElement(
              "text",
              { "class": "click-note" },
              "(click element for info)"
            ),
            React.createElement(ExtraInfo, null)
          ),
          React.createElement(
            "div",
            { id: "chart" },
            React.createElement(
              ResponsiveContainer,
              { className: "chartChart", width: "60%", height: 350 },
              React.createElement(
                BarChart,
                { data: this.data(),
                  margin: { top: 5, right: 30, left: 20, bottom: 5 } },
                React.createElement(CartesianGrid, { strokeDasharray: "2 2" }),
                React.createElement(XAxis, { dataKey: "name", hide: "true" }),
                React.createElement(YAxis, { tickCount: 7, tickFormatter: this.formatY }),
                React.createElement(TooltipChart, { content: React.createElement(CustomTooltip, null) }),
                React.createElement(Legend, { payload: [{ id: 'General', value: 'General', type: 'rect', color: catColors.general }, { id: 'Address', value: 'Address', type: 'rect', color: catColors.address }, { id: 'Tax', value: 'Tax', type: 'rect', color: catColors.tax }] }),
                React.createElement(ReferenceLine, { y: 0, stroke: "#000" }),
                React.createElement(
                  Bar,
                  { onClick: this.onBarClick.bind(this), dataKey: "Percentage of Last Years Value" },
                  this.data().map(function (entry, index) {
                    return React.createElement(Cell, { stroke: entry.name === _this3.state.selectedBar.name ? '#FFC90E' : "none", strokeWidth: 3, fill: entry.cat === "general" ? catColors.general : entry.cat === "tax" ? catColors.tax : catColors.address });
                  })
                )
              )
            ),
            React.createElement(
              ResponsiveContainer,
              { className: "chartpair", width: "35%", height: 150 },
              this.state.selectedBar ? this.renderSelectedBar(this.state.selectedBar) : undefined
            )
          ),
          React.createElement(
            Expand,
            null,
            React.createElement(Positive, { positives: fd, fdexp: fdExplained }),
            React.createElement(Zero, { zeroes: fd, fdexp: fdExplained }),
            React.createElement(Negative, { negatives: fd, fdexp: fdExplained })
          )
        )
      );
    }
  }]);

  return App;
}(React.Component);

// This component is for the hover tooltips on the chart area.


var CustomTooltip = function (_React$Component2) {
  _inherits(CustomTooltip, _React$Component2);

  function CustomTooltip() {
    _classCallCheck(this, CustomTooltip);

    return _possibleConstructorReturn(this, (CustomTooltip.__proto__ || Object.getPrototypeOf(CustomTooltip)).apply(this, arguments));
  }

  _createClass(CustomTooltip, [{
    key: "render",
    value: function render() {
      var active = this.props.active;

      if (active) {
        var _props = this.props,
            payload = _props.payload,
            label = _props.label;

        return React.createElement(
          "div",
          { className: "custom-tooltip" },
          React.createElement(
            "p",
            { className: "label" },
            React.createElement(
              "b",
              null,
              label
            ),
            " ",
            ":" + payload[0].value,
            "%"
          ),
          React.createElement(
            "p",
            { className: "intro" },
            payload[0].payload.tell
          ),
          React.createElement(
            "p",
            { className: "desc" },
            "Click for field details."
          )
        );
      }
      return null;
    }
  }]);

  return CustomTooltip;
}(React.Component);

;
//This component renders the "more" information above the chart.

var ExtraInfo = function (_React$Component3) {
  _inherits(ExtraInfo, _React$Component3);

  function ExtraInfo() {
    _classCallCheck(this, ExtraInfo);

    var _this5 = _possibleConstructorReturn(this, (ExtraInfo.__proto__ || Object.getPrototypeOf(ExtraInfo)).call(this));

    _this5.showHide = function () {
      if (_this5.state.display == 'none') {
        _this5.setState({ display: 'block' });
        _this5.setState({ name: "Less" });
      } else {
        _this5.setState({ display: 'none' });
        _this5.setState({ name: "More" });
      }
    };

    _this5.state = {
      display: 'none',
      name: "More"
    };
    return _this5;
  }

  _createClass(ExtraInfo, [{
    key: "render",
    value: function render() {
      return React.createElement(
        "div",
        null,
        React.createElement(
          "button",
          { id: "moreButton", onClick: this.showHide },
          this.state.name
        ),
        React.createElement(
          "ul",
          { id: "extra", style: { display: this.state.display } },
          React.createElement(
            "li",
            { className: "noHover" },
            "It is expected that parcel submissions continue to grow in quality and attribute completeness, as well as natural increases in quantity of records. These subtle changes may be reflected in the chart and are not necessarily indicative of errors."
          ),
          React.createElement(
            "li",
            { className: "noHover" },
            "Significant differences, however, in the number of records populated from one submission to the next (e.g., from V4 to V5) are indications of possible error or possible improvement."
          ),
          React.createElement(
            "li",
            { className: "noHover" },
            "The chart below is created by comparing your current submission against what was established in the previous year\u2019s parcel data (the final, standardized V4 statewide parcel layer)."
          ),
          React.createElement(
            "li",
            { className: "noHover" },
            "Please take a moment to review this chart. When reviewing an exceptional field perhaps an explanation will be immediately apparent, if not, examine the attribute field for an explanation.  Explanations are uses by the parcel processing team and may be placed in the ",
            React.createElement(
              "a",
              { href: "https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf#nameddest=inputting_explain_certification", target: "_blank" },
              "Explain-Certification.txt."
            )
          ),
          React.createElement(
            "li",
            { className: "noHover" },
            "Note: An exceptional value does not necessarily mean your data is incorrect. This chart is intended to highlight large discrepancies that could indicate missing or incorrect data."
          )
        )
      );
    }
  }]);

  return ExtraInfo;
}(React.Component);
//This component renders the list of inline errors items and sets up a tooltip on them to render on click.


var InLineErrors = function (_React$Component4) {
  _inherits(InLineErrors, _React$Component4);

  function InLineErrors() {
    _classCallCheck(this, InLineErrors);

    return _possibleConstructorReturn(this, (InLineErrors.__proto__ || Object.getPrototypeOf(InLineErrors)).apply(this, arguments));
  }

  _createClass(InLineErrors, [{
    key: "list",
    value: function list() {
      var p = this.props.inline;
      var e = this.props.inlineexp;
      var listArray = [];
      var taxOrderAray = ["General_Errors", "Address_Errors", "Tax_Errors", "Geometric_Errors"]; // Determines the order of elements from top to bottom
      for (var l in taxOrderAray) {
        var i = taxOrderAray[l];
        var x = i.split("_").join(" ");
        var l = i.split("_")[0];
        var lv = Number(p[i]).toLocaleString(navigator.language, { minimumFractionDigits: 0 });
        if (l == "Tax") {
          x = "Tax Roll Element Errors";
          var ds = {
            color: catColors.tax
          };
        } else if (l == "Address") {
          x = "Address Element Errors";
          var ds = {
            color: catColors.address
          };
        } else if (l == "General") {
          x = "General Element Errors";
          var ds = {
            color: catColors.general
          };
        } else {
          x = "Geometric Element Errors";
          var ds = {
            color: 'black'
          };
        }
        listArray.push(React.createElement(
          Tooltip,
          { key: i
            // options
            , html: React.createElement(
              "div",
              { id: "errortooltip" },
              React.createElement(
                "strong",
                null,
                x
              ),
              React.createElement("div", { style: ds, dangerouslySetInnerHTML: { __html: "<br>" + "There were " + '<a id="reportedValue">' + lv + '</a>' + " errors found that relate to " + l.toLowerCase() + " attributes in the feature class. To review these errors, sort descending on the " + x + " field, which was added to your output feature class while executing the tool." } })
            ),
            position: "top",
            trigger: "click",
            animation: "fade",
            touchHold: "true",
            size: "large",
            offset: "-300",
            theme: "light"
          },
          React.createElement(
            "li",
            { /*style={ds}*/className: "lihover", id: i, key: i },
            React.createElement(
              "b",
              null,
              x + ": "
            ),
            " ",
            lv
          )
        ));
      }
      return listArray;
    }
  }, {
    key: "render",
    value: function render() {
      return React.createElement(
        "div",
        null,
        React.createElement(
          "h2",
          { id: "smallerrors" },
          " In Line Errors"
        ),
        React.createElement(
          "p",
          null,
          "The following lines summarize the element-specific errors that were found while validating your parcel dataset.  The stats below are meant as a means of reviewing the output.  ",
          React.createElement(
            "text",
            { "class": "attention" },
            "Please see the GeneralElementErrors, AddressElementErrors, TaxrollElementErrors, and GeometricElementErrors fields within the output feature class to address these errors individually"
          ),
          ". ",
          React.createElement(
            "text",
            { "class": "click-note" },
            "(click element for info)"
          )
        ),
        React.createElement(
          "ul",
          { className: "data" },
          " ",
          this.list()
        )
      );
    }
  }]);

  return InLineErrors;
}(React.Component);
// Messages included in popup of each respective Broad Level error:


var Geometric_Misplacement_Flag_Link = "Please review the directives in the documentation here: <a class='breakable' href='http://www.sco.wisc.edu/parcels/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf' target='_blank'>http://www.sco.wisc.edu/parcels/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf</a> (section #2) for advice on how to project native data to the Statewide Parcel CRS.";
var Coded_Domain_Fields_Link = "Please ensure that all coded domains are removed from the feature class before submitting.";
var Geometric_File_Error_Link = "Please review the directives in the documentation here: <a class='breakable' href='https://www.sco.wisc.edu/parcels/tools/Validation/Validation_and_Submission_Tool_Guide.pdf#nameddest=geometric_file_errors' target='_blank'>https://www.sco.wisc.edu/parcels/tools/Validation/Validation_and_Submission_Tool_Guide.pdf#nameddest=geometric_file_errors</a>";
var Geometric_Misplacement_Flag_Pre = "";
var Coded_Domain_Fields_Pre = "<text class='normal-text'>The following fields contain coded domains or subtypes: </text>";
var Geometric_File_Error_Pre = "";
var Geometric_Misplacement_Flag_Attn = "Geometries appear to be misplaced.";
var Coded_Domain_Fields_Attn = "Coded domains or subtypes were found.";
var Geometric_File_Error_Attn = "Click for detail.";
//This component renders the list of broad level errors items and sets up a tooltip on them to render on click.

var BroadLevelErrors = function (_React$Component5) {
  _inherits(BroadLevelErrors, _React$Component5);

  function BroadLevelErrors() {
    _classCallCheck(this, BroadLevelErrors);

    return _possibleConstructorReturn(this, (BroadLevelErrors.__proto__ || Object.getPrototypeOf(BroadLevelErrors)).apply(this, arguments));
  }

  _createClass(BroadLevelErrors, [{
    key: "list",
    value: function list() {
      var p = this.props.broadLevel;
      var e = this.props.broadLevelexp;
      var listArray = [];
      for (var i in p) {
        console.log(i);
        var x = i.split("_").join(" ");
        if (p[i] == "None" || p[i] == "") {
          var z = "No action required";
          var t = "No broad-level errors found!";
          var y = "";
        } else if (p[i] != "None" && p[i] != "") {
          var splitable = String(p[i]);
          var z = "<p>" + window[i + "_Pre"] + "</p><p><b>" + splitable.split(" Please see ")[0] + "</b>";
          var t = "<text class='attention-required'>Attention required! </text>" + window[i + "_Attn"];
          var y = window[i + "_Link"];
        }
        listArray.push(React.createElement(
          Tooltip,
          { key: i
            // options
            , html: React.createElement(
              "div",
              { id: "errortooltip" },
              React.createElement("p", { dangerouslySetInnerHTML: { __html: z } }),
              React.createElement("p", { dangerouslySetInnerHTML: { __html: y } })
            ),
            position: "top",
            trigger: "click",
            animation: "fade",
            touchHold: "true",
            size: "large",
            offset: "-300",
            theme: "light"
          },
          React.createElement(
            "li",
            { className: "lihover", id: i, key: i },
            React.createElement(
              "b",
              null,
              x + ": "
            ),
            " ",
            React.createElement("text", { dangerouslySetInnerHTML: { __html: t } })
          )
        ));
      }
      return listArray;
    }
  }, {
    key: "render",
    value: function render() {
      return React.createElement(
        "div",
        null,
        React.createElement(
          "h2",
          { id: "smallerrors" },
          " Broad Level Errors"
        ),
        React.createElement(
          "p",
          null,
          "The following lines explain any broad geometric errors that were found while validating your parcel dataset. If any of the \"Missing Records\" values are greater than 0, please add missing values. ",
          React.createElement(
            "text",
            { "class": "click-note" },
            "(click element for info)"
          )
        ),
        React.createElement(
          "ul",
          { className: "data" },
          " ",
          this.list()
        )
      );
    }
  }]);

  return BroadLevelErrors;
}(React.Component);
////This component renders the list of Taxroll errors items and sets up a tooltip on them to render on click.


var TaxRoll = function (_React$Component6) {
  _inherits(TaxRoll, _React$Component6);

  function TaxRoll() {
    _classCallCheck(this, TaxRoll);

    return _possibleConstructorReturn(this, (TaxRoll.__proto__ || Object.getPrototypeOf(TaxRoll)).apply(this, arguments));
  }

  _createClass(TaxRoll, [{
    key: "list",
    value: function list() {
      var p = this.props.taxroll;
      var e = this.props.taxrollexp;
      var listArray = [];
      var orderArray = ["Expected_Taxroll_Year", "Previous_Taxroll_Year", "Future_Taxroll_Years", "Other_Taxroll_Years"]; // Determines the order to which the elements appear from top to bottom
      for (var l in orderArray) {
        console.log(orderArray[l]);
        console.log(p);

        var i = orderArray[l];
        console.log(i);
        var x = i.split("_").join(" ");
        var z = x.replace(/Taxroll/g, "Tax Roll");
        var d = new Date();
        var d = d.getFullYear();
        var h = "";
        var t = "";
        var year = "2018";
        if (i == "Previous_Taxroll_Year") {
          year = " (2017)";
          var h = "<br>" + '<a id="reportedValue">' + p[i] + "%" + '</a>' + " of the TAXROLLYEAR field contains previous (" + d + ") tax roll year values.<br><br>";

          if (p[i] > 0) {
            var t = "<br>" + "Ensure that all TAXROLLYEAR values are valid and make sure to update other attributes appropriately so that this data is of the appropriate vintage. Under normal circumstances, the expected and future TAXROLLYEAR values should equal 100%. If TAXROLLYEAR values cannot be of the appropriate vintage, please include a general explanation of this in the <a href='https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf#nameddest=inputting_explain_certification' target='_blank'>Explain-Certification.txt.</a>";
          }
        } else if (i == "Expected_Taxroll_Year") {
          year = " (2018)";
          var h = "<br>" + '<a id="reportedValue">' + p[i] + "%" + '</a>' + " of the TAXROLLYEAR field contains expected (" + d + ") tax roll year values.<br>";

          if (p[i] <= 97) {
            var t = "<br>" + " Under normal circumstances, the expected (" + d + ") and future (" + (d + 1) + ") TAXROLLYEAR values should equal 100% and expected TAXROLLYEAR values should account for no less than 97% of this field. Parcels may carry the future TAXROLLYEAR if the parcel will not be assessed until the next tax year (e.g. a split). If TAXROLLYEAR values cannot be of the appropriate vintage, please include a general explanation of this in the <a href='https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf#nameddest=inputting_explain_certification' target='_blank'>Explain-Certification.txt.</a>. <br><br> *Note that non-parcel features, such as ROW or Hydro, are excluded from this summary.";
          }
        } else if (i == "Other_Taxroll_Years") {
          year = "";
          var h = "<br>" + '<a id="reportedValue">' + "0%" + '</a>' + " of the TAXROLLYEAR field contains values other than the previous (" + (d - 1) + "), future (" + (d + 1) + "), or expected (" + d + ") tax roll year.<br><br>";

          if (p[i] > 0) {
            var t = "<br>" + "Ensure that all TAXROLLYEAR values are valid and make sure to update other attributes appropriately so that this data is of the appropriate vintage. Under normal circumstances, the expected and future TAXROLLYEAR values should equal 100%. If TAXROLLYEAR values cannot be of the appropriate vintage, please include a general explanation of this in the <a href='https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf#nameddest=inputting_explain_certification' target='_blank'>Explain-Certification.txt.</a>.";
          }
        } else if (i == "Future_Taxroll_Years") {
          year = "";
          var h = "<br>" + '<a id="reportedValue">' + p[i] + "%" + '</a>' + " of the TAXROLLYEAR field contains future (" + d + ") tax roll year values.<br><br>";

          if (p[i] >= 3) {
            var t = "<br>" + "Under normal circumstances, the expected (" + d + ") and future (" + (d + 1) + ") TAXROLLYEAR values should equal 100% and future TAXROLLYEAR values should account for no more than 3% of this field. Parcels may carry the future TAXROLLYEAR if the parcel will not be assessed until the next tax year (e.g. a split). If TAXROLLYEAR values cannot be of the appropriate vintage, please include a general explanation of this in the <a href='https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf#nameddest=inputting_explain_certification' target='_blank'>Explain-Certification.txt.</a>.";
          }
        }
        listArray.push(React.createElement(
          Tooltip,
          { id: "errortooltip", key: i
            // options
            , html: React.createElement(
              "div",
              { id: "errortooltip" },
              React.createElement(
                "strong",
                null,
                z
              ),
              React.createElement("div", { dangerouslySetInnerHTML: { __html: h + t } })
            ),
            position: "top",
            trigger: "click",
            animation: "fade",
            touchHold: "true",
            size: "large",
            offset: "-300",
            theme: "light"
          },
          React.createElement(
            "li",
            { className: "lihover", id: i, key: i },
            React.createElement(
              "b",
              null,
              z + year + ": "
            ),
            " ",
            +p[i] + "%"
          )
        ));
      }
      return listArray;
    }
  }, {
    key: "render",
    value: function render() {
      return React.createElement(
        "div",
        { id: "broadlevel" },
        React.createElement(
          "div",
          { id: "broadlevelparent" },
          React.createElement(
            "h3",
            { id: "smallerrors", "class": "tax-roll-missing" },
            "Tax Roll Percentages"
          ),
          React.createElement(
            "ul",
            { className: "data" },
            " ",
            this.list()
          )
        )
      );
    }
  }]);

  return TaxRoll;
}(React.Component);

var MissingRecords = function (_React$Component7) {
  _inherits(MissingRecords, _React$Component7);

  function MissingRecords() {
    _classCallCheck(this, MissingRecords);

    return _possibleConstructorReturn(this, (MissingRecords.__proto__ || Object.getPrototypeOf(MissingRecords)).apply(this, arguments));
  }

  _createClass(MissingRecords, [{
    key: "list",
    value: function list() {
      var p = this.props.missing;
      var e = this.props.missingexp;
      var listArray = [];
      for (var i in p) {
        var x = i.split("_").join(" ");
        var y = x.split(" ")[1];
        var lv = Number(p[i]).toLocaleString(navigator.language, { minimumFractionDigits: 0 });
        if (p[i] > 0) {
          var innerText = "There are " + '<a id="reportedValue">' + lv + '</a>' + " missing values in this field. Please ensure that all values in the " + y + " field are populated appropriately.";
        } else if (e[i] == 0) {
          var innerText = "There are 0 missing values in this field, no action required.";
        }
        if (y.charAt(y.length - 1) == "E") {
          var t = " (County Name)";
        } else if (y.charAt(y.length - 1) == "C") {
          var t = " (Parcel Source Name)";
        } else if (y.charAt(y.length - 1) == "S") {
          var t = " (Parcel Source FIPS)";
        }
        var fieldName = "<text class='bold-fieldname'>" + y + t + "</tex><br><br>";
        listArray.push(React.createElement(
          Tooltip,
          { key: i
            // options
            , html: React.createElement(
              "div",
              { id: "errortooltip" },
              React.createElement("div", { dangerouslySetInnerHTML: { __html: fieldName } }),
              React.createElement("div", { dangerouslySetInnerHTML: { __html: innerText } })
            ),
            position: "top",
            trigger: "click",
            animation: "fade",
            touchHold: "true",
            size: "large",
            offset: "-300",
            theme: "light"
          },
          React.createElement(
            "li",
            { className: "lihover", id: i, key: i },
            React.createElement(
              "b",
              null,
              x + ": "
            ),
            " ",
            lv
          )
        ));
      }
      return listArray;
    }
  }, {
    key: "render",
    value: function render() {
      return React.createElement(
        "div",
        { id: "broadlevel" },
        React.createElement(
          "div",
          { id: "broadlevelparent" },
          React.createElement(
            "h3",
            { id: "smallerrors", "class": "tax-roll-missing" },
            "Missing Records"
          ),
          React.createElement(
            "ul",
            { className: "data" },
            " ",
            this.list()
          )
        )
      );
    }
  }]);

  return MissingRecords;
}(React.Component);
// The following three components render the lists of Positive, Negative, and Zero value fields in the expandable area below the chart. They also setup a tooltip


var Zero = function (_React$Component8) {
  _inherits(Zero, _React$Component8);

  function Zero() {
    _classCallCheck(this, Zero);

    return _possibleConstructorReturn(this, (Zero.__proto__ || Object.getPrototypeOf(Zero)).apply(this, arguments));
  }

  _createClass(Zero, [{
    key: "list",
    value: function list() {
      var p = this.props.zeroes;
      var e = this.props.fdexp;
      var listArray = [];
      for (var i in p) {
        if (p[i] == 0) {
          listArray.push(React.createElement(
            Tooltip,
            { key: i
              // options
              , html: React.createElement(
                "div",
                { id: "tippytooltip" },
                React.createElement(
                  "strong",
                  null,
                  i
                ),
                React.createElement("div", { dangerouslySetInnerHTML: { __html: e[i] } })
              ),
              position: "top",
              trigger: "click",
              animation: "fade",
              touchHold: "true",
              size: "large",
              offset: "-300",
              theme: "light"
            },
            React.createElement(
              "li",
              { className: "lihover", key: i },
              React.createElement(
                "a",
                _defineProperty({ id: i, value: p[i] }, "id", "desc"),
                i + ": "
              ),
              " ",
              +p[i]
            )
          ));
        }
      }
      return listArray;
    }
  }, {
    key: "render",
    value: function render() {
      return React.createElement(
        "div",
        { id: "zeroes", className: "values" },
        React.createElement(
          "h2",
          { id: "fields" },
          "Zero Diference"
        ),
        React.createElement(
          "p",
          null,
          "No change in value from the previous submission. Double check that this fits with current submission."
        ),
        React.createElement(
          "ul",
          { className: "Pdata" },
          this.list()
        )
      );
    }
  }]);

  return Zero;
}(React.Component);

var Positive = function (_React$Component9) {
  _inherits(Positive, _React$Component9);

  function Positive() {
    _classCallCheck(this, Positive);

    return _possibleConstructorReturn(this, (Positive.__proto__ || Object.getPrototypeOf(Positive)).apply(this, arguments));
  }

  _createClass(Positive, [{
    key: "list",
    value: function list() {
      var p = this.props.positives;
      var e = this.props.fdexp;
      var listArray = [];
      for (var i in p) {
        if (p[i] > 0) {

          listArray.push(React.createElement(
            Tooltip,
            { key: i
              // options
              , html: React.createElement(
                "div",
                { id: "tippytooltip" },
                React.createElement(
                  "strong",
                  null,
                  i
                ),
                React.createElement("div", { dangerouslySetInnerHTML: { __html: e[i] } })
              ),
              position: "top",
              trigger: "click",
              animation: "fade",
              touchHold: "true",
              size: "large",
              offset: "-300",
              theme: "light"
            },
            React.createElement(
              "li",
              { className: "lihover", key: i },
              React.createElement(
                "a",
                _defineProperty({ id: i, value: p[i] }, "id", "desc"),
                i + ": "
              ),
              " ",
              +p[i]
            )
          ));
        }
      }
      return listArray.sort(function (a, b) {
        return a.props.value - b.props.value;
      });
    }
  }, {
    key: "render",
    value: function render() {

      return React.createElement(
        "div",
        { id: "positives", className: "values" },
        React.createElement(
          "h2",
          { id: "fields" },
          "Positive Difference"
        ),
        React.createElement(
          "p",
          null,
          "Error/Flag: Value is significant in the positive direction. This difference could be indicative of an improvement in data."
        ),
        React.createElement(
          "ul",
          { className: "Pdata" },
          this.list()
        )
      );
    }
  }]);

  return Positive;
}(React.Component);

var Negative = function (_React$Component10) {
  _inherits(Negative, _React$Component10);

  function Negative() {
    _classCallCheck(this, Negative);

    return _possibleConstructorReturn(this, (Negative.__proto__ || Object.getPrototypeOf(Negative)).apply(this, arguments));
  }

  _createClass(Negative, [{
    key: "list",
    value: function list() {
      var p = this.props.negatives;
      var e = this.props.fdexp;
      var listArray = [];
      for (var i in p) {
        if (p[i] < 0) {
          listArray.push(React.createElement(
            Tooltip,
            { key: i
              // options
              , html: React.createElement(
                "div",
                { id: "tippytooltip" },
                React.createElement(
                  "strong",
                  null,
                  i
                ),
                React.createElement("div", { dangerouslySetInnerHTML: { __html: e[i] } })
              ),
              position: "top",
              trigger: "click",
              animation: "fade",
              touchHold: "true",
              size: "large",
              offset: "-300",
              theme: "light"
            },
            React.createElement(
              "li",
              { className: "lihover", key: i },
              React.createElement(
                "a",
                _defineProperty({ id: i, value: p[i] }, "id", "desc"),
                i + ": "
              ),
              " ",
              +p[i]
            )
          ));
        }
      }

      return listArray.sort(function (a, b) {
        return a.props.value - b.props.value;
      });
    }
  }, {
    key: "render",
    value: function render() {
      return React.createElement(
        "div",
        { id: "negatives", className: "values" },
        React.createElement(
          "h2",
          { id: "fields" },
          "Negative Difference"
        ),
        React.createElement(
          "p",
          null,
          "Error/Flag: Value is significant in the negative direction. This difference could be indicative of a problem in data."
        ),
        React.createElement(
          "ul",
          { className: "Pdata" },
          this.list()
        )
      );
    }
  }]);

  return Negative;
}(React.Component);
// This component renders the expandable area below the chart theat houses the above three components : Zero, Positive, Negative


var Expand = function (_React$Component11) {
  _inherits(Expand, _React$Component11);

  function Expand() {
    _classCallCheck(this, Expand);

    var _this13 = _possibleConstructorReturn(this, (Expand.__proto__ || Object.getPrototypeOf(Expand)).call(this));

    _this13.countLines = function () {
      var height = _this13.testComp.offsetHeight;
      if ((height - 2) / 16 > 3.3) {
        _this13.setState({ showButton: true });
      }
    };

    _this13.showHidePara = function () {
      if (_this13.state.height == 'auto') {
        _this13.setState({ height: '.5em' });
      } else {
        _this13.setState({ height: 'auto' });
      }
    };

    _this13.state = {
      height: '.5em'
    };
    return _this13;
  }

  _createClass(Expand, [{
    key: "componentDidMount",
    value: function componentDidMount() {
      this.countLines();
    }
  }, {
    key: "render",
    value: function render() {
      var _this14 = this;

      return React.createElement(
        "div",
        null,
        this.state.showButton ? React.createElement(
          "button",
          { id: "subbutton", onClick: this.showHidePara },
          " + "
        ) : null,
        React.createElement(
          "div",
          { id: "parent", style: { height: this.state.height } },
          React.createElement(
            "div",
            { id: "content", ref: function ref(c) {
                return _this14.testComp = c;
              }, style: { height: 'auto' } },
            this.props.children
          )
        )
      );
    }
  }]);

  return Expand;
}(React.Component);

ReactDOM.render(React.createElement(App, null), document.getElementById('root'));

// Animated tutorial (using jQuery because it is fastest to implement right now)
var broad_A;
var inline_B;
var summary_C;

var interval_X = 6000;

var interval_Y_obj;
var interval_Y = 1000;

var firstRound = true;

function administerTutorial(_directive) {
  if (_directive == "stop") {
    clearTimeout(broad_A);
    clearTimeout(inline_B);
    clearTimeout(summary_C);
    clearInterval(interval_Y_obj);
    $("#inline").css("opacity", "1");
    $("#comparison").css("opacity", "1");
    $("#summary").css("opacity", "1");
    $("#broad").css("opacity", "1");
    $("#summary").trigger("click"); // to disengage any on-click popups that may be open
    $(".fake-highlight").removeClass("fake-highlight");
    $("#popupHider").append($("#popupTutorial"));
  } else {
    $("#inline").css("opacity", "0.25");
    $("#comparison").css("opacity", "0.25");
    $("#summary").css("opacity", "0.25");
    if (firstRound) {
      $("#summary").append("<div id='popupTutorial' class='popup-tutorial'><img style='width: 20px; position:absolute;' src='pointer.png' alt='pointer'></div>");
      $("#summary").append("<div id='popupHider' class='popup-hider'></div>");
      firstRound = false;
    }
    feed(["Geometric_File_Error", "Geometric_Misplacement_Flag", "Coded_Domain_Fields"]);

    broad_A = setTimeout(function () {
      $("#summary").trigger("click"); // to disengage any on-click popups that may be open
      $("#inline").css("opacity", "1");
      $("#broad").css("opacity", "0.25");
      feed(["General_Errors", "Address_Errors", "Tax_Errors", "Geometric_Errors"]);
    }, interval_X);

    inline_B = setTimeout(function () {
      $("#summary").trigger("click"); // to disengage any on-click popups that may be open
      $("#comparison").css("opacity", "1");
      $("#inline").css("opacity", "0.25");
    }, interval_X * 2);

    summary_C = setTimeout(function () {
      $("#summary").trigger("click"); // to disengage any on-click popups that may be open
      $("#helpButton").trigger("click"); // to disengage any on-click popups that may be open
      administerTutorial("stop");
    }, interval_X * 3);
  }
}

function feed(_ids) {
  var count_Y = 0;
  switch_Y();
  interval_Y_obj = setInterval(switch_Y, 1000);
  function switch_Y() {
    if (count_Y > _ids.length) {
      clearInterval(interval_Y_obj);
      $("#" + _ids[_ids.length - 1]).trigger("click");
    } else {
      $(".fake-highlight").removeClass("fake-highlight");
      $("#" + _ids[count_Y]).addClass("fake-highlight").append($("#popupTutorial"));
      count_Y++;
    }
  }
}
