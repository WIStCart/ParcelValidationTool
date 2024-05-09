import tkinter as tk
from tkinter import tix 
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *

from tkinter.filedialog import *
from tkinter import scrolledtext
#from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox

import os, sys
from os import path
import collections

import importlib
import shutil
from osgeo import ogr, gdal

import ValidationToolScriptFoss
from ValidationToolScriptFoss import validation_tool_run_all

class App(ttk.Frame):    
    def __init__(self, master=None):
        self.folder_icon = tk.PhotoImage(file=folder_gif_path)

        def emptyWork():
            print('\n\n    Initializing Validation Tool...')
            print('\n')

        ttk.Frame.__init__(self, master)
        self.pack(padx=5, pady=5)

        self.inputNameList = ['isSearchable','isFinal','county','inFC','outDir',
                        'outName','outINIDir','subName','subEmail','condoModel',
                        'inCert','isNameRedact','redactPolicy', 'certifCompleteness', 'zoningGenType',
                        'zoningGenFC','zoningShoreType','zoningShoreFC',
                        'zoningAirType','zoningAirFC','PLSSType','PLSSFC',
                        'RightOfWayType','RightOfWayFC','RoadStreetCenterlineType',
                        'RoadStreetCenterlineFC','HydroLineType','HydroLineFC',
                        'HydroPolyType','HydroPolyFC','AddressesType','AddressesFC',
                        'BuildingBuildingFootprintType','BuildingBuildingFootprintFC',
                        'LandUseType','LandUseFC','ParksOpenSpaceType','ParksOpenSpaceFC',
                        'TrailsType','TrailsFC','OtherRecreationType','OtherRecreationFC',
                        'certifiedBy','PLSSOtherDigitalFile']
        
        global defaultInputComparator 
        defaultInputComparator = {'county': '', 'inFC': '', 'outName': '', 'outDir': '',
                                    'plssRunWindow': False, 'parcelinfoRunWindow': False, 'explainCertifyRunWindow': False,
                                    'zoningRunWindow': False, 'othersRunWindow': False}

        #Ordered dictionary that will hold Tkinter strings of the inputs
        self.input_dict = collections.OrderedDict()

        #Create dictionary kvp for each input name and give it a blank Tkinter string value        
        for i in self.inputNameList:
            self.input_dict[i] = tk.StringVar(value="")
            
        # simplify certification functionality slightly
        self.input_dict['inCert'] = {element: tk.StringVar(value = '') for element in ['explainedErrorsNumber',
                                                                          'noticeOfNewStreetName',
                                                                          'noticeOfNewNonParcelFeaturePARCELIDs',
                                                                          'noticeOfMissingDataOmissions',
                                                                          'noticeErrorsSumsUnresolvable',
                                                                          'noticeOther']}

        self.files_list = []
        self.feature_classes = []
        self.inputObjectMap = list()

        # variables to control input in children windows
        global plssRunWindow, parcelinfoRunWindow, explainCertifyRunWindow, zoningRunWindow, othersRunWindow 
        plssRunWindow = tk.BooleanVar(False)
        parcelinfoRunWindow = tk.BooleanVar(False)
        explainCertifyRunWindow = tk.BooleanVar(False)
        zoningRunWindow = tk.BooleanVar(False)
        othersRunWindow = tk.BooleanVar(False)
        
        self.create_widgets()

        emptyWork()
    
       ### App class methods ###
    # this function is outside of the scope of all windows
    # @param exitButton: reference to any exit button for any window
    # @param inputObjectMap: list of 3-tuples corresponding
    # stored variables address references in dictionary, 
    # associated widget objects, and aliases
    # @param inputObjectMap: TODO: consider if inputs need to be organized
    # in a tree in cases of complex decisions
    # @return TODO: decide if its a boolean or other type
    


    def isExitableState(self, exitableStatus, exitButton):# inputObjectMap):
        unfilledFields = list()
        for inputVar in self.inputObjectMap:
            #print('current input variable: ', inputVar[0].get(), inputVar[1])  

            if (inputVar[0].get() == defaultInputComparator[inputVar[1]]) or \
                    (   inputVar[1] == 'inFC' and not self.FC_exists(inputVar[0].get())) or \
                    (  (inputVar[1] == 'outDir' and os.path.exists(inputVar[0].get()) and inputVar[0].get()[-4:] != '.gdb') or
                            (inputVar[1] == 'outDir' and not os.path.exists(inputVar[0].get()))):
                #print('comparison to defaults: ', inputVar[2], defaultInputComparator[inputVar[1]])
                unfilledFields.append(inputVar[2])
            else:
                if inputVar[2] in unfilledFields:
                    unfilledFields.remove(inputVar[2])
        
        if len(unfilledFields) > 0:
            exitButton['state'] = 'disabled'
            exitableStatus.bind_widget(exitButton, balloonmsg = 'Missing input: {}'.format(unfilledFields))
        elif len(unfilledFields) == 0:
            exitButton['state'] = 'normal'
            exitableStatus.bind_widget(exitButton, balloonmsg = 'Ready to Execute')        
        #print('unfill :' , unfilledFields)
        return unfilledFields


    def FC_exists(self, fc):
        gdal.UseExceptions()
        datasource = os.path.split (fc)[0]
        layer = os.path.normpath(fc).split(os.path.sep)[-1]   
        try:
            ds = gdal.OpenEx(datasource)
            if layer is not None:
                return ds.GetLayerByName(layer) is not None
            else:
                return True
        except RuntimeError as e:
            return False
                    
    def askdir_basic(self, path_name):
        """returns a path to a directory - no gdb, and no path checking"""
        dirname = askdirectory()  
        if dirname:
            path_name.set(dirname) 

    def askdir(self, file_name):
        """returns a file name"""
        filetypes = (
        ('Text files', '*.txt'),
        ('Excel files', '*.xlsx; *.xls'),
        ('CSV files', '*.csv'),
        ('Shape files', '*.shp'),
        ('All files', '*.*'))
        start_path = os.path.dirname (os.path.abspath(__file__))
        filename = askopenfilename(title='Open PLSS file',
                                   initialdir = start_path,
                                   filetype=filetypes)
        file_name.set(filename)

    def onselect(self, event, full_path):
        """ select a feature class to be procesed, i.e. compared """
        w = event.widget
        index = w.curselection()[0] #position of fc in the list
        full_path.set(self.feature_classes[index])

    def open_win(self, full_path, childWin):
        """ open a window with a list of the feature classes list in the gdb"""
        new= Toplevel(childWin)
        new.iconbitmap(wisconsin_icon_path)
        new.title("Feature Classes")
  
        scrollbar = Scrollbar(new)
        scrollbar.pack (side = RIGHT, fill = BOTH)

        fc_listbox=Listbox(new, width=50, height=20)
        fc_listbox.pack(pady=15)
   
        for item in self.files_list:
            fc_listbox.insert(END, item)
        #select a feature -name of the fc- from the list
        fc_listbox.config(yscrollcommand = scrollbar.set)
        scrollbar.config(command = fc_listbox.yview)

        fc_listbox.bind('<<ListboxSelect>>', lambda event: self.onselect(event, full_path))

        button_ok = ttk.Button(new, width=8, text = "OK", command = new.destroy)
        button_ok.pack()

    def browseFor_inFC(self, full_path, childWin2):
        """browse for a FC, first looks for a fgdb"""
        self.files_list = []
        self.feature_classes = []
        path_name = str()

        while True: 
            path_name = askdirectory()
            if (path_name.lower().endswith('.gdb')) or path_name is None:
                break
        
        #print (path_name)         
        if path_name and path_name.lower().endswith('.gdb') :
            dr = ogr.GetDriverByName('OpenFileGDB')
            datasource = dr.Open(path_name, 0)

            for layerIndex in range(datasource.GetLayerCount()):
                layer = datasource.GetLayerByIndex(layerIndex)
                self.feature_classes.append(path_name + "/" + layer.GetName())
                self.files_list.append(layer.GetName())

            self.open_win(full_path, childWin = childWin2)
            datasource = None

    def browse_to_GDB(self, gdb):
        """browse to selected a gdb directory (no Feature Class)"""
        gdb_dir = askdirectory()   
        
        if gdb_dir:
            if gdb_dir.endswith('.gdb'):
                gdb.set(gdb_dir)   

    def create_widgets(self):
        """create the widgets in the app gui """

        # inputObjectMap = [(inputObject, inputVariable, alias), TODO]

        def statusDrawer(event):
            colorizer = lambda colorState: "grey" if colorState == False else "#00FF00"
            if (self.input_dict['isFinal'].get() == 'finalModeSelected'): # redundant given calling scope below
                canvasDrawer.create_rectangle(3, 15, 12, 24, fill = colorizer(parcelinfoRunWindow.get()))
                canvasDrawer.create_rectangle(3, 60, 12, 69, fill = colorizer(plssRunWindow.get()))
                canvasDrawer.create_rectangle(3, 105, 12, 114, fill = colorizer(zoningRunWindow.get()))
                canvasDrawer.create_rectangle(3, 150, 12, 159, fill = colorizer(othersRunWindow.get()))
                canvasDrawer.create_rectangle(3, 195, 12, 204, fill = colorizer(all([parcelinfoRunWindow.get(),
                                                                                    plssRunWindow.get(),
                                                                                    zoningRunWindow.get(),
                                                                                    othersRunWindow.get()])))
            else:
                colorizable = all([True if (self.input_dict[item].get() != "") else False for item in ['county', 'inFC', 'outDir', 'outName']])
                canvasDrawer.create_rectangle(3, 195, 12, 204, fill = colorizer(colorizable))
                
        # Radio Buttons for Test or Final mode
        # TODO: implement this inner function outside the scope of this outer function.
        # Also check if user is accidentally changing
        # these buttons state if they have input from final mode.
        def startScreenWidgetStateMutator():
            self.bind("<Motion>", statusDrawer)
            self.bind("<FocusIn>", statusDrawer)
            if (self.input_dict['isFinal'].get() == 'testModeSelected'):
                indicesToCheck = (
                    list(range(6, self.inputNameList.index('inCert'))) 
                    + list(range(self.inputNameList.index('inCert') + 1, len(self.inputNameList)))
                )
                if (
                    any(
                        [False if (self.input_dict[self.inputNameList[index]].get() == "") 
                        else True for index in indicesToCheck]
                        ) == False
                    ):
                    plssRunWindow.set(False)
                    parcelinfoRunWindow.set(False)
                    explainCertifyRunWindow.set(False)
                    zoningRunWindow.set(False)
                    othersRunWindow.set(False)
                    canvasDrawer.delete("all")
                    # self.unbind("<Enter>")
                    button_main_1['state'] = 'disabled'
                    button_main_2['state'] = 'disabled'
                    button_main_3['state'] = 'disabled'
                    button_main_4['state'] = 'disabled'
                    # map(lambda x: x['state'] = 'disabled', [button_main_1, button_main_2, button_main_3, button_main_4])
                    outDir_input_dirBut['state'] = 'normal'
                    outDir_input['state'] = 'normal'
                    outName_input['state'] = 'normal'
                    outDir_input.delete(0, END)
                    outName_input.delete(0, END)
                    self.input_dict['isFinal'].set('testModeSelected')
                    self.inputObjectMap = [(inFC_input, 'inFC', 'Input Feature Class'),
                                           (outDir_input, 'outDir', 'Output Directory Path'),
                                           (outName_input, 'outName', 'Output Filename'),
                                           (county_input, 'county', 'County')]
                else:
                    windowsNameMaps = [['Parcel Data Information', 'PLSS Layer', 'Explain Certification', 'Zoning Layer', 'Other Layers'],
                                       [parcelinfoRunWindow, plssRunWindow, explainCertifyRunWindow, zoningRunWindow, othersRunWindow]]
                    #print("here")
                    inputtedWindows = [window if state.get() else None for window, state in zip(windowsNameMaps[0], windowsNameMaps[1])]
                    #print (inputtedWindows)
                    movMsg = "You are about to leave Final mode and have input in subwindow(s) ({}) which would be deleted. Continue?".format([inputted for inputted in inputtedWindows if inputted != None])
                    moveToTest = messagebox.askokcancel(title = "Proceed to Test Mode", message = movMsg)
                    if moveToTest:
                        self.input_dict['isFinal'].set('testModeSelected')
                        for index in indicesToCheck:
                            self.input_dict[self.inputNameList[index]] = tk.StringVar(value="")
                        canvasDrawer.delete("all")
                        # self.unbind("<Enter>")
                        startScreenWidgetStateMutator()
                    else:
                        self.input_dict['isFinal'].set('finalModeSelected')
                        startScreenWidgetStateMutator()
                        pass
            else:
                # self.bind("<Enter>", statusDrawer)
                
                button_main_1['state'] = 'normal'
                button_main_2['state'] = 'normal'
                button_main_3['state'] = 'normal'
                button_main_4['state'] = 'normal'
                outDir_input_dirBut['state'] = 'disabled'
                outDir_input.insert(0, 'Use Output Directory for .ini in Parcel Data Information')
                outName_input.insert(0, 'Generated automatically with county name')
                outDir_input['state'] = 'disabled'
                outName_input['state'] = 'disabled'
                self.input_dict['isFinal'].set('finalModeSelected')
                self.inputObjectMap = [(inFC_input, 'inFC', 'Input Feature Class'),
                                        (county_input, 'county', 'County'),
                                        (plssRunWindow, 'plssRunWindow', 'PLSS Data'),
                                        (parcelinfoRunWindow, 'parcelinfoRunWindow', 'Parcel Information'), 
                                        (explainCertifyRunWindow, 'explainCertifyRunWindow', 'Explain Certify'), 
                                        (zoningRunWindow, 'zoningRunWindow', 'Zoning Layers' ),
                                        (othersRunWindow, 'othersRunWindow', 'Other Layers')]

        run_mode_sel_label = Label(self, text = 'Select Run Mode:')
        run_mode_sel_label.grid(column = 0, row = 0, sticky = tk.NW)

        # TODO: see why True/False cannot be used as states
        self.input_dict['isFinal'].set('testModeSelected') # default state
        # state is enforced at the bottom of this function
        
        testModeSel = Radiobutton(self, text = 'Test',
                                  variable = self.input_dict['isFinal'],
                                  value = 'testModeSelected',
                                  command = startScreenWidgetStateMutator)
        testModeSel.grid(column = 0, row = 0, sticky = tk.N)

        finalModeSel = Radiobutton(self, text = 'Final',
                                   variable = self.input_dict['isFinal'],
                                   value = 'finalModeSelected',
                                   command = startScreenWidgetStateMutator)
        finalModeSel.grid(column = 0, row = 0, sticky = tk.NE)

        # County combo box (drop down) menu
        county_input_label = Label(self, text='Select County:') 
        county_input_label.grid(column=0, row=1, sticky=tk.W)
        county_input = ttk.Combobox(self, width=53, textvariable=self.input_dict['county'])  
        county_input.grid(column=0, row=2, sticky=tk.W)
        county_input.focus()
        # get names of counties
        county_input['values'] = ["ADAMS","ASHLAND","BARRON","BAYFIELD","BROWN","BUFFALO",
                                "BURNETT","CALUMET","CHIPPEWA","CLARK","COLUMBIA","CRAWFORD","DANE","DODGE","DOOR",
                                "DOUGLAS","DUNN","EAU CLAIRE","FLORENCE","FOND DU LAC","FOREST","GRANT","GREEN",
                                "GREEN LAKE","IOWA","IRON","JACKSON","JEFFERSON","JUNEAU","KENOSHA","KEWAUNEE",
                                "LA CROSSE","LAFAYETTE","LANGLADE","LINCOLN","MANITOWOC","MARATHON","MARINETTE",
                                "MARQUETTE","MENOMINEE","MILWAUKEE","MONROE","OCONTO","ONEIDA","OUTAGAMIE","OZAUKEE",
                                "PEPIN","PIERCE","POLK","PORTAGE","PRICE","RACINE","RICHLAND","ROCK","RUSK","SAUK",
                                "SAWYER","SHAWANO","SHEBOYGAN","ST CROIX","TAYLOR","TREMPEALEAU","VERNON","VILAS",
                                "WALWORTH","WASHBURN","WASHINGTON","WAUKESHA","WAUPACA","WAUSHARA","WINNEBAGO","WOOD"]
        county_input['state'] = 'readonly' # prevent typing in combo box

        '''
        #global defaultInputComparator 
        defaultInputComparator = {'county': '', 'inFC': '', 'outName': '', 'outDir': '',
                                    'plssRunWindow': False, 'parcelinfoRunWindow': False, 'explainCertifyRunWindow': False,
                                    'zoningRunWindow': False, 'othersRunWindow': False}
        '''
        def updateCounty(_):
            self.input_dict['county'].set(county_input.get())
            #print(self.input_dict['county'].get())
        
        county_input.bind('<<ComboboxSelected>>', updateCounty) #, self.selected_county)
     
        inFC_input_label = ttk.Label(self, text='Input Parcels Feature Class Path:')
        inFC_input_label.grid(column=0, row=3, sticky=tk.W)
        inFC_input = ttk.Entry(self,  width=56, textvariable= self.input_dict['inFC'])
        #inFC_input['state'] = 'readonly' 
        inFC_input.grid(column=0, row=4, sticky=tk.W)
        inFC_dirBut = ttk.Button(self, width=8, image=self.folder_icon, 
                                command = lambda: self.browseFor_inFC(self.input_dict['inFC'], 
                                childWin2=self)) 
        inFC_dirBut.grid(column=1, row=4, sticky=tk.W, padx=5)

        outDir_input_label = ttk.Label(self, text='Output Directory Path (gdb):')
        outDir_input_label.grid(column=0, row=5, sticky=tk.W)
        outDir_input = ttk.Entry(self, width=56, textvariable= self.input_dict['outDir'])
        outDir_input.grid(column=0, row=6, sticky=tk.W)
        
        outDir_input_dirBut = ttk.Button(self, width=8, image=self.folder_icon, 
                                        command = lambda: self.browse_to_GDB(self.input_dict['outDir']))
        outDir_input_dirBut.grid(column=1, row=6, sticky=tk.W, padx=5)
        
        outName_input_label = ttk.Label(self, text='Output Feature Class File Name:')
        outName_input_label.grid(column=0, row=7, sticky=tk.W)
        
        outName_input = ttk.Entry(self, width=56, textvariable= self.input_dict['outName'])
        outName_input.grid(column=0, row=8, sticky=tk.W)

        buttonsFrame = Frame(self)
        buttonsFrame.grid(column = 0, row = 9, sticky = tk.N)

        canvasDrawer = Canvas(buttonsFrame, height = 210, width = 15)   #200 and 10
        canvasDrawer.grid(column = 1, rowspan = 5, row = 0, padx = 10)
        
        button_main_1 = ttk.Button(buttonsFrame, width=25, text = "Parcel Data Information",
                                   command = self.open_parcelDataInformationWindow)
        button_main_1.grid(column=0, row = 0, sticky=tk.N, pady=(20,10))

        button_main_2 = ttk.Button(buttonsFrame, width=25, text = "PLSS Layer", command = self.open_plssLayerWindow) 
        button_main_2.grid(column=0, row=1, sticky=tk.N, pady=10)       

        button_main_3 = ttk.Button(buttonsFrame, width=25, text = "Zoning Layer", command = self.open_zoningLayerWindow)
        button_main_3.grid(column=0, row=2, sticky=tk.N, pady=10)

        button_main_4 = ttk.Button(buttonsFrame, width=25, text = "Other Layers", command = self.open_otherLayersWindow) 
        button_main_4.grid(column=0, row=3, sticky=tk.N, pady=10)
        
        button_main_5 = ttk.Button(buttonsFrame, width=15, text = "Run", command = self.big_run_button) 
        button_main_5.grid(column=0, row=4, sticky=tk.N, pady=10)
 
        runStatus = tix.Balloon(self)
        
        startScreenWidgetStateMutator() # hacky way to enforce state on first load

        def exitableStateRunner():
                return "Missing input: {}".format(self.isExitableState(runStatus, button_main_5)) #, self.inputObjectMap))
                  
        runStatus.bind_widget(button_main_5, balloonmsg = exitableStateRunner())
        button_main_5.bind('<Enter>', lambda event, rs=runStatus,  b=button_main_5: self.isExitableState(rs, b)) 

    
    def open_parcelDataInformationWindow(self):
            
        #child window attributes
        parcelDataInformationWindow = Toplevel(self)
        parcelDataInformationWindow.grab_set() #disables parent window while child is open
        parcelDataInformationWindow.iconbitmap(wisconsin_icon_path)
        parcelDataInformationWindow.title('Parcel Data Information')

        outINIDir_input_label = ttk.Label(parcelDataInformationWindow, text= 'Output folder DIRECTORY for final .gdbs and *.ini:')
        outINIDir_input_label.grid(row=0, column=0, padx=5, sticky='w')
        outINIDir_input = ttk.Entry(parcelDataInformationWindow,  width=56, textvariable= self.input_dict['outINIDir'])
        outINIDir_input.grid(row=1, column=0, padx=5, sticky='w')
        outINIDir_input_dirBut = ttk.Button(parcelDataInformationWindow, width=0, image=self.folder_icon, 
                                            command = lambda: self.askdir_basic(self.input_dict['outINIDir']))
        outINIDir_input_dirBut.grid(row=1, column=1, padx=5)
        
        subName_input_label = ttk.Label(parcelDataInformationWindow, text='Submitter Name:')
        subName_input_label.grid(row=2, column=0, padx=5, sticky='w')
        subName_input = ttk.Entry (parcelDataInformationWindow,  width=56)
        subName_input.insert(0, self.input_dict['subName'].get())  #Displays value stored in dictionary in the entry box
        subName_input.grid(row=3, column=0, padx=5, sticky='w')

        subEmail_input_label = ttk.Label(parcelDataInformationWindow, text='Submitter Email')
        subEmail_input_label.grid(row=4, column=0, padx=5, sticky='w')
        subEmail_input = ttk.Entry(parcelDataInformationWindow,  width=56)
        subEmail_input.insert(0, self.input_dict['subEmail'].get())  #Displays value stored in dictionary in the entry box
        subEmail_input.grid(row=5, column=0, padx=5, sticky='w')

        ## Condo Model combo box (drop down) menu
        condoModel_input_label = Label(parcelDataInformationWindow, text='Select Condo Model:') 
        condoModel_input_label.grid(row=6, column=0, padx=5, sticky='w')
        condoModel_input_holder = tk.StringVar(value=self.input_dict['condoModel'].get())
        condoModel_input = ttk.Combobox(parcelDataInformationWindow, width=53, textvariable=condoModel_input_holder)  #font=('arial', 10), 
        condoModel_input.grid(row=7, column=0, padx=5, sticky='w')
        # TO_STUDY get condoModel types (what does this loop do?)
        condoModel_input['values'] = ['Condo Type #1 - Discrete', 'Condo Type #2 - Stacked', 
                                    'Condo Type #3 - Divided', 'Condo Type #4 - Distributed', 
                                    'Condo Type #1-4 - Mixed Modeling', 
                                    'Condo Type N/A because no condos exist in county']
        condoModel_input['state'] = 'readonly' # prevent typing a value

        explainCert_window_label = ttk.Label(parcelDataInformationWindow, text='Explain-Certification (REQUIRED), click Add:')
        explainCert_window_label.grid(row=8, column=0, padx=5, sticky='w')
      
        def open_explanationCertificateWindow():
        
            #grandchild window attributes
            explanationCertificateWindow = Toplevel(parcelDataInformationWindow)
            explanationCertificateWindow.grab_set() #disables parent window while child is open
            explanationCertificateWindow.iconbitmap(wisconsin_icon_path)
            explanationCertificateWindow.title('Explanation Certification')
            explanationCertificateWindow.geometry('615x800')
                    
            # TODO: enforce required input and also use default text

            default_text = {'street': 'Enter new Street Names here or type None if no values exist',
                            'non parcel': 'Enter new Non-Parcel Feature Parcel IDs or type None if no values exist',
                            'omission': 'Enter omission information here or type None if no omissions exist',
                            'error': 'Enter justification for unresolvability or type None if no value exist'}

            def clickedOutExplain(inputObject, inputClass, event = None):
                if len(inputObject.get('1.0', 'end-1c')) == 0:
                    inputObject.tag_config('default', background="white", foreground= '#808080' )
                    inputObject.insert('1.0', default_text[inputClass], 'default')
                if '<Key>' in inputObject.bind():
                    inputObject.unbind('<Key>')

            def clickedInExplain(inputObject, inputClass, event = None):
                def keyPressed(event = None):
                    if inputObject.get('1.0', 'end-1c') == default_text[inputClass]:
                        inputObject.delete('1.0', END)
                    if event.keysym == 'BackSpace' or event.keysym == 'Delete':
                        if len(inputObject.get('1.0', 'end-1c')) == 1:
                            inputObject.tag_config('default', background="white", foreground= '#808080' )
                            inputObject.insert('1.0', default_text[inputClass], 'default') 
                inputObject.bind('<Key>', keyPressed)

            def onFrameConfigure(canvas):
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            explanationCertifyCanvas = tk.Canvas (explanationCertificateWindow )
            explanationCertifyCanvas.pack(side=LEFT, fill = BOTH, expand = True)

            explanationCertifyFrame = tk.Frame (explanationCertifyCanvas, width=510, height=700)
            explanationCertifyFrame.pack()

            explanationCertifyScrollbar = Scrollbar(explanationCertificateWindow)
            explanationCertifyScrollbar.config ( command=explanationCertifyCanvas.yview)
            explanationCertifyCanvas.configure(yscrollcommand = explanationCertifyScrollbar.set)
            explanationCertifyScrollbar.pack (side = RIGHT, fill= BOTH)
     
            explanationCertifyCanvas.create_window((0,0), window = explanationCertifyFrame, 
                    anchor = NW, tags = explanationCertifyFrame)
            explanationCertifyFrame.bind ("<Configure>", lambda event, 
                    explanationCertifyCanvas=explanationCertifyCanvas: onFrameConfigure(explanationCertifyCanvas))        
           
            noticeOfNewStreetName_input_label = ttk.Label(explanationCertifyFrame, text='Notice of New Street Names:')
            noticeOfNewStreetName_input_label.pack () #grid(column=0, row=0, sticky=tk.W)
            noticeOfNewStreetName_input = scrolledtext.ScrolledText(explanationCertifyFrame, #state = 'normal',
                                               # textvariable = self.input_dict['inCert']['noticeOfNewStreetName'],
                                               width=71, height=7)
            noticeOfNewStreetName_input.tag_config('default', background="white", foreground= '#808080' )
            noticeOfNewStreetName_input.insert('1.0', self.input_dict['inCert']['noticeOfNewStreetName'].get()) #Displays value stored in dictionary
            noticeOfNewStreetName_input.pack(padx=5, pady=5)
            noticeOfNewStreetName_input.yview(tk.END)
            noticeOfNewStreetName_input.bind('<FocusOut>', clickedOutExplain(noticeOfNewStreetName_input, 'street'))
            noticeOfNewStreetName_input.bind('<FocusIn>', clickedInExplain(noticeOfNewStreetName_input, 'street'))
            

            noticeOfNewNonParcelFeaturePARCELIDs_input_label = ttk.Label(explanationCertifyFrame,
                                                                         text='Notice of New Non-Parcel Feature PARCELIDs:')
            noticeOfNewNonParcelFeaturePARCELIDs_input_label.pack () #grid(column=0, row=0, sticky=tk.W)
            noticeOfNewNonParcelFeaturePARCELIDs_input = scrolledtext.ScrolledText(explanationCertifyFrame, #state = 'normal',
                                                              # textvariable = self.input_dict['inCert']['noticeOfNewNonParcelFeaturePARCELIDs'],
                                                              width=71, height=7)
            noticeOfNewNonParcelFeaturePARCELIDs_input.tag_config('default', background="white", foreground= '#808080' )
            noticeOfNewNonParcelFeaturePARCELIDs_input.insert('1.0', self.input_dict['inCert']['noticeOfNewNonParcelFeaturePARCELIDs'].get()) #, 'default')  #Displays value stored in dictionary
            noticeOfNewNonParcelFeaturePARCELIDs_input.pack(padx=5, pady=5)
            noticeOfNewNonParcelFeaturePARCELIDs_input.yview(tk.END)
            noticeOfNewNonParcelFeaturePARCELIDs_input.bind('<FocusOut>', clickedOutExplain(noticeOfNewNonParcelFeaturePARCELIDs_input, 'non parcel'))
            noticeOfNewNonParcelFeaturePARCELIDs_input.bind('<FocusIn>', clickedInExplain(noticeOfNewNonParcelFeaturePARCELIDs_input, 'non parcel'))

            noticeOfMissingDataOmissions_input_label = ttk.Label(explanationCertifyFrame, text='Notice of Missing Data/Omissions')
            noticeOfMissingDataOmissions_input_label.pack () #grid(column=0, row=0, sticky=tk.W)
            noticeOfMissingDataOmissions_input = scrolledtext.ScrolledText(explanationCertifyFrame, state = 'normal',
                                                      # textvariable = self.input_dict['inCert']['noticeOfMissingDataOmissions'],
                                                      width=71, height=7)
            noticeOfMissingDataOmissions_input.tag_config('default', background="white", foreground= '#808080' )                                                     
            noticeOfMissingDataOmissions_input.insert('1.0', self.input_dict['inCert']['noticeOfMissingDataOmissions'].get())#, 'default')  #Displays value stored in dictionary
            noticeOfMissingDataOmissions_input.pack(padx=5, pady=5)
            noticeOfMissingDataOmissions_input.yview(tk.END)           
            noticeOfMissingDataOmissions_input.bind('<FocusOut>', clickedOutExplain(noticeOfMissingDataOmissions_input, 'omission'))
            noticeOfMissingDataOmissions_input.bind('<FocusIn>', clickedInExplain(noticeOfMissingDataOmissions_input, 'omission'))

            # TODO: keep statistics of these
        
            noticeErrorsSumsUnresolvable_input_label = ttk.Label(explanationCertifyFrame, text='Error Sums That Are Unresolvable')
            noticeErrorsSumsUnresolvable_input_label.pack () #grid(column=0, row=0, sticky=tk.W)
            noticeErrorsSumsUnresolvable_input = scrolledtext.ScrolledText(explanationCertifyFrame, state = 'normal',
                                                      # textvariable = self.input_dict['inCert']['noticeErrorsSumsUnresolvable'],
                                                      width=71, height=7)
            noticeErrorsSumsUnresolvable_input.tag_config('default', background="white", foreground= '#808080' )     
            noticeErrorsSumsUnresolvable_input.insert('1.0', self.input_dict['inCert']['noticeErrorsSumsUnresolvable'].get())#, 'default')  #Displays value stored in dictionary
            noticeErrorsSumsUnresolvable_input.pack(padx=5, pady=5)
            noticeErrorsSumsUnresolvable_input.yview(tk.END)
            noticeErrorsSumsUnresolvable_input.configure(state='normal')
            noticeErrorsSumsUnresolvable_input.bind('<FocusOut>', clickedOutExplain(noticeErrorsSumsUnresolvable_input, 'error'))
            noticeErrorsSumsUnresolvable_input.bind('<FocusIn>', clickedInExplain(noticeErrorsSumsUnresolvable_input, 'error'))

            noticeOther_input_label = ttk.Label(explanationCertifyFrame, text='Other:')
            noticeOther_input_label.pack () #grid(column=0, row=0, sticky=tk.W)
            noticeOther_input = scrolledtext.ScrolledText(explanationCertifyFrame,  state = 'normal',  width=71, height=7)
            noticeOther_input.tag_config('default', background="white", foreground= '#808080' )              
            noticeOther_input.insert('1.0', self.input_dict['inCert']['noticeOther'].get() )# , 'default')  #Displays value stored in dictionary
            noticeOther_input.pack(padx=5, pady=5)
            noticeOther_input.configure(state='normal')
            noticeOther_input.yview(tk.END)    

            # TODO: can possibly consider some local caching
            noticeOther_input_label = ttk.Label(explanationCertifyFrame, text='NOTE: ENTRIES HERE ARE NOT SAVED if the validation tool is restarted.')
            noticeOther_input_label.pack () #grid(column=0, row=0, sticky=tk.W)


            def putInput_in_DictionaryEC():
                self.input_dict['inCert']['noticeOfNewStreetName'] = tk.StringVar(value=noticeOfNewStreetName_input.get('1.0', 'end'))
                self.input_dict['inCert']['noticeOfNewNonParcelFeaturePARCELIDs'] = tk.StringVar(value=noticeOfNewNonParcelFeaturePARCELIDs_input.get('1.0', 'end'))
                self.input_dict['inCert']['noticeOfMissingDataOmissions'] = tk.StringVar(value=noticeOfMissingDataOmissions_input.get('1.0', 'end'))
                self.input_dict['inCert']['noticeErrorsSumsUnresolvable'] = tk.StringVar(value=noticeErrorsSumsUnresolvable_input.get('1.0', 'end'))
                self.input_dict['inCert']['noticeOther'] = tk.StringVar(value=noticeOther_input.get('1.0', 'end'))
                
                explainCertifyRunWindow.set(True) 
                #close window
                explanationCertificateWindow.destroy()

            bottomFrame = Frame(explanationCertifyFrame)
            bottomFrame.pack(side = BOTTOM)

            def isSaveableState(_):
                unfilledFields = list()
                for inputVar in [(noticeOfNewStreetName_input, 'street'),
                                (noticeOfNewNonParcelFeaturePARCELIDs_input, 'non parcel'),
                                (noticeOfMissingDataOmissions_input, 'omission'),
                                (noticeErrorsSumsUnresolvable_input, 'error')]:
                    if (inputVar[0].get('1.0', 'end-1c') == default_text[inputVar[1]]) or (inputVar[0].get('1.0', 'end-1c') == ""):
                        unfilledFields.append(inputVar[1])
                    else:
                        if inputVar in unfilledFields:
                            unfilledFields.remove(inputVar)
                    #print(unfilledFields)
                if len(unfilledFields) > 0:
                    ok_button['state'] = 'disabled'
                    saveableStatus.bind_widget(ok_button,
                            balloonmsg = "Missing input: {}".format(unfilledFields)) # poor design
                elif len(unfilledFields) == 0:
                    ok_button['state'] = 'normal'
                    saveableStatus.bind_widget(ok_button, balloonmsg = "Ready to Save") # poor design
                return unfilledFields

            # Trivial helper method that should be anonymized
            def saveableStateRunner():
                return "Missing input: {}".format(isSaveableState(None))

            saveableStatus = tix.Balloon(explanationCertificateWindow)
            
            ok_button = ttk.Button(bottomFrame, width=8, text="OK", command=putInput_in_DictionaryEC)
            ok_button.grid(row = 0, column = 0, padx=5, pady=5)
            explanationCertificateWindow.bind('<Enter>', isSaveableState)

            # TODO: use string types only and also write English aliases for the input items
            saveableStatus.bind_widget(ok_button, balloonmsg = saveableStateRunner())

            cancel_button = ttk.Button(bottomFrame, width=8, text = "Cancel", command = explanationCertificateWindow.destroy)
            cancel_button.grid(row = 0, column = 1, padx=5, pady=5)

            #TODO - consider where/how to write the certification explanation to file or INI will occur

        explainCert_window_button = ttk.Button(parcelDataInformationWindow, width=25, text = "Add", command = open_explanationCertificateWindow)
        explainCert_window_button.grid(row=9, column=0, padx=5, sticky='w')

        #redaction checkbox
        isNameRedact_input_holder = tk.StringVar(value=self.input_dict['isNameRedact'].get())
        isNameRedact_input = Checkbutton(parcelDataInformationWindow, text="Check here if any owner names are redacted:", variable=isNameRedact_input_holder, onvalue='true', offvalue='false')
        # isNameRedact_input_holder.set(self.input_dict['isNameRedact'].get())  #This was the first way I tried, but using the value attribute of the holder variable seems to work just as well for reflecting the stored value
        isNameRedact_input.grid(row=10, column=0, padx=5, sticky='w')
                    
        redactPolicy_input_label = ttk.Label(parcelDataInformationWindow, text='URL or Filename of Redaction Policy (if any):')
        redactPolicy_input_label.grid(row=11, column=0, padx=5, sticky='w')
        redactPolicy_input = ttk.Entry(parcelDataInformationWindow,  width=56)
        redactPolicy_input.insert(0, self.input_dict['redactPolicy'].get())  #Displays value stored in dictionary in the entry box
        redactPolicy_input.grid(row=12, column=0, pady=5, padx=5, sticky='w')

        
        s = ttk.Separator(parcelDataInformationWindow, orient='horizontal')
        s.grid(row=13, column = 0, columnspan=2, padx= 5, pady=10, sticky='ew') 

        CertText ="I certify this dataset is complete, correct, and all error messages \nhave been explained in the Explain Certification."

        certCompletness_check_holder = tk.StringVar(value=self.input_dict['certifCompleteness'].get())  
        certCompletness_check = Checkbutton(parcelDataInformationWindow, text=CertText,  variable=certCompletness_check_holder, onvalue='Complete', offvalue='')
        certCompletness_check.grid(row=15, column=0,  padx=5, pady = 5, sticky='w')
  
        explainedErrorsNumber_input_label = ttk.Label(parcelDataInformationWindow, text='How many errors of the ERROR SUM did you explain in the Certification Explanation?:')
        explainedErrorsNumber_input_label.grid(row=16, column=0, padx=5, sticky='w') #grid(column=0, row=0, sticky=tk.W)
        explainedErrorsNumber_input = ttk.Entry(parcelDataInformationWindow,  width=7)
        explainedErrorsNumber_input.insert(0, self.input_dict['inCert']['explainedErrorsNumber'].get())  #Displays value stored in dictionary in the entry box
        explainedErrorsNumber_input.grid(row=17, column=0, padx=5, sticky='w')

        def putInput_in_DictionaryPDI():

            self.input_dict['outINIDir'] = tk.StringVar(value=outINIDir_input.get())
            self.input_dict['subEmail'] = tk.StringVar(value=subEmail_input.get())
            self.input_dict['subName'] = tk.StringVar(value=subName_input.get())
            self.input_dict['condoModel'] = tk.StringVar(value=condoModel_input_holder.get())
            self.input_dict['redactPolicy'] = tk.StringVar(value=redactPolicy_input.get())
            self.input_dict['certifCompleteness'] = tk.StringVar(value=certCompletness_check_holder.get()) 
            self.input_dict['inCert']['explainedErrorsNumber'] = tk.StringVar(value=explainedErrorsNumber_input.get())

            self.input_dict['isNameRedact'] = tk.StringVar(value=isNameRedact_input_holder.get())
            
            parcelinfoRunWindow.set(True) 
            
            parcelDataInformationWindow.destroy()

        bottomFrame = Frame(parcelDataInformationWindow)
        bottomFrame.grid(row = 18, column = 0, columnspan = 2)

        ok_button = ttk.Button(bottomFrame, width=8, text = "OK", command=putInput_in_DictionaryPDI)
        ok_button.grid(row = 0, column = 0, padx=5, pady=5)

        cancel_button = ttk.Button(bottomFrame, width=8, text = "Cancel", command = parcelDataInformationWindow.destroy)
        cancel_button.grid(row = 0, column = 1, padx=5, pady=5)            

        # inputObjectMap for the PDI data and default values
        PDIinputObjectMap = [(outINIDir_input, 'outINIDir', 'Output Directory'),
                            (subEmail_input, 'subEmail', 'Submitter Email'),  
                            (subName_input, 'subName', 'Submitter Name'),
                            (condoModel_input, 'condoModel', 'Condo Model'),
                            (explainedErrorsNumber_input, 'explainedErrorNumber', 'Error Sum Explained'),
                            (certCompletness_check_holder, 'certifCompleteness', 'Certification of Completness'),
                            (explainCertifyRunWindow, 'explainCertifyRunWindow', 'Explain Certify Information')  ]

        PDIdefaultInputComparator = {'outINIDir': '', 'subEmail': '', 'subName': '', 'condoModel': '',
                                    'explainedErrorNumber': '', 'certifCompleteness': '',
                                    'explainCertifyRunWindow': False}
    
        def isPDIReadytoRun(event ):
            unfilledFields = list()
            for inputVar in PDIinputObjectMap:
                #print('current input variable: ', inputVar[0].get(), inputVar[1])
                if (inputVar[0].get() == PDIdefaultInputComparator[inputVar[1]]) or \
                    (inputVar[1] == 'outINIDir' and os.path.isdir( inputVar[0].get()) and inputVar[0].get()[-4:] == '.gdb') or \
                    (inputVar[1] == 'outINIDir' and not os.path.isdir(inputVar[0].get())): 
                    #print('comparison to defaults: ', inputVar[2], PDIdefaultInputComparator[inputVar[1]])
                    unfilledFields.append(inputVar[2])
                else:
                    if inputVar[2] in unfilledFields:
                        unfilledFields.remove(inputVar[2])
            
            if len(unfilledFields) > 0:
                ok_button['state'] = 'disabled'
                PDIStatus.bind_widget(ok_button, balloonmsg = 'Missing or incorrect input: {}'.format(unfilledFields))
            elif len(unfilledFields) == 0:
                ok_button['state'] = 'normal'
                PDIStatus.bind_widget(ok_button, balloonmsg = 'Ready to Save')
            #print (unfilledFields)
            return unfilledFields

        def PDIsaveableStateRunner():
            return "Missing or incorrect input: {}".format(isPDIReadytoRun(None))

        PDIStatus = tix.Balloon(parcelDataInformationWindow)
        ok_button.bind('<Enter>', isPDIReadytoRun)
        PDIStatus.bind_widget(ok_button, balloonmsg = PDIsaveableStateRunner () )
        
    ######### plss Layer Window
    def open_plssLayerWindow(self):  
        #child window attributes
        plssLayerWindow = Toplevel(self)
        plssLayerWindow.grab_set() #disables parent window while child is open
        plssLayerWindow.iconbitmap(wisconsin_icon_path)
        plssLayerWindow.title('PLSS Layer Input')

        def selectDataFormatStateMutator(_):
            # need to use better comparisons than full on string equivalency;
            # for example, all these options can be put into dictionaries as values
            # with a key summarizing it in a single word
            if (self.input_dict['PLSSType'].get() == 'Maintained by county as other digital format'):
                plssFC_input['state'] = 'disabled'
                #plssFC_input_holder.set( '')
                plssFC_input_dirBut['state'] = 'disabled'
                plssOtherDigitalFile_input['state'] = 'normal'
                plssOtherDigitalFile_input_dirBut['state'] = 'normal'
            elif (self.input_dict['PLSSType'].get() == 'Maintained by county as feature class'):
                plssFC_input['state'] = 'normal'
                plssFC_input_dirBut['state'] = 'normal'
                plssOtherDigitalFile_input['state'] = 'disabled'
                plssOtherDigitalFile_input_holder.set('')
                plssOtherDigitalFile_input_dirBut['state'] = 'disabled'
            else:
                plssFC_input['state'] = 'disabled'
                #plssFC_input_holder.set( '')
                plssFC_input_dirBut['state'] = 'disabled'
                plssOtherDigitalFile_input['state'] = 'disabled'
                plssOtherDigitalFile_input_holder.set('')
                plssOtherDigitalFile_input_dirBut['state'] = 'disabled'

        ## PLSS combo box (drop down) menu
        plssType_input_label = Label(plssLayerWindow, text='Select PLSS Data Format:') 
        plssType_input_label.grid(row = 0, column = 0, padx=5, sticky='w')
        # plssType_input_holder = tk.StringVar(value=self.input_dict['PLSSType'].get())
        # plssType_input = ttk.Combobox(plssLayerWindow, width=53, textvariable=plssType_input_holder) 
        plssType_input = ttk.Combobox(plssLayerWindow, width = 53,
                                      values = ['Maintained by county as feature class',
                                                'Maintained by county as other digital format',
                                                'Not in digital format'],
                                      textvariable = self.input_dict['PLSSType'])
        
        plssType_input.grid(row = 1, column = 0, padx=5)
        plssType_input['state'] = 'readonly' # prevent typing a value
        
        plssFC_input_label = ttk.Label(plssLayerWindow, text='PLSS Feature Class:')
        plssFC_input_label.grid(row=3, column=0, padx=5, sticky='w')
        plssFC_input_holder = tk.StringVar(value=self.input_dict['PLSSFC'].get())
        plssFC_input = ttk.Entry(plssLayerWindow,  width=56, textvariable=plssFC_input_holder)
        plssFC_input.grid(row=4, column=0, padx=5, sticky='w')
        plssFC_input_dirBut = ttk.Button(plssLayerWindow, width=8, image=self.folder_icon, 
                                        command = lambda: self.browseFor_inFC(plssFC_input_holder, 
                                        childWin2 = plssLayerWindow ))
        plssFC_input_dirBut.grid(row=4, column=1, padx=5)
       
        plssOtherDigitalFile_input_label = ttk.Label(plssLayerWindow, text='PLSS Digital File:')
        plssOtherDigitalFile_input_label.grid(row=5, column=0, padx=5, sticky='w')
        plssOtherDigitalFile_input_holder = tk.StringVar(value=self.input_dict['PLSSOtherDigitalFile'].get())
        plssOtherDigitalFile_input = ttk.Entry(plssLayerWindow,  width=56, textvariable=plssOtherDigitalFile_input_holder)
        plssOtherDigitalFile_input.grid(row=6, column=0, padx=5, sticky='w')
        plssOtherDigitalFile_input_dirBut = ttk.Button(plssLayerWindow, width=0, image=self.folder_icon,
                                                       command = lambda: self.askdir(plssOtherDigitalFile_input_holder))
        plssOtherDigitalFile_input_dirBut.grid(row=6, column=1, padx=5)

        plssType_input.bind('<<ComboboxSelected>>', selectDataFormatStateMutator)

        selectDataFormatStateMutator(None)
        
        def putInput_in_DictionaryPLSS():
            self.input_dict['PLSSType'] = tk.StringVar(value = plssType_input.get())
            self.input_dict['PLSSFC'] = tk.StringVar(value=plssFC_input_holder.get())
            self.input_dict['PLSSOtherDigitalFile'] = tk.StringVar(value=plssOtherDigitalFile_input_holder.get())
            ## global variable
            plssRunWindow.set(True)
            
            # self.input_dict['PLSSOtherDigitalFile'] = tk.StringVar(value=plssOtherDigitalFile_input.get())
        
            plssLayerWindow.destroy()

        bottomFrame = Frame(plssLayerWindow)
        bottomFrame.grid(row = 7, column = 0, columnspan = 2)

        ok_button = ttk.Button(bottomFrame, width=8, text="OK", command=putInput_in_DictionaryPLSS)
        ok_button.grid(row = 0, column = 0, padx=5, pady=5)

        cancel_button = ttk.Button(bottomFrame, width=8, text = "Cancel", command = plssLayerWindow.destroy)
        cancel_button.grid(row = 0, column = 1, padx=5, pady=5)

        # inputObjectMap for the PLSS data and default values
        plssinputObjectMap = [(plssType_input, 'PLSSType', 'PLSS format type'),
                                (plssFC_input_holder, 'PLSSFC', 'PLSS feature Class'),  
                                (plssOtherDigitalFile_input_holder, 'PLSSOtherDigitalFile', 'PLSS Other Digital File')
                            ]
        defaultInputComparator = {'PLSSType': '', 'PLSSFC': '', 'PLSSOtherDigitalFile': ''}
     
        def isPLSSReadytoRun(event ):
            unfilledFields = list()
            typeVar = plssinputObjectMap[0]
            if typeVar[0].get() == defaultInputComparator[typeVar[1]]: 
                unfilledFields.append(typeVar[2])
            else:
                #print('plsstype: ', typeVar[0].get(), typeVar[2], defaultInputComparator[typeVar[1]])
                if typeVar[0].get() == 'Maintained by county as feature class':
                        plssinputObject = plssinputObjectMap[1]     #better finding the object index
                        if (plssinputObject[0].get() == defaultInputComparator[plssinputObject[1]]) or \
                            (plssinputObject[1] == 'PLSSFC' and not self.FC_exists(plssinputObject[0].get())):
                            #print('comparison to defaults: ', plssinputObject[2], defaultInputComparator[plssinputObject[1]])
                            unfilledFields.append(plssinputObject[2]) 
                        else:
                            if plssinputObject[2] in unfilledFields:
                                unfilledFields.remove(plssinputObject[2])
                if typeVar[0].get() ==   'Maintained by county as other digital format':
                        plssinputObject = plssinputObjectMap[2]     #this can be better finding the object index
                        if (plssinputObject[0].get() == defaultInputComparator[plssinputObject[1]]) or (plssinputObject[1] == 'PLSSOtherDigitalFile' and not os.path.isfile( plssinputObject[0].get()) ) :
                            unfilledFields.append(plssinputObject[2]) 
                        else:
                            if plssinputObject[2] in unfilledFields:
                                unfilledFields.remove(plssinputObject[2])                
                         
            #print ('unfill: ',   unfilledFields)
            if len (unfilledFields) > 0:  #really only one case is possible at a time
                plssStatus.bind_widget(ok_button, balloonmsg  = "Missing: {}".format(unfilledFields))
                ok_button['state'] = 'disabled'
            elif len (unfilledFields) == 0 :
                plssStatus.bind_widget(ok_button, balloonmsg  = "Ready to Continue")
                ok_button['state'] = 'normal'
                
            return unfilledFields
            
        def saveableStateRunner():
                return "Missing input: {}".format(isPLSSReadytoRun(None))

        #selectDataFormatStateMutator(None)   #do we need this?
    
        plssStatus = tix.Balloon(plssLayerWindow)
        ok_button.bind('<Enter>', isPLSSReadytoRun)
        plssStatus.bind_widget(ok_button, balloonmsg = saveableStateRunner () )

         ################ zoning window
    def open_zoningLayerWindow(self):  
    
        #child window attributes
        zoningLayerWindow = Toplevel(self)
        zoningLayerWindow.grab_set() #disables parent window while child is open
        zoningLayerWindow.iconbitmap(wisconsin_icon_path)
        zoningLayerWindow.title('Zoning Layer Input')

        def zoningGenStateMutator(_):
            if (self.input_dict['zoningGenType'].get() == 'Administered by county'):
                zoningGenFC_input['state'] = 'normal'
                zoningGenFC_input_dirBut['state'] = 'normal'
            else:
                zoningGenFC_input['state'] = 'disabled'
                self.input_dict['zoningGenFC'].set('')
                zoningGenFC_input_dirBut['state'] = 'disabled'

        #combo box
        zoningGenType_input_label = Label(zoningLayerWindow, text='County General - with DESCRIPTION/LINK Field:') 
        zoningGenType_input_label.grid(row=0, column=0, padx=5, sticky='w')
        zoningGenType_input = ttk.Combobox(zoningLayerWindow, width=53, textvariable=self.input_dict['zoningGenType'])  #font=('arial', 10),
        zoningGenType_input.grid(row=1, column=0, padx=5)
        zoningGenType_input['values'] = ['Administered by county', 'Administered by county but not in GIS format', 
                                         'Unchanged from last year, not submitted', 'Not administered by county']
        zoningGenType_input['state'] = 'readonly' # prevent typing a value
        zoningGenType_input.bind('<<ComboboxSelected>>', zoningGenStateMutator)
        
        zoningGenFC_input_label = ttk.Label(zoningLayerWindow, text='County General Feature Class:')
        zoningGenFC_input_label.grid(row=3, column=0, padx=5, sticky='w') #grid(column=0, row=0, sticky=tk.W)
        zoningGenFC_input = ttk.Entry(zoningLayerWindow,  width=56, textvariable= self.input_dict['zoningGenFC'])
        
        if self.input_dict['zoningGenFC'].get() == '':  #to prevent overwrite entry
            zoningGenFC_input.insert(0, self.input_dict['zoningGenFC'].get())  #Displays value stored in dictionary in the entry box

        #zoningGenFC_input.insert(0, self.input_dict['zoningGenFC'].get())  #Displays value stored in dictionary in the entry box
        zoningGenFC_input.grid(row=4, column=0, padx=5)
        zoningGenFC_input_dirBut = ttk.Button(zoningLayerWindow, width=8, image=self.folder_icon, 
                                                command = lambda: self.browseFor_inFC(self.input_dict['zoningGenFC'],
                                                                                      childWin2 = zoningLayerWindow))
        zoningGenFC_input_dirBut.grid(row=4, column=1, padx=5)

        def zoningShoreStateMutator(_):
            if (self.input_dict['zoningShoreType'].get() == 'Administered by county'):
                zoningShoreFC_input['state'] = 'normal'
                zoningShoreFC_input_dirBut['state'] = 'normal'
            else:
                zoningShoreFC_input['state'] = 'disabled'
                self.input_dict['zoningShoreFC'].set('')
                zoningShoreFC_input_dirBut['state'] = 'disabled'
        
        #combo box
        zoningShoreType_input_label = Label(zoningLayerWindow, text='Shoreland - with DESCRIPTION/LINK Field:') 
        zoningShoreType_input_label.grid(row=5, column=0, padx=5, sticky='w')
        zoningShoreType_input = ttk.Combobox(zoningLayerWindow, width=53, textvariable=self.input_dict['zoningShoreType'])  #font=('arial', 10), 
        zoningShoreType_input.grid(row=6, column=0, padx=5)
        # TODO: can just assign a reference to an array
        # rather than an object referencing the same array
        zoningShoreType_input['values'] = zoningGenType_input['values'] 
        zoningShoreType_input['state'] = 'readonly' # prevent typing a value
        zoningShoreType_input.bind('<<ComboboxSelected>>', zoningShoreStateMutator)

        zoningShoreFC_input_label = ttk.Label(zoningLayerWindow, text='Shoreland Feature Class:')
        zoningShoreFC_input_label.grid(row=7, column=0, padx=5, sticky='w') #grid(column=0, row=0, sticky=tk.W)
        zoningShoreFC_input = ttk.Entry(zoningLayerWindow,  width=56, textvariable= self.input_dict['zoningShoreFC'])
        if self.input_dict['zoningShoreFC'].get() == '':  #to prevent overwrite entry
            zoningShoreFC_input.insert(0, self.input_dict['zoningShoreFC'].get())  #Displays value stored in dictionary in the entry box
        #zoningShoreFC_input.insert(0, self.input_dict['zoningShoreFC'].get())  #Displays value stored in dictionary in the entry box
        zoningShoreFC_input.grid(row=8, column=0, padx=5)
        zoningShoreFC_input_dirBut = ttk.Button(zoningLayerWindow, width=8, image=self.folder_icon, 
                                                command = lambda: self.browseFor_inFC(self.input_dict['zoningShoreFC'],
                                                                                      childWin2 = zoningLayerWindow))
        zoningShoreFC_input_dirBut.grid(row=8, column=1, padx=5)

        def zoningAirStateMutator(_):
            if (self.input_dict['zoningAirType'].get() == 'Administered by county'):
                zoningAirFC_input['state'] = 'normal'
                zoningAirFC_input_dirBut['state'] = 'normal'
            else:
                zoningAirFC_input['state'] = 'disabled'
                self.input_dict['zoningAirFC'].set('')
                zoningAirFC_input_dirBut['state'] = 'disabled'
        
        #combo box
        zoningAirType_input_label = Label(zoningLayerWindow, text='Airport Protection - with DESCRIPTION/LINK Field:') 
        zoningAirType_input_label.grid(row=9, column=0, padx=5, sticky='w')
        zoningAirType_input = ttk.Combobox(zoningLayerWindow, width=53, textvariable=self.input_dict['zoningAirType'])  #font=('arial', 10), 
        zoningAirType_input.grid(row=10, column=0, padx=5)
        zoningAirType_input['values'] = zoningGenType_input['values']
        zoningAirType_input['state'] = 'readonly' # prevent typing a value
        zoningAirType_input.bind('<<ComboboxSelected>>', zoningAirStateMutator)

        zoningAirFC_input_label = ttk.Label(zoningLayerWindow, text='Airport Protection Feature Class:')
        zoningAirFC_input_label.grid(row=11, column=0, padx=5, sticky='w') #grid(column=0, row=0, sticky=tk.W)
        zoningAirFC_input = ttk.Entry(zoningLayerWindow,  width=56, textvariable= self.input_dict['zoningAirFC'])
        if self.input_dict['zoningAirFC'].get() == '':  #to prevent overwrite entry
            zoningAirFC_input.insert(0, self.input_dict['zoningAirFC'].get())  #Displays value stored in dictionary in the entry box
        #zoningAirFC_input.insert(0, self.input_dict['zoningAirFC'].get())  #Displays value stored in dictionary in the entry box
        zoningAirFC_input.grid(row=12, column=0, padx=5)
        zoningAirFC_input_dirBut = ttk.Button(zoningLayerWindow, width=8, image=self.folder_icon, 
                                                command = lambda: self.browseFor_inFC(self.input_dict['zoningAirFC'],
                                                                                      childWin2 = zoningLayerWindow))
        zoningAirFC_input_dirBut.grid(row=12, column=1, padx=5)

        zoningGenStateMutator(None)
        zoningShoreStateMutator(None)
        zoningAirStateMutator(None)
        
        def putInput_in_DictionaryZoning():
            self.input_dict['zoningGenType'] = tk.StringVar(value=zoningGenType_input.get())
            self.input_dict['zoningGenFC'] = tk.StringVar(value=zoningGenFC_input.get())
            self.input_dict['zoningShoreType'] = tk.StringVar(value=zoningShoreType_input.get())
            self.input_dict['zoningShoreFC'] = tk.StringVar(value=zoningShoreFC_input.get())
            self.input_dict['zoningAirType'] = tk.StringVar(value=zoningAirType_input.get())
            self.input_dict['zoningAirFC'] = tk.StringVar(value=zoningAirFC_input.get())

            zoningRunWindow.set(True)
            
            zoningLayerWindow.destroy()

        bottomFrame = Frame(zoningLayerWindow)
        bottomFrame.grid(row = 13, column = 0, columnspan = 2)

        ok_button = ttk.Button(bottomFrame, width=8,
                               text="OK", command=putInput_in_DictionaryZoning)
        ok_button.grid(row = 0, column = 0, padx=5, pady=5)

        cancel_button = ttk.Button(bottomFrame, width=8,
                                   text = "Cancel", command = zoningLayerWindow.destroy)
        cancel_button.grid(row = 0, column = 1, padx=5, pady=5)
    
        ZLinputObjectMap = [(zoningGenType_input, 'zoningGenType', 'Zoning General Type'),
                                (zoningGenFC_input, 'zoningGenFC', 'Zoning General Feature Class'),  
                                (zoningShoreType_input, 'zoningShoreType', 'Shoreland Type') , 
                                (zoningShoreFC_input, 'zoningShoreFC', 'Shoreland Feature Class'),
                                (zoningAirType_input, 'zoningAirType', 'Airport Protection Type' ),
                                (zoningAirFC_input, 'zoningAirFC', 'Airport Protection Feature Class' )   ]
        defaultInputComparator = {'zoningGenType': '', 'zoningGenFC': '', 'zoningShoreType': '', 'zoningShoreFC': '', 'zoningAirType': '', 'zoningAirFC': ''}
   
        def isZLReadytoRun(event ):
            unfilledFields = list()
            for i in range(0,6,2):
                typeVar = ZLinputObjectMap[i]

                if typeVar[0].get() == defaultInputComparator[typeVar[1]]: 
                    unfilledFields.append(typeVar[2])
                else:
                    #print('type: ', typeVar[0].get(), typeVar[2], defaultInputComparator[typeVar[1]])
                    if typeVar[0].get() == 'Administered by county':
                        fcVar = ZLinputObjectMap[i+1]
                        if (fcVar[0].get() == defaultInputComparator[fcVar[1]]) or (not self.FC_exists(fcVar[0].get())):
                            unfilledFields.append(fcVar[2]) 
                        else:
                            if fcVar[2] in unfilledFields:
                                unfilledFields.remove(fcVar)

            #print ('unfill: ',   unfilledFields)
            if len (unfilledFields) > 0: 
                ZLStatus.bind_widget(ok_button, balloonmsg  = "Missing: {}".format(unfilledFields))
                ok_button['state'] = 'disabled'
            elif len (unfilledFields) == 0 :
                ZLStatus.bind_widget(ok_button, balloonmsg  = "Ready to Continue")
                ok_button['state'] = 'normal'

            return unfilledFields
      
        zoningGenStateMutator(None)
        zoningShoreStateMutator(None)
        zoningAirStateMutator(None)

        def saveableStateRunner():
                return "Missing input: {}".format(isZLReadytoRun(None))

        ZLStatus = tix.Balloon(zoningLayerWindow)
        ok_button.bind('<Enter>', isZLReadytoRun)
        ZLStatus.bind_widget(ok_button, balloonmsg = saveableStateRunner () )
        
    ############## Other layers window
    def open_otherLayersWindow(self):
        #child window attributes
        otherLayerWindow = Toplevel(self)
        otherLayerWindow.grab_set() #disables parent window while child is open
        otherLayerWindow.iconbitmap(wisconsin_icon_path)
        otherLayerWindow.title('Other Layers Input')

        comboBoxOptions = ['Unchanged from last year - not submitted',
                           'Maintained by county',
                           'Not in GIS format']

        def rightOfWayStateMutator(_):
            if (self.input_dict['RightOfWayType'].get() == 'Maintained by county'):
                rightsOfWayFCInput['state'] = 'normal'
                rightsOfWayFCInputDirBut['state'] = 'normal'
            else:
                rightsOfWayFCInput['state'] = 'disabled'
                self.input_dict['RightOfWayFC'].set('')
                rightsOfWayFCInputDirBut['state'] = 'disabled'

        rightOfWayLabel = Label(otherLayerWindow, text = 'Rights-of-Way') # remove optionals
        rightOfWayLabel.grid(row = 0, column = 0, sticky = tk.W)
        rightOfWayComboBox = ttk.Combobox(otherLayerWindow, width = 40, values = comboBoxOptions,
                                          textvariable = self.input_dict['RightOfWayType'])
        rightOfWayComboBox.bind('<<ComboboxSelected>>', rightOfWayStateMutator)
        rightOfWayComboBox.grid(row = 1, column = 0, padx = 5, sticky = tk.W)
        rightOfWayComboBox['state'] = 'readonly'
        rightOfWayFCLabel = Label(otherLayerWindow, text = 'Rights-of-Way Feature Class')
        rightOfWayFCLabel.grid(row = 2, column = 0, sticky = tk.W)
        rightsOfWayFCInput = ttk.Entry(otherLayerWindow, width=56,
                                       textvariable = self.input_dict['RightOfWayFC'])
        #rightsOfWayFCInput.insert(0, self.input_dict['RightOfWayFC'].get()) # displays stored value
        if self.input_dict['RightOfWayFC'].get() == '':  #to prevent overwrite entry                        
            rightsOfWayFCInput.insert(0, self.input_dict['RightOfWayFC'].get()) # displays stored value
        rightsOfWayFCInput.grid(row = 3, column = 0, padx = 5, sticky = tk.W)
        rightsOfWayFCInputDirBut = ttk.Button(otherLayerWindow, width = 8, image = self.folder_icon,
                                              command = lambda: self.browseFor_inFC(self.input_dict['RightOfWayFC'],
                                                                                             childWin2 = otherLayerWindow))
        rightsOfWayFCInputDirBut.grid(row = 3, column = 1, padx = 5, sticky = tk.W)

        def roadStreetCenterStateMutator(_):
            if (self.input_dict['RoadStreetCenterlineType'].get() == 'Maintained by county'):
                roadsStreetCenterFCInput['state'] = 'normal'
                roadsStreetCenterFCInputDirBut['state'] = 'normal'
            else:
                roadsStreetCenterFCInput['state'] = 'disabled'
                self.input_dict['RoadStreetCenterlineFC'].set('')
                roadsStreetCenterFCInputDirBut['state'] = 'disabled'
        
        roadStreetsCenterLabel = Label(otherLayerWindow, text = 'Roads/Streets/Centerline')
        roadStreetsCenterLabel.grid(row = 4, column = 0, sticky = tk.W)
        roadStreetCenterComboBox = ttk.Combobox(otherLayerWindow, width = 40, values = comboBoxOptions[1:3],
                                                textvariable = self.input_dict['RoadStreetCenterlineType'])
        roadStreetCenterComboBox.bind("<<ComboboxSelected>>", roadStreetCenterStateMutator)
        roadStreetCenterComboBox.grid(row = 5, column = 0, padx = 5, sticky = tk.W)
        roadStreetCenterComboBox['state'] = 'readonly'
        roadStreetCenterFCLabel = Label(otherLayerWindow, text = 'Roads/Streets/Centerline Feature Class')
        roadStreetCenterFCLabel.grid(row = 6, column = 0, sticky = tk.W)
        roadsStreetCenterFCInput = ttk.Entry(otherLayerWindow, width=56, 
                                       textvariable = self.input_dict['RoadStreetCenterlineFC'])
        if self.input_dict['RoadStreetCenterlineFC'].get() == '':  #to prevent overwrite entry                                                
            roadsStreetCenterFCInput.insert(0, self.input_dict['RoadStreetCenterlineFC'].get()) # displays stored value
        #roadsStreetCenterFCInput.insert(0, self.input_dict['RoadStreetCenterlineFC'].get()) # displays stored value
        roadsStreetCenterFCInput.grid(row = 7, column = 0, padx = 5, sticky = tk.W)
        roadsStreetCenterFCInputDirBut = ttk.Button(otherLayerWindow, width = 8, image = self.folder_icon,
                                                    command = lambda: self.browseFor_inFC(self.input_dict['RoadStreetCenterlineFC'],
                                                                                             childWin2 = otherLayerWindow))
        roadsStreetCenterFCInputDirBut.grid(row = 7, column = 1, padx = 5, sticky = tk.W)

        def hydrographyMutator(_):
            if (self.input_dict['HydroLineType'].get() == 'Maintained by county'):
                hydroFCInput['state'] = 'normal'
                hydroFCInputDirBut['state'] = 'normal'
            else:
                hydroFCInput['state'] = 'disabled'
                hydroFCInputDirBut['state'] = 'disabled'
        
        hydroLabel = Label(otherLayerWindow, text = 'Hydrography (line)')
        hydroLabel.grid(row = 8, column = 0, sticky = tk.W)
        hydroComboBox = ttk.Combobox(otherLayerWindow, width = 40, values = comboBoxOptions,
                                                textvariable = self.input_dict['HydroLineType'])
        hydroComboBox.bind("<<ComboboxSelected>>", hydrographyMutator)
        hydroComboBox.grid(row = 9, column = 0, padx = 5, sticky = tk.W)
        hydroComboBox['state'] = 'readonly'
        hydroFCLabel = Label(otherLayerWindow, text = 'Hydrography (line) Feature Class')
        hydroFCLabel.grid(row = 10, column = 0, sticky = tk.W)
        hydroFCInput = ttk.Entry(otherLayerWindow, width=56, 
                                       textvariable = self.input_dict['HydroLineFC'])
        if self.input_dict['HydroLineFC'].get() == '':  #to prevent overwrite entry                                                
            hydroFCInput.insert(0, self.input_dict['HydroLineFC'].get()) # displays stored value
        #hydroFCInput.insert(0, self.input_dict['HydroLineFC'].get()) # displays stored value
        hydroFCInput.grid(row = 11, column = 0, padx = 5, sticky = tk.W)
        hydroFCInputDirBut = ttk.Button(otherLayerWindow, width = 8, image = self.folder_icon,
                                        command = lambda: self.browseFor_inFC(self.input_dict['HydroLineFC'],
                                                                                             childWin2 = otherLayerWindow))
        hydroFCInputDirBut.grid(row = 11, column = 1, padx = 5, sticky = tk.W)

        def hydroPolyMutator(_):
            if (self.input_dict['HydroPolyType'].get() == 'Maintained by county'):
                hydroPolyFCInput['state'] = 'normal'
                hydroPolyFCInputDirBut['state'] = 'normal'
            else:
                hydroPolyFCInput['state'] = 'disabled'
                self.input_dict['HydroPolyFC'].set('')
                hydroPolyFCInputDirBut['state'] = 'disabled'
        
        hydroPolyLabel = Label(otherLayerWindow, text = 'Hydrography (poly)')
        hydroPolyLabel.grid(row = 12, column = 0, sticky = tk.W)
        hydroPolyComboBox = ttk.Combobox(otherLayerWindow, width = 40, values = comboBoxOptions,
                                                textvariable = self.input_dict['HydroPolyType'])
        hydroPolyComboBox.bind("<<ComboboxSelected>>", hydroPolyMutator)
        hydroPolyComboBox.grid(row = 13, column = 0, padx = 5, sticky = tk.W)
        hydroPolyComboBox['state'] = 'readonly'
        hydroPolyFCLabel = Label(otherLayerWindow, text = 'Hydrography (poly) Feature Class')
        hydroPolyFCLabel.grid(row = 14, column = 0, sticky = tk.W)
        hydroPolyFCInput = ttk.Entry(otherLayerWindow, width=56, 
                                       textvariable = self.input_dict['HydroPolyFC'])
               
        if self.input_dict['HydroPolyFC'].get() == '':  #to prevent overwrite entry                                                
            hydroPolyFCInput.insert(0, self.input_dict['HydroPolyFC'].get()) # displays stored value
        #hydroPolyFCInput.insert(0, self.input_dict['HydroPolyFC'].get()) # displays stored value
        hydroPolyFCInput.grid(row = 15, column = 0, padx = 5, sticky = tk.W)
        hydroPolyFCInputDirBut = ttk.Button(otherLayerWindow, width = 8, image = self.folder_icon,
                                              command = lambda: self.browseFor_inFC(self.input_dict['HydroPolyFC'],
                                                                                    childWin2 = otherLayerWindow))
        hydroPolyFCInputDirBut.grid(row = 15, column = 1, padx = 5, sticky = tk.W)

        def addressesMutator(_):
            if (self.input_dict['AddressesType'].get() == 'Maintained by county'):
                addressesFCInput['state'] = 'normal'
                addressesFCInputDirBut['state'] = 'normal'
            else:
                addressesFCInput['state'] = 'disabled'
                self.input_dict['AddressesFC'].set('')
                addressesFCInputDirBut['state'] = 'disabled'
        
        addressesLabel = Label(otherLayerWindow, text = 'Addresses')
        addressesLabel.grid(row = 16, column = 0, sticky = tk.W)
        addressesComboBox = ttk.Combobox(otherLayerWindow, width = 40, values = comboBoxOptions[1:3],
                                                textvariable = self.input_dict['AddressesType'])
        addressesComboBox.bind("<<ComboboxSelected>>", addressesMutator)
        addressesComboBox.grid(row = 17, column = 0, padx = 5, sticky = tk.W)
        addressesComboBox['state'] = 'readonly'
        addressesFCLabel = Label(otherLayerWindow, text = 'Addresses Feature Class')
        addressesFCLabel.grid(row = 18, column = 0, sticky = tk.W)
        addressesFCInput = ttk.Entry(otherLayerWindow, width=56, 
                                       textvariable = self.input_dict['AddressesFC'])
        if self.input_dict['AddressesFC'].get() == '':  #to prevent overwrite entry                                                
            addressesFCInput.insert(0, self.input_dict['AddressesFC'].get()) # displays stored value
        #addressesFCInput.insert(0, self.input_dict['AddressesFC'].get()) # displays stored value
        addressesFCInput.grid(row = 19, column = 0, padx = 5, sticky = tk.W)
        addressesFCInputDirBut = ttk.Button(otherLayerWindow, width = 8, image = self.folder_icon,
                                              command = lambda: self.browseFor_inFC(self.input_dict['AddressesFC'],
                                               childWin2 = otherLayerWindow))
        addressesFCInputDirBut.grid(row = 19, column = 1, padx = 5, sticky = tk.W)

        def bldgMutator(_):
            if (self.input_dict['BuildingBuildingFootprintType'].get() == 'Maintained by county'):
                bldgFCInput['state'] = 'normal'
                bldgFCInputDirBut['state'] = 'normal'
            else:
                bldgFCInput['state'] = 'disabled'
                self.input_dict['BuildingBuildingFootprintFC'].set('')
                bldgFCInputDirBut['state'] = 'disabled'
        
        bldgLabel = Label(otherLayerWindow, text = 'Building(s) Footprints')
        bldgLabel.grid(row = 0, column = 2, sticky = tk.W)
        bldgComboBox = ttk.Combobox(otherLayerWindow, width = 40, values = comboBoxOptions,
                                                textvariable = self.input_dict['BuildingBuildingFootprintType'])
        bldgComboBox.bind("<<ComboboxSelected>>", bldgMutator)
        bldgComboBox.grid(row = 1, column = 2, padx = 5, sticky = tk.W)
        bldgComboBox['state'] = 'readonly'
        bldgFCLabel = Label(otherLayerWindow, text = 'Building(s) Footprints Feature Class')
        bldgFCLabel.grid(row = 2, column = 2, sticky = tk.W)
        bldgFCInput = ttk.Entry(otherLayerWindow, width=56, 
                                       textvariable = self.input_dict['BuildingBuildingFootprintFC'])
        
        if self.input_dict['BuildingBuildingFootprintFC'].get() == '':  #to prevent overwrite entry                                                
            bldgFCInput.insert(0, self.input_dict['BuildingBuildingFootprintFC'].get()) # displays stored value
        #bldgFCInput.insert(0, self.input_dict['BuildingBuildingFootprintFC'].get()) # displays stored value
        bldgFCInput.grid(row = 3, column = 2, padx = 5, sticky = tk.W)
        bldgFCInputDirBut = ttk.Button(otherLayerWindow, width = 8, image = self.folder_icon,
                                       command = lambda: self.browseFor_inFC(self.input_dict['BuildingBuildingFootprintFC'],
                                        childWin2 = otherLayerWindow))
        bldgFCInputDirBut.grid(row = 3, column = 3, padx = 5, sticky = tk.W)

        def luMutator(_):
            if (self.input_dict['LandUseType'].get() == 'Maintained by county'):
                luFCInput['state'] = 'normal'
                luFCInputDirBut['state'] = 'normal'
            else:
                luFCInput['state'] = 'disabled'
                self.input_dict['LandUseFC'].set('')
                luFCInputDirBut['state'] = 'disabled'
        
        luLabel = Label(otherLayerWindow, text = 'Land Use')
        luLabel.grid(row = 4, column = 2, sticky = tk.W)
        luComboBox = ttk.Combobox(otherLayerWindow, width = 40, values = comboBoxOptions,
                                                textvariable = self.input_dict['LandUseType'])
        luComboBox.bind("<<ComboboxSelected>>", luMutator)
        luComboBox.grid(row = 5, column = 2, padx = 5, sticky = tk.W)
        luComboBox['state'] = 'readonly'
        luFCLabel = Label(otherLayerWindow, text = 'Land Use Feature Class')
        luFCLabel.grid(row = 6, column = 2, sticky = tk.W)
        luFCInput = ttk.Entry(otherLayerWindow, width=56, 
                                       textvariable = self.input_dict['LandUseFC'])
        if self.input_dict['LandUseFC'].get() == '':  #to prevent overwrite entry                                                
            luFCInput.insert(0, self.input_dict['LandUseFC'].get()) # displays stored value
        #luFCInput.insert(0, self.input_dict['LandUseFC'].get()) # displays stored value
        luFCInput.grid(row = 7, column = 2, padx = 5, sticky = tk.W)
        luFCInputDirBut = ttk.Button(otherLayerWindow, width = 8, image = self.folder_icon,
                                       command = lambda: self.browseFor_inFC(self.input_dict['LandUseFC'],
                                        childWin2 = otherLayerWindow))
        luFCInputDirBut.grid(row = 7, column = 3, padx = 5, sticky = tk.W)

        def parksMutator(_):
            if (self.input_dict['ParksOpenSpaceType'].get() == 'Maintained by county'):
                parksFCInput['state'] = 'normal'
                parksFCInputDirBut['state'] = 'normal'
            else:
                parksFCInput['state'] = 'disabled'
                self.input_dict['ParksOpenSpaceFC'].set('')
                parksFCInputDirBut['state'] = 'disabled'
        
        parksLabel = Label(otherLayerWindow, text = 'Parks/Open Space (e.g. county forests)')
        parksLabel.grid(row = 8, column = 2, sticky = tk.W)
        parksComboBox = ttk.Combobox(otherLayerWindow, width = 40, values = comboBoxOptions,
                                                textvariable = self.input_dict['ParksOpenSpaceType'])
        parksComboBox.bind("<<ComboboxSelected>>", parksMutator)
        parksComboBox.grid(row = 9, column = 2, padx = 5, sticky = tk.W)
        parksComboBox['state'] = 'readonly'
        parksFCLabel = Label(otherLayerWindow, text = 'Parks/Open Space Feature Class')
        parksFCLabel.grid(row = 10, column = 2, sticky = tk.W)
        parksFCInput = ttk.Entry(otherLayerWindow, width=56,
                                 textvariable = self.input_dict['ParksOpenSpaceFC'])
        if self.input_dict['ParksOpenSpaceFC'].get() == '':  #to prevent overwrite entry                                                
            parksFCInput.insert(0, self.input_dict['ParksOpenSpaceFC'].get()) # displays stored value
        #parksFCInput.insert(0, self.input_dict['ParksOpenSpaceFC'].get()) # displays stored value
        parksFCInput.grid(row = 11, column = 2, padx = 5, sticky = tk.W)
        parksFCInputDirBut = ttk.Button(otherLayerWindow, width = 8, image = self.folder_icon,
                                        command = lambda: self.browseFor_inFC(self.input_dict['ParksOpenSpaceFC'],
                                         childWin2 = otherLayerWindow))
        parksFCInputDirBut.grid(row = 11, column = 3, padx = 5, sticky = tk.W)

        def trailsMutator(_):
            if (self.input_dict['TrailsType'].get() == 'Maintained by county'):
                trailsFCInput['state'] = 'normal'
                trailsFCInputDirBut['state'] = 'normal'
            else:
                trailsFCInput['state'] = 'disabled'
                self.input_dict['TrailsFC'].set('')
                trailsFCInputDirBut['state'] = 'disabled'
        
        trailsLabel = Label(otherLayerWindow, text = 'Trails')
        trailsLabel.grid(row = 12, column = 2, sticky = tk.W)
        trailsComboBox = ttk.Combobox(otherLayerWindow, width = 40, values = comboBoxOptions,
                                                textvariable = self.input_dict['TrailsType'])
        trailsComboBox.bind("<<ComboboxSelected>>", trailsMutator)
        trailsComboBox.grid(row = 13, column = 2, padx = 5, sticky = tk.W)
        trailsComboBox['state'] = 'readonly'
        trailsFCLabel = Label(otherLayerWindow, text = 'Trails Feature Class')
        trailsFCLabel.grid(row = 14, column = 2, sticky = tk.W)
        trailsFCInput = ttk.Entry(otherLayerWindow, width=56,
                                 textvariable = self.input_dict['TrailsFC'])
        if self.input_dict['TrailsFC'].get() == '':  #to prevent overwrite entry                                                  
            trailsFCInput.insert(0, self.input_dict['TrailsFC'].get()) # displays stored value
        #trailsFCInput.insert(0, self.input_dict['TrailsFC'].get()) # displays stored value
        trailsFCInput.grid(row = 15, column = 2, padx = 5, sticky = tk.W)
        trailsFCInputDirBut = ttk.Button(otherLayerWindow, width = 8, image = self.folder_icon,
                                       command = lambda: self.browseFor_inFC(self.input_dict['TrailsFC'],
                                        childWin2 = otherLayerWindow))
        trailsFCInputDirBut.grid(row = 15, column = 3, padx = 5, sticky = tk.W)

        def otherRecMutator(_):
            if (self.input_dict['OtherRecreationType'].get() == 'Maintained by county'):
                otherRecFCInput['state'] = 'normal'
                otherRecFCInputDirBut['state'] = 'normal'
            else:
                otherRecFCInput['state'] = 'disabled'            
                self.input_dict['OtherRecreationFC'].set('')
                otherRecFCInputDirBut['state'] = 'disabled'
        
        otherRecLabel = Label(otherLayerWindow, text = 'Other Recreation (boat launches, etc.)')
        otherRecLabel.grid(row = 16, column = 2, sticky = tk.W)
        otherRecComboBox = ttk.Combobox(otherLayerWindow, width = 40, values = comboBoxOptions,
                                                textvariable = self.input_dict['OtherRecreationType'])
        otherRecComboBox.bind("<<ComboboxSelected>>", otherRecMutator)
        otherRecComboBox.grid(row = 17, column = 2, padx = 5, sticky = tk.W)
        otherRecComboBox['state'] = 'readonly'
        otherRecFCLabel = Label(otherLayerWindow, text = 'Other Recreation')
        otherRecFCLabel.grid(row = 18, column = 2, sticky = tk.W)
        otherRecFCInput = ttk.Entry(otherLayerWindow, width=56,
                                 textvariable = self.input_dict['OtherRecreationFC'])
        if self.input_dict['OtherRecreationFC'].get() == '':  #to prevent overwrite entry                                                
            otherRecFCInput.insert(0, self.input_dict['OtherRecreationFC'].get()) # displays stored value
        #otherRecFCInput.insert(0, self.input_dict['OtherRecreationFC'].get()) # displays stored value
        otherRecFCInput.grid(row = 19, column = 2, padx = 5, sticky = tk.W)
        otherRecFCInputDirBut = ttk.Button(otherLayerWindow, width = 8, image = self.folder_icon,
                                       command = lambda: self.browseFor_inFC(self.input_dict['OtherRecreationFC'], 
                                       childWin2 = otherLayerWindow))
        otherRecFCInputDirBut.grid(row = 19, column = 3, padx = 5, sticky = tk.W)

        # enforce default states
        rightOfWayStateMutator(None) 
        roadStreetCenterStateMutator(None)
        hydrographyMutator(None)
        hydroPolyMutator(None)
        addressesMutator(None)
        bldgMutator(None)
        luMutator(None)
        parksMutator(None)
        trailsMutator(None)
        otherRecMutator(None)

        def putInput_in_DictionaryOther():
            self.input_dict['RightOfWayType'] = tk.StringVar(value = rightOfWayComboBox.get())
            self.input_dict['RightOfWayFC'] = tk.StringVar(value = rightsOfWayFCInput.get())
            self.input_dict['RoadStreetCenterlineType'] = tk.StringVar(value = roadStreetCenterComboBox.get())
            self.input_dict['RoadStreetCenterFCInput'] = tk.StringVar(value = roadsStreetCenterFCInput.get())
            self.input_dict['HydroLineType'] = tk.StringVar(value = hydroComboBox.get())
            self.input_dict['HydroLineFC'] = tk.StringVar(value = hydroFCInput.get())
            self.input_dict['HydroPolyType'] = tk.StringVar(value = hydroPolyComboBox.get())
            self.input_dict['HydroPolyFC'] = tk.StringVar(value = hydroPolyFCInput.get())
            self.input_dict['AddressesType'] = tk.StringVar(value = addressesComboBox.get())
            self.input_dict['AddressesFC'] = tk.StringVar(value = addressesFCInput.get())
            self.input_dict['BuildingBuildingFootprintType'] = tk.StringVar(value = bldgComboBox.get())
            self.input_dict['BuildingBuildingFootprintFC'] = tk.StringVar(value = bldgFCInput.get())
            self.input_dict['LandUseType'] = tk.StringVar(value = luComboBox.get())
            self.input_dict['LandUseFC'] = tk.StringVar(value = luFCInput.get())
            self.input_dict['ParksOpenSpaceType'] = tk.StringVar(value = parksComboBox.get())
            self.input_dict['ParksOpenSpaceFC'] = tk.StringVar(value = parksFCInput.get())
            self.input_dict['TrailsType'] = tk.StringVar(value = trailsComboBox.get())
            self.input_dict['TrailsFC'] = tk.StringVar(value = trailsFCInput.get())
            self.input_dict['OtherRecreationType'] = tk.StringVar(value = otherRecComboBox.get())
            self.input_dict['OtherRecreationFC'] = tk.StringVar(value = otherRecFCInput.get())
            othersRunWindow.set(True)
            
            otherLayerWindow.destroy()

        bottomFrame = Frame(otherLayerWindow)
        bottomFrame.grid(row = 40, column = 0, columnspan = 4, sticky = tk.S)

        ok_button = ttk.Button(bottomFrame, width=8, text= "OK",
                               command = putInput_in_DictionaryOther)
        ok_button.grid(row = 0, column = 0, padx=5, pady=5, sticky = tk.S)

        cancel_button = ttk.Button(bottomFrame, width=8, text = "Cancel",
                                   command = otherLayerWindow.destroy)
        cancel_button.grid(row = 0, column = 1, padx=5, pady=5, sticky = tk.S)

        OLinputObjectMap = [(rightOfWayComboBox, 'RightOfWayType', 'Right of Way Type'),
                                (rightsOfWayFCInput, 'RightOfWayFC', 'ROW Feature Class'),  
                                (roadStreetCenterComboBox, 'RoadStreetCenterlineType', 'Road Street Center Line Type') , 
                                (roadsStreetCenterFCInput, 'RoadStreetCenterlineFC', 'Road Street Center Line Feature Class'),
                                (hydroComboBox, 'HydroLineType', 'Hydro Line Type' ),
                                (hydroFCInput, 'HydroLineFC', 'Hydro Line Feature Class' ) ,
                                (hydroPolyComboBox, 'HydroPolyType', 'Hydro Poly Type') , 
                                (hydroPolyFCInput, 'HydroPolyFC', 'Hydro Poly Feature Class'),
                                (addressesComboBox, 'AddressesType', 'Addresses Type' ),
                                (addressesFCInput, 'AddressesFC', 'Addresses Feature Class' ),  
                                (bldgComboBox, 'BuildingBuildingFootprintType', 'Building Footprint Type'),
                                (bldgFCInput, 'BuildingBuildingFootprintFC', 'Building Footprint Feature Class'),  
                                (luComboBox, 'LandUseType', 'Land Use Type') , 
                                (luFCInput, 'LandUseFC', 'Land Use Feature Class'),
                                (parksComboBox, 'ParksOpenSpaceType', 'Parks Type' ),
                                (parksFCInput, 'ParksOpenSpaceFC', 'Parks Feature Class' ),
                                (trailsComboBox, 'TrailsType', 'Trails Type'), 
                                (trailsFCInput, 'TrailsFC', 'Trails Feature Class'),
                                (otherRecComboBox, 'OtherRecreationType', 'Other Recreation Type' ),
                                (otherRecFCInput, 'OtherRecreationFC', 'Other Reacreation Feature Class' )    ]

        defaultInputComparator = {'RightOfWayType': '', 'RightOfWayFC': '', 'RoadStreetCenterlineType': '', 'RoadStreetCenterlineFC': '', 
                                    'HydroLineType': '', 'HydroLineFC': '', 'HydroPolyType': '', 'HydroPolyFC': '', 
                                    'AddressesType': '', 'AddressesFC': '', 'BuildingBuildingFootprintType': '', 'BuildingBuildingFootprintFC': '', 
                                    'LandUseType': '', 'LandUseFC': '', 'ParksOpenSpaceType': '', 'ParksOpenSpaceFC': '', 
                                    'TrailsType': '', 'TrailsFC': '', 'OtherRecreationType': '', 'OtherRecreationFC': ''    }

        def isOLReadytoRun(event ):
            unfilledFields = list()
            for i in range(0,20,2):
                typeVar = OLinputObjectMap[i]

                if typeVar[0].get() == defaultInputComparator[typeVar[1]]: 
                    unfilledFields.append(typeVar[2])
                else:
                    #print('type: ', typeVar[0].get(), typeVar[2], defaultInputComparator[typeVar[1]])
                    if typeVar[0].get() == 'Maintained by county':
                        fcVar = OLinputObjectMap[i+1]
                        #print (fcVar[0].get() )
                        #if (fcVar[0].get() == defaultInputComparator[fcVar[1]]):
                        if (fcVar[0].get() == defaultInputComparator[fcVar[1]]) or (not self.FC_exists(fcVar[0].get())):
                            unfilledFields.append(fcVar[2]) 
                        else:
                            if fcVar[2] in unfilledFields:
                                unfilledFields.remove(fcVar)

            #print ('unfill: ',   unfilledFields)
            if len (unfilledFields) > 0: 
                OLStatus.bind_widget(ok_button, balloonmsg  = "Missing: {}".format(unfilledFields))
                ok_button['state'] = 'disabled'
            elif len (unfilledFields) == 0 :
                OLStatus.bind_widget(ok_button, balloonmsg  = "Ready to Continue")
                ok_button['state'] = 'normal'

            return unfilledFields

        def saveableStateRunner():
                return "Missing input: {}".format(isOLReadytoRun(None))

        OLStatus = tix.Balloon(otherLayerWindow)
        ok_button.bind('<Enter>', isOLReadytoRun)
        OLStatus.bind_widget(ok_button, balloonmsg = saveableStateRunner () )
                              
    def big_run_button(self):
        #Convert Tkinter strings to regular string in dictionary
        self.input_string_dict = collections.OrderedDict()

        #Convert tkinter strings to regular string in dictionary
        self.input_string_dict['inCert'] = {element: '' for element in ['explainedErrorsNumber',
                                                                    'noticeOfNewStreetName',
                                                                    'noticeOfNewNonParcelFeaturePARCELIDs',
                                                                    'noticeOfMissingDataOmissions',
                                                                    'noticeErrorsSumsUnresolvable',
                                                                    'noticeOther']}
        for i in self.inputNameList:
            if i != 'inCert':
                self.input_string_dict[i] = self.input_dict[i].get()
            else :
                for j in self.input_dict[i]:
                    self.input_string_dict[i][j] = self.input_dict[i][j].get()
              
        # sets required variable to test run the validation tool in Test Mode
        self.input_string_dict['isSearchable'] = 'true'

        #print (self.input_string_dict)
        validation_tool_run_all(self.input_string_dict)

if __name__ == '__main__':  
    gui = tix.Tk()
    gui.title('SCO Validation Tool v2.0') #title of main menu
    gui.geometry('420x450')  #dimensions of main menu window (W x H)
    
    #ogr.DontUseExceptions()
    #ogr.UseExceptions()
    #ogr.PushErrorHandler('CPLQuietErrorHandler')

    #logging.basicConfig(filename='c:/temp/somefile.log',  format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

    """
    try:
        #raise a GDAL error on purpose
        ogr.Error(ogr.CE_Failure, 1, "Some error message")
    except:
        logging.error(ogr.GetLastErrorMsg())
    """
        
    path_ofScript = os.path.dirname (os.path.abspath(__file__))
    
    try:
        wd = sys._MEIPASS
        path_of_script = os.path.join (wd, path_ofScript)
        
    except AttributeError:
        path_of_script = path_ofScript 

    wisconsin_icon_path = path_of_script + '\\assets\\V1.ico' 
    folder_gif_path =  path_of_script + '\\assets\\openfilefolder.gif' 
    gui.iconbitmap(wisconsin_icon_path)
    print ("hello, world")

    import importlib
    from os.path import dirname, basename
    fp, pathname, description = importlib.find_module('_gdal', [dirname(gdal.__file__)])

    print (pathname)
    print (description)

    dist_dir = "dist"
    shutil.copy(pathname, dist_dir)
    print ( dist_dir )

    #app = App (master=gui)
    #app.mainloop()