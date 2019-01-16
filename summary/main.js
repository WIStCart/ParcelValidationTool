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
                <FieldsList fields={this.state.validation.Fields_Diffs} legacyFields={this.state.validation.County_Info.Legacy} />
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
    for (var i in f)
      if (Math.abs(l[i] - f[i]) != 0){
        tableArray.push(
          <tr>
            <td style={{  textAlign: "left" }}><a style={{ fontWeight: 'bold'}}>{i + ": "}</a></td>
            <td style={{ textAlign: "right" }}>{l[i] - f[i]}</td>
          </tr>

        );
      }
    return tableArray
}
  render() {
      return (
      <div className="tablecase">
        <tr className="table">
          <th style={{  textAlign: "left", width: "70%" }}>Field</th>
          <th style={{ textAlign: "right", fontWeight: "30%" }}>Change</th>
        </tr>
        <hr/>
        <tr className="table">{this.list()}</tr>
      </div>
  );
  }
}
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
          var lv = (Number(p[i])).toLocaleString(navigator.language, { minimumFractionDigits: 0 })

          listArray.push(
            <tr>
              <td style={{  textAlign: "left" }}><a style={{ fontWeight: 'bold'}}>{x + ": "}</a></td>
              <td style={{ textAlign: "right" }}>{lv}</td>
            </tr>
          );
      }
      return listArray
    }
    render() {
    return (
     <div>
       <h2 id = "smallerrors"> FLAGS IN OUTPUT FEATURE CLASS</h2>
       <p>The following lines summarize the element-specific errors that were found while validating your parcel dataset.  The stats below are meant as a means of reviewing the output.  <text class='attention'>Please see the GeneralElementErrors, AddressElementErrors, TaxrollElementErrors, and GeometricElementErrors fields within the output feature class to address these errors individually</text>. <text class="click-note">(click element for info)</text></p>
       <tr className="table">{this.list()}</tr>
     </div>
    );
    }
}

//This component renders the list of broad level errors items and sets up a tooltip on them to render on click.
class BroadLevelErrors extends React.Component {
  list(){
    var p = this.props.broadLevel
    var e = this.props.broadLevelexp
    var listArray = []
    for (var i in p){

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
          <tr>
            <td style={{  textAlign: "left" }}><a style={{ fontWeight: 'bold'}}>{x + ": "}</a></td>
            <td style={{ textAlign: "right" }}>{t + " " + z}</td>
          </tr>
        );
    }
    return listArray
  }
  render() {
    return (
       <div>
        <h2 id = "smallerrors"> GENERAL FILE ERRORS</h2>
        <p>The following lines explain any broad geometric errors that were found while validating your parcel dataset.
        If any of the "Missing Records" values are greater than 0, please add missing values. <text class="click-note">(click element for info)</text></p>
        <tr className="data"> {this.list()}</tr>
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
            <tr>
              <td style={{  textAlign: "left" }}><a style={{ fontWeight: 'bold'}}>{z + year + ": "}</a></td>
              <td style={{ textAlign: "right" }}>{+ p[i] + "%"}</td>
            </tr>
          );
      }
      return listArray
    }
    render() {
      return (
         <div id="broadlevel">
            <div id="broadlevelparent">
                <h3 id = "smallerrors"  class= "tax-roll-missing" >Tax Roll Percentages</h3>
                <tr className="data"> {this.list()}</tr>
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
              <td style={{  textAlign: "left" }}><a style={{ fontWeight: 'bold'}}>{x + ": "}</a></td>
              <td style={{ textAlign: "right" }}>{lv}</td>
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
                <tr className="data"> {this.list()}</tr>
            </div>
         </div>
      );
    }
}
// The following three components render the lists of Positive, Negative, and Zero value fields in the expandable area below the chart. They also setup a tooltip

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
