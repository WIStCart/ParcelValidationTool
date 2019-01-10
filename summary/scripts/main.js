const Tooltip = reactTippy.Tooltip;
const {ResponsiveContainer, BarChart, Bar, ReferenceLine, XAxis, YAxis, CartesianGrid, Legend, Cell} = window.Recharts;
const TooltipChart = window.Recharts.Tooltip;

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

//three variables declared for sorting the data into three categories.
const address = ["SUFFIX",
              "STREETTYPE",
              "STREETNAME",
              "PREFIX",
              "ADDNUMPREFIX",
              "ADDNUM",
              "ADDNUMSUFFIX",
              "SITEADRESS",
              "PSTLADRESS",
              "OWNERNME1",
              "OWNERNME2",
              "TAXROLLYEAR",
              "PARCELDATE",
              "TAXPARCELID",
              "PARCELID",
              "STATEID"]
const general =[
        "LANDMARKNAME",
        "PLACENAME",
        "UNITTYPE",
        "UNITID",
        "ZIPCODE",
        "ZIP4",
        "STATE",
        "SCHOOLDIST",
        "SCHOOLDISTNO"
      ]
const tax = [
        "LONGITUDE",
        "LOADDATE",
        "GISACRES",
        "LATITUDE",
        "AUXCLASS",
        "GRSPRPTA",
        "IMPVALUE",
        "ASSDACRES",
        "LNDVALUE",
        "NETPRPTA",
        "CONAME",
        "PARCELSRC",
        "DEEDACRES",
        "IMPROVED",
        "FORESTVALUE",
        "CNTASSDVALUE",
        "PARCELFIPS",
        "ESTFMKVALUE",
        "PROPCLASS"
      ]
// Variable declared for the colors for each category
const catColors = {
  tax: "#004282",
  general:"#002549",
  address:"#003466"
}

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
  //this function creates the data we want to work with for the chart out of the raw output JSON
  data(){
    var data=[]
    for (let i in testValues.County_Info.Legacy){
        // if change is zero don't display if old value is zero and new is X explain.
        if ((testValues.County_Info.Legacy[i] === 0) && (!(testValues.Fields_Diffs[i] === "0")) ){
          data.push({
           name: i,
           'Percentage of Last Years Value': 100,

           cat: general.indexOf(i) > -1 ? "general" : tax.indexOf(i) > -1 ? 'tax' : 'address',
           tell: ("There are: " + testValues.Fields_Diffs[i] + " new values since last submission.")
           })
        }
        // if neither field is null push the record.
         if ( (!(testValues.County_Info.Legacy[i] === null) && !(testValues.Fields_Diffs[i] === null)) ){
           //console.log("Field: ", i, "LEGACY: ", testValues.County_Info.Legacy[i], "New Value: ", testValues.Fields_Diffs[i])
           data.push({
            name: i,
            'Percentage of Last Years Value': getPcnt(testValues.County_Info.Legacy[i], testValues.Fields_Diffs[i]),
            cat: general.indexOf(i) > -1 ? "general" : tax.indexOf(i) > -1 ? 'tax' : 'address',
            tell: ("Last submission: " + (testValues.County_Info.Legacy[i]).toLocaleString(navigator.language, { minimumFractionDigits: 0 }) + "; This submission: " + (Number(testValues.Fields_Diffs[i]) +  testValues.County_Info.Legacy[i]).toLocaleString(navigator.language, { minimumFractionDigits: 0 }))
          })
           }
    }
    // filter the records for NaN percentages.
    data = data.filter(x => (!isNaN(x['Percentage of Last Years Value']) && !(x['Percentage of Last Years Value'] === 0)) )
    //sort the data by category so that each category is clumped on the graph.
    data = data.sort(function(a,b){
      var categoryA = a.cat.toLowerCase(), categoryB = b.cat.toLowerCase()
      if (categoryA > categoryB){
        return -1
      }
      if (categoryA < categoryB){
        return 1
      }
    })
    //console.log(data)
   return data
  }
  // the selected bar state is changed when this function fires
  onBarClick(bar) {
    this.setState({selectedBar: bar});
  }
  // this function updates the chart info panel beside the chart whenever the selected bar changes
  renderSelectedBar(bar) {
    // the following code generates the unique messages for each of the breakpoints >2.5%, <2.5% and if there were new values added with no previous existing values in the legacy data.
      var n = testValues.Fields_Diffs[bar.name]
      var o = testValues.County_Info.Legacy[bar.name]
      var t = testValues.County_Info.Total_Records
      var pct = getPcnt(o, n)
      var less = "<u><b id='less'>fewer</u></b>"
      var more = "<u><b id='more'>more</b></u>"
      var newV = "<u><b id='more'>new</b></u>"
      var refName = bar.name ? "https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf#nameddest=" + bar.name.toString().toLowerCase() : "blank"
      var target = "_blank"

      var total = pct.toString().replace("-", "") + "%  (" + Math.abs(Number(n)).toLocaleString(navigator.language, { minimumFractionDigits: 0 }) + " of " + Number(o).toLocaleString(navigator.language, { minimumFractionDigits: 0 }) + " records)"
          if (pct > 2.5) {
              var sub = pct + "% " + more + " non-null values than V4 data.<br><br>"
              var text = "There are " + pct + "% " + more + " " + `<a href=${refName} target=${target}>` + bar.name + "</a>" + " values than the number present in the final V4 data. This condition suggests there may be a problem within the " + bar.name + " field, please examine this field. This condition may also be the result of new parcels or new values added to the data (in which case they can be left as is.)";
          }
          else if (pct < -2.5) {
              pct = pct.toString().replace("-", "")
              var sub = pct + "% " + less + "  non-null values than V4 data.<br><br>"
              var text = "There are " + pct + "% " + less + " "+ bar.name + " values than the number present in the final V4 data. This condition suggests there may be a problem within the " + bar.name + " field, please examine this field."
          }
          else if (pct > -2.5 && pct < 2.5) {
              if ((pct < 2.5) && (pct > 0)) {
                  var sub = pct + "% " + more + " non-null values than V4 data.<br><br>"
                  var text = "There are " + pct + "% " + more + " " + bar.name + " values than the number present in the final V4 data."
              }
              else if ((pct > -2.5) && (pct < 0)) {
                  pct = pct.toString().replace("-", "")
                  var sub = pct + "% " + less + " non-null values than V4 data.<br><br>"
                  var text = "There are " + pct + "% " + less + " " + bar.name + " values than the number present in the final V4 data."
              }

          }
          else if (bar.name && isNaN(pct)){
              var sub = n + " " + newV + " non-null values added since V4 data submission. <br><br>"
              var text = "Keep up the good work!"
          }
       return (
           <div className='infoPanel'>
               <div id="tooltip">
                 <strong id= "infoTitle">
                   {bar.name}
                 </strong>

                 {sub ? <div dangerouslySetInnerHTML={{ __html: "<br>" + sub}}></div> : <strong>Click on a bar to display info.</strong>}
                 <div dangerouslySetInnerHTML={{ __html: text}}></div>
                 {isFinite(pct) ? <footer dangerouslySetInnerHTML={{ __html: total}}></footer> :  " "}
               </div>
           </div>
       );
    }
    // Function to add % signs to the Yaxis
    formatY(tickitem){
      return tickitem + "%"
    }

    startHelp =() => {
      if (this.state.helpName == 'Stop!') {
          this.setState({helpName:"Start Tutorial"})
          administerTutorial("stop")
      } else {
          this.setState({helpName:"Stop!"})
          administerTutorial("start")
      }
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

     const bLL = this.state.validation.broadLevelErrors;
     const bLLExplained = this.state.explanations.broadLevelErrors;

     const coInfo = this.state.validation.County_Info;
      return (

         <div>
             <button id="helpButton" onClick={this.startHelp}>{this.state.helpName}</button>
             <div id="summary" className="bricks">
               <h1> {coInfo.CO_NAME.charAt(0) + coInfo.CO_NAME.slice(1).toLowerCase()} Parcel Validation Summary <img className="img-responsive" src="withumb.png" alt="" height="30" width="30"/></h1><hr/>
               <p>This validation summary page contains an overview of <i>possible</i> errors found by the Parcel Validation Tool. Please review the contents of this file and make changes to your parcel dataset as necessary.</p>
             </div>
             <div id="row">
                <div id="inline" className="bricks">
                    <InLineErrors inline={inL} inlineexp ={inLExplained}/>
                </div>

                <div id="broad" className="bricks">
                    <BroadLevelErrors broadLevel={bLL} broadLevelexp={bLLExplained} />
                    <hr/>
                    <TaxRoll taxroll={tr} taxrollexp={trExplained} />
                    <MissingRecords missing={mr} missingexp={mrExplained} />
                </div>
              </div>
            <div id="comparison" className="bricks">
                <h2>Submission Comparison</h2>
                <p>BELOW IS A COMPARISON OF COMPLETENESS VALUES FROM YOUR PREVIOUS PARCEL SUBMISSION AND THIS CURRENT SUBMISSION. <text class='attention'>If the value shown is a seemingly large negative number, please verify that all data was joined correctly and no data was lost during processing</text>. Note: This does not necessarily mean your data is incorrect, we just want to highlight large discrepancies that could indicate missing or incorrect data. <text class="click-note">(click element for info)</text><ExtraInfo></ExtraInfo></p>
                <div id="chart">

                  <ResponsiveContainer className="chartChart" width="60%" height={350}>
                    <BarChart  data={this.data()}
                          margin={{top: 5, right: 30, left: 20, bottom: 5}}>
                       <CartesianGrid strokeDasharray="2 2"/>
                       <XAxis dataKey="name" hide="true"/>
                       <YAxis tickCount={7} tickFormatter={this.formatY}/>
                       <TooltipChart content={<CustomTooltip/>}/>
                       <Legend payload={
                        [
                          { id: 'General', value: 'General', type: 'rect', color: catColors.general},
                          { id: 'Address', value: 'Address', type: 'rect', color: catColors.address},
                          { id: 'Tax', value: 'Tax', type: 'rect', color: catColors.tax},
                        ]
                       }/>
                       <ReferenceLine y={0} stroke='#000'/>
                       <Bar onClick={this.onBarClick.bind(this)} dataKey="Percentage of Last Years Value">
                        {
                          this.data().map((entry, index) => (
                            <Cell  stroke={entry.name === this.state.selectedBar.name ? '#FFC90E' : "none"} strokeWidth={3} fill={entry.cat === "general" ? catColors.general : entry.cat === "tax" ? catColors.tax : catColors.address }/>
                          ))
                        }
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                  <ResponsiveContainer className="chartpair" width="35%" height={150} >
                    { this.state.selectedBar ? this.renderSelectedBar(this.state.selectedBar) : undefined }
                  </ResponsiveContainer>
                </div>
                <Expand>
                    <Positive positives={fd} fdexp={fdExplained}/>
                    <Zero zeroes={fd} fdexp={fdExplained}/>
                    <Negative negatives={fd} fdexp={fdExplained}/>
                </Expand>
            </div>

         </div>
      );
   }
}

// This component is for the hover tooltips on the chart area.
class CustomTooltip  extends React.Component{
  render() {
    const { active } = this.props;
    if (active) {
      const { payload, label } = this.props;
      return (
        <div className="custom-tooltip">
          <p className="label"><b>{label}</b> {":" + payload[0].value}%</p>
          <p className="intro">{payload[0].payload.tell}</p>
          <p className="desc">Click for field details.</p>
        </div>
      );
    }
    return null;
  }
};
//This component renders the "more" information above the chart.
class ExtraInfo extends React.Component {
    constructor(){
      super();
      this.state = {
         display: 'none',
         name: "More"
      };
    }

    showHide =() => {
        if (this.state.display == 'none') {
            this.setState({display:'block'});
            this.setState({name:"Less"})
        } else {
            this.setState({display:'none'});
            this.setState({name:"More"})
        }
    }

    render() {
        return (
        <div>
            <button id="moreButton" onClick={this.showHide}>{this.state.name}</button>
            <ul id ="extra" style={{display:this.state.display}}>
                <li className="noHover">
                It is expected that parcel submissions continue to grow in quality and attribute completeness, as well as natural increases in quantity of records. These subtle changes may be reflected in the chart and are not necessarily indicative of errors.
                </li>
                <li className="noHover">
                Significant differences, however, in the number of records populated from one submission to the next (e.g., from V4 to V5) are indications of possible error or possible improvement.
                </li>
                <li className="noHover">
                The chart below is created by comparing your current submission against what was established in the previous year’s parcel data (the final, standardized V4 statewide parcel layer).
                </li>
                <li className="noHover">
                Please take a moment to review this chart. When reviewing an exceptional field perhaps an explanation will be immediately apparent, if not, examine the attribute field for an explanation.  Explanations are uses by the parcel processing team and may be placed in the <a href="https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf#nameddest=inputting_explain_certification" target="_blank">Explain-Certification.txt.</a>
                </li>
                <li className="noHover">
                Note: An exceptional value does not necessarily mean your data is incorrect. This chart is intended to highlight large discrepancies that could indicate missing or incorrect data.
                </li>
            </ul>
        </div>
    );
    }
}
//This component renders the list of inline errors items and sets up a tooltip on them to render on click.
class InLineErrors extends React.Component {
    list(){
      var p = this.props.inline
      var e = this.props.inlineexp
      var listArray = []
      var taxOrderAray = ["General_Errors","Address_Errors","Tax_Errors","Geometric_Errors"] // Determines the order of elements from top to bottom
      for (var l in taxOrderAray){
          var i = taxOrderAray[l]
          var x = i.split("_").join(" ")
          var l = i.split("_")[0]
          var lv = (Number(p[i])).toLocaleString(navigator.language, { minimumFractionDigits: 0 })
          if (l == "Tax") {
              x = "Tax Roll Element Errors"
              var ds = {
                  color: catColors.tax
              }
          }
          else if (l == "Address") {
              x = "Address Element Errors"
              var ds = {
                  color: catColors.address
              }
          }
          else if (l == "General") {
              x = "General Element Errors"
              var ds = {
                  color: catColors.general
              }
          }
          else {
              x = "Geometric Element Errors"
              var ds = {
                  color: 'black'
              }
          }
          listArray.push(
            <Tooltip key={i}
               // options
               html={(
                <div id="errortooltip">
                  <strong>
                    {x}
                  </strong>
               <div style={ds} dangerouslySetInnerHTML={{ __html: "<br>" + "There were " + '<a id="reportedValue">' + lv +'</a>' + " errors found that relate to " + l.toLowerCase() + " attributes in the feature class. To review these errors, sort descending on the " + x + " field, which was added to your output feature class while executing the tool."}}></div>
                </div>
              )}
               position="top"
               trigger="click"
               animation = "fade"
               touchHold = "true"
               size = "large"
               offset = "-300"
               theme = "light"
             >
               <li /*style={ds}*/ className="lihover" id={i} key={i}><b>{x + ": "}</b> {lv}</li>
            </Tooltip>

          );
      }
      return listArray
    }
    render() {
    return (
     <div>
       <h2 id = "smallerrors"> In Line Errors</h2>
       <p>The following lines summarize the element-specific errors that were found while validating your parcel dataset.  The stats below are meant as a means of reviewing the output.  <text class='attention'>Please see the GeneralElementErrors, AddressElementErrors, TaxrollElementErrors, and GeometricElementErrors fields within the output feature class to address these errors individually</text>. <text class="click-note">(click element for info)</text></p>
        <ul className="data"> {this.list()}</ul>
     </div>
    );
    }
}
// Messages included in popup of each respective Broad Level error:
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
    var p = this.props.broadLevel
    var e = this.props.broadLevelexp
    var listArray = []
    for (var i in p){
        console.log(i)
       var x = i.split("_").join(" ")
        if ((p[i] == "None")||(p[i] == "")) {
            var z = "No action required"
            var t = "No broad-level errors found!"
            var y = ""
        }
        else if ((p[i] != "None")&&(p[i] != "")) {
            var splitable = String(p[i])
            var z = "<p>" + window[ i + "_Pre"] + "</p><p><b>" + splitable.split(" Please see ")[0] + "</b>"
            var t = "<text class='attention-required'>Attention required! </text>" + window[ i + "_Attn"]
            var y = window[ i + "_Link"]
        }
        listArray.push(
          <Tooltip key={i}
             // options
             html={(
              <div id="errortooltip">
              <p dangerouslySetInnerHTML={{ __html: z}}></p>
              <p dangerouslySetInnerHTML={{ __html: y}}></p>
              </div>
            )}
             position="top"
             trigger="click"
             animation = "fade"
             touchHold = "true"
             size = "large"
             offset = "-300"
             theme = "light"
           >
             <li className="lihover" id={i} key={i}><b>{x + ": "}</b> <text dangerouslySetInnerHTML={{ __html: t}}></text></li>
          </Tooltip>

        );
    }
    return listArray
  }
  render() {
    return (
       <div>
        <h2 id = "smallerrors"> Broad Level Errors</h2>
        <p>The following lines explain any broad geometric errors that were found while validating your parcel dataset.
        If any of the "Missing Records" values are greater than 0, please add missing values. <text class="click-note">(click element for info)</text></p>
        <ul className="data"> {this.list()}</ul>
       </div>
    );
  }
}
////This component renders the list of Taxroll errors items and sets up a tooltip on them to render on click.
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
            <Tooltip  id="errortooltip" key={i}
               // options
               html={(
                <div id="errortooltip">
                <strong>
                  {z}

                </strong>
                <div dangerouslySetInnerHTML={{ __html: h + t}}></div>
                </div>
              )}
               position="top"
               trigger="click"
               animation = "fade"
               touchHold = "true"
               size = "large"
               offset = "-300"
               theme = "light"
             >
               <li className="lihover" id={i} key={i}><b>{z + year + ": "}</b> {+ p[i] + "%"}</li>
            </Tooltip>

          );
      }
      return listArray
    }
    render() {
      return (
         <div id="broadlevel">
            <div id="broadlevelparent">
                <h3 id = "smallerrors"  class= "tax-roll-missing" >Tax Roll Percentages</h3>
                <ul className="data"> {this.list()}</ul>
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
          var y = x.split(" ")[1]
          var lv = (Number(p[i])).toLocaleString(navigator.language, { minimumFractionDigits: 0 })
          if (p[i] > 0) {
              var innerText = "There are " + '<a id="reportedValue">' +  lv + '</a>'  + " missing values in this field. Please ensure that all values in the " + y + " field are populated appropriately."
          }
          else if (e[i] == 0) {
              var innerText = "There are 0 missing values in this field, no action required."
          }
          if (y.charAt(y.length - 1) == "E") {
              var t = " (County Name)"
          }
          else if (y.charAt(y.length - 1) == "C") {
              var t = " (Parcel Source Name)"
          }
          else if (y.charAt(y.length - 1) == "S") {
              var t = " (Parcel Source FIPS)"
          }
          var fieldName = "<text class='bold-fieldname'>" + y + t + "</tex><br><br>"
          listArray.push(
            <Tooltip key={i}
               // options
               html={(
                <div id="errortooltip">
                <div dangerouslySetInnerHTML={{ __html: fieldName}}></div>
                <div dangerouslySetInnerHTML={{ __html: innerText}}></div>
                </div>
              )}
               position="top"
               trigger="click"
               animation = "fade"
               touchHold = "true"
               size = "large"
               offset = "-300"
               theme = "light"
             >
               <li className="lihover" id={i} key={i}><b>{x + ": "}</b> {lv}</li>
            </Tooltip>
          );
      }
      return listArray
    }
    render() {
      return (
         <div id="broadlevel">
            <div id="broadlevelparent">
                <h3 id = "smallerrors" class= "tax-roll-missing" >Missing Records</h3>
                <ul className="data"> {this.list()}</ul>
            </div>
         </div>
      );
    }
}
// The following three components render the lists of Positive, Negative, and Zero value fields in the expandable area below the chart. They also setup a tooltip
class Zero extends React.Component {
  list(){
    var p = this.props.zeroes
    var e = this.props.fdexp
    var listArray = []
    for (var i in p){
      if (p[i] == 0){
        listArray.push(
          <Tooltip key={i}
             // options
             html={(
              <div id="tippytooltip">
              <strong>
                {i}
              </strong>
              <div dangerouslySetInnerHTML={{ __html: e[i]}}></div>
              </div>
            )}
             position="top"
             trigger="click"
             animation = "fade"
             touchHold = "true"
             size = "large"
             offset = "-300"
             theme = "light"
           >
             <li className="lihover" key={i}><a id={i} value={p[i]} id="desc">{i + ": "}</a> {+ p[i]}</li>
          </Tooltip>
        );
      }
    }
    return listArray
  }
   render() {
      return (
         <div id="zeroes" className="values">

            <h2 id="fields">Zero Diference</h2>
            <p>No change in value from the previous submission. Double check that this fits with current submission.</p>
             <ul className="Pdata">
             {this.list()}
             </ul>

         </div>

      );
   }
}
class Positive extends React.Component {
  list(){
    var p = this.props.positives
    var e = this.props.fdexp
    var listArray = []
    for (var i in p){
      if (p[i] > 0){

        listArray.push(
          <Tooltip key={i}
             // options
             html={(
              <div id="tippytooltip">
              <strong>
                {i}
              </strong>
              <div dangerouslySetInnerHTML={{ __html: e[i]}}></div>
              </div>
            )}
             position="top"
             trigger="click"
             animation = "fade"
             touchHold = "true"
             size = "large"
             offset = "-300"
             theme = "light"
           >
             <li className="lihover" key={i}><a id={i} value={p[i]} id="desc">{i + ": "}</a> {+ p[i]}</li>
          </Tooltip>

        );
      }
    }
    return listArray.sort(function(a, b){return a.props.value - b.props.value});
  }
   render() {

      return (

         <div id="positives" className="values">
          <h2 id="fields">Positive Difference</h2>
           <p>Error/Flag: Value is significant in the positive direction. This difference could be indicative of an improvement in data.</p>
           <ul className="Pdata">
           {this.list()}
           </ul>
         </div>

      );
   }
}
class Negative extends React.Component {
  list(){
    var p = this.props.negatives
    var e = this.props.fdexp
    var listArray = []
    for (var i in p){
      if (p[i] < 0){
        listArray.push(
          <Tooltip key={i}
             // options
             html={(
              <div id="tippytooltip">
              <strong>
                {i}
              </strong>
              <div dangerouslySetInnerHTML={{ __html: e[i]}}></div>
              </div>
            )}
             position="top"
             trigger="click"
             animation = "fade"
             touchHold = "true"
             size = "large"
             offset = "-300"
             theme = "light"
           >
             <li className="lihover" key={i}><a id={i} value={p[i]} id="desc">{i + ": "}</a> {+ p[i]}</li>
          </Tooltip>
        );
      }
    }

    return listArray.sort(function(a, b){return a.props.value - b.props.value});
  }
   render() {
      return (
         <div id="negatives" className="values" >
            <h2 id="fields">Negative Difference</h2>
            <p>Error/Flag: Value is significant in the negative direction. This difference could be indicative of a problem in data.</p>
             <ul className="Pdata" >
             {this.list()}
             </ul>
         </div>

      );
   }
}
// This component renders the expandable area below the chart theat houses the above three components : Zero, Positive, Negative
class Expand extends React.Component {

   constructor(){
     super();
     this.state = {
        height:'.5em'
     };
   }

  countLines =() => {
    let height = this.testComp.offsetHeight;
    if ( (height - 2 ) / 16 > 3.3 ) {
       this.setState({showButton:true});
    }
  }

  showHidePara =() => {
     if (this.state.height == 'auto') {
        this.setState({height:'.5em'});
     } else {
        this.setState({height:'auto'});
     }
  }

  componentDidMount() {
      this.countLines();
  }

  render() {
    return (
    < div>
        { this.state.showButton ? <button id="subbutton"onClick={this.showHidePara}> + </button>: null}
        <div id ="parent" style={{height:this.state.height}}>

          <div id = "content" ref={(c) => this.testComp = c } style={{height:'auto'}}>
         {this.props.children}
         </div>
      </div>
    </div>
    );
  }
}


ReactDOM.render(<App/>,document.getElementById('root'));

// Animated tutorial (using jQuery because it is fastest to implement right now)
var broad_A
var inline_B
var summary_C

var interval_X = 6000;

var interval_Y_obj
var interval_Y = 1000;

var firstRound = true;

function administerTutorial(_directive){
  if (_directive == "stop"){
    clearTimeout(broad_A);
    clearTimeout(inline_B);
    clearTimeout(summary_C);
    clearInterval(interval_Y_obj);
    $("#inline").css("opacity","1")
    $("#comparison").css("opacity","1")
    $("#summary").css("opacity","1")
    $("#broad").css("opacity","1")
    $("#summary").trigger( "click" ); // to disengage any on-click popups that may be open
    $(".fake-highlight").removeClass("fake-highlight")
    $("#popupHider").append($("#popupTutorial"))
  }else{
    $("#inline").css("opacity","0.25")
    $("#comparison").css("opacity","0.25")
    $("#summary").css("opacity","0.25")
    if (firstRound){
      $("#summary").append("<div id='popupTutorial' class='popup-tutorial'><img style='width: 20px; position:absolute;' src='pointer.png' alt='pointer'></div>");
      $("#summary").append("<div id='popupHider' class='popup-hider'></div>");
      firstRound = false;
    }
    feed(["Geometric_File_Error","Geometric_Misplacement_Flag","Coded_Domain_Fields"])


    broad_A = setTimeout(function(){
      $("#summary").trigger( "click" ); // to disengage any on-click popups that may be open
      $("#inline").css("opacity","1")
      $("#broad").css("opacity","0.25")
      feed(["General_Errors","Address_Errors","Tax_Errors","Geometric_Errors"])
    }, interval_X);

    inline_B = setTimeout(function(){
      $("#summary").trigger( "click" ); // to disengage any on-click popups that may be open
      $("#comparison").css("opacity","1")
      $("#inline").css("opacity","0.25")
    }, interval_X * 2);

    summary_C = setTimeout(function(){
      $("#summary").trigger( "click" ); // to disengage any on-click popups that may be open
      $("#helpButton").trigger( "click" ); // to disengage any on-click popups that may be open
      administerTutorial("stop")
    }, interval_X * 3);
  }
}

function feed(_ids){
  var count_Y = 0
  switch_Y();
  interval_Y_obj = setInterval(switch_Y, 1000);
  function switch_Y(){
    if (count_Y > _ids.length){
      clearInterval(interval_Y_obj);
      $("#" + _ids[_ids.length - 1] ).trigger( "click" );
    }else{
      $(".fake-highlight").removeClass("fake-highlight")
      $("#" + _ids[count_Y] ).addClass("fake-highlight").append($("#popupTutorial"))
      count_Y++;
    }
  }
}
