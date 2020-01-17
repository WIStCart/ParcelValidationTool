"use strict";

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

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
var schemaOrder = ["STATEID", "PARCELID", "TAXPARCELID", "PARCELDATE", "TAXROLLYEAR", "OWNERNME1", "OWNERNME2", "PSTLADRESS", "SITEADRESS", "ADDNUMPREFIX", "ADDNUM", "ADDNUMSUFFIX", "PREFIX", "STREETNAME", "STREETTYPE", "SUFFIX", "LANDMARKNAME", "UNITTYPE", "UNITID", "PLACENAME", "ZIPCODE", "ZIP4", "STATE", "SCHOOLDIST", "SCHOOLDISTNO", "CNTASSDVALUE", "LNDVALUE", "IMPVALUE", "MFLVALUE", "ESTFMKVALUE", "NETPRPTA", "GRSPRPTA", "PROPCLASS", "AUXCLASS", "ASSDACRES", "DEEDACRES", "GISACRES", "CONAME", "LOADDATE", "PARCELFIPS", "PARCELSRC", "LONGITUDE", "LATITUDE"];

var fieldStyle = {
  height: 25,
  textAlign: "left",
  border: ".0px solid black",
  backgroundColor: "#9c27b000",
  borderBottomWidth: 0,
  borderRightWidth: 0.0,
  minWidth: '131px',
  verticalAlign: "bottom"
};
var changeStyle = {
  textAlign: "right",
  backgroundColor: "#9c27b000",
  border: ".0px solid black",
  borderBottomWidth: 0,
  borderLeftWidth: 0,
  minWidth: '62px',
  verticalAlign: "bottom"
};
var changeHeaderStyle = {
  textAlign: "left",
  backgroundColor: "#9c27b000",
  border: ".0px solid black",
  borderBottomWidth: 0,
  borderLeftWidth: 0,
  minWidth: '62px',
  verticalAlign: "bottom"
};
var directiveStyle = {
  textAlign: "left",
  backgroundColor: "#9c27b000",
  border: ".0px solid black",
  borderBottomWidth: 0,
  borderLeftWidth: 0,
  minWidth: '131px',
  verticalAlign: "bottom",
  paddingLeft: '3px'

  //three variables declared for sorting the data into three categories.
  // This is the main App component
};
var App = function (_React$Component) {
  _inherits(App, _React$Component);

  function App(props) {
    _classCallCheck(this, App);

    var _this = _possibleConstructorReturn(this, (App.__proto__ || Object.getPrototypeOf(App)).call(this, props));

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
        // callback function for the asyncronous setState call.
      }, function () {
        return console.log("State: ", _this2.state.validation, _this2.state.explanations);
      });
    }

    //main render function of the App component

  }, {
    key: "render",
    value: function render() {
      var mr = this.state.validation.Records_Missing;
      var mrExplained = this.state.explanations.Records_Missing;

      var tr = this.state.validation.Tax_Roll_Years_Pcnt;
      var trExplained = this.state.explanations.Tax_Roll_Years_Pcnt;

      var fd = this.state.validation.Fields_Diffs;
      var fdExplained = this.state.explanations.Fields_Diffs;

      var inL = this.state.validation.inLineErrors;
      var inLExplained = this.state.explanations.inLineErrors;

      var bLL = this.state.validation;
      var bLLExplained = this.state.explanations;

      var coInfo = this.state.validation.County_Info;
      return React.createElement(
        "div",
        null,
        React.createElement(
          "div",
          { id: "summary", className: "bricks" },
          React.createElement(
            "h1",
            null,
            "Validation Summary Page - ",
            coInfo.CO_NAME.charAt(0) + coInfo.CO_NAME.slice(1).toLowerCase(),
            " ",
            React.createElement("img", { className: "img-responsive", src: "withumb.png", alt: "", height: "30", width: "30" })
          ),
          React.createElement(
            "div",
            { style: { marginLeft: 10, textAlign: "left" } },
            "Summary of possible errors found by the Validation Tool, for which you must:"
          ),
          React.createElement(
            "ol",
            null,
            React.createElement(
              "li",
              { style: { textAlign: "left" } },
              React.createElement(
                "b",
                null,
                "Eliminate."
              ),
              " Eliminate the flags. Go back to the output feature class to resolve each error by making the data consistent with the schema specs in ",
              React.createElement(
                "a",
                { href: "https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf", target: "_blank" },
                "Submission Documentation"
              ),
              ", or,"
            ),
            React.createElement(
              "li",
              { style: { textAlign: "left" } },
              React.createElement(
                "b",
                null,
                "Explain."
              ),
              " Provide explanations in writing for any legitimately missing/non-conforming data in the ",
              React.createElement(
                "a",
                { href: "https://www.sco.wisc.edu/parcels/tools/Validation/Validation_Tool_Guide.pdf#nameddest=inputting_explain_certification", target: "_blank" },
                "Explain-Certification.txt"
              ),
              " file."
            )
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
            React.createElement(BroadLevelErrors, { broadLevel: bLL, broadLevelexp: bLLExplained })
          )
        ),
        React.createElement(
          "div",
          { id: "row" },
          React.createElement(
            "div",
            { id: "comparison", className: "bricks" },
            React.createElement(
              "h2",
              null,
              "ATTRIBUTE COMPARISON"
            ),
            React.createElement(FieldsList, { fields: this.state.validation.Fields_Diffs, legacyFields: this.state.validation.County_Info.Legacy })
          )
        ),
        React.createElement(
          "div",
          { id: "row" },
          React.createElement(
            "div",
            { id: "next", className: "bricks" },
            React.createElement(
              "h2",
              null,
              "NEXT STEPS"
            ),
            React.createElement(
              "h3",
              { "class": "next-steps-h3 margin-h3" },
              "VALIDATE WITH VALIDATION TOOL"
            ),
            React.createElement(
              "ul",
              { className: "Pdata" },
              React.createElement(
                "li",
                null,
                "Work to either ",
                React.createElement(
                  "b",
                  { style: { color: "#000000" } },
                  "eliminate"
                ),
                " or ",
                React.createElement(
                  "b",
                  { style: { color: "#000000" } },
                  "explain"
                ),
                " each error message on this Validation_Summary_Page"
              ),
              React.createElement(
                "li",
                null,
                "Run Validation Tool in FINAL mode"
              ),
              React.createElement(
                "li",
                null,
                "Input your Explain-Certification.txt file"
              ),
              React.createElement(
                "li",
                null,
                "Save the \".ini\" file\u2014which is your *mandatory* submission form"
              )
            ),
            React.createElement(
              "h3",
              { "class": "next-steps-h3" },
              "ZIP & SUBMIT"
            ),
            React.createElement(
              "ul",
              { className: "Pdata" },
              React.createElement(
                "li",
                null,
                "Submit .ini Submission Form + data"
              )
            )
          )
        )
      );
    }
  }]);

  return App;
}(React.Component);

//This component renders the "more" information above the chart.


var FieldsList = function (_React$Component2) {
  _inherits(FieldsList, _React$Component2);

  function FieldsList() {
    _classCallCheck(this, FieldsList);

    return _possibleConstructorReturn(this, (FieldsList.__proto__ || Object.getPrototypeOf(FieldsList)).apply(this, arguments));
  }

  _createClass(FieldsList, [{
    key: "list",
    value: function list() {
      var f = this.props.fields;
      var l = this.props.legacyFields;
      var tableArray = [];
      var i = "";
      for (var g in schemaOrder) {
        // Use schemaOrder to implement the order of the Statewide Schema
        if (f.hasOwnProperty(schemaOrder[g])) {
          // some fields in the schemaOrder are not displayed (dont exist in the output .JSON from the tool)
          i = schemaOrder[g];
          var directiveString = "";
          var valueString = "";
          var negativeAddOn = "/omissions";

          if (f[i] > 0) {
            valueString = React.createElement(
              "text",
              null,
              "+ ",
              String(Number(Math.abs(f[i])).toLocaleString(navigator.language, { minimumFractionDigits: 0 }))
            );
            negativeAddOn = "";
          } else {
            if (Math.abs(f[i]) == 0) {
              valueString = React.createElement(
                "text",
                null,
                String(Number(Math.abs(f[i])).toLocaleString(navigator.language, { minimumFractionDigits: 0 }))
              );
            } else {
              valueString = React.createElement(
                "text",
                null,
                React.createElement(
                  "b",
                  null,
                  "-"
                ),
                " ",
                String(Number(Math.abs(f[i])).toLocaleString(navigator.language, { minimumFractionDigits: 0 }))
              );
            }
          }
          if (Math.abs(f[i]) != 0) {
            directiveString = "records compared to last year's dataset. Inspect the " + i + " field for possible errors" + negativeAddOn + ".";
          }
          tableArray.push(React.createElement(
            "tr",
            { style: { backgroundColor: "#9c27b000" }, mag: l[i] - f[i] },
            React.createElement(
              "td",
              { style: fieldStyle },
              React.createElement(
                "a",
                { href: "https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf#nameddest=" + i.toLowerCase(), target: "_blank", style: { fontWeight: 'bold', padding: '3px' } },
                i + ": "
              )
            ),
            React.createElement(
              "td",
              { style: changeStyle },
              React.createElement(
                "a",
                { style: { padding: '3px' } },
                valueString
              )
            ),
            React.createElement(
              "td",
              { style: directiveStyle },
              directiveString
            )
          ));
        }
      }
      /**
      tableArray = tableArray.sort(function(a,b){
        var mag_a = a.props.mag;
        var mag_b = b.props.mag;
        return mag_b - mag_a;
       })
       **/
      return tableArray;
    }
  }, {
    key: "render",
    value: function render() {
      var array = this.list();
      var m = Math.floor(array.length / 2);
      var first = array.slice(0, array.length);
      //var second = array.slice(m, array.length)
      var tableHeader = [React.createElement(
        "th",
        { style: fieldStyle },
        React.createElement("a", { style: { padding: '3px' } })
      ), React.createElement(
        "th",
        { colspan: "2", style: changeHeaderStyle },
        React.createElement(
          "a",
          { style: { padding: '3px' } },
          "Difference Compared to Last Year's Dataset - Click attribute name to view schema definition"
        )
      )];

      return React.createElement(
        "div",
        { className: "tablecase" },
        React.createElement(
          "tr",
          { className: "table", style: { border: "0.0px solid black", borderWidth: "0px 0px 0px 0px" } },
          tableHeader[0],
          tableHeader[1],
          first
        )
      );
    }
  }]);

  return FieldsList;
}(React.Component);

//This component renders the list of inline errors items and sets up a tooltip on them to render on click.


var greater0 = {
  padding: '0px',
  color: '#dc143c',
  fontWeight: 'bold'
};
var equalLess0 = {
  padding: '0px',
  color: '#000000',
  fontWeight: 'bold'
};

var InLineErrors = function (_React$Component3) {
  _inherits(InLineErrors, _React$Component3);

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
        var x = i.split("_").join(" Element ");
        if (Number(p[i]) == 0) {
          var lv = "None.";
          var lv2 = "";
          var st = equalLess0;
        } else {
          var lv = Number(p[i]).toLocaleString(navigator.language, { minimumFractionDigits: 0 });
          var lv2 = " possible errors found.  See the attribute table in the output feature class to resolve these.";
          var st = greater0;
        }

        listArray.push(React.createElement(
          "div",
          { "class": "general-file-errors" },
          React.createElement(
            "text",
            { style: { fontWeight: 'bold' } },
            x + ": "
          ),
          React.createElement(
            "text",
            { style: st },
            lv
          ),
          React.createElement(
            "text",
            { style: { padding: '0px' } },
            lv2
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
          " FLAGS IN OUTPUT FEATURE CLASS"
        ),
        React.createElement(
          "div",
          { "class": "flags-in-fc" },
          this.list()
        ),
        React.createElement(
          "p",
          { "class": "flag-note" },
          "*There are detailed error messages associated with these flags, which have been added to your output feature class.",
          React.createElement("br", null),
          React.createElement("br", null),
          " Scroll to the far right of the attribute table, sort each of the 4 error fields in descending order, and work to either ",
          React.createElement(
            "b",
            { style: { color: '#000000' } },
            "eliminate"
          ),
          " or ",
          React.createElement(
            "b",
            { style: { color: '#000000' } },
            "explain"
          ),
          " each error message."
        )
      );
    }
  }]);

  return InLineErrors;
}(React.Component);

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

var BroadLevelErrors = function (_React$Component4) {
  _inherits(BroadLevelErrors, _React$Component4);

  function BroadLevelErrors() {
    _classCallCheck(this, BroadLevelErrors);

    return _possibleConstructorReturn(this, (BroadLevelErrors.__proto__ || Object.getPrototypeOf(BroadLevelErrors)).apply(this, arguments));
  }

  _createClass(BroadLevelErrors, [{
    key: "list",
    value: function list() {
      /////////////////////////////
      // Add general (broad-level) errors
      var p = this.props.broadLevel.broadLevelErrors;
      var e = this.props.broadLevelexp.broadLevelErrors;
      var listArray = [];
      for (var i in p) {
        var x = i.split("_").join(" ");
        if (p[i] == "None" || p[i] == "") {
          var z = "";
          var t = "None.";
          var y = "";
        } else if (p[i] != "None" && p[i] != "") {
          var splitable = String(p[i]);
          var z = "<p>" + window[i + "_Pre"] + "</p><p><b>" + splitable.split(" Please see ")[0] + "</b>";
          var t = "Attention required! " + window[i + "_Attn"];
          var y = window[i + "_Link"];
        }
        listArray.push(React.createElement(
          "div",
          { "class": "general-file-errors" },
          React.createElement(
            "text",
            { style: { fontWeight: 'bold' } },
            x + ": "
          ),
          React.createElement(
            "text",
            { style: { padding: '1px' } },
            t
          )
        ));
      }
      listArray.push(React.createElement(
        "div",
        { "class": "general-file-errors" },
        React.createElement("br", null)
      ));

      /////////////////////////////
      // Add missing records
      var m = this.props.broadLevel.Records_Missing;
      for (var l in m) {
        var y = l.split("_").join(" ");
        if (Number(m[l]) == 0) {
          var lv = "None.";
        } else {
          var lv = Number(m[l]).toLocaleString(navigator.language, { minimumFractionDigits: 0 }) + " missing values in this field. Populate " + y + " for ALL records in the dataset.";
        }
        listArray.push(React.createElement(
          "div",
          { "class": "general-file-errors" },
          React.createElement(
            "text",
            { style: { fontWeight: 'bold' } },
            y + ": "
          ),
          React.createElement(
            "text",
            { style: { padding: '1px' } },
            lv
          )
        ));
      }
      listArray.push(React.createElement(
        "div",
        { "class": "general-file-errors" },
        React.createElement("br", null)
      ));
      /////////////////////////////
      // Add tax roll year errors
      var p = this.props.broadLevel.Tax_Roll_Years_Pcnt;
      var orderArray = [["Expected_Taxroll_Year", "TAXROLLYEAR \"2019\" (Expected year value)"], ["Previous_Taxroll_Year", "TAXROLLYEAR \"2018\" (Previous year value)"], ["Future_Taxroll_Years", "TAXROLLYEAR \"2020 or 2021\" (Future year values)"], ["Other_Taxroll_Years", "TAXROLLYEAR (Other year values)"]]; // Determines the order to which the elements appear from top to bottom
      for (var l in orderArray) {
        //console.log(p)
        var i = orderArray[l][0];
        var x = orderArray[l][1]; //.split("_").join(" ")
        var z = x.replace(/Taxroll/g, "Tax Roll");
        listArray.push(React.createElement(
          "div",
          { "class": "general-file-errors" },
          React.createElement(
            "text",
            { style: { fontWeight: 'bold' } },
            z + ": "
          ),
          React.createElement(
            "text",
            { style: { padding: '1px' } },
            p[i] + "%"
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
          " GENERAL FILE ERRORS"
        ),
        React.createElement(
          "div",
          null,
          " ",
          this.list()
        )
      );
    }
  }]);

  return BroadLevelErrors;
}(React.Component);
////This component renders the list of Taxroll errors items and sets up a tooltip on them to render on click.
/* TaxRoll and MissingRecords classes Removed and content added to GENERAL FILE ERRORS
class TaxRoll extends React.Component {
    list(){
      var p = this.props.taxroll
      var e = this.props.taxrollexp
      var listArray = []
      var orderArray = ["Expected_Taxroll_Year", "Previous_Taxroll_Year", "Future_Taxroll_Years", "Other_Taxroll_Years"] // Determines the order to which the elements appear from top to bottom
      for (var l in orderArray){
          console.log(orderArray[l])
          console.log(p)

          var i = orderArray[l]
          console.log(i)
          var x = i.split("_").join(" ")
          var z = x.replace(/Taxroll/g, "Tax Roll")
          var d = new Date()
          var d = d.getFullYear()
          var h = ""
          var t = ""
          var year = "2018"
          if (i == "Previous_Taxroll_Year") {
              year = " (2017)"
              var h = "<br>" + '<a id="reportedValue">' + p[i] + "%" + '</a>' + " of the TAXROLLYEAR field contains previous (" + d + ") tax roll year values.<br><br>"

              if (p[i] > 0) {
                  var t = "<br>" + "Ensure that all TAXROLLYEAR values are valid and make sure to update other attributes appropriately so that this data is of the appropriate vintage. Under normal circumstances, the expected and future TAXROLLYEAR values should equal 100%. If TAXROLLYEAR values cannot be of the appropriate vintage, please include a general explanation of this in the <a href='https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf#nameddest=inputting_explain_certification' target='_blank'>Explain-Certification.txt.</a>"
              }
          }
          else if (i == "Expected_Taxroll_Year") {
              year = " (2018)"
              var h = "<br>" + '<a id="reportedValue">' + p[i] + "%" + '</a>' + " of the TAXROLLYEAR field contains expected (" + d + ") tax roll year values.<br>"

              if (p[i] <= 97) {
                  var t = "<br>" + " Under normal circumstances, the expected (" + d + ") and future (" + (d + 1) + ") TAXROLLYEAR values should equal 100% and expected TAXROLLYEAR values should account for no less than 97% of this field. Parcels may carry the future TAXROLLYEAR if the parcel will not be assessed until the next tax year (e.g. a split). If TAXROLLYEAR values cannot be of the appropriate vintage, please include a general explanation of this in the <a href='https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf#nameddest=inputting_explain_certification' target='_blank'>Explain-Certification.txt.</a>. <br><br> *Note that non-parcel features, such as ROW or Hydro, are excluded from this summary."
              }
          }
          else if (i == "Other_Taxroll_Years") {
                  year = ""
                  var h = "<br>" + '<a id="reportedValue">' + "0%" + '</a>' + " of the TAXROLLYEAR field contains values other than the previous (" + (d - 1) + "), future (" + (d + 1) + "), or expected (" + d + ") tax roll year.<br><br>"

                  if (p[i] > 0) {
                      var t = "<br>" + "Ensure that all TAXROLLYEAR values are valid and make sure to update other attributes appropriately so that this data is of the appropriate vintage. Under normal circumstances, the expected and future TAXROLLYEAR values should equal 100%. If TAXROLLYEAR values cannot be of the appropriate vintage, please include a general explanation of this in the <a href='https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf#nameddest=inputting_explain_certification' target='_blank'>Explain-Certification.txt.</a>."
              }
          }
          else if (i == "Future_Taxroll_Years") {
              year = ""
              var h = "<br>" + '<a id="reportedValue">' + p[i] + "%" + '</a>' +  " of the TAXROLLYEAR field contains future (" + d + ") tax roll year values.<br><br>"

              if (p[i] >= 3) {
                  var t = "<br>" + "Under normal circumstances, the expected (" + d + ") and future (" + (d + 1) + ") TAXROLLYEAR values should equal 100% and future TAXROLLYEAR values should account for no more than 3% of this field. Parcels may carry the future TAXROLLYEAR if the parcel will not be assessed until the next tax year (e.g. a split). If TAXROLLYEAR values cannot be of the appropriate vintage, please include a general explanation of this in the <a href='https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf#nameddest=inputting_explain_certification' target='_blank'>Explain-Certification.txt.</a>."
              }
          }
          listArray.push(
            <tr>
              <td style={fieldStyle}><a style={{ fontWeight: 'bold', padding: '10px'}}>{z + year + ": "}</a></td>
              <td style={changeStyle}><a style={{ padding: '10px'}}>{+ p[i] + "%"}</a></td>
            </tr>
          );
      }
      return listArray
    }
    render() {
      return (
         <div id="broadlevel">
            <div className="table">
                <h3 id = "smallerrors"  class= "tax-roll-missing" >Tax Roll Percentages</h3>
                <tr className="table" style={{border: "1px solid black", borderWidth: ".5px .5px 1px 0px", marginBottom: 5}}> {this.list()}</tr>
            </div>
         </div>
      );
    }
}
class MissingRecords extends React.Component {
    list(){
      var p = this.props.missing
      var e = this.props.missingexp
      var listArray = []
      for (var i in p){
          var x = i.split("_").join(" ")
          var lv = (Number(p[i])).toLocaleString(navigator.language, { minimumFractionDigits: 0 })
          listArray.push(
            <tr>
              <td style={fieldStyle}><a style={{ fontWeight: 'bold', padding: '10px'}}>{x + ": "}</a></td>
              <td style={changeStyle}><a style={{ padding: '10px'}}>{lv}</a></td>
            </tr>
          );
      }
      return listArray
    }
    render() {
      return (
         <div id="broadlevel">
            <div id="broadlevelparent">
                <h3 id = "smallerrors" class= "tax-roll-missing" >Missing Records</h3>
                <tr className="table" style={{border: "1px solid black", borderWidth: ".5px .5px 1px 0px"}}> {this.list()}</tr>
            </div>
         </div>
      );
    }
}
// The following three components render the lists of Positive, Negative, and Zero value fields in the expandable area below the chart. They also setup a tooltip
*/

ReactDOM.render(React.createElement(App, null), document.getElementById('root'));
