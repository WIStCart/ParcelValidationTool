
// simple function for getting percent change negative or positive.
function getPcnt(oldNumber, newNumber){
  if (newNumber == null){
    return 0;
  }else{
    newNumber = Number(newNumber)
    var percentDifference = (newNumber / oldNumber) * 100
    return percentDifference.toLocaleString(navigator.language, { minimumFractionDigits: 0, maximumFractionDigits: 2 });
  }
};
var schemaOrder = ["STATEID",
  "PARCELID",
  "TAXPARCELID",
  "PARCELDATE",
  "TAXROLLYEAR",
  "OWNERNME1",
  "OWNERNME2",
  "PSTLADRESS",
  "SITEADRESS",
  "ADDNUMPREFIX",
  "ADDNUM",
  "ADDNUMSUFFIX",
  "PREFIX",
  "STREETNAME",
  "STREETTYPE",
  "SUFFIX",
  "LANDMARKNAME",
  "UNITTYPE",
  "UNITID",
  "PLACENAME",
  "ZIPCODE",
  "ZIP4",
  "STATE",
  "SCHOOLDIST",
  "SCHOOLDISTNO",
  "CNTASSDVALUE",
  "LNDVALUE",
  "IMPVALUE",
  "ESTFMKVALUE",
  "NETPRPTA",
  "GRSPRPTA",
  "PROPCLASS",
  "AUXCLASS",
  "ASSDACRES",
  "DEEDACRES",
  "GISACRES",
  "CONAME",
  "LOADDATE",
  "PARCELFIPS",
  "PARCELSRC",
  "LONGITUDE",
  "LATITUDE"]

var fieldStyle = {
  height: 25,
  textAlign: "left",
  border: ".0px solid black",
  backgroundColor: "#9c27b000",
  borderBottomWidth: 0,
  borderRightWidth:0.0,
  minWidth: '131px',
  verticalAlign:"bottom"
}
var changeStyle = {
  textAlign: "right",
  backgroundColor: "#9c27b000",
  border: ".0px solid black",
  borderBottomWidth: 0,
  borderLeftWidth:0,
  minWidth: '62px',
  verticalAlign:"bottom"
}
var changeHeaderStyle = {
  textAlign: "left",
  backgroundColor: "#9c27b000",
  border: ".0px solid black",
  borderBottomWidth: 0,
  borderLeftWidth:0,
  minWidth: '62px',
  verticalAlign:"bottom"
}
var directiveStyle = {
  textAlign: "left",
  backgroundColor: "#9c27b000",
  border: ".0px solid black",
  borderBottomWidth: 0,
  borderLeftWidth:0,
  minWidth: '131px',
  verticalAlign:"bottom",
  paddingLeft:'3px'
}

//three variables declared for sorting the data into three categories.
// This is the main App component
class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedBar: {},
      error: null,
      isLoaded: false,
      items: [],
      validation: [],
      explanations: [],
      helpName: "Start Tutorial"
    };
  }
  // when the component mounts we set the state to contain the values from the output JSON, they are in the console in a callback funtion.
  componentWillMount(){
    this.setState({
      validation: testValues,
      explanations: explain
    // callback function for the asyncronous setState call.
    }, () => console.log("State: ", this.state.validation, this.state.explanations)
  )
  }

    //main render function of the App component
   render() {
     const mr = this.state.validation.Records_Missing;
     const mrExplained = this.state.explanations.Records_Missing;

     const tr = this.state.validation.Tax_Roll_Years_Pcnt;
     const trExplained = this.state.explanations.Tax_Roll_Years_Pcnt;

     const fd = this.state.validation.Fields_Diffs;
     const fdExplained = this.state.explanations.Fields_Diffs;

     const inL = this.state.validation.inLineErrors;
     const inLExplained = this.state.explanations.inLineErrors;

     const bLL = this.state.validation;
     const bLLExplained = this.state.explanations;

     const coInfo = this.state.validation.County_Info;
      return (

         <div>
             <div id="summary" className="bricks">
               <h1>Validation Summary Page - {coInfo.CO_NAME.charAt(0) + coInfo.CO_NAME.slice(1).toLowerCase()} <img className="img-responsive" src="withumb.png" alt="" height="30" width="30"/></h1>
               <div style = {{marginLeft: 10, textAlign: "left"}}>Summary of possible errors found by the Validation Tool, for which you must:</div>
               <ol>
                  <li style = {{textAlign: "left"}}><b>Eliminate.</b> Eliminate the flags. Go back to the output feature class to resolve each error by making the data consistent with the schema specs in <a href="https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf" target="_blank">Submission Documentation</a>, or,</li>
                  <li style = {{textAlign: "left"}}><b>Explain.</b> Provide explanations in writing for any legitimately missing/non-conforming data in the <a href="https://www.sco.wisc.edu/parcels/tools/Validation/Validation_Tool_Guide.pdf#nameddest=inputting_explain_certification" target="_blank">Explain-Certification.txt</a> file.</li>
               </ol>
             </div>
             <div id="row">
                <div id="inline" className="bricks">
                    <InLineErrors inline={inL} inlineexp ={inLExplained}/>
                </div>

                <div id="broad" className="bricks">
                    <BroadLevelErrors broadLevel={bLL} broadLevelexp={bLLExplained} />
                </div>
              </div>
            <div id="row">
              <div id="comparison" className="bricks">
                  <h2>ATTRIBUTE COMPARISON</h2>
                  <FieldsList fields={this.state.validation.Fields_Diffs} legacyFields={this.state.validation.County_Info.Legacy} />
              </div>
            </div>
            <div id="row">
            <div id="next" className="bricks">
              <h2>NEXT STEPS</h2>
              <h3 class="next-steps-h3 margin-h3">VALIDATE WITH VALIDATION TOOL</h3>
                <ul className="Pdata">
                  <li>Work to either <b style = {{color:"#000000"}}>eliminate</b> or <b style = {{color:"#000000"}}>explain</b> each error message on this Validation_Summary_Page</li>
                  <li>Run Validation Tool in FINAL mode</li>
                  <li>Input your Explain-Certification.txt file</li>
                  <li>Save the ".ini" file—which is your *mandatory* submission form</li>
                </ul>
                <h3 class="next-steps-h3">ZIP & SUBMIT</h3>
                <ul className="Pdata">
                  <li>Submit .ini Submission Form + data</li>
                </ul>
            </div>
            </div>
          </div>
      );
   }
}

//This component renders the "more" information above the chart.
class FieldsList extends React.Component {
  list(){
    var f = this.props.fields
    var l = this.props.legacyFields
    var tableArray = []
    var i = ""
    for (var g in schemaOrder){ // Use schemaOrder to implement the order of the Statewide Schema
      if(f.hasOwnProperty(schemaOrder[g])){ // some fields in the schemaOrder are not displayed (dont exist in the output .JSON from the tool)
        i = schemaOrder[g]
        var directiveString = ""
        var valueString = ""
        var negativeAddOn = "/omissions"

        if ((f[i]) > 0){
          valueString = <text>+ {String((Number(Math.abs(f[i]))).toLocaleString(navigator.language, { minimumFractionDigits: 0 }))}</text>
          negativeAddOn = ""
        }else{
          if (Math.abs(f[i]) == 0){
            valueString = <text>{String((Number(Math.abs(f[i]))).toLocaleString(navigator.language, { minimumFractionDigits: 0 }))}</text>
          }else{
            valueString = <text><b>-</b> {String((Number(Math.abs(f[i]))).toLocaleString(navigator.language, { minimumFractionDigits: 0 }))}</text>
          }
        }
        if (Math.abs(f[i]) != 0){
          directiveString = "records compared to last year's dataset. Inspect the "+ i +" field for possible errors" + negativeAddOn + "."
        }
        tableArray.push(
          <tr style={{ backgroundColor: "#9c27b000"}} mag= {l[i] - f[i]}>
            <td style={fieldStyle}><a href={"https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf#nameddest=" +  i.toLowerCase()} target="_blank" style={{ fontWeight: 'bold', padding: '3px'}}>{i + ": "}</a></td>
            <td style={changeStyle}><a style={{ padding: '3px'}}>{valueString}</a></td>
            <td style={directiveStyle}>{directiveString}</td>
          </tr>
        );
        }
      }
      /**
      tableArray = tableArray.sort(function(a,b){
        var mag_a = a.props.mag;
        var mag_b = b.props.mag;
        return mag_b - mag_a;
       })
       **/
      return tableArray

}
  render() {
    var array = this.list()
    var m = Math.floor(array.length / 2)
    var first = array.slice(0, array.length)
    //var second = array.slice(m, array.length)
    var tableHeader = [<th style={fieldStyle}><a style={{ padding: '3px'}}></a></th>, <th colspan='2' style={changeHeaderStyle}><a style={{ padding: '3px'}}>Difference Compared to Last Year's Dataset - Click attribute name to view schema definition</a></th>]

      return (
      <div className="tablecase">
        <tr className="table" style={{border: "0.0px solid black", borderWidth: "0px 0px 0px 0px"}}>{tableHeader[0]}{tableHeader[1]}{first}</tr>
      </div>
  );
  }
}

//This component renders the list of inline errors items and sets up a tooltip on them to render on click.
var greater0 = {
  padding: '0px',
  color: '#dc143c',
  fontWeight:'bold'
}
var equalLess0 = {
  padding: '0px',
  color: '#000000',
  fontWeight:'bold'
}
class InLineErrors extends React.Component {
    list(){
      var p = this.props.inline
      var e = this.props.inlineexp
      var listArray = []
      var taxOrderAray = ["General_Errors","Address_Errors","Tax_Errors","Geometric_Errors"] // Determines the order of elements from top to bottom
      for (var l in taxOrderAray){
        var i = taxOrderAray[l]
        var x = i.split("_").join(" Element ")
        if (Number(p[i]) == 0){
          var lv = "None."
          var lv2 = ""
          var st = equalLess0
        }else{
          var lv = (Number(p[i])).toLocaleString(navigator.language, { minimumFractionDigits: 0 })
          var lv2 = " possible errors found.  See the attribute table in the output feature class to resolve these."
          var st = greater0
        }

        listArray.push(
          <div class="general-file-errors">
            <text style={{ fontWeight:'bold'}}>{x + ": "}</text>
            <text style={ st }>{lv}</text>
            <text style={{ padding: '0px' }}>{lv2}</text>
          </div>
        );
      }
      return listArray
    }
    render() {
    return (
     <div>
       <h2 id = "smallerrors"> FLAGS IN OUTPUT FEATURE CLASS</h2>
       <div class="flags-in-fc">
          {this.list()}
      </div>
       <p class="flag-note">*There are detailed error messages associated with these flags, which have been added to your output feature class.<br></br><br></br> Scroll to the far right of the attribute table, sort each of the 4 error fields in descending order, and work to either <b style={{ color:'#000000'}}>eliminate</b> or <b style={{ color:'#000000'}}>explain</b> each error message.</p>
     </div>
    );
    }
}
var Geometric_Misplacement_Flag_Link = "Please review the directives in the documentation here: <a class='breakable' href='http://www.sco.wisc.edu/parcels/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf' target='_blank'>http://www.sco.wisc.edu/parcels/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf</a> (section #2) for advice on how to project native data to the Statewide Parcel CRS."
var Coded_Domain_Fields_Link = "Please ensure that all coded domains are removed from the feature class before submitting."
var Geometric_File_Error_Link = "Please review the directives in the documentation here: <a class='breakable' href='https://www.sco.wisc.edu/parcels/tools/Validation/Validation_and_Submission_Tool_Guide.pdf#nameddest=geometric_file_errors' target='_blank'>https://www.sco.wisc.edu/parcels/tools/Validation/Validation_and_Submission_Tool_Guide.pdf#nameddest=geometric_file_errors</a>"
var Geometric_Misplacement_Flag_Pre = ""
var Coded_Domain_Fields_Pre = "<text class='normal-text'>The following fields contain coded domains or subtypes: </text>"
var Geometric_File_Error_Pre = ""
var Geometric_Misplacement_Flag_Attn = "Geometries appear to be misplaced."
var Coded_Domain_Fields_Attn = "Coded domains or subtypes were found."
var Geometric_File_Error_Attn = "Click for detail."
//This component renders the list of broad level errors items and sets up a tooltip on them to render on click.
class BroadLevelErrors extends React.Component {
  list(){
    /////////////////////////////
    // Add general (broad-level) errors
    var p = this.props.broadLevel.broadLevelErrors
    var e = this.props.broadLevelexp.broadLevelErrors
    var listArray = []
    for (var i in p){
       var x = i.split("_").join(" ")
        if ((p[i] == "None")||(p[i] == "")) {
            var z = ""
            var t = "None."
            var y = ""
        }
        else if ((p[i] != "None")&&(p[i] != "")) {
            var splitable = String(p[i])
            var z = "<p>" + window[ i + "_Pre"] + "</p><p><b>" + splitable.split(" Please see ")[0] + "</b>"
            var t = "Attention required! " + window[ i + "_Attn"]
            var y = window[ i + "_Link"]
        }
        listArray.push(
            <div class="general-file-errors">
              <text style={{ fontWeight:'bold'}}>{x + ": "}</text>
              <text style={{ padding: '1px'}}>{t}</text>
            </div>
        );
    }
    listArray.push(
      <div class="general-file-errors">
        <br></br>
      </div>
    );

    /////////////////////////////
    // Add missing records
    var m = this.props.broadLevel.Records_Missing
    for (var l in m){
      var y = l.split("_").join(" ")
      if (Number(m[l]) == 0){
        var lv = "None."
      }else{
        var lv = (Number(m[l])).toLocaleString(navigator.language, { minimumFractionDigits: 0 }) + " missing values in this field. Populate " + y + " for ALL records in the dataset."
      }
      listArray.push(
          <div class="general-file-errors">
            <text style={{ fontWeight:'bold'}}>{ y + ": "}</text>
            <text style={{ padding: '1px'}}>{lv}</text>
          </div>
      );
    }
    listArray.push(
      <div class="general-file-errors">
        <br></br>
      </div>
    );
    /////////////////////////////
    // Add tax roll year errors
    var p = this.props.broadLevel.Tax_Roll_Years_Pcnt
    var orderArray = [["Expected_Taxroll_Year","TAXROLLYEAR \"2019\" (Expected year value)"], ["Previous_Taxroll_Year","TAXROLLYEAR \"2018\" (Previous year value)"], ["Future_Taxroll_Years","TAXROLLYEAR \"2020 or 2021\" (Future year values)"], [ "Other_Taxroll_Years", "TAXROLLYEAR (Other year values)"]] // Determines the order to which the elements appear from top to bottom
    for (var l in orderArray){
      //console.log(p)
      var i = orderArray[l][0]
      var x = orderArray[l][1] //.split("_").join(" ")
      var z = x.replace(/Taxroll/g, "Tax Roll")
        listArray.push(
            <div class="general-file-errors">
              <text style={{ fontWeight:'bold'}}>{ z + ": "}</text>
              <text style={{ padding: '1px'}}>{p[i]+ "%"}</text>
            </div>
        );
    }
    return listArray
  }
  render() {
    return (
       <div>
        <h2 id = "smallerrors"> GENERAL FILE ERRORS</h2>
        <div> {this.list()}</div>
       </div>
    );
  }
}
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


ReactDOM.render(<App/>,document.getElementById('root'));
