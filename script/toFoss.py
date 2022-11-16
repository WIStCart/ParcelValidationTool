import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import *
import tkinter.tix as tix
import os
from os import path
import collections
from osgeo import gdal
from osgeo import ogr

class App(ttk.Frame):    
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.pack(padx=5, pady=5)

        self.inputNameList = ['isSearchable','isFinal','county','inFC','outDir',
                              'outName','outINIDir','subName','subEmail','condoModel',
                              'inCert','isNameRedact','redactPolicy','zoningGenType',
                              'zoningGenFC','zoningShoreType','zoningShoreFC',
                              'zoningAirType','zoningAirFC','PLSSType','PLSSFC',
                              'RightOfWayType','RightOfWayFC','RoadStreetCenterlineType',
                              'RoadStreetCenterlineFC','HydroLineType','HydroLineFC',
                              'HydroPolyType','HydroPolyFC','AddressesType','AddressesFC',
                              'BuildingBuildingFootprintType','BuildingBuildingFootprintFC',
                              'LandUseType','LandUseFC','ParksOpenSpaceType','ParksOpenSpaceFC',
                              'TrailsType','TrailsFC','OtherRecreationType','OtherRecreationFC',
                              'certifiedBy','PLSSOtherDigitalFile']

        self.input_dict = collections.OrderedDict()

        for i in self.inputNameList:
            self.input_dict[i] = tk.StringVar(value="")
        self.create_widgets()

    def onselect(self, event, full_path):
        """ select a feature class to be procesed, i.e. compared """
        w = event.widget
        index = w.curselection()[0] #position of fc in the list
        full_path.set(self.feature_classes[index])

    def open_win(self, full_path, childWin):
        """ open a window with a list of the feature classes list in the gdb"""
        new= Toplevel(childWin)
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

        # TODO: insert some warning for wrong file type
        # in either external logging window or reactive 
        # pop-up message
        while not(path_name.lower().endswith('.gdb')):
            path_name = askdirectory()

        if path_name:
            datasource = ogr.GetDriverByName('OpenFileGDB').Open(path_name, 0)

            for layerIndex in range(datasource.GetLayerCount()):
                layer = datasource.GetLayerByIndex(layerIndex)
                self.feature_classes.append(os.path.join(path_name, layer.GetName()))
                self.files_list.append(layer.GetName())

            self.open_win(full_path, childWin = childWin2)

    def create_widgets(self):
        """create the widgets in the app gui """
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

        def updateCounty(_):
            self.input_dict['county'].set(county_input.get())
            #print(self.input_dict['county'].get())
        
        county_input.bind('<<ComboboxSelected>>', updateCounty) #, self.selected_county)
     
        inFC_input_label = ttk.Label(self, text='Input Parcels Feature Class Path:')
        inFC_input_label.grid(column=0, row=3, sticky=tk.W)
        inFC_input = ttk.Entry(self,  width=56, textvariable= self.input_dict['inFC'])
        #inFC_input['state'] = 'readonly' 
        inFC_input.grid(column=0, row=4, sticky=tk.W)
        inFC_dirBut = ttk.Button(self, width=8, 
                                command = lambda: self.browseFor_inFC(self.input_dict['inFC'], 
                                childWin2=self)) 
        inFC_dirBut.grid(column=1, row=4, sticky=tk.W, padx=5)

        outDir_input_label = ttk.Label(self, text='Output Directory Path (gdb):')
        outDir_input_label.grid(column=0, row=5, sticky=tk.W)
        outDir_input = ttk.Entry(self, width=56, textvariable= self.input_dict['outDir'])
        outDir_input.grid(column=0, row=6, sticky=tk.W)
        #TO ASK - ask how and why this lambda function works
        outDir_input_dirBut = ttk.Button(self, width=8, 
                                        command = lambda: self.browse_to_GDB(self.input_dict['outDir']))
        outDir_input_dirBut.grid(column=1, row=6, sticky=tk.W, padx=5)
        
        outName_input_label = ttk.Label(self, text='Output Feature Class File Name:')
        outName_input_label.grid(column=0, row=7, sticky=tk.W)
        outName_input = ttk.Entry(self, width=56, textvariable= self.input_dict['outName'])
        outName_input.grid(column=0, row=8, sticky=tk.W)

        buttonsFrame = Frame(self)
        buttonsFrame.grid(column = 0, row = 9, sticky = tk.N)

        canvasDrawer = Canvas(buttonsFrame, height = 200, width = 10)
        canvasDrawer.grid(column = 1, rowspan = 5, row = 0, padx = 10)
        
        button_main_1 = ttk.Button(buttonsFrame, width=25, text = "Parcel Data Information")#,
                                   #command = self.open_parcelDataInformationWindow)
        button_main_1.grid(column=0, row = 0, sticky=tk.N, pady=(20,10))

        button_main_2 = ttk.Button(buttonsFrame, width=25, text = "PLSS Layer")#, command = self.open_plssLayerWindow) 
        button_main_2.grid(column=0, row=1, sticky=tk.N, pady=10)       

        button_main_3 = ttk.Button(buttonsFrame, width=25, text = "Zoning Layer")#, command = self.open_zoningLayerWindow)
        button_main_3.grid(column=0, row=2, sticky=tk.N, pady=10)

        button_main_4 = ttk.Button(buttonsFrame, width=25, text = "Other Layers")#, command = self.open_otherLayersWindow) 
        button_main_4.grid(column=0, row=3, sticky=tk.N, pady=10)
        
        button_main_5 = ttk.Button(buttonsFrame, width=15, text = "Run")#, command = self.big_run_button) 
        button_main_5.grid(column=0, row=4, sticky=tk.N, pady=10)

if __name__ == '__main__':  
    gui = tix.Tk()
    app = App (master=gui)
    app.mainloop()