import "./App.css";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import Typography from "@mui/material/Typography";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import { Grid } from "@mui/material";
import { useState } from "react";
import { IconButton, Snackbar } from "@mui/material";
import CopyIcon from "@mui/icons-material/ContentCopy";
import { testValues } from "./summary.js";
import { FieldDiffsBar } from "./fieldDiffsBarChart.js";
import { ThemeProvider, createTheme, keyframes } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Link from '@mui/material/Link';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import Tooltip from '@mui/material';

const darkTheme = createTheme({
  palette: {
    background: {
      default: '#CBDAEE',
      paper: '#fffff8',
    },
  },
});

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

const flagSumsNamesDictionary = {
  "General_Errors": "General Element Errors",
  "Geometric_Errors": "Geometric Element Errors",
  "Address_Errors": "Address Element Errors",
  "Tax_Errors": "Tax Element Errors",
  "Error_Sum": <b>Error Elements Sums</b>
}

const taxRollYearNamesDictionary = {
  "Previous_Taxroll_Year": new Date().getFullYear() - 1 + " (Previous Year Value)",
  "Expected_Taxroll_Year": new Date().getFullYear() + " (Expected Year Value)",
  "Future_Taxroll_Years": new Date().getFullYear() + 1 + " or " + (new Date().getFullYear() + 2) + " (Future Year Values)",
  "Other_Taxroll_Years": "Other Year Values"
}

function App() {
  const [open, setOpen] = useState(false);

  const handleCopyFlagClick = (elementType, key) => {
    setOpen(true);
    navigator.clipboard.writeText(elementType + "LIKE '%" + key + "%'");
  };

  return (
    <div className="App">
    <ThemeProvider theme={darkTheme}>
    <CssBaseline />
      <Box mx={24}>
        <Stack direction={"column"} spacing={1}>
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
            <Box component="span" fontWeight="fontWeightBold">
            </Box>
          </Typography>
          <Grid
            direction={"row"}
            justifyContent={"space-evenly"}
            container
          >
            <Box>
              <Accordion defaultExpanded>
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                  aria-controls="panel1-content"
                  id="panel1-header"
                >
                  <Typography fontWeight="fontWeightBold">Flag Sum</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Stack>
                    <div>
                      {Object.keys(testValues.inLineErrors).filter((key, index) => key != 'Geometric_Errors').map(
                        (key, index) => (
                          <Stack
                            direction="row"
                            spacing={4}
                            justifyContent={"space-between"}
                          >
                            <Box>
                              <Typography class="QueryText">
                                <p key={index}> {flagSumsNamesDictionary[key]}</p>
                              </Typography>
                            </Box>
                            <Box>
                              <Typography class="QueryText">
                                <p key={index}>
                                  {" "}
                                  <font color = "#DC143C" fontWeight = "bold">{testValues.inLineErrors[key]}</font>
                                </p>
                              </Typography>
                            </Box>
                          </Stack>
                        )
                      )}
                    </div>
                  </Stack>
                </AccordionDetails>
              </Accordion>
            </Box>
            <Box>
              <Accordion defaultExpanded>
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                  aria-controls="panel1-content"
                  id="panel1-header"
                >
                  <Typography fontWeight="fontWeightBold">
                    Taxroll Year
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <div>
                    {Object.keys(testValues.Tax_Roll_Years_Pcnt).map(
                      (key, index) => (
                        <Stack
                          direction="row"
                          spacing={4}
                          justifyContent={"space-between"}
                        >
                          <Box>
                            <Typography class="QueryText">
                              <p key={index}> {taxRollYearNamesDictionary[key]}</p>
                            </Typography>
                          </Box>
                          <Box>
                            <Typography class="QueryText">
                              <p key={index}>
                                {" "}
                                {Number(testValues.Tax_Roll_Years_Pcnt[key]).toFixed(1)}{"%"}
                              </p>
                            </Typography>
                          </Box>
                        </Stack>
                      )
                    )}
                  </div>
                </AccordionDetails>
              </Accordion>
            </Box>
          </Grid>

          <Accordion defaultExpanded>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              aria-controls="panel1-content"
              id="panel1-header"
              display="flex"
            >
              <Stack   
                direction="row"
                spacing={0}
                flex={1}
                sx={{
                  alignItems: "center",
                }}>
                <Typography align="left" fontWeight="fontWeightBold" flex={10.5}>
                  General Element Flags
                </Typography>
                <Typography fontWeight="fontWeightBold" flex={1}>
                  {testValues.inLineErrors.General_Errors}
                </Typography>
              </Stack>
            </AccordionSummary>
            <AccordionDetails align="center">
              <Stack>
                <div>
                  {Object.keys(testValues.Flags_Dictionary.General).map(
                    (key, index) => (
                      <Stack
                        direction="row"
                        spacing={4}
                        justifyContent="space-between"
                        alignItems="center"
                      >
                        <Box>
                          <Typography class="QueryText" align="left">
                            <p align = "left" key={index}> {key}</p>
                          </Typography>
                        </Box>
                        <Stack direction="row" alignItems="center" spacing={2}>
                          <Box>{testValues.Flags_Dictionary.General[key]}</Box>
                          <Box>
                            <IconButton
                              onClick={() => {
                                handleCopyFlagClick("generalElementError ", key);
                              }}
                              color="primary"
                            >
                              <CopyIcon />
                            </IconButton>
                          </Box>
                        </Stack>

                        <Snackbar
                          message="Copied to clipboard"
                          anchorOrigin={{
                            vertical: "top",
                            horizontal: "center",
                          }}
                          autoHideDuration={2000}
                          onClose={() => setOpen(false)}
                          open={open}
                        />
                      </Stack>
                    )
                  )}
                </div>
              </Stack>
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              aria-controls="panel1-content"
              id="panel1-header"
            >
              <Stack   
                direction="row"
                spacing={0}
                flex={1}
                sx={{
                  alignItems: "center",
                }}>
                <Typography align="left" fontWeight="fontWeightBold" flex={11.5}>
                  Address Element Flags
                </Typography>
                <Typography fontWeight="fontWeightBold" flex={1}>
                  {testValues.inLineErrors.Address_Errors}
                </Typography>
              </Stack>
            </AccordionSummary>
            <AccordionDetails>
              <Stack>
                <div>
                  {Object.keys(testValues.Flags_Dictionary.Address).map(
                    (key, index) => (
                      <Stack
                        direction="row"
                        spacing={4}
                        justifyContent="space-between"
                        alignItems="center"
                      >
                        <Box>
                          <Typography class="QueryText" align="left">
                            <p align = "left" key={index}> {key}</p>
                          </Typography>
                        </Box>
                        <Stack direction="row" alignItems="center" spacing={2}>
                          <Box>{testValues.Flags_Dictionary.Address[key]}</Box>
                          <Box>
                            <IconButton
                              onClick={() => {
                                handleCopyFlagClick("addressElementErrors ", key);
                              }}
                              color="primary"
                            >
                              <CopyIcon />
                            </IconButton>
                          </Box>
                        </Stack>

                        <Snackbar
                          message="Copied to clipboard"
                          anchorOrigin={{
                            vertical: "top",
                            horizontal: "center",
                          }}
                          autoHideDuration={2000}
                          onClose={() => setOpen(false)}
                          open={open}
                        />
                      </Stack>
                    )
                  )}
                </div>
              </Stack>
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              aria-controls="panel1-content"
              id="panel1-header"
            >
              <Stack   
                direction="row"
                spacing={0}
                flex={1}
                sx={{
                  alignItems: "center",
                }}>
                <Typography align="left" fontWeight="fontWeightBold" flex={11}>
                  Tax Element Flags
                </Typography>
                <Typography fontWeight="fontWeightBold" flex={1}>
                  {testValues.inLineErrors.Tax_Errors}
                </Typography>
              </Stack>
            </AccordionSummary>
            <AccordionDetails>
              <Stack>
                <div>
                  {Object.keys(testValues.Flags_Dictionary.Tax).map(
                    (key, index) => (
                      <Stack
                        direction="row"
                        spacing={4}
                        justifyContent="space-between"
                        alignItems="center"
                      >
                        <Box>
                          <Typography class="QueryText" align="left">
                            <p align = "left" key={index}> {key}</p>
                          </Typography>
                        </Box>
                        <Stack direction="row" alignItems="center" spacing={2}>
                          <Box>{testValues.Flags_Dictionary.Tax[key]}</Box>
                          <Box>
                            <IconButton
                              onClick={() => {
                                handleCopyFlagClick("taxElementErrors ", key);
                              }}
                              color="primary"
                            >
                              <CopyIcon />
                            </IconButton>
                          </Box>
                        </Stack>

                        <Snackbar
                          message="Copied to clipboard"
                          anchorOrigin={{
                            vertical: "top",
                            horizontal: "center",
                          }}
                          autoHideDuration={2000}
                          onClose={() => setOpen(false)}
                          open={open}
                        />
                      </Stack>
                    )
                  )}
                </div>
              </Stack>
            </AccordionDetails>
          </Accordion>

          {/*<Accordion>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              aria-controls="panel1-content"
              id="panel1-header"
            >
              <Typography fontWeight="fontWeightBold">
                Geometry Element Flags
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Stack>
                <div>
                  {Object.keys(testValues.Flags_Dictionary.Geometric).map(
                    (key, index) => (
                      <Stack
                        direction="row"
                        spacing={4}
                        justifyContent="space-between"
                        alignItems="center"
                      >
                        <Box>
                          <Typography class="QueryText">
                            <p align = "left" key={index}> {key}</p>
                          </Typography>
                        </Box>
                        <Stack direction="row" alignItems="center" spacing={2}>
                          <Box>{testValues.Flags_Dictionary.Geometric[key]}</Box>
                          <Box>
                            <IconButton
                              onClick={() => {
                                handleCopyFlagClick(key);
                              }}
                              color="primary"
                            >
                              <CopyIcon />
                            </IconButton>
                          </Box>
                        </Stack>

                        <Snackbar //https://mui.com/material-ui/api/snackbar/
                          message="Copied to clipboard"
                          anchorOrigin={{
                            vertical: "top",
                            horizontal: "center",
                          }}
                          autoHideDuration={2000}
                          onClose={() => setOpen(false)}
                          open={open}
                        />
                      </Stack>
                    )
                  )}
                </div>
              </Stack>
            </AccordionDetails>
          </Accordion>*/}
          <Accordion defaultExpanded>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              aria-controls="panel1-content"
              id="panel1-header"
            >
              <Typography fontWeight="fontWeightBold">
                Attribute Comparison
              </Typography>
            </AccordionSummary>
            <AccordionDetails align="center">
              {Object.values(testValues.Fields_Diffs).some(e => 15 < Math.abs(e)) ? (
                <FieldDiffsBar/>
                ) : (
                  <Typography>
                    No attributes with 15% increase/decrease in record value
                  </Typography>
                )}
            </AccordionDetails>
          </Accordion>
        </Stack>
      </Box>
      </ThemeProvider>
    </div>
  );
}

export default App;