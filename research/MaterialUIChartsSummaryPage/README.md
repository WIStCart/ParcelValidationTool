For viewing in developer mode:
1. Install https://nodejs.org/en/download
2. Verify existence of environmental variable in system path
3. Try `npm -v` or `node -v` in terminal
  - Try [powershell - How to fix "running scripts is disabled on this system"? - Stack Overflow ](https://stackoverflow.com/questions/64633727/how-to-fix-running-scripts-is-disabled-on-this-system) if you recieve script run disabled status when setting up node package manager (npm)
4. Install this repository
5. Enter repository within chosen programming environment
6. Try `npm install` in terminal
7. Once modules are installed, try `npm start` in terminal
8. The project should appear in the default web browser

For (re)building the project:
1. Try `npm build` in terminal

This new built folder can be copied over to the tool's directory and the filepath to allow the tool to access it can be modified in the ValidationToolScriptFoss.py at `jsonInject = base + '\summary\\build\static\js\#########.js'`

General Syntax in the App.js file and some descriptions:
```
const pulse = keyframes`
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
`;
...
  const [open, setOpen] = useState(false);

  const handleCopyFlagClick = (elementType, key) => {
    setOpen(true);
    navigator.clipboard.writeText(elementType + "LIKE '%" + key + "%'");
  };
...
<Typography variant="h3" gutterBottom fontWeight="fontWeightBold">
  Validation Summary Page - {testValues.County_Info.CO_NAME}{" "} <img src = {require("./withumb.png")} alt="" width = {35}/>
</Typography>

<Typography gutterBottom py={2} style={{textAlign: 'left'}}>
  Summary of possible errors found by the Validation Tool, for which you must:
  <List sx={{ listStyle: "decimal", pl: 4}}>
    <ListItem sx={{ display: "list-item"}}>
      <Box component="span" fontWeight="fontWeightBold">
        Eliminate.{" "}
      </Box>
      Go back to the output feature class to resolve each error by making the data consistent with the schema specs in {" "}
      <Link href = "https://www.sco.wisc.edu/parcels/Submission_Documentation.pdf">
        Submission Documentation
      </Link>.
    </ListItem>
    <ListItem sx={{ display: "list-item" }}>
      <Box component="span" fontWeight="fontWeightBold">
        Filter.{" "} 
      </Box>
      Scroll down this page to find flags on various attributes for given records. Click 
      <IconButton
        onClick={() => {
          handleCopyFlagClick("Copied ", "to clipboard!");
        }}
        color="primary"
        sx={{
          animation: `${pulse} 2s infinite`, // Apply pulsing animation
          ':hover': {
            animation: `${pulse} 1.5s infinite`, // Faster pulse on hover
          }
        }}
      >
        <CopyIcon /> 
      </IconButton> 
      at end of flag description and paste (Ctrl + V) in the expression section of the dialogue 
      box that appears found by choosing <img src = {require("./slctAttrIcon.png")} alt="" width = {115}/> in output feature class Attribute Table
      to find all records with chosen attribute error.
    </ListItem>
    <ListItem sx={{ display: "list-item" }}>
      <Box component="span" fontWeight="fontWeightBold">
        Explain.{" "}
      </Box>
      Provide explanations for any legitimately missing/non-conforming data in the {" "}
      <Link href = "https://www.sco.wisc.edu/parcels/tools/Validation/Validation_Tool_Guide.pdf#nameddest=inputting_explain_certification">
        Explain-Certification
      </Link> {" "}
      form on the Parcel Validation Tool User Interface.
    </ListItem>
  </List>
</Typography>
```
