import tkinter
from tkinter import ttk
from PIL import Image 
import customtkinter
import os
import pandas as pd
import sys
from CreateIDF import createIDF
from OptimizationBruteForce import runOptimization
from InvestmentCost import investmentCost
from threading import Thread
from eppy.modeleditor import IDF

mode = "light"
customtkinter.set_appearance_mode(mode)
customtkinter.set_default_color_theme("dark-blue")

class runSimulationThreading(Thread):
    def __init__(self, currentPath, simulationName, simulationStateLabel):
        super().__init__()

        self.currentPath = currentPath
        self.simulationName = simulationName
        self.simulationStateLabel = simulationStateLabel
    
    def run(self):
        # Write console to file
        stdout_obj = sys.stdout                                 # store it somewhare so I can reset it after writing to file
        logFilePath = self.currentPath + "/log.txt"
        sys.stdout = open(logFilePath, "w")                     # now I write to file what should appear on the console
        self.simulationStateLabel.configure(text="Simulation starting", fg_color="#FCD12A", text_color="white", font=("", 13, "bold"), width=150)
        createIDF(self.currentPath, self.simulationName)
        runOptimization(self.currentPath, self.simulationName, self.simulationStateLabel)
        sys.stdout.close()                                      # I close writing to file
        sys.stdout = stdout_obj                                 # assing it back to starting environment to put things as usual being able to close everything when closing GUI
        self.simulationStateLabel.configure(text="Simulation completed", fg_color="#3B8132", text_color="white", font=("", 13, "bold"), width=150)

class App(customtkinter.CTk):

    frames = {"Main": None, "Building": None, "Results": None}
    
    def initialPage_selector(self):
        App.frames["Building"].pack_forget()
        App.frames["Results"].pack_forget()
        App.frames["Main"].pack(in_=self.right_side_container,side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
    
    def buildingPage_selector(self):
        App.frames["Main"].pack_forget()
        App.frames["Results"].pack_forget()
        App.frames["Building"].pack(in_=self.right_side_container,side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
    
    def ResultsPage_selector(self):
        App.frames["Main"].pack_forget()
        App.frames["Building"].pack_forget()
        App.frames["Results"].pack(in_=self.right_side_container,side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
        simulationStateLabel.configure(text="", fg_color="transparent")
       
    def __init__(self):
        super().__init__()
        global simulationStateLabel
        # self.state('withdraw')
        self.title("Building Performance Simulation - Simplified Configurator")
    
        self.geometry("{0}x{0}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))
    
        # contains everything
        main_container = customtkinter.CTkFrame(self)
        main_container.pack(fill=tkinter.BOTH, expand=True, padx=10, pady=10)
    
        # left side panel -> for frame selection
        self.left_side_panel = customtkinter.CTkFrame(main_container, width=150)
        self.left_side_panel.pack(side=tkinter.LEFT, fill=tkinter.Y, expand=False, padx=10, pady=10)
    
        # buttons to select the frames
        bt_Main = customtkinter.CTkButton(self.left_side_panel, text="Main", command=self.initialPage_selector)
        bt_Main.grid(row=0, column=0, padx=20, pady=10)
    
        bt_Building = customtkinter.CTkButton(self.left_side_panel, text="Building", command=self.buildingPage_selector)
        bt_Building.grid(row=1, column=0, padx=20, pady=10)
        
        bt_Results = customtkinter.CTkButton(self.left_side_panel, text="Results", command=self.ResultsPage_selector)
        bt_Results.grid(row=2, column=0, padx=20, pady=10)
    
        # right side panel -> to show the frame1 or frame 2
        self.right_side_panel = customtkinter.CTkFrame(main_container)
        self.right_side_panel.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True, padx=10, pady=10)
    
        self.right_side_container = customtkinter.CTkFrame(self.right_side_panel)
        self.right_side_container.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
 
#%%     # Functions to make it work

        # Create required folders if not present
        currentPath = os.getcwd()
        simulationsFolderPath = currentPath + "/Simulations"
        if not os.path.exists(simulationsFolderPath):
            os.mkdir(simulationsFolderPath)
        if len(os.listdir(simulationsFolderPath)) == 0:
            availableSimulations = ["No simulations yet"]  
        else:
            availableSimulations = os.listdir(simulationsFolderPath)
        
        def saveInputFiles():
            nonlocal availableSimulations
            simulationName = varSimulationName.get()
            thisSimulationFolderPath = simulationsFolderPath + '/' + simulationName
            if not os.path.exists(thisSimulationFolderPath):
                os.mkdir(thisSimulationFolderPath)
            if gainsMenu.get() != "Other":
                gainsToSave = internalGains[buildingUses.index(variableGains.get())]
            else:
                gainsToSave = gainsSlider.get()            
            buildingDF = pd.DataFrame({"Weather file": [variableepw.get()], "Height": [variableHeight.get()], "Width": [xSlider.get()], "Depth": [ySlider.get()],
                                       "adiabaticS": [adSSlider.get()], "adiabaticN": [adNSlider.get()], "adiabaticE": [adESlider.get()], "adiabaticW": [adWSlider.get()], "adiabaticF": [adFSlider.get()], "adiabaticR": [adRSlider.get()], 
                                       "WWRS": [round(wwrSSlider.get(),2)], "WWRN": [round(wwrNSlider.get(),2)], "WWRE": [round(wwrESlider.get(),2)], "WWRW": [round(wwrWSlider.get(),2)],
                                       "Massive index": [structuralMaterials[structuralMaterials == structuralMaterialsMenu.get()].index[0]], "Massive thickness": [structuralSlider.get()], "Insulation position": [opaquePositionButton.get()], 
                                       "Ins optimization": [insulationMaterialOptimizationButton.get()], "Fixed insulation index": [fixedInsulationMaterialMenu.get()], "Optimized insulation index1": [optimizedInsulationMaterialMenu1.get()], "Optimized insulation index2": [optimizedInsulationMaterialMenu2.get()],
                                       "Ins thick optimization": [insulationThicknessOptimizationButton.get()], "Ins thickness": [fixedInsulationThicknessSlider.get()], "Min ins thickness": [optimizedInsulationThicknessMin.get()], "Max ins thickness": [optimizedInsulationThicknessMax.get()], "Step ins thickness": [optimizedInsulationThicknessStep.get()], "Insulation cost": [economicAnalysisInsulationlMenu.get().split(",")[0]], 
                                       "Glazing optimization": [glazingMaterialOptimizationButton.get()], "Fixed glazing index": [fixedGlazingMaterialMenu.get()], "Optimized glazing index1": [optimizedGlazingMaterialMenu1.get()], "Optimized glazing index2": [optimizedGlazingMaterialMenu2.get()], 
                                       "Glazing cost": [economicAnalysisGlazinglMenu.get().split(",")[0]], "Gains": [gainsToSave], "GainsUse": [variableGains.get()], 
                                       "Met": [rates[activities.index(variableActivities.get())]], "Clo": [clothings[activities.index(variableActivities.get())]], 
                                       "Ventilation": [ventilationSlider.get()], "Internal mass": [int(internalMassSlider.get())],
                                       "Schedule1": [sliders[0].get()], "Schedule2": [sliders[1].get()], "Schedule3": [sliders[2].get()], "Schedule4": [sliders[3].get()], "Schedule5": [sliders[4].get()], "Schedule6": [sliders[5].get()], "Schedule7": [sliders[6].get()], "Schedule8": [sliders[7].get()], 
                                       "Schedule9": [sliders[8].get()], "Schedule10": [sliders[9].get()], "Schedule11": [sliders[10].get()], "Schedule12": [sliders[11].get()], "Schedule13": [sliders[12].get()], "Schedule14": [sliders[13].get()], "Schedule15": [sliders[14].get()], "Schedule16": [sliders[15].get()], 
                                       "Schedule17": [sliders[16].get()], "Schedule18": [sliders[17].get()], "Schedule19": [sliders[18].get()], "Schedule20": [sliders[19].get()], "Schedule21": [sliders[20].get()], "Schedule22": [sliders[21].get()], "Schedule23": [sliders[22].get()], "Schedule24": [sliders[23].get()],
                                       "Electricity price": [electricityPriceElSlider.get()], "Natural gas price": [gasPriceElSlider.get()],
                                       "Heating setpoint": [setpointMenu1.get()], "Cooling setpoint": [setpointMenu2.get()],
                                       "Heating setback": [setbackMenu1.get()], "Cooling setback": [setbackMenu2.get()],
                                       "Heating setback start": [heatingSetbackStartMenu.get()], "Heating setback finish": [heatingSetbackFinishMenu.get()],
                                       "Cooling setback start": [coolingSetbackStartMenu.get()], "Cooling setback finish": [coolingSetbackFinishMenu.get()],
                                       "Heating season start month": [heatingSeasonStartMonthMenu.get()], "Heating season start day": [heatingSeasonStartDayMenu.get()],
                                       "Heating season end month": [heatingSeasonEndMonthMenu.get()], "Heating season end day": [heatingSeasonEndDayMenu.get()],
                                       "Cooling season start month": [coolingSeasonStartMonthMenu.get()], "Cooling season start day": [coolingSeasonStartDayMenu.get()],
                                       "Cooling season end month": [coolingSeasonEndMonthMenu.get()], "Cooling season end day": [coolingSeasonEndDayMenu.get()],
                                       "Shading presence": [shadingButton.get()], "Shading setpoint": [shadingEntry.get()], "Floors number": [floorMenu.get()]})
            buildingDF.to_csv(thisSimulationFolderPath + "/BuildingInputs.csv")
            # add saved simulation name to list for loading
            if availableSimulations[0] == "No simulations yet":
                availableSimulations = [simulationName]
            elif simulationName not in availableSimulations:
                availableSimulations.append(simulationName)
            varLoadSimulationName.set(simulationName)
            varLoadSimulationName.set(simulationName)
            loadSimulationMenu.configure(variable=varLoadSimulationName, values=availableSimulations)
            varLoadSimulationName.set(simulationName)
            simulationStateLabel.configure(text="", fg_color="transparent") # to be sure reset simulation completed label to empty
            
        def loadInputFiles():
            simulationToLoad = loadSimulationMenu.get()
            simulationToLoadPath = simulationsFolderPath + '/' + simulationToLoad
            """ Building """
            buildingInputsDF = pd.read_csv(simulationToLoadPath + '/BuildingInputs.csv', index_col = 0)
            variableepw.set(buildingInputsDF.loc[0,'Weather file']), variableHeight.set(buildingInputsDF.loc[0,'Height'])
            variableFloor.set(buildingInputsDF.loc[0,'Floors number'])
            xSlider.set(buildingInputsDF.loc[0,'Width']), ySlider.set(buildingInputsDF.loc[0,'Depth'])
            xLengthLabel.configure(text="x length [m]: "+ str(buildingInputsDF.loc[0,'Width']))
            yLengthLabel.configure(text="y length [m]: "+ str(buildingInputsDF.loc[0,'Depth']))            
            adSSlider.set(buildingInputsDF.loc[0,'adiabaticS']), adNSlider.set(buildingInputsDF.loc[0,'adiabaticN']), adESlider.set(buildingInputsDF.loc[0,'adiabaticE']), adWSlider.set(buildingInputsDF.loc[0,'adiabaticW']), adFSlider.set(buildingInputsDF.loc[0,'adiabaticF']), adRSlider.set(buildingInputsDF.loc[0,'adiabaticR'])
            adSLabel.configure(text="Ad_s [%]: {:.2f}".format(buildingInputsDF.loc[0,'adiabaticS']))
            adNLabel.configure(text="Ad_n [%]: {:.2f}".format(buildingInputsDF.loc[0,'adiabaticN']))
            adELabel.configure(text="Ad_e [%]: {:.2f}".format(buildingInputsDF.loc[0,'adiabaticE']))
            adWLabel.configure(text="Ad_w [%]: {:.2f}".format(buildingInputsDF.loc[0,'adiabaticW']))
            adFLabel.configure(text="Ad_f [%]: {:.2f}".format(buildingInputsDF.loc[0,'adiabaticF']))
            adRLabel.configure(text="Ad_r [%]: {:.2f}".format(buildingInputsDF.loc[0,'adiabaticR']))
            wwrSSlider.set(buildingInputsDF.loc[0,'WWRS']), wwrNSlider.set(buildingInputsDF.loc[0,'WWRN']), wwrESlider.set(buildingInputsDF.loc[0,'WWRE']), wwrWSlider.set(buildingInputsDF.loc[0,'WWRW'])
            wwrSLabel.configure(text="WWR_s [%]: {:.2f}".format(buildingInputsDF.loc[0,'WWRS']))
            wwrNLabel.configure(text="WWR_n [%]: {:.2f}".format(buildingInputsDF.loc[0,'WWRN']))
            wwrELabel.configure(text="WWR_e [%]: {:.2f}".format(buildingInputsDF.loc[0,'WWRE']))
            wwrWLabel.configure(text="WWR_w [%]: {:.2f}".format(buildingInputsDF.loc[0,'WWRW']))
            variableStructuralMaterial.set(structuralMaterials[buildingInputsDF.loc[0,'Massive index']]), structuralSlider.set(buildingInputsDF.loc[0,'Massive thickness'])
            structuralLabel.configure(text="Layer thickness [cm]: {}".format(int(buildingInputsDF.loc[0,'Massive thickness'])))
            structuralMaterialIndex = buildingInputsDF.loc[0,'Massive index']
            structuralMaterialProperties = "{} thermal properties: \n Density {} kg m\u207b\u00B3   |   Thermal conductivity {} W m\u207b\u00B9 K\u207b\u00B9   |   Specific Heat Capacity {} kJ kg\u207b\u00B9 K\u207b\u00B9".format(selectedStructuralMaterial, structuralMaterialDensities[structuralMaterialIndex], structuralMaterialConductivities[structuralMaterialIndex], structuralMaterialHeats[structuralMaterialIndex])
            chosenStructuralMaterialLabel.configure(text=structuralMaterialProperties)
            opaquePositionButton.set(buildingInputsDF.loc[0,'Insulation position'])
            insulationPosition = buildingInputsDF.loc[0,'Insulation position']
            # activate all buttons and menus to update values, than set to current file
            insulationMaterialOptimizationButton.configure(state="normal")
            fixedInsulationMaterialMenu.configure(state="normal")
            optimizedInsulationMaterialMenu1.configure(state="normal")
            optimizedInsulationMaterialMenu2.configure(state="normal")
            insulationThicknessOptimizationButton.configure(state="normal")
            fixedInsulationThicknessSlider.configure(state="normal")
            optimizedInsulationThicknessMin.configure(state="normal")
            optimizedInsulationThicknessMax.configure(state="normal")
            optimizedInsulationThicknessStep.configure(state="normal")
            # update insulation optimization button
            insulationMaterialOptimizationButton.set(buildingInputsDF.loc[0,'Ins optimization'])
            #update fixed insulation case
            variableFixedInsulation.set(buildingInputsDF.loc[0,'Fixed insulation index'])
            selectedFixedInsulationMaterial = variableFixedInsulation.get()
            fixedInsulationMaterialIndex = insulationMaterials[insulationMaterials == selectedFixedInsulationMaterial].index[0]
            insulationTable.item(item=1, values=(insulationMaterials[fixedInsulationMaterialIndex], insulationMaterialDensities[fixedInsulationMaterialIndex], insulationMaterialConductivities[fixedInsulationMaterialIndex], insulationMaterialHeats[fixedInsulationMaterialIndex], insulationMaterialPrices[fixedInsulationMaterialIndex]))
            fixedInsulationMaterialMenu.set(buildingInputsDF.loc[0,'Fixed insulation index'])
            #update optimized insulation case
            variableOptimizedInsulation1.set(buildingInputsDF.loc[0,'Optimized insulation index1'])
            selectedOptimizedInsulationMaterial1 = variableOptimizedInsulation1.get()
            optimizedInsulationMaterialIndex1 = insulationMaterials[insulationMaterials == selectedOptimizedInsulationMaterial1].index[0]
            insulationTable.item(item=2, values=(insulationMaterials[optimizedInsulationMaterialIndex1], insulationMaterialDensities[optimizedInsulationMaterialIndex1], insulationMaterialConductivities[optimizedInsulationMaterialIndex1], insulationMaterialHeats[optimizedInsulationMaterialIndex1], insulationMaterialPrices[optimizedInsulationMaterialIndex1])) 
            optimizedInsulationMaterialMenu1.set(buildingInputsDF.loc[0,'Optimized insulation index1'])
            
            variableOptimizedInsulation2.set(buildingInputsDF.loc[0,'Optimized insulation index2'])
            selectedOptimizedInsulationMaterial2 = variableOptimizedInsulation2.get()
            optimizedInsulationMaterialIndex2 = insulationMaterials[insulationMaterials == selectedOptimizedInsulationMaterial2].index[0]
            insulationTable.item(item=3, values=(insulationMaterials[optimizedInsulationMaterialIndex2], insulationMaterialDensities[optimizedInsulationMaterialIndex2], insulationMaterialConductivities[optimizedInsulationMaterialIndex2], insulationMaterialHeats[optimizedInsulationMaterialIndex2], insulationMaterialPrices[optimizedInsulationMaterialIndex2])) 
            optimizedInsulationMaterialMenu2.set(buildingInputsDF.loc[0,'Optimized insulation index2'])
            
            # insulation thickness optimization
            insulationThicknessOptimizationButton.set(buildingInputsDF.loc[0,'Ins thick optimization'])
            
            fixedInsulationThickness = buildingInputsDF.loc[0,'Ins thickness']
            fixedInsulationThicknessLabel.configure(text="s₀ [cm]: {}".format(int(fixedInsulationThickness)))
            fixedInsulationThicknessSlider.set(fixedInsulationThickness)
            
            variableOptimizedInsulationThicknessMin.set(buildingInputsDF.loc[0,'Min ins thickness'])
            optimizedInsulationThicknessMin.configure(buildingInputsDF.loc[0,'Min ins thickness'])
            variableOptimizedInsulationThicknessMax.set(buildingInputsDF.loc[0,'Max ins thickness'])
            optimizedInsulationThicknessMax.configure(buildingInputsDF.loc[0,'Max ins thickness'])
            variableOptimizedInsulationThicknessStep.set(buildingInputsDF.loc[0,'Step ins thickness'])
            optimizedInsulationThicknessStep.configure(buildingInputsDF.loc[0,'Step ins thickness'])
            
            if insulationPosition == 'Non insulated':
                insulationMaterialOptimizationButton.configure(state="disabled")
                fixedInsulationMaterialMenu.configure(state="disabled")
                optimizedInsulationMaterialMenu1.configure(state="disabled")
                optimizedInsulationMaterialMenu2.configure(state="disabled")
                insulationTable.tag_configure('fixed', background='white')
                insulationTable.tag_configure('opt', background='white')
                insulationThicknessOptimizationButton.configure(state="disabled")
                fixedInsulationThicknessSlider.configure(state="disabled")
                optimizedInsulationThicknessMin.configure(state="disabled")
                optimizedInsulationThicknessMax.configure(state="disabled")
                optimizedInsulationThicknessStep.configure(state="disabled")
            else:
                insulationMaterialOptimizationButton.configure(state="normal")
                insulationThicknessOptimizationButton.configure(state="normal")
                insulationMaterialOptimization_here = buildingInputsDF.loc[0,'Ins optimization']
                if insulationMaterialOptimization_here == 'Fixed':
                    fixedInsulationMaterialMenu.configure(state="normal")
                    optimizedInsulationMaterialMenu1.configure(state="disabled")
                    optimizedInsulationMaterialMenu2.configure(state="disabled")
                    insulationTable.tag_configure('fixed', background='light grey')
                    insulationTable.tag_configure('opt', background='white')
                else:
                    fixedInsulationMaterialMenu.configure(state="disabled")
                    optimizedInsulationMaterialMenu1.configure(state="normal")
                    optimizedInsulationMaterialMenu2.configure(state="normal")
                    insulationTable.tag_configure('fixed', background='white')
                    insulationTable.tag_configure('opt', background='light grey')
                insulationThicknessOptimization_here = buildingInputsDF.loc[0,'Ins thick optimization']
                if insulationThicknessOptimization_here == 'Fixed':
                    fixedInsulationThicknessSlider.configure(state="normal")
                    optimizedInsulationThicknessMin.configure(state="disabled")
                    optimizedInsulationThicknessMax.configure(state="disabled")
                    optimizedInsulationThicknessStep.configure(state="disabled")
                else:
                    fixedInsulationThicknessSlider.configure(state="disabled")
                    optimizedInsulationThicknessMin.configure(state="normal")
                    optimizedInsulationThicknessMax.configure(state="normal")
                    optimizedInsulationThicknessStep.configure(state="normal")
            ''' Insulation material optimization'''
            insulationMaterialOptimization_here = buildingInputsDF.loc[0,'Ins optimization']
            if insulationMaterialOptimization_here == "Fixed":
                fixedInsulationMaterialMenu.configure(state="normal")
                optimizedInsulationMaterialMenu1.configure(state="disabled")
                optimizedInsulationMaterialMenu2.configure(state="disabled")
                insulationTable.tag_configure('fixed', background='light grey')
                insulationTable.tag_configure('opt', background='white')
            else:
                fixedInsulationMaterialMenu.configure(state="disabled")
                optimizedInsulationMaterialMenu1.configure(state="normal")
                optimizedInsulationMaterialMenu2.configure(state="normal")
                insulationTable.tag_configure('fixed', background='white')
                insulationTable.tag_configure('opt', background='light grey')
            ''' Insulation thickness optimization'''
            insulationThicknessOptimization_here = buildingInputsDF.loc[0,'Ins thick optimization']
            if insulationThicknessOptimization_here == "Fixed":
                fixedInsulationThicknessSlider.configure(state="normal")
                optimizedInsulationThicknessMin.configure(state="disabled")
                optimizedInsulationThicknessMax.configure(state="disabled")
                optimizedInsulationThicknessStep.configure(state="disabled")
            else:
                fixedInsulationThicknessSlider.configure(state="disabled")
                optimizedInsulationThicknessMin.configure(state="normal")
                optimizedInsulationThicknessMax.configure(state="normal")
                optimizedInsulationThicknessStep.configure(state="normal")
            
            variableEconomicAnalysisInsulation.set([s for s in ['No, the insulation is already present', 'Yes, the insulation represents a new intervention'] if buildingInputsDF.loc[0,'Insulation cost'] in s][0])
            economicAnalysisInsulationlMenu.set([s for s in ['No, the insulation is already present', 'Yes, the insulation represents a new intervention'] if buildingInputsDF.loc[0,'Insulation cost'] in s][0])
            ''' Glazing optimizaion '''
            glazingMaterialOptimizationButton.set(buildingInputsDF.loc[0,'Glazing optimization'])
            # activate all menus to update them before disabling some
            fixedGlazingMaterialMenu.configure(state="normal")
            optimizedGlazingMaterialMenu1.configure(state="normal")
            optimizedGlazingMaterialMenu2.configure(state="normal")
            # fixed glazing
            variableFixedGlazing.set(buildingInputsDF.loc[0,'Fixed glazing index'])
            selectedFixedGlazingMaterial = variableFixedGlazing.get()
            fixedGlazingMaterialIndex = glazingMaterials[glazingMaterials == selectedFixedGlazingMaterial].index[0]
            glazingTable.item(item=1, values=(glazingMaterials[fixedGlazingMaterialIndex], glazingMaterialThermalTransmittances[fixedGlazingMaterialIndex], glazingMaterialSolarFactor[fixedGlazingMaterialIndex], glazingMaterialSolarTransmittances[fixedGlazingMaterialIndex], glazingMaterialSolarReflectances [fixedGlazingMaterialIndex], glazingMaterialPrices[fixedGlazingMaterialIndex]))
            fixedGlazingMaterialMenu.set(selectedFixedGlazingMaterial)
            # optimized glazing
            variableOptimizedGlazing1.set(buildingInputsDF.loc[0,'Optimized glazing index1'])
            selectedOptimizedGlazingMaterial1 = variableOptimizedGlazing1.get()
            optimizedGlazingMaterialIndex1 = glazingMaterials[glazingMaterials == selectedOptimizedGlazingMaterial1].index[0]
            glazingTable.item(item=2, values=(glazingMaterials[optimizedGlazingMaterialIndex1], glazingMaterialThermalTransmittances[optimizedGlazingMaterialIndex1], glazingMaterialSolarFactor[optimizedGlazingMaterialIndex1], glazingMaterialSolarTransmittances[optimizedGlazingMaterialIndex1], glazingMaterialSolarReflectances [optimizedGlazingMaterialIndex1], glazingMaterialPrices[optimizedGlazingMaterialIndex1]))    
            optimizedGlazingMaterialMenu1.set(selectedOptimizedGlazingMaterial1)
            
            variableOptimizedGlazing2.set(buildingInputsDF.loc[0,'Optimized glazing index2'])
            selectedOptimizedGlazingMaterial2 = variableOptimizedGlazing2.get()
            optimizedGlazingMaterialIndex2 = glazingMaterials[glazingMaterials == selectedOptimizedGlazingMaterial2].index[0]
            glazingTable.item(item=3, values=(glazingMaterials[optimizedGlazingMaterialIndex2], glazingMaterialThermalTransmittances[optimizedGlazingMaterialIndex2], glazingMaterialSolarFactor[optimizedGlazingMaterialIndex2], glazingMaterialSolarTransmittances[optimizedGlazingMaterialIndex2], glazingMaterialSolarReflectances [optimizedGlazingMaterialIndex2], glazingMaterialPrices[optimizedGlazingMaterialIndex2]))
            optimizedGlazingMaterialMenu2.set(selectedOptimizedGlazingMaterial2)
            
            glazingMaterialOptimization_here = buildingInputsDF.loc[0,'Glazing optimization']
            if glazingMaterialOptimization_here == "Fixed":
                fixedGlazingMaterialMenu.configure(state="normal")
                optimizedGlazingMaterialMenu1.configure(state="disabled")
                optimizedGlazingMaterialMenu2.configure(state="disabled")
                glazingTable.tag_configure('fixed', background='light grey')
                glazingTable.tag_configure('opt', background='white')
            else:
                fixedGlazingMaterialMenu.configure(state="disabled")
                optimizedGlazingMaterialMenu1.configure(state="normal")
                optimizedGlazingMaterialMenu2.configure(state="normal")
                glazingTable.tag_configure('fixed', background='white')
                glazingTable.tag_configure('opt', background='light grey')
                
            variableEconomicAnalysisGlazing.set([s for s in ['No, the glazing is already present', 'Yes, the glazing represents a new intervention'] if buildingInputsDF.loc[0,'Glazing cost'] in s][0])
            economicAnalysisGlazinglMenu.set([s for s in ['No, the glazing is already present', 'Yes, the glazing represents a new intervention'] if buildingInputsDF.loc[0,'Glazing cost'] in s][0])

            # Internal gains
            gainsMenu.set(buildingInputsDF.loc[0,'GainsUse'])
            if buildingInputsDF.loc[0,'GainsUse'] != "Other":
                gainsIndex = buildingUses.index(buildingInputsDF.loc[0,'GainsUse'])
                gainsOut.set(value="G [W m\u207b\u00B2]: {}".format(internalGains[gainsIndex]))
                gainsSlider.configure(state="normal")
                gainsSlider.set(buildingInputsDF.loc[0,'Gains'])
                gainsSlider.configure(state="disabled")
            else:
                gainsSlider.configure(state="normal")
                gainsSlider.set(buildingInputsDF.loc[0,'Gains'])
                gainsOut.set(value="G [W m\u207b\u00B2]: {}".format(gainsSlider.get()))
            
            comfort(buildingInputsDF.loc[0,'Met'])
            
            rateIndex = rates.index(buildingInputsDF.loc[0,'Met'])
            variableActivities.set(activities[rateIndex])
            comfortMenu.set(activities[rateIndex])
            rateOut.set(value=" Metabolic rate [met]: {} ".format(rates[rateIndex]))
            cloOut.set(value="R [clo]: {} ".format(clothings[rateIndex]))
                        
            ventilationLabel.configure(text="Ventilation [ach]: {:.2f}".format(buildingInputsDF.loc[0,'Ventilation']))
            ventilationSlider.set(buildingInputsDF.loc[0,'Ventilation'])

            internalMassSlider.set(buildingInputsDF.loc[0,'Internal mass'])
            internalMassLabel.configure(text="m coefficient: {}".format(buildingInputsDF.loc[0,'Internal mass']))
            
            for i in range(24):
                labels[i].configure(text="{:.2f}".format(buildingInputsDF.loc[0,'Schedule{:d}'.format(i+1)]))
                sliders[i].set(buildingInputsDF.loc[0,'Schedule{:d}'.format(i+1)])
            
            variableSetpoint1.set(buildingInputsDF.loc[0,'Heating setpoint'])
            variableSetpoint2.set(buildingInputsDF.loc[0,'Cooling setpoint'])
            variableSetback1.set(buildingInputsDF.loc[0,'Heating setback'])
            variableSetback2.set(buildingInputsDF.loc[0,'Cooling setback'])
            
            heatingSetbackStartMenu.configure(state="normal")
            heatingSetbackFinishMenu.configure(state="normal")
            heatingSetbackStartMenu.set(buildingInputsDF.loc[0,'Heating setback start'])
            heatingSetbackFinishMenu.set(buildingInputsDF.loc[0,'Heating setback finish'])
            if buildingInputsDF.loc[0,'Heating setback'] == "No":
                heatingSetbackStartMenu.configure(state="disabled")
                heatingSetbackFinishMenu.configure(state="disabled")
            
            coolingSetbackStartMenu.configure(state="normal")
            coolingSetbackFinishMenu.configure(state="normal")
            coolingSetbackStartMenu.set(buildingInputsDF.loc[0,'Cooling setback start'])
            coolingSetbackFinishMenu.set(buildingInputsDF.loc[0,'Cooling setback finish'])
            if buildingInputsDF.loc[0,'Cooling setback'] == "No":
                coolingSetbackStartMenu.configure(state="disabled")
                coolingSetbackFinishMenu.configure(state="disabled")
            
            if buildingInputsDF.loc[0,'Heating season start month'] or buildingInputsDF.loc[0,'Heating season start day'] or buildingInputsDF.loc[0,'Heating season end month'] or buildingInputsDF.loc[0,'Heating season end day'] == "On":
                variableHeatingSeasonStartMonth.set(heatingSeasonStartMonth[0])
                variableHeatingSeasonStartDay.set(heatingSeasonStartDay[0])
                variableHeatingSeasonEndMonth.set(heatingSeasonEndMonth[0])
                variableHeatingSeasonEndDay.set(heatingSeasonEndDay[0])
                
            variableHeatingSeasonStartMonth.set(buildingInputsDF.loc[0,'Heating season start month'])
            heatingSeasonStartMonthMenu.set(buildingInputsDF.loc[0,'Heating season start month'])
            variableHeatingSeasonStartDay.set(buildingInputsDF.loc[0,'Heating season start day'])
            heatingSeasonStartDayMenu.set(buildingInputsDF.loc[0,'Heating season start day'])
            variableHeatingSeasonEndMonth.set(buildingInputsDF.loc[0,'Heating season end month'])
            heatingSeasonEndMonthMenu.set(buildingInputsDF.loc[0,'Heating season end month'])
            variableHeatingSeasonEndDay.set(buildingInputsDF.loc[0,'Heating season end day'])
            heatingSeasonEndDayMenu.set(buildingInputsDF.loc[0,'Heating season end day'])
            
            if buildingInputsDF.loc[0,'Cooling season start month'] or buildingInputsDF.loc[0,'Cooling season start day'] or buildingInputsDF.loc[0,'Cooling season end month'] or buildingInputsDF.loc[0,'Cooling season end day'] == "On":
                variableCoolingSeasonStartMonth.set(coolingSeasonStartMonth[0])
                variableCoolingSeasonStartDay.set(coolingSeasonStartDay[0])
                variableCoolingSeasonEndMonth.set(coolingSeasonEndMonth[0])
                variableCoolingSeasonEndDay.set(coolingSeasonEndDay[0])
                
            variableCoolingSeasonStartMonth.set(buildingInputsDF.loc[0,'Cooling season start month'])
            coolingSeasonStartMonthMenu.set(buildingInputsDF.loc[0,'Cooling season start month'])
            variableCoolingSeasonStartDay.set(buildingInputsDF.loc[0,'Cooling season start day'])
            coolingSeasonStartDayMenu.set(buildingInputsDF.loc[0,'Cooling season start day'])
            variableCoolingSeasonEndMonth.set(buildingInputsDF.loc[0,'Cooling season end month'])
            coolingSeasonEndMonthMenu.set(buildingInputsDF.loc[0,'Cooling season end month'])
            variableCoolingSeasonEndDay.set(buildingInputsDF.loc[0,'Cooling season end day'])
            coolingSeasonEndDayMenu.set(buildingInputsDF.loc[0,'Cooling season end day'])
            
            shadingEntry.configure(state="normal")
            variableShadingEntry.set(buildingInputsDF.loc[0,'Shading setpoint'])
            shadingEntry.configure(buildingInputsDF.loc[0,'Shading setpoint'])
            shadingPresent = buildingInputsDF.loc[0,'Shading presence']
            shadingButton.set(shadingPresent)
            if shadingPresent == "Yes":
                shadingEntry.configure(state="normal")
            else:
                shadingEntry.configure(state="disabled")
            
            electricityPriceElSlider.set(buildingInputsDF.loc[0,'Electricity price'])
            getEnergyPriceEl(buildingInputsDF.loc[0,'Electricity price'])
            gasPriceElSlider.set(buildingInputsDF.loc[0,'Natural gas price'])
            getEnergyPriceGas(buildingInputsDF.loc[0,'Natural gas price'])
            varSimulationName.set(simulationToLoad)
            
            simulationStateLabel.configure(text="", fg_color="transparent")

        def runSimulation():
            runSimulationThread = runSimulationThreading(currentPath, varSimulationName.get(), simulationStateLabel)
            runSimulationThread.start()
      
#%%     ########### Initial page ###########

        App.frames['Main'] = customtkinter.CTkFrame(self.right_side_container, fg_color="transparent")
        App.frames["Main"].grid_columnconfigure(0, weight=1)
        App.frames["Main"].pack(in_=self.right_side_container,side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
    
        # frame for the title
        titleFrame = customtkinter.CTkFrame(App.frames["Main"], fg_color="transparent")
        titleFrame.grid(row=0, column=0, columnspan = 4)
        
        # interreg icon
        projectImage = customtkinter.CTkImage(light_image=Image.open("Images/ProjectIcon.png"),
                                              size=(200,80))
        customtkinter.CTkLabel(titleFrame, image = projectImage, text='').grid(row = 0, column = 0, padx=20, pady=10)
        
        # Title
        label = customtkinter.CTkLabel(titleFrame, text ="A Configurator Prototype for Building Energy Modeling", font=("",20))
        label.grid(row = 0, column = 1, columnspan = 3)
        
        # iNest icon
        iNestImage = customtkinter.CTkImage(light_image=Image.open("Images/iNest.png"),
                                              size=(160,120))
        customtkinter.CTkLabel(titleFrame, image = iNestImage, text='').grid(row = 0, column = 4, padx=10, pady=10)
        
        # unibz icon
        unibzImage = customtkinter.CTkImage(light_image=Image.open("Images/unibz.png"),
                                              size=(120,100))
        customtkinter.CTkLabel(titleFrame, image = unibzImage, text='').grid(row = 0, column = 5, padx=10, pady=10)
        
        # Initial page image
        initialPageImage = customtkinter.CTkImage(light_image=Image.open("Images/InitialPage.png"),
                                              size=(700,300))
        customtkinter.CTkLabel(titleFrame, image = initialPageImage, text='').grid(row = 1, column = 0, columnspan = 6)
        
        # Project input and save
        simulationNameFrame = customtkinter.CTkFrame(App.frames['Main'], fg_color="transparent")
        simulationNameFrame.grid(row=1, column=0, columnspan = 6)
        customtkinter.CTkLabel(simulationNameFrame, text="Simulation name:").grid(row=0, column=0, padx=10, pady=20)
        varSimulationName = customtkinter.StringVar(value = "Simulation1")
        simulationNameEntry = customtkinter.CTkEntry(simulationNameFrame, width = 150, justify='center', textvariable=varSimulationName)
        simulationNameEntry.grid(row=0, column=1, padx=10, pady=20)
        initialPageSave = customtkinter.CTkButton(simulationNameFrame, text="Save", command=saveInputFiles)
        initialPageSave.grid(row = 0, column = 2, padx=10, pady=20)
        
        # Load project
        varLoadSimulationName = customtkinter.StringVar(value = availableSimulations[0])
        customtkinter.CTkLabel(simulationNameFrame, text="Load simulation:", height = 4).grid(row=1, column=0, padx=10)
        loadSimulationMenu = customtkinter.CTkOptionMenu(simulationNameFrame, width=150, anchor='center', variable=varLoadSimulationName, values=availableSimulations)
        loadSimulationMenu.grid(row=1, column=1, padx=10)
        initialPageLoad = customtkinter.CTkButton(simulationNameFrame, text ="Load", command = loadInputFiles)
        initialPageLoad.grid(row = 1, column = 2, padx=10)
        
        # Create buttons to change window
        buttonsFrame = customtkinter.CTkFrame(App.frames['Main'], fg_color="transparent")
        buttonsFrame.grid(row=6, column=0, columnspan = 6)
        buildingButton = customtkinter.CTkButton(buttonsFrame, text ="Building", command = self.buildingPage_selector)
        buildingButton.grid(row = 0, column = 0, padx=10, pady=20)
        
        # Create button to run simulation
        runButton = customtkinter.CTkButton(buttonsFrame, text ="Run simulation", command = runSimulation)
        runButton.grid(row = 0, column = 1, padx=10, pady=20)
        
        # Put empty spacing
        resultsButton = customtkinter.CTkButton(buttonsFrame, text ="Results",command = self.ResultsPage_selector)
        resultsButton.grid(row = 0, column = 2, padx=10, pady=20)
        
        # Simulation label
        simulationStateLabel = customtkinter.CTkLabel(buttonsFrame, text="")
        simulationStateLabel.grid(row = 1, column = 0, columnspan = 3, padx=10)
        
#%%     ########### Building page ###########

        App.frames['Building'] = customtkinter.CTkScrollableFrame(self.right_side_container,fg_color="transparent")
        App.frames["Building"].grid_columnconfigure(0, weight=1)
        
        # Location
        locationFrame =  customtkinter.CTkFrame(App.frames['Building']) 
        locationFrame.grid(row=0, column=0, columnspan = 3)
        
        weatherFilesPath = currentPath + "/Weather files/" # weather files base path
        weatherFiles = [f for f in os.listdir(weatherFilesPath) if os.path.isfile(os.path.join(weatherFilesPath, f))]
        locations = [loc.split(".")[0] for loc in weatherFiles] # locations' names for interface
        
        variableepw = customtkinter.StringVar(value = locations[0])
        locationImage = customtkinter.CTkImage(light_image=Image.open("Images/Location.png"),
                                               size=(30,30))
        customtkinter.CTkLabel(locationFrame, image = locationImage, text='').grid(row = 0, column = 0, pady=10)
        
        epwLabel = customtkinter.CTkLabel(locationFrame, text="Location:")
        epwLabel.grid(row=0, column=1, padx=10, pady=10)
        epwMenu = customtkinter.CTkOptionMenu(locationFrame, width=150, anchor='center', variable=variableepw, values=locations)
        epwMenu.grid(row=0, column=2, padx=10, pady=10)
        
        # Geometry
        geometryFrame =  customtkinter.CTkFrame(App.frames['Building']) 
        geometryFrame.grid(row=1, column=0, columnspan = 8)
        
        geometryLabel = customtkinter.CTkLabel(geometryFrame, text="GEOMETRY DEFINITION", font=("", 20, "bold","underline"))
        geometryLabel.grid(row=0, column=0, columnspan=6, padx=10, pady=10)
        
        heights = ['2.5','3.0','3.5','4.0','4.5','5.0','5.5','6.0','6.5','7.0','7.5','8.0','8.5','9.0']
        variableHeight = customtkinter.StringVar(value = heights[0])
        heightLabel = customtkinter.CTkLabel(geometryFrame, text="Height [m]:")
        heightLabel.grid(row=1, column=0, padx=10, pady=10)
        heightMenu = customtkinter.CTkOptionMenu(geometryFrame, width=50, anchor='center', variable=variableHeight, values=heights)
        heightMenu.grid(row=1, column=1, pady=10)
        
        floors = ['1','2','3','4','5','6']
        variableFloor = customtkinter.StringVar(value = floors[0])
        floorsLabel = customtkinter.CTkLabel(geometryFrame, text="Number of floors:")
        floorsLabel.grid(row=1, column=2, padx=10, pady=10)
        floorMenu = customtkinter.CTkOptionMenu(geometryFrame, width=50, anchor='center', variable=variableFloor, values=floors)
        floorMenu.grid(row=1, column=3, pady=10)
        
        def getX(val):
            xDim = float(round(val,1))
            xLengthLabel.configure(text="x length [m]: "+str(xDim))
            
        xLengthLabel = customtkinter.CTkLabel(geometryFrame, text="x length [m]: 12.0")
        xLengthLabel.grid(row=2, column=0, columnspan=2, sticky='w')
        xSlider = customtkinter.CTkSlider(geometryFrame, from_=4.0, to=20.0, number_of_steps=160, command=getX)
        xSlider.grid(row=2, column=2, columnspan=3)
        
        def getY(val):
            yDim = float(round(val,1))
            yLengthLabel.configure(text="y length [m]: "+str(yDim))
            
        yLengthLabel = customtkinter.CTkLabel(geometryFrame, text="y length [m]: 12.0")
        yLengthLabel.grid(row=3, column=0, columnspan=2, sticky='w')
        ySlider = customtkinter.CTkSlider(geometryFrame, from_=4.0, to=20.0, number_of_steps=160, command=getY)
        ySlider.grid(row=3, column=2, columnspan=3)
        
        # shoebox image
        shoeboxImage = customtkinter.CTkImage(light_image=Image.open("Images/Shoebox.png"),
                                              size=(240,190))
        customtkinter.CTkLabel(geometryFrame, image = shoeboxImage, text='').grid(row = 0, column = 6, columnspan=3, rowspan=4, padx= 10)
        
        def getAdS(val):
            adS = float(round(val,2))
            adSLabel.configure(text="Ad_s [%]: {:.2f}".format(adS))
            
        def getAdN(val):
            adN = float(round(val,2))
            adNLabel.configure(text="Ad_n [%]: {:.2f}".format(adN))
        
        def getAdE(val):
            adE = float(round(val,2))
            adELabel.configure(text="Ad_e [%]: {:.2f}".format(adE))
            
        def getAdW(val):
            adW = float(round(val,2))
            adWLabel.configure(text="Ad_w [%]: {:.2f}".format(adW))
        
        def getAdF(val):
            adF = float(round(val,2))
            adFLabel.configure(text="Ad_f [%]: {:.2f}".format(adF))
            
        def getAdR(val):
            adR = float(round(val,2))
            adRLabel.configure(text="Ad_r [%]: {:.2f}".format(adR))
        
        adRatioLabelFrame =  customtkinter.CTkFrame(App.frames['Building']) 
        adRatioLabelFrame.grid(row=2, column=0, columnspan = 8)
        adRatioLabel = customtkinter.CTkLabel(adRatioLabelFrame, text="Ratios of surfaces in contact with other heated buildings (Ad)", font=("", 14, "bold"))
        adRatioLabel.grid(row=0, column=0, columnspan = 6)
        
        adSLabel = customtkinter.CTkLabel(adRatioLabelFrame, text="Ad_s [%]: 0.50")
        adSLabel.grid(row=1, column=0, sticky='w')
        adSSlider = customtkinter.CTkSlider(adRatioLabelFrame, from_=0.0, to=1.0, number_of_steps=100, command=getAdS,
                                            fg_color="#F7A37A", progress_color="#F7A37A", button_color="silver", button_hover_color="gray")
        adSSlider.grid(row=1, column=1, columnspan=2, padx=10)
        
        adNLabel = customtkinter.CTkLabel(adRatioLabelFrame, text="Ad_n [%]: 0.50")
        adNLabel.grid(row=1, column=3, sticky='w', padx=10)
        adNSlider = customtkinter.CTkSlider(adRatioLabelFrame, from_=0.0, to=1.0, number_of_steps=100, command=getAdN,
                                            fg_color="#F7A37A", progress_color="#F7A37A", button_color="silver", button_hover_color="gray")
        adNSlider.grid(row=1, column=4, columnspan=2)
        
        adELabel = customtkinter.CTkLabel(adRatioLabelFrame, text="Ad_e [%]: 0.50")
        adELabel.grid(row=2, column=0, sticky='w')
        adESlider = customtkinter.CTkSlider(adRatioLabelFrame, from_=0.0, to=1.0, number_of_steps=100, command=getAdE,
                                            fg_color="#F7A37A", progress_color="#F7A37A", button_color="silver", button_hover_color="gray")
        adESlider.grid(row=2, column=1, columnspan=2, padx=10)
        
        adWLabel = customtkinter.CTkLabel(adRatioLabelFrame, text="Ad_w [%]: 0.50")
        adWLabel.grid(row=2, column=3, sticky='w', padx=10)
        adWSlider = customtkinter.CTkSlider(adRatioLabelFrame, from_=0.0, to=1.0, number_of_steps=100, command=getAdW,
                                            fg_color="#F7A37A", progress_color="#F7A37A", button_color="silver", button_hover_color="gray")
        adWSlider.grid(row=2, column=4, columnspan=2)

        adFLabel = customtkinter.CTkLabel(adRatioLabelFrame, text="Ad_f [%]: 0")
        adFLabel.grid(row=3, column=0, sticky='w')
        adFSlider = customtkinter.CTkSlider(adRatioLabelFrame, from_=0.0, to=1.0, number_of_steps=100, command=getAdF,
                                            state="disabled", fg_color="white", progress_color="white", button_color="black", button_hover_color="black")
        adFSlider.grid(row=3, column=1, columnspan=2, padx=10)
        adFSlider.set(0)
        
        adRLabel = customtkinter.CTkLabel(adRatioLabelFrame, text="Ad_r [%]: 0")
        adRLabel.grid(row=3, column=3, sticky='w', padx=10)
        adRSlider = customtkinter.CTkSlider(adRatioLabelFrame, from_=0.0, to=1.0, number_of_steps=100, command=getAdR,
                                            state="disabled", fg_color="white", progress_color="white", button_color="black", button_hover_color="black")
        adRSlider.grid(row=3, column=4, columnspan=2)
        adRSlider.set(0)
        
        def getWWRS(val):
            wwrS = float(round(val,2))
            wwrSLabel.configure(text="WWR_s [%]: {:.2f}".format(wwrS))
        
        def getWWRN(val):
            wwrN = float(round(val,2))
            wwrNLabel.configure(text="WWR_n [%]: {:.2f}".format(wwrN))
        
        def getWWRE(val):
            wwrE = float(round(val,2))
            wwrELabel.configure(text="WWR_e [%]: {:.2f}".format(wwrE))
        
        def getWWRW(val):
            wwrW = float(round(val,2))
            wwrWLabel.configure(text="WWR_w [%]: {:.2f}".format(wwrW))
        
        windowFrame =  customtkinter.CTkFrame(App.frames['Building']) 
        windowFrame.grid(row=3, column=0, columnspan = 8)
        widnowLabel = customtkinter.CTkLabel(windowFrame, text="Window-to-wall ratios (WWR)", font=("", 14, "bold"))
        widnowLabel.grid(row=0, column=0, columnspan = 6)
        
        wwrSLabel = customtkinter.CTkLabel(windowFrame, text="WWR_s [%]: 0.50")
        wwrSLabel.grid(row=1, column=0, sticky='w', padx=10)
        wwrSSlider = customtkinter.CTkSlider(windowFrame, from_=0, to=0.95, number_of_steps=94, command=getWWRS,
                                            fg_color="#689FCF", progress_color="#689FCF", button_color="silver", button_hover_color="gray")
        wwrSSlider.grid(row=1, column=1, columnspan=2)
        
        wwrNLabel = customtkinter.CTkLabel(windowFrame, text="WWR_n [%]: 0.50")
        wwrNLabel.grid(row=1, column=3, sticky='w', padx=10)
        wwrNSlider = customtkinter.CTkSlider(windowFrame, from_=0, to=0.95, number_of_steps=94, command=getWWRN,
                                            fg_color="#689FCF", progress_color="#689FCF", button_color="silver", button_hover_color="gray")
        wwrNSlider.grid(row=1, column=4, columnspan=2)
        
        wwrELabel = customtkinter.CTkLabel(windowFrame, text="WWR_e [%]: 0.50")
        wwrELabel.grid(row=2, column=0, sticky='w', padx=10)
        wwrESlider = customtkinter.CTkSlider(windowFrame, from_=0, to=0.95, number_of_steps=94, command=getWWRE,
                                            fg_color="#689FCF", progress_color="#689FCF", button_color="silver", button_hover_color="gray")
        wwrESlider.grid(row=2, column=1, columnspan=2)
        
        wwrWLabel = customtkinter.CTkLabel(windowFrame, text="WWR_w [%]: 0.50")
        wwrWLabel.grid(row=2, column=3, sticky='w', padx=10)
        wwrWSlider = customtkinter.CTkSlider(windowFrame, from_=0, to=0.95, number_of_steps=94, command=getWWRW,
                                            fg_color="#689FCF", progress_color="#689FCF", button_color="silver", button_hover_color="gray")
        wwrWSlider.grid(row=2, column=4, columnspan=2)
        
        # Envelope
        envelopeFrame =  customtkinter.CTkFrame(App.frames['Building']) 
        envelopeFrame.grid(row=4, column=0, columnspan = 8)
        
        envelopeLabel = customtkinter.CTkLabel(envelopeFrame, text="ENVELOPE CHARACTERIZATION", font=("", 20, "bold","underline"))
        envelopeLabel.grid(row=0, column=0, columnspan=8, padx=10, pady=10)
        
        # shoebox image
        envelopeImage = customtkinter.CTkImage(light_image=Image.open("Images/Envelope.png"),
                                              size=(400,150))
        customtkinter.CTkLabel(envelopeFrame, image = envelopeImage, text='').grid(row = 1, column = 0, columnspan=5, rowspan=4)
        
        # Structural material
        def getStructuralMaterial(choice):
            selectedStructuralMaterial = choice
            structuralMaterialIndex = structuralMaterials[structuralMaterials == selectedStructuralMaterial].index[0]
            structuralMaterialProperties = "{} thermal properties: \n Density {} kg m\u207b\u00B3   |   Thermal conductivity {} W m\u207b\u00B9 K\u207b\u00B9   |   Specific Heat Capacity {} kJ kg\u207b\u00B9 K\u207b\u00B9".format(selectedStructuralMaterial, structuralMaterialDensities[structuralMaterialIndex], structuralMaterialConductivities[structuralMaterialIndex], structuralMaterialHeats[structuralMaterialIndex])
            chosenStructuralMaterialLabel.configure(text=structuralMaterialProperties)
            
        structuralMaterialsDF = pd.read_csv("SimulationFiles/Structural-material.csv")
        structuralMaterials = structuralMaterialsDF.loc[:,"Material"]
        structuralMaterialDensities = structuralMaterialsDF.loc[:,"Density"]
        structuralMaterialConductivities = structuralMaterialsDF.loc[:,"Thermal conductivity"]
        structuralMaterialHeats = structuralMaterialsDF.loc[:,"Specific heat capacity"]
        variableStructuralMaterial = customtkinter.StringVar(value=structuralMaterials[0])
        selectedStructuralMaterial = structuralMaterials[0]
        structuralMaterialIndex = structuralMaterials[structuralMaterials == selectedStructuralMaterial].index[0]
        customtkinter.CTkLabel(envelopeFrame, text="Structural material:").grid(row=1, column=5, padx=10)
        structuralMaterialsMenu = customtkinter.CTkOptionMenu(envelopeFrame, width=100, anchor='center', 
                                                              variable=variableStructuralMaterial, 
                                                              command=getStructuralMaterial, 
                                                              values=structuralMaterials)
        structuralMaterialsMenu.grid(row=1, column=6)
        
        def getStructuralThickness(val):
            structuralThickness = int(val)
            structuralLabel.configure(text="Layer thickness [cm]: {}".format(structuralThickness))
        
        structuralLabel = customtkinter.CTkLabel(envelopeFrame, text="Layer thickness [cm]: 5")
        structuralLabel.grid(row=2, column=5, columnspan=2, sticky="w", padx=15)
        structuralSlider = customtkinter.CTkSlider(envelopeFrame, from_=5, to=50, number_of_steps=45, command=getStructuralThickness,
                                            button_color="silver", button_hover_color="gray")
        structuralSlider.grid(row=3, column=5, columnspan=2)
        structuralSlider.set(5)
        
        def opaqueSolution(value):
            insulationPosition = value
            if insulationPosition == "Non insulated":
                insulationMaterialOptimizationButton.configure(state="disabled")
                fixedInsulationMaterialMenu.configure(state="disabled")
                optimizedInsulationMaterialMenu1.configure(state="disabled")
                optimizedInsulationMaterialMenu2.configure(state="disabled")
                insulationTable.tag_configure('fixed', background='white')
                insulationTable.tag_configure('opt', background='white')
                insulationThicknessOptimizationButton.configure(state="disabled")
                fixedInsulationThicknessSlider.configure(state="disabled")
                optimizedInsulationThicknessMin.configure(state="disabled")
                optimizedInsulationThicknessMax.configure(state="disabled")
                optimizedInsulationThicknessStep.configure(state="disabled")
            else:
                insulationMaterialOptimizationButton.configure(state="normal")
                insulationThicknessOptimizationButton.configure(state="normal")
                insulationMaterialOptimization_here = insulationMaterialOptimizationButton.get()
                if insulationMaterialOptimization_here == "Fixed":
                    fixedInsulationMaterialMenu.configure(state="normal")
                    optimizedInsulationMaterialMenu1.configure(state="disabled")
                    optimizedInsulationMaterialMenu2.configure(state="disabled")
                    insulationTable.tag_configure('fixed', background='light grey')
                    insulationTable.tag_configure('opt', background='white')
                else:
                    fixedInsulationMaterialMenu.configure(state="disabled")
                    optimizedInsulationMaterialMenu1.configure(state="normal")
                    optimizedInsulationMaterialMenu2.configure(state="normal")
                    insulationTable.tag_configure('fixed', background='white')
                    insulationTable.tag_configure('opt', background='light grey')
                insulationThicknessOptimization_here = insulationThicknessOptimizationButton.get()
                if insulationThicknessOptimization_here == "Fixed":
                    fixedInsulationThicknessSlider.configure(state="normal")
                    optimizedInsulationThicknessMin.configure(state="disabled")
                    optimizedInsulationThicknessMax.configure(state="disabled")
                    optimizedInsulationThicknessStep.configure(state="disabled")
                else:
                    fixedInsulationThicknessSlider.configure(state="disabled")
                    optimizedInsulationThicknessMin.configure(state="normal")
                    optimizedInsulationThicknessMax.configure(state="normal")
                    optimizedInsulationThicknessStep.configure(state="normal")
                
        opaquePositionButton = customtkinter.CTkSegmentedButton(envelopeFrame,
                                                                values=["External", "Internal", "Non insulated"],
                                                                command=opaqueSolution)
        opaquePositionButton.grid(row=4, column=5, columnspan=2, padx=10)
        opaquePositionButton.set("External")
        chosenStructuralMaterialLabel = customtkinter.CTkLabel(envelopeFrame, text="Layer thickness [cm]: 5")
        
        structuralMaterialProperties = "{} thermal properties: \n Density {} kg m\u207b\u00B3   |   Thermal conductivity {} W m\u207b\u00B9 K\u207b\u00B9   |   Specific Heat Capacity {} kJ kg\u207b\u00B9 K\u207b\u00B9".format(selectedStructuralMaterial, structuralMaterialDensities[structuralMaterialIndex], structuralMaterialConductivities[structuralMaterialIndex], structuralMaterialHeats[structuralMaterialIndex])
        chosenStructuralMaterialLabel = customtkinter.CTkLabel(envelopeFrame, text=structuralMaterialProperties, font=("", 13, "bold"))
        chosenStructuralMaterialLabel.grid(row=5, column=0, columnspan=8, padx=10, pady=10)
        
        # Insulation
        insulationMaterialFrame =  customtkinter.CTkFrame(App.frames['Building']) 
        insulationMaterialFrame.grid(row=5, column=0, columnspan = 8)
        
        insulationMaterialsDF = pd.read_csv("SimulationFiles/Insulation-material.csv")
        insulationMaterials = insulationMaterialsDF.loc[:,"Material"]
        insulationMaterialDensities = insulationMaterialsDF.loc[:,"Density"]
        insulationMaterialConductivities = insulationMaterialsDF.loc[:,"Thermal conductivity"]
        insulationMaterialHeats = insulationMaterialsDF.loc[:,"Specific heat capacity"]
        insulationMaterialCostBase = insulationMaterialsDF.loc[:,"Cost base"]
        insulationMaterialCostIncrease = insulationMaterialsDF.loc[:,"Cost increase"]
        
        insulationIntroLabel = customtkinter.CTkLabel(insulationMaterialFrame, text="Insulation material fixed or optimized (any solution from insulation 1 to 2 will be tested)?", font=("", 13, "bold"))
        insulationIntroLabel.grid(row=0, column=0, columnspan=8)
        
        def insulationMaterialOptimization(value):
            insulationMaterialOptimization_here = value
            if insulationMaterialOptimization_here == "Fixed":
                fixedInsulationMaterialMenu.configure(state="normal")
                optimizedInsulationMaterialMenu1.configure(state="disabled")
                optimizedInsulationMaterialMenu2.configure(state="disabled")
                insulationTable.tag_configure('fixed', background='light grey')
                insulationTable.tag_configure('opt', background='white')
            else:
                fixedInsulationMaterialMenu.configure(state="disabled")
                optimizedInsulationMaterialMenu1.configure(state="normal")
                optimizedInsulationMaterialMenu2.configure(state="normal")
                insulationTable.tag_configure('fixed', background='white')
                insulationTable.tag_configure('opt', background='light grey')
        
        insulationMaterialOptimizationButton = customtkinter.CTkSegmentedButton(insulationMaterialFrame,
                                                                                values=["Fixed", "Optimized"],
                                                                                command=insulationMaterialOptimization)
        insulationMaterialOptimizationButton.grid(row=1, column=0, columnspan=2, rowspan=2, padx=10)
        insulationMaterialOptimizationButton.set("Fixed")
        
        def fixedInsulationMaterial(choice):
            selectedFixedInsulationMaterial = variableFixedInsulation.get()
            fixedInsulationMaterialIndex = insulationMaterials[insulationMaterials == selectedFixedInsulationMaterial].index[0]
            insulationTable.item(item=1, values=(insulationMaterials[fixedInsulationMaterialIndex], insulationMaterialDensities[fixedInsulationMaterialIndex], insulationMaterialConductivities[fixedInsulationMaterialIndex], insulationMaterialHeats[fixedInsulationMaterialIndex], insulationMaterialPrices[fixedInsulationMaterialIndex]))
            
        variableFixedInsulation = customtkinter.StringVar(value = insulationMaterials[0])
        selectedFixedInsulationMaterial = variableFixedInsulation.get()
        fixedInsulationMaterialIndex = insulationMaterials[insulationMaterials == selectedFixedInsulationMaterial].index[0]
        fixedInsulationMaterialLabel = customtkinter.CTkLabel(insulationMaterialFrame, text="ins₀:")
        fixedInsulationMaterialLabel.grid(row=1, column=2, rowspan=2, pady=10)
        fixedInsulationMaterialMenu = customtkinter.CTkOptionMenu(insulationMaterialFrame, width=150, anchor='center', variable=variableFixedInsulation, command=fixedInsulationMaterial, values=insulationMaterials)
        fixedInsulationMaterialMenu.grid(row=1, column=3, rowspan=2, padx=10, pady=10)
        
        def optimizedInsulationMaterial1(choice):
            selectedOptimizedInsulationMaterial1 = variableOptimizedInsulation1.get()
            optimizedInsulationMaterialIndex1 = insulationMaterials[insulationMaterials == selectedOptimizedInsulationMaterial1].index[0]
            insulationTable.item(item=2, values=(insulationMaterials[optimizedInsulationMaterialIndex1], insulationMaterialDensities[optimizedInsulationMaterialIndex1], insulationMaterialConductivities[optimizedInsulationMaterialIndex1], insulationMaterialHeats[optimizedInsulationMaterialIndex1], insulationMaterialPrices[optimizedInsulationMaterialIndex1])) 
                        
        variableOptimizedInsulation1 = customtkinter.StringVar(value = insulationMaterials[1])
        selectedOptimizedInsulationMaterial1 = variableOptimizedInsulation1.get()
        optimizedInsulationMaterialIndex1 = insulationMaterials[insulationMaterials == selectedOptimizedInsulationMaterial1].index[0]
        optimizedInsulationMaterialLabel1 = customtkinter.CTkLabel(insulationMaterialFrame, text="ins₁:")
        optimizedInsulationMaterialLabel1.grid(row=1, column=4, pady=10)
        optimizedInsulationMaterialMenu1 = customtkinter.CTkOptionMenu(insulationMaterialFrame, width=150, anchor='center', variable=variableOptimizedInsulation1, command=optimizedInsulationMaterial1, values=insulationMaterials, state="disabled")
        optimizedInsulationMaterialMenu1.grid(row=1, column=5, padx=10, pady=10)
        
        def optimizedInsulationMaterial2(choice):
            selectedOptimizedInsulationMaterial2 = variableOptimizedInsulation2.get()
            optimizedInsulationMaterialIndex2 = insulationMaterials[insulationMaterials == selectedOptimizedInsulationMaterial2].index[0]
            insulationTable.item(item=3, values=(insulationMaterials[optimizedInsulationMaterialIndex2], insulationMaterialDensities[optimizedInsulationMaterialIndex2], insulationMaterialConductivities[optimizedInsulationMaterialIndex2], insulationMaterialHeats[optimizedInsulationMaterialIndex2], insulationMaterialPrices[optimizedInsulationMaterialIndex2])) 
            
        variableOptimizedInsulation2 = customtkinter.StringVar(value = insulationMaterials[2])
        selectedOptimizedInsulationMaterial2 = variableOptimizedInsulation2.get()
        optimizedInsulationMaterialIndex2 = insulationMaterials[insulationMaterials == selectedOptimizedInsulationMaterial2].index[0]
        optimizedInsulationMaterialLabel2 = customtkinter.CTkLabel(insulationMaterialFrame, text="ins₂:")
        optimizedInsulationMaterialLabel2.grid(row=2, column=4, pady=10)
        optimizedInsulationMaterialMenu2 = customtkinter.CTkOptionMenu(insulationMaterialFrame, width=150, anchor='center', variable=variableOptimizedInsulation2, command=optimizedInsulationMaterial2, values=insulationMaterials, state="disabled")
        optimizedInsulationMaterialMenu2.grid(row=2, column=5, padx=10, pady=10)
        
        dummyForPrices = pd.Series(' + s·', index=range(len(insulationMaterialCostBase)))
        insulationMaterialPrices = insulationMaterialCostBase.astype(str).str.cat(dummyForPrices, sep='')
        insulationMaterialPrices = insulationMaterialPrices.astype(str).str.cat(insulationMaterialCostIncrease.astype(str), sep='')
        
        insulationTable = ttk.Treeview(insulationMaterialFrame, height=4)
        insulationTable['columns'] = ('Name', 'Density', 'Thermal Conductivity', 'Specific Heat Capacity', 'Price')
        insulationTable.column("#0", width=0,  stretch='no')
        insulationTable.column("Name", anchor='center', width=180)
        insulationTable.column("Density", anchor='center', width=120)
        insulationTable.column("Thermal Conductivity", anchor='center', width=180)
        insulationTable.column("Specific Heat Capacity", anchor='center', width=180)
        insulationTable.column("Price", anchor='center', width=120)
        insulationTable.heading('#0', text='', anchor='center')
        insulationTable.heading('Name', text='', anchor='center')
        insulationTable.heading('Density', text='Density', anchor='center')
        insulationTable.heading('Thermal Conductivity', text='Thermal Conductivity', anchor='center')
        insulationTable.heading('Specific Heat Capacity', text='Specific Heat Capacity', anchor='center')
        insulationTable.heading('Price', text='Price', anchor='center')
        insulationTable.insert(parent='', index=0, iid=0, text='', values=('', 'ρ [kg m\u207b\u00B3]','λ [W m\u207b\u00B9 K\u207b\u00B9]', 'c [kJ kg\u207b\u00B9 K\u207b\u00B9]', 'P [€ m\u207b\u00B2]'))
        insulationTable.insert(parent='', index=1, iid=1, text='', values=(insulationMaterials[fixedInsulationMaterialIndex], insulationMaterialDensities[fixedInsulationMaterialIndex], insulationMaterialConductivities[fixedInsulationMaterialIndex], insulationMaterialHeats[fixedInsulationMaterialIndex], insulationMaterialPrices[fixedInsulationMaterialIndex]), tags=('fixed'))
        insulationTable.insert(parent='', index=2, iid=2, text='', values=(insulationMaterials[optimizedInsulationMaterialIndex1], insulationMaterialDensities[optimizedInsulationMaterialIndex1], insulationMaterialConductivities[optimizedInsulationMaterialIndex1], insulationMaterialHeats[optimizedInsulationMaterialIndex1], insulationMaterialPrices[optimizedInsulationMaterialIndex1]), tags=('opt'))
        insulationTable.insert(parent='', index=3, iid=3, text='', values=(insulationMaterials[optimizedInsulationMaterialIndex2], insulationMaterialDensities[optimizedInsulationMaterialIndex2], insulationMaterialConductivities[optimizedInsulationMaterialIndex2], insulationMaterialHeats[optimizedInsulationMaterialIndex2], insulationMaterialPrices[optimizedInsulationMaterialIndex2]), tags=('opt'))
        insulationTable.grid(row=3, column=0, columnspan=8, rowspan = 4)
        insulationTable.tag_configure('fixed', background='light grey')
        
        insulationThicknessFrame =  customtkinter.CTkFrame(App.frames['Building']) 
        insulationThicknessFrame.grid(row=6, column=0, columnspan = 8)
        
        insulationIntroLabel = customtkinter.CTkLabel(insulationThicknessFrame, text="Insulation thickness fixed or optimized?")
        insulationIntroLabel.grid(row=0, column=0, columnspan=8, pady=10)
        
        def insulationThicknessOptimization(value):
            insulationThicknessOptimization_here = value
            if insulationThicknessOptimization_here == "Fixed":
                fixedInsulationThicknessSlider.configure(state="normal")
                optimizedInsulationThicknessMin.configure(state="disabled")
                optimizedInsulationThicknessMax.configure(state="disabled")
                optimizedInsulationThicknessStep.configure(state="disabled")
            else:
                fixedInsulationThicknessSlider.configure(state="disabled")
                optimizedInsulationThicknessMin.configure(state="normal")
                optimizedInsulationThicknessMax.configure(state="normal")
                optimizedInsulationThicknessStep.configure(state="normal")
        
        insulationThicknessOptimizationButton = customtkinter.CTkSegmentedButton(insulationThicknessFrame,
                                                                                values=["Fixed", "Optimized"],
                                                                                command=insulationThicknessOptimization)
        insulationThicknessOptimizationButton.grid(row=1, column=0, columnspan=8)
        insulationThicknessOptimizationButton.set("Fixed")
        
        def getFixedInsulationThickness(val):
            fixedInsulationThickness = int(val)
            fixedInsulationThicknessLabel.configure(text="s₀ [cm]: {}".format(fixedInsulationThickness))
            
        fixedInsulationThicknessLabel = customtkinter.CTkLabel(insulationThicknessFrame, text="s₀ [cm]: 5", width=60)
        fixedInsulationThicknessLabel.grid(row=2, column=0, columnspan=2, sticky='e', pady=10)
        fixedInsulationThicknessSlider = customtkinter.CTkSlider(insulationThicknessFrame, from_=0, to=40, number_of_steps=40, command=getFixedInsulationThickness)
        fixedInsulationThicknessSlider.grid(row=2, column=2, columnspan=4, pady=10)
        fixedInsulationThicknessSlider.set(5)
        
        optimizedInsulationThicknessMinLabel = customtkinter.CTkLabel(insulationThicknessFrame, text="s\u2098\u1d62\u2099  [cm]:")
        optimizedInsulationThicknessMinLabel.grid(row=3, column=0, sticky='w')
        variableOptimizedInsulationThicknessMin = customtkinter.StringVar(value = "2")
        optimizedInsulationThicknessMin = customtkinter.CTkEntry(insulationThicknessFrame, textvariable=variableOptimizedInsulationThicknessMin, width=40, state="disabled")
        optimizedInsulationThicknessMin.grid(row=3, column=1, padx= 10)
        
        optimizedInsulationThicknessMaxLabel = customtkinter.CTkLabel(insulationThicknessFrame, text="s\u2098\u2090\u2093  [cm]:")
        optimizedInsulationThicknessMaxLabel.grid(row=3, column=2, sticky='w')
        variableOptimizedInsulationThicknessMax = customtkinter.StringVar(value = "10")
        optimizedInsulationThicknessMax = customtkinter.CTkEntry(insulationThicknessFrame, textvariable=variableOptimizedInsulationThicknessMax, width=40, state="disabled")
        optimizedInsulationThicknessMax.grid(row=3, column=3, padx= 10)
        
        optimizedInsulationThicknessStepLabel = customtkinter.CTkLabel(insulationThicknessFrame, text="s\u209b\u209c\u2091\u209a  [cm]:")
        optimizedInsulationThicknessStepLabel.grid(row=3, column=4, sticky='w')
        variableOptimizedInsulationThicknessStep = customtkinter.StringVar(value = "1")
        optimizedInsulationThicknessStep = customtkinter.CTkEntry(insulationThicknessFrame, textvariable=variableOptimizedInsulationThicknessStep, width=40, state="disabled")
        optimizedInsulationThicknessStep.grid(row=3, column=5, padx= 10)
        
        economicAnalysisInsulationOptions = ['No, the insulation is already present', 'Yes, the insulation represents a new intervention']
        variableEconomicAnalysisInsulation = customtkinter.StringVar(value = economicAnalysisInsulationOptions[0])
        economicAnalysisInsulationLabel = customtkinter.CTkLabel(insulationThicknessFrame, text="Is the insulation to be accounted in the investments costs?")
        economicAnalysisInsulationLabel.grid(row=4, column=0, columnspan=8, pady= 10)
        economicAnalysisInsulationlMenu = customtkinter.CTkOptionMenu(insulationThicknessFrame, width=150, anchor='center', variable=variableEconomicAnalysisInsulation, values=economicAnalysisInsulationOptions)
        economicAnalysisInsulationlMenu.grid(row=5, column=0, columnspan=8)
        
        # Glazing
        glazingMaterialFrame =  customtkinter.CTkFrame(App.frames['Building']) 
        glazingMaterialFrame.grid(row=7, column=0, columnspan = 8)
        
        glazingMaterialsDF = pd.read_csv("SimulationFiles/Glazing-material.csv")
        glazingMaterials = glazingMaterialsDF.loc[:,"Material"]
        glazingMaterialThermalTransmittances = glazingMaterialsDF.loc[:,"Thermal transmittance"]
        glazingMaterialSolarFactor = glazingMaterialsDF.loc[:,"Solar factor"]
        glazingMaterialSolarTransmittances = glazingMaterialsDF.loc[:,"Solar transmittance"]
        glazingMaterialSolarReflectances = glazingMaterialsDF.loc[:,"Solar reflectance"]
        glazingMaterialPrices = glazingMaterialsDF.loc[:,"Price"]
        
        glazingIntroLabel = customtkinter.CTkLabel(glazingMaterialFrame, text="Glazing material fixed or optimized (any solution from glazing 1 to 2 will be tested)?", font=("", 13, "bold"))
        glazingIntroLabel.grid(row=0, column=0, columnspan=8, pady=10)
        
        def glazingMaterialOptimization(value):
            glazingMaterialOptimization_here = value
            if glazingMaterialOptimization_here == "Fixed":
                fixedGlazingMaterialMenu.configure(state="normal")
                optimizedGlazingMaterialMenu1.configure(state="disabled")
                optimizedGlazingMaterialMenu2.configure(state="disabled")
                glazingTable.tag_configure('fixed', background='light grey')
                glazingTable.tag_configure('opt', background='white')
            else:
                fixedGlazingMaterialMenu.configure(state="disabled")
                optimizedGlazingMaterialMenu1.configure(state="normal")
                optimizedGlazingMaterialMenu2.configure(state="normal")
                glazingTable.tag_configure('fixed', background='white')
                glazingTable.tag_configure('opt', background='light grey')
        
        glazingMaterialOptimizationButton = customtkinter.CTkSegmentedButton(glazingMaterialFrame,
                                                                                values=["Fixed", "Optimized"],
                                                                                command=glazingMaterialOptimization)
        glazingMaterialOptimizationButton.grid(row=1, column=0, columnspan=2, rowspan=2, padx=10)
        glazingMaterialOptimizationButton.set("Fixed")
        
        def fixedGlazingMaterial(choice):
            selectedFixedGlazingMaterial = variableFixedGlazing.get()
            fixedGlazingMaterialIndex = glazingMaterials[glazingMaterials == selectedFixedGlazingMaterial].index[0]
            glazingTable.item(item=1, values=(glazingMaterials[fixedGlazingMaterialIndex], glazingMaterialThermalTransmittances[fixedGlazingMaterialIndex], glazingMaterialSolarFactor[fixedGlazingMaterialIndex], glazingMaterialSolarTransmittances[fixedGlazingMaterialIndex], glazingMaterialSolarReflectances [fixedGlazingMaterialIndex], glazingMaterialPrices[fixedGlazingMaterialIndex]))
            
        variableFixedGlazing = customtkinter.StringVar(value = glazingMaterials[0])
        selectedFixedGlazingMaterial = variableFixedGlazing.get()
        fixedGlazingMaterialIndex = glazingMaterials[glazingMaterials == selectedFixedGlazingMaterial].index[0]
        fixedGlazingMaterialLabel = customtkinter.CTkLabel(glazingMaterialFrame, text="GLZ₀:")
        fixedGlazingMaterialLabel.grid(row=1, column=2, rowspan=2, pady=10)
        fixedGlazingMaterialMenu = customtkinter.CTkOptionMenu(glazingMaterialFrame, width=150, anchor='center', variable=variableFixedGlazing, command=fixedGlazingMaterial, values=glazingMaterials)
        fixedGlazingMaterialMenu.grid(row=1, column=3, rowspan=2, padx=10, pady=10)
        
        def optimizedGlazingMaterial1(choice):
            selectedOptimizedGlazingMaterial1 = variableOptimizedGlazing1.get()
            optimizedGlazingMaterialIndex1 = glazingMaterials[glazingMaterials == selectedOptimizedGlazingMaterial1].index[0]
            glazingTable.item(item=2, values=(glazingMaterials[optimizedGlazingMaterialIndex1], glazingMaterialThermalTransmittances[optimizedGlazingMaterialIndex1], glazingMaterialSolarFactor[optimizedGlazingMaterialIndex1], glazingMaterialSolarTransmittances[optimizedGlazingMaterialIndex1], glazingMaterialSolarReflectances [optimizedGlazingMaterialIndex1], glazingMaterialPrices[optimizedGlazingMaterialIndex1]))    
            
        variableOptimizedGlazing1 = customtkinter.StringVar(value = glazingMaterials[1])
        selectedOptimizedGlazingMaterial1 = variableOptimizedGlazing1.get()
        optimizedGlazingMaterialIndex1 = glazingMaterials[glazingMaterials == selectedOptimizedGlazingMaterial1].index[0]
        optimizedGlazingMaterialLabel1 = customtkinter.CTkLabel(glazingMaterialFrame, text="GLZ₁:")
        optimizedGlazingMaterialLabel1.grid(row=1, column=4, pady=10)
        optimizedGlazingMaterialMenu1 = customtkinter.CTkOptionMenu(glazingMaterialFrame, width=150, anchor='center', variable=variableOptimizedGlazing1, command=optimizedGlazingMaterial1, values=glazingMaterials, state="disabled")
        optimizedGlazingMaterialMenu1.grid(row=1, column=5, padx=10, pady=10)
        
        def optimizedGlazingMaterial2(choice):
            selectedOptimizedGlazingMaterial2 = variableOptimizedGlazing2.get()
            optimizedGlazingMaterialIndex2 = glazingMaterials[glazingMaterials == selectedOptimizedGlazingMaterial2].index[0]
            glazingTable.item(item=3, values=(glazingMaterials[optimizedGlazingMaterialIndex2], glazingMaterialThermalTransmittances[optimizedGlazingMaterialIndex2], glazingMaterialSolarFactor[optimizedGlazingMaterialIndex2], glazingMaterialSolarTransmittances[optimizedGlazingMaterialIndex2], glazingMaterialSolarReflectances [optimizedGlazingMaterialIndex2], glazingMaterialPrices[optimizedGlazingMaterialIndex2]))
            
        variableOptimizedGlazing2 = customtkinter.StringVar(value = glazingMaterials[2])
        selectedOptimizedGlazingMaterial2 = variableOptimizedGlazing2.get()
        optimizedGlazingMaterialIndex2 = glazingMaterials[glazingMaterials == selectedOptimizedGlazingMaterial2].index[0]
        optimizedGlazingMaterialLabel2 = customtkinter.CTkLabel(glazingMaterialFrame, text="GLZ₂:")
        optimizedGlazingMaterialLabel2.grid(row=2, column=4, pady=10)
        optimizedGlazingMaterialMenu2 = customtkinter.CTkOptionMenu(glazingMaterialFrame, width=150, anchor='center', variable=variableOptimizedGlazing2, command=optimizedGlazingMaterial2, values=glazingMaterials, state="disabled")
        optimizedGlazingMaterialMenu2.grid(row=2, column=5, padx=10, pady=10)
        
        
        glazingTable = ttk.Treeview(glazingMaterialFrame, height=4)
        glazingTable['columns'] = ('Name', 'Thermal Transmittance', 'Solar Factor', 'Solar Transmittance', 'Solar Reflectance', 'Price')
        glazingTable.column("#0", width=0,  stretch='no')
        glazingTable.column("Name", anchor='center', width=180)
        glazingTable.column("Thermal Transmittance", anchor='center', width=180)
        glazingTable.column("Solar Factor", anchor='center', width=100)
        glazingTable.column("Solar Transmittance", anchor='center', width=150)
        glazingTable.column("Solar Reflectance", anchor='center', width=140)
        glazingTable.column("Price", anchor='center', width=80)
        glazingTable.heading('#0', text='', anchor='center')
        glazingTable.heading('Name', text='', anchor='center')
        glazingTable.heading('Thermal Transmittance', text='Thermal Transmittance', anchor='center')
        glazingTable.heading('Solar Factor', text='Solar Factor', anchor='center')
        glazingTable.heading('Solar Transmittance', text='Solar Transmittance', anchor='center')
        glazingTable.heading('Solar Reflectance', text='Solar Reflectance', anchor='center')
        glazingTable.heading('Price', text='Price', anchor='center')
        glazingTable.insert(parent='', index=0, iid=0, text='', values=('', 'U [W m\u207b\u00B9 K\u207b\u00B9]', 'G[-]', 'τ_sol [-]', 'ρ_sol [-]', 'P [€ m\u207b\u00B2]'))
        glazingTable.insert(parent='', index=1, iid=1, text='', values=(glazingMaterials[fixedGlazingMaterialIndex], glazingMaterialThermalTransmittances[fixedGlazingMaterialIndex], glazingMaterialSolarFactor[fixedGlazingMaterialIndex], glazingMaterialSolarTransmittances[fixedGlazingMaterialIndex], glazingMaterialSolarReflectances [fixedGlazingMaterialIndex], glazingMaterialPrices[fixedGlazingMaterialIndex]), tags=('fixed'))
        glazingTable.insert(parent='', index=2, iid=2, text='', values=(glazingMaterials[optimizedGlazingMaterialIndex1], glazingMaterialThermalTransmittances[optimizedGlazingMaterialIndex1], glazingMaterialSolarFactor[optimizedGlazingMaterialIndex1], glazingMaterialSolarTransmittances[optimizedGlazingMaterialIndex1], glazingMaterialSolarReflectances[optimizedGlazingMaterialIndex1], glazingMaterialPrices[optimizedGlazingMaterialIndex1]), tags=('opt'))
        glazingTable.insert(parent='', index=3, iid=3, text='', values=(glazingMaterials[optimizedGlazingMaterialIndex2], glazingMaterialThermalTransmittances[optimizedGlazingMaterialIndex2], glazingMaterialSolarFactor[optimizedGlazingMaterialIndex2], glazingMaterialSolarTransmittances[optimizedGlazingMaterialIndex2], glazingMaterialSolarReflectances [optimizedGlazingMaterialIndex2], glazingMaterialPrices[optimizedGlazingMaterialIndex2]), tags=('opt'))
        glazingTable.grid(row=3, column=0, columnspan=8, rowspan = 4)
        glazingTable.tag_configure('fixed', background='light grey')
        
        glazingEconomicAnalysFrame =  customtkinter.CTkFrame(App.frames['Building']) 
        glazingEconomicAnalysFrame.grid(row=8, column=0, columnspan = 8)
        
        economicAnalysisGlazingOptions = ['No, the glazing is already present', 'Yes, the glazing represents a new intervention']
        variableEconomicAnalysisGlazing = customtkinter.StringVar(value = economicAnalysisGlazingOptions[0])
        economicAnalysisGlazingLabel = customtkinter.CTkLabel(glazingEconomicAnalysFrame, text="Is the glazing to be accounted in the investments costs?")
        economicAnalysisGlazingLabel.grid(row=1, column=0, columnspan=8, pady= 10)
        economicAnalysisGlazinglMenu = customtkinter.CTkOptionMenu(glazingEconomicAnalysFrame, width=150, anchor='center', variable=variableEconomicAnalysisGlazing, values=economicAnalysisGlazingOptions)
        economicAnalysisGlazinglMenu.grid(row=2, column=0, columnspan=8)
        
        # other inputs
        otherInputsFrame =  customtkinter.CTkFrame(App.frames['Building']) 
        otherInputsFrame.grid(row=9, column=0, columnspan = 8)
        
        # Internal gains
        def getInternalGains(choice):
            selectedGains = variableGains.get()
            if selectedGains != "Other":
                gainsIndex = buildingUses.index(selectedGains)
                gainsOut.set(value="G [W m\u207b\u00B2]: {}".format(internalGains[gainsIndex]))
                gainsSlider.configure(state="normal")
                gainsSlider.set(internalGains[gainsIndex])
                gainsSlider.configure(state="disabled")
            else:
                gainsSlider.configure(state="normal")
                gainsOut.set(value="G [W m\u207b\u00B2]: {}".format(gainsSlider.get()))
                
        internalGainsLabel = customtkinter.CTkLabel(otherInputsFrame, text="Internal gains", font=("", 13, "bold"))
        internalGainsLabel.grid(row=0, column=0, columnspan=8, pady=10)
        buildingUses = ["Residential", "Office", "Commercial", "School", "Hospital", "Hotels", "Other"]
        internalGains = [6.0, 8.0, 8.0, 6.0, 9.0, 7.0, ""]
        gainsIndex = 0
        variableGains = customtkinter.StringVar(value = buildingUses[gainsIndex])
        gainsLabel = customtkinter.CTkLabel(otherInputsFrame, text="Building intended use: ")
        gainsLabel.grid(row=1, column=0)
        gainsMenu = customtkinter.CTkOptionMenu(otherInputsFrame, width=120, anchor='center', variable=variableGains, command=getInternalGains, values=buildingUses)
        gainsMenu.grid(row=1, column=1, padx=10)
        gainsOut = customtkinter.StringVar(value = "G [W m\u207b\u00B2]: {}".format(internalGains[gainsIndex]))
        internalGain = customtkinter.CTkLabel(otherInputsFrame, textvariable=gainsOut, width=100)  
        internalGain.grid(row=1, column=2)
        gainsSlider = customtkinter.CTkSlider(otherInputsFrame, from_=0, to=20, number_of_steps=40, command=getInternalGains)
        gainsSlider.grid(row=1, column=3, columnspan=2, padx=10)
        gainsSlider.set(4)
        gainsSlider.configure(state="disabled")
        
        # other inputs
        otherInputsFrame0 =  customtkinter.CTkFrame(App.frames['Building']) 
        otherInputsFrame0.grid(row=11, column=0, columnspan = 8)
        
        # Comfort 
        def comfort(choice):
            selectedComfort = variableActivities.get()
            rateIndex = activities.index(selectedComfort)
            rateOut.set(value=" Metabolic rate [met]: {} ".format(rates[rateIndex]))
            cloOut.set(value="R [clo]: {} ".format(clothings[rateIndex]))
        
        comfortLabel = customtkinter.CTkLabel(otherInputsFrame0, text="Activity definition (comfort)", font=("", 13, "bold"))
        comfortLabel.grid(row=2, column=0, columnspan=8, pady=10)
        activities = ["Standing-moderate wok", "Standing-light work", "Seated-light work", "Seated-relax"]
        rates = [2.0, 1.6, 1.2, 1.0]
        clothings = ['1.0', '1.0', '1.0', '1.0']
        rateIndex = 0
        variableActivities = customtkinter.StringVar(value = activities[rateIndex])
        rateLabel = customtkinter.CTkLabel(otherInputsFrame0, text="Activity level: ")
        rateLabel.grid(row=3, column=0)
        comfortMenu = customtkinter.CTkOptionMenu(otherInputsFrame0, width=200, anchor='center', variable=variableActivities, command=comfort, values=activities)
        comfortMenu.grid(row=3, column=1)
        # Change clo and met according to choice
        rateOut = customtkinter.StringVar(value=" Metabolic rate [met]: {} ".format(rates[rateIndex]))
        rate = customtkinter.CTkLabel(otherInputsFrame0, textvariable=rateOut)  
        rate.grid(row=3, column=2, padx=10) 
        cloOut = customtkinter.StringVar(value="R [clo]: {} ".format(clothings[rateIndex]))
        clo = customtkinter.CTkLabel(otherInputsFrame0, textvariable=cloOut, padx=20)  
        clo.grid(row=3, column=3) 
        
        # new frame to center better next items
        otherInputsFrame1 =  customtkinter.CTkFrame(App.frames['Building']) 
        otherInputsFrame1.grid(row=13, column=0, columnspan = 8)
        # Ventilation
        def getVentilation(val):
            ach = float(round(val,2))
            ventilationLabel.configure(text="Ventilation [ach]: {:.2f}".format(ach))
            
        ventilationTitleLabel = customtkinter.CTkLabel(otherInputsFrame1, text="Ventilation", font=("", 13, "bold"))
        ventilationTitleLabel.grid(row=0, column=0, columnspan=8, pady=10)
        ach = 0.15
        ventilationLabel = customtkinter.CTkLabel(otherInputsFrame1, text="Ventilation [ach]: {:.2f}".format(ach))
        ventilationLabel.grid(row=1, column=0)
        ventilationSlider = customtkinter.CTkSlider(otherInputsFrame1, from_=0.0, to=1.5, number_of_steps=30, command=getVentilation)
        ventilationSlider.grid(row=1, column=1, columnspan=2)
        ventilationSlider.set(0.15)
        
        # Internal mass
        def getInternalMass(val):
            internalMass = int(val)
            internalMassLabel.configure(text="m coefficient: {}".format(internalMass))
            
        internalMassTitleLabel = customtkinter.CTkLabel(otherInputsFrame1, text="Internal mass", font=("", 13, "bold"))
        internalMassTitleLabel.grid(row=2, column=0, columnspan=8, pady=10)
        internalMass = 1
        internalMassLabel = customtkinter.CTkLabel(otherInputsFrame1, text="m coefficient: {}".format(internalMass))
        internalMassLabel.grid(row=3, column=0)
        internalMassSlider = customtkinter.CTkSlider(otherInputsFrame1, from_=1, to=10, number_of_steps=10, command=getInternalMass)
        internalMassSlider.grid(row=3, column=1, columnspan=2)
        internalMassSlider.set(1)
        
        # Daily schedule
        dailyScheduleFrame =  customtkinter.CTkFrame(App.frames['Building']) 
        dailyScheduleFrame.grid(row=16, column=0, columnspan = 24)
        scheduleTitleLabel = customtkinter.CTkLabel(dailyScheduleFrame, text="Daily representative schedule", font=("", 13, "bold"))
        scheduleTitleLabel.grid(row=0, column=0, columnspan=24, pady=10)
        
        def hours(i):
            value = sliders[i].get()
            labels[i].configure(text="{:.2f}".format(value))
            
        hourValues = [0, 0, 0, 0, 0, 0, 0.5, 0.5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 0.5, 0, 0, 0]
        labels, sliders = [], []
        for i in range(len(hourValues)):
            hourValueLabel = customtkinter.CTkLabel(dailyScheduleFrame, text="{:.2f}".format(hourValues[i]))
            hourValueLabel.grid(row=1, column=i, padx=4)
            labels.append(hourValueLabel)
            hourSlider = customtkinter.CTkSlider(dailyScheduleFrame, from_=0, to=1, number_of_steps=20, command=lambda value, i=i: hours(i), orientation="vertical", height=100)
            hourSlider.grid(row=2, column=i)
            hourSlider.set(hourValues[i])
            hourLabel = customtkinter.CTkLabel(dailyScheduleFrame, text="{:d}".format(i+1))
            hourLabel.grid(row=3, column=i)
            sliders.append(hourSlider)
        
        # new frame to center better next items
        otherInputsFrame2 =  customtkinter.CTkFrame(App.frames['Building']) 
        otherInputsFrame2.grid(row=20, column=0, columnspan = 8)
        
        # Setpoints
        setpointsTitle = customtkinter.CTkLabel(otherInputsFrame2, text="Heating and cooling setpoints", font=("", 13, "bold"))
        setpointsTitle.grid(row=0, column=0, columnspan=8, pady=10)
        
        # Heating            
        setpoints1 = ["5", "15", "16", "17", "18", "19", "20", "21", "22"]
        variableSetpoint1 = customtkinter.StringVar(value = setpoints1[6])
        heatingSetpointLabel = customtkinter.CTkLabel(otherInputsFrame2, text="Heating setpoint Theat [°C]:")
        heatingSetpointLabel.grid(row=1, column=0)
        setpointMenu1 = customtkinter.CTkOptionMenu(otherInputsFrame2, width=50, anchor='center', variable=variableSetpoint1, values=setpoints1)
        setpointMenu1.grid(row=1, column=1, padx=10)
        
        # Heating setback
        def heatingSetback(choice):
            selectedHeatingSetback = variableSetback1.get()
            if selectedHeatingSetback != "No":
                heatingSetbackStartMenu.configure(state="normal")
                heatingSetbackFinishMenu.configure(state="normal")
            else:
                heatingSetbackStartMenu.configure(state="disabled")
                heatingSetbackFinishMenu.configure(state="disabled")
            
        setbacks1 = ["No", "5", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]
        variableSetback1 = customtkinter.StringVar(value = setbacks1[0])
        heatingSetbackLabel = customtkinter.CTkLabel(otherInputsFrame2, text="Heating setback [°C]:")
        heatingSetbackLabel.grid(row=1, column=2)
        setbackMenu1 = customtkinter.CTkOptionMenu(otherInputsFrame2, width=50, anchor='center', variable=variableSetback1, command=heatingSetback, values=setbacks1)
        setbackMenu1.grid(row=1, column=3, padx=10)
        
        # Heating setback start and finish hours
        heatingSetbackStart = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"]
        variableHeatingSetbackStart = customtkinter.StringVar(value = heatingSetbackStart[19])
        heatingSetbackStartLabel = customtkinter.CTkLabel(otherInputsFrame2, text="Heating setback start [h]:")
        heatingSetbackStartLabel.grid(row=1, column=4)
        heatingSetbackStartMenu = customtkinter.CTkOptionMenu(otherInputsFrame2, width=50, anchor='center', variable=variableHeatingSetbackStart, values=heatingSetbackStart)
        heatingSetbackStartMenu.grid(row=1, column=5, padx=10)
        heatingSetbackStartMenu.configure(state="disabled")
        
        heatingSetbackFinish = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"]
        variableHeatingSetbackFinish = customtkinter.StringVar(value = heatingSetbackFinish[6])
        heatingSetbackFinishLabel = customtkinter.CTkLabel(otherInputsFrame2, text="Heating setback finish [h]:")
        heatingSetbackFinishLabel.grid(row=1, column=6)
        heatingSetbackFinishMenu = customtkinter.CTkOptionMenu(otherInputsFrame2, width=50, anchor='center', variable=variableHeatingSetbackFinish, values=heatingSetbackFinish)
        heatingSetbackFinishMenu.grid(row=1, column=7, padx=10)
        heatingSetbackFinishMenu.configure(state="disabled")
        
        # Heating season
        def heatingSeason(choice):
            if choice == "On":
                variableHeatingSeasonStartMonth.set(heatingSeasonStartMonth[0])
                variableHeatingSeasonStartDay.set(heatingSeasonStartDay[0])
                variableHeatingSeasonEndMonth.set(heatingSeasonEndMonth[0])
                variableHeatingSeasonEndDay.set(heatingSeasonEndDay[0])
                
        heatingSeasonStartMonth = ["On", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        variableHeatingSeasonStartMonth = customtkinter.StringVar(value = heatingSeasonStartMonth[10])
        heatingSeasonStartMonthLabel = customtkinter.CTkLabel(otherInputsFrame2, text="Heating season start month:")
        heatingSeasonStartMonthLabel.grid(row=2, column=0)
        heatingSeasonStartMonthMenu = customtkinter.CTkOptionMenu(otherInputsFrame2, width=50, anchor='center', command=heatingSeason, variable=variableHeatingSeasonStartMonth, values=heatingSeasonStartMonth)
        heatingSeasonStartMonthMenu.grid(row=2, column=1, padx=10)
        
        heatingSeasonStartDay = ["On", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"]
        variableHeatingSeasonStartDay = customtkinter.StringVar(value = heatingSeasonStartDay[15])
        heatingSeasonStartDayLabel = customtkinter.CTkLabel(otherInputsFrame2, text="Heating season start day:")
        heatingSeasonStartDayLabel.grid(row=2, column=2)
        heatingSeasonStartDayMenu = customtkinter.CTkOptionMenu(otherInputsFrame2, width=50, anchor='center', command=heatingSeason, variable=variableHeatingSeasonStartDay, values=heatingSeasonStartDay)
        heatingSeasonStartDayMenu.grid(row=2, column=3, padx=10)
        
        heatingSeasonEndMonth = ["On", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        variableHeatingSeasonEndMonth = customtkinter.StringVar(value = heatingSeasonEndMonth[4])
        heatingSeasonEndMonthLabel = customtkinter.CTkLabel(otherInputsFrame2, text="Heating season end month:")
        heatingSeasonEndMonthLabel.grid(row=2, column=4)
        heatingSeasonEndMonthMenu = customtkinter.CTkOptionMenu(otherInputsFrame2, width=50, anchor='center', command=heatingSeason, variable=variableHeatingSeasonEndMonth, values=heatingSeasonEndMonth)
        heatingSeasonEndMonthMenu.grid(row=2, column=5, padx=10)
        
        heatingSeasonEndDay = ["On", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"]
        variableHeatingSeasonEndDay = customtkinter.StringVar(value = heatingSeasonEndDay[15])
        heatingSeasonEndDayLabel = customtkinter.CTkLabel(otherInputsFrame2, text="Heating season end day:")
        heatingSeasonEndDayLabel.grid(row=2, column=6)
        heatingSeasonEndDayMenu = customtkinter.CTkOptionMenu(otherInputsFrame2, width=50, anchor='center', command=heatingSeason, variable=variableHeatingSeasonEndDay, values=heatingSeasonEndDay)
        heatingSeasonEndDayMenu.grid(row=2, column=7, padx=10)

        # Cooling
        setpoints2 = ["23", "24", "25", "26", "27", "28", "29", "30", "50"]
        variableSetpoint2 = customtkinter.StringVar(value = setpoints2[3])
        coolingSetpointLabel = customtkinter.CTkLabel(otherInputsFrame2, text="Cooling setpoint Tcool [°C]:")
        coolingSetpointLabel.grid(row=3, column=0)
        setpointMenu2 = customtkinter.CTkOptionMenu(otherInputsFrame2, width=50, anchor='center', variable=variableSetpoint2, values=setpoints2)
        setpointMenu2.grid(row=3, column=1, padx=10, pady=5)
        
        # Cooling setback
        def coolingSetback(choice):
            selectedCoolingSetback = variableSetback2.get()
            if selectedCoolingSetback != "No":
                coolingSetbackStartMenu.configure(state="normal")
                coolingSetbackFinishMenu.configure(state="normal")
            else:
                coolingSetbackStartMenu.configure(state="disabled")
                coolingSetbackFinishMenu.configure(state="disabled")
            
        setbacks2 = ["No", "26", "27", "28", "29", "30", "31", "32", "33", "50"]
        variableSetback2 = customtkinter.StringVar(value = setbacks2[0])
        coolingSetbackLabel = customtkinter.CTkLabel(otherInputsFrame2, text="Cooling setback [°C]:")
        coolingSetbackLabel.grid(row=3, column=2)
        setbackMenu2 = customtkinter.CTkOptionMenu(otherInputsFrame2, width=50, anchor='center', variable=variableSetback2, command=coolingSetback, values=setbacks2)
        setbackMenu2.grid(row=3, column=3, padx=10, pady=5)
        
        # Cooling setback start and finish hour
        coolingSetbackStart = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"]
        variableCoolingSetbackStart = customtkinter.StringVar(value = coolingSetbackStart[19])
        coolingSetbackStartLabel = customtkinter.CTkLabel(otherInputsFrame2, text="Cooling setback start [h]:")
        coolingSetbackStartLabel.grid(row=3, column=4)
        coolingSetbackStartMenu = customtkinter.CTkOptionMenu(otherInputsFrame2, width=50, anchor='center', variable=variableCoolingSetbackStart, values=coolingSetbackStart)
        coolingSetbackStartMenu.grid(row=3, column=5, padx=10)
        coolingSetbackStartMenu.configure(state="disabled")
        
        coolingSetbackFinish = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"]
        variableCoolingSetbackFinish = customtkinter.StringVar(value = coolingSetbackFinish[6])
        coolingSetbackFinishLabel = customtkinter.CTkLabel(otherInputsFrame2, text="Cooling setback finish [h]:")
        coolingSetbackFinishLabel.grid(row=3, column=6)
        coolingSetbackFinishMenu = customtkinter.CTkOptionMenu(otherInputsFrame2, width=50, anchor='center', variable=variableCoolingSetbackFinish, values=coolingSetbackFinish)
        coolingSetbackFinishMenu.grid(row=3, column=7, padx=10)
        coolingSetbackFinishMenu.configure(state="disabled")
        
        # Cooling season
        def coolingSeason(choice):
            if choice == "On":
                variableCoolingSeasonStartMonth.set(coolingSeasonStartMonth[0])
                variableCoolingSeasonStartDay.set(coolingSeasonStartDay[0])
                variableCoolingSeasonEndMonth.set(coolingSeasonEndMonth[0])
                variableCoolingSeasonEndDay.set(coolingSeasonEndDay[0])
        coolingSeasonStartMonth = ["On", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        variableCoolingSeasonStartMonth = customtkinter.StringVar(value = coolingSeasonStartMonth[6])
        coolingSeasonStartMonthLabel = customtkinter.CTkLabel(otherInputsFrame2, text="Cooling season start month:")
        coolingSeasonStartMonthLabel.grid(row=4, column=0)
        coolingSeasonStartMonthMenu = customtkinter.CTkOptionMenu(otherInputsFrame2, width=50, anchor='center', command=coolingSeason, variable=variableCoolingSeasonStartMonth, values=coolingSeasonStartMonth)
        coolingSeasonStartMonthMenu.grid(row=4, column=1, padx=10)
        
        coolingSeasonStartDay = ["On", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"]
        variableCoolingSeasonStartDay = customtkinter.StringVar(value = coolingSeasonStartDay[1])
        coolingSeasonStartDayLabel = customtkinter.CTkLabel(otherInputsFrame2, text="Cooling season start day:")
        coolingSeasonStartDayLabel.grid(row=4, column=2)
        coolingSeasonStartDayMenu = customtkinter.CTkOptionMenu(otherInputsFrame2, width=50, anchor='center', command=coolingSeason, variable=variableCoolingSeasonStartDay, values=coolingSeasonStartDay)
        coolingSeasonStartDayMenu.grid(row=4, column=3, padx=10)
        
        coolingSeasonEndMonth = ["On", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        variableCoolingSeasonEndMonth = customtkinter.StringVar(value = coolingSeasonEndMonth[8])
        coolingSeasonEndMonthLabel = customtkinter.CTkLabel(otherInputsFrame2, text="Cooling season end month:")
        coolingSeasonEndMonthLabel.grid(row=4, column=4)
        coolingSeasonEndMonthMenu = customtkinter.CTkOptionMenu(otherInputsFrame2, width=50, anchor='center', command=coolingSeason, variable=variableCoolingSeasonEndMonth, values=coolingSeasonEndMonth)
        coolingSeasonEndMonthMenu.grid(row=4, column=5, padx=10)
        
        coolingSeasonEndDay = ["On", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"]
        variableCoolingSeasonEndDay = customtkinter.StringVar(value = coolingSeasonEndDay[31])
        coolingSeasonEndDayLabel = customtkinter.CTkLabel(otherInputsFrame2, text="Cooling season end day:")
        coolingSeasonEndDayLabel.grid(row=4, column=6)
        coolingSeasonEndDayMenu = customtkinter.CTkOptionMenu(otherInputsFrame2, width=50, anchor='center', command=coolingSeason, variable=variableCoolingSeasonEndDay, values=coolingSeasonEndDay)
        coolingSeasonEndDayMenu.grid(row=4, column=7, padx=10)
        
        # new frame to center better next items
        otherInputsFrame3 =  customtkinter.CTkFrame(App.frames['Building']) 
        otherInputsFrame3.grid(row=22, column=0, columnspan = 8)
        
        # External shadings
        shadingTitleLabel = customtkinter.CTkLabel(otherInputsFrame3, text="External shadings", font=("", 13, "bold"))
        shadingTitleLabel.grid(row=0, column=0, columnspan=8, pady=10)
        
        def shadings(value):
            shadingPresent = value
            if shadingPresent == "Yes":
                shadingEntry.configure(state="normal")
            else:
                shadingEntry.configure(state="disabled")
        
        shadingLabel = customtkinter.CTkLabel(otherInputsFrame3, text="Do you want to include external shadings in the model?")
        shadingLabel.grid(row=1, column=0, columnspan=3)
        shadingButton = customtkinter.CTkSegmentedButton(otherInputsFrame3,
                                                         values=["Yes", "No"],
                                                         command=shadings)
        shadingButton.grid(row=1, column=3)
        shadingButton.set("No")
        
        shadingEntryLabel = customtkinter.CTkLabel(otherInputsFrame3, text="Shading setpoint [W m\u207b\u00B2]: ")
        shadingEntryLabel.grid(row=2, column=0, columnspan=3, sticky='e')
        variableShadingEntry = customtkinter.StringVar(value = "300")
        shadingEntry = customtkinter.CTkEntry(otherInputsFrame3, textvariable=variableShadingEntry, width=40, state="disabled")
        shadingEntry.grid(row=2, column=3, pady=5)
        
        # Price of energy
        
        energyPriceLabel = customtkinter.CTkLabel(otherInputsFrame3, text="Price of energy", font=("", 13, "bold"))
        energyPriceLabel.grid(row=3, column=0, columnspan=8, pady=10)

        def getEnergyPriceEl(val):
            electricityPrice = float(round(val,2))
            electricityPriceLabel.configure(text="Electricity energy price [EUR/kWhe]: {:.2f}".format(electricityPrice))
        
        electricityPrice = 0.15
        electricityPriceLabel = customtkinter.CTkLabel(otherInputsFrame3, text="Electricity energy price [EUR/kWhe]: {:.2f}".format(electricityPrice))
        electricityPriceLabel.grid(row=4, column=0, columnspan=2)
        electricityPriceElSlider = customtkinter.CTkSlider(otherInputsFrame3, from_=0.0, to=1.5, number_of_steps=150, command=getEnergyPriceEl)
        electricityPriceElSlider.grid(row=4, column=2, columnspan=2)
        electricityPriceElSlider.set(electricityPrice)
        
        def getEnergyPriceGas(val):
            gasPrice = float(round(val,2))
            gasPriceLabel.configure(text="Natural gas price [EUR/Sm3]: {:.2f}".format(gasPrice))
        
        gasPrice = 0.7
        gasPriceLabel = customtkinter.CTkLabel(otherInputsFrame3, text="Natural gas price [EUR/Sm3]: {:.2f}".format(gasPrice))
        gasPriceLabel.grid(row=5, column=0, columnspan=2)
        gasPriceElSlider = customtkinter.CTkSlider(otherInputsFrame3, from_=0.0, to=1.5, number_of_steps=150, command=getEnergyPriceGas)
        gasPriceElSlider.grid(row=5, column=2, columnspan=2)
        gasPriceElSlider.set(gasPrice)
        
#%%     ########### Results page ###########     

        App.frames['Results'] = customtkinter.CTkScrollableFrame(self.right_side_container, fg_color="transparent")
        App.frames["Results"].grid_columnconfigure(0, weight=1)
        
        mainFrameResults =  customtkinter.CTkFrame(App.frames['Results']) 
        mainFrameResults.grid(row=0, column=0, columnspan=15)
        
        def showOptimizedResults():
            simulationToLoad = loadSimulationMenu.get()
            # 1st chart
            paretoImage1 = customtkinter.CTkImage(light_image=Image.open(simulationsFolderPath + '/' + simulationToLoad + "/Results/Pareto_HeatingCooling.png"),
                                                  size=(425,325))
            customtkinter.CTkLabel(mainFrameResults, image = paretoImage1, text='').grid(row = 0, column = 0, columnspan = 5)
            # 2nd chart
            paretoImage2 = customtkinter.CTkImage(light_image=Image.open(simulationsFolderPath + '/' + simulationToLoad + "/Results/Pareto_HeatingComfort.png"),
                                                  size=(425,325))
            customtkinter.CTkLabel(mainFrameResults, image = paretoImage2, text='').grid(row = 0, column = 5, columnspan = 5)
            # 3rd chart
            paretoImage3 = customtkinter.CTkImage(light_image=Image.open(simulationsFolderPath + '/' + simulationToLoad + "/Results/Pareto_HeatingNPV.png"),
                                                  size=(425,325))
            customtkinter.CTkLabel(mainFrameResults, image = paretoImage3, text='').grid(row = 0, column = 10, columnspan = 5)
            # 4th chart
            paretoImage4 = customtkinter.CTkImage(light_image=Image.open(simulationsFolderPath + '/' + simulationToLoad + "/Results/Pareto_CoolingComfort.png"),
                                                  size=(425,325))
            customtkinter.CTkLabel(mainFrameResults, image = paretoImage4, text='').grid(row = 1, column = 0, columnspan = 5)
            # 5th chart
            paretoImage5 = customtkinter.CTkImage(light_image=Image.open(simulationsFolderPath + '/' + simulationToLoad + "/Results/Pareto_CoolingNPV.png"),
                                                  size=(425,325))
            customtkinter.CTkLabel(mainFrameResults, image = paretoImage5, text='').grid(row = 1, column = 5, columnspan = 5)
            # 6th chart
            paretoImage5 = customtkinter.CTkImage(light_image=Image.open(simulationsFolderPath + '/' + simulationToLoad + "/Results/Pareto_ComfortNPV.png"),
                                                  size=(425,325))
            customtkinter.CTkLabel(mainFrameResults, image = paretoImage5, text='').grid(row = 1, column = 10, columnspan = 5)

            paretoInputs = pd.read_csv(simulationsFolderPath + '/' + simulationToLoad + "/Results/Pareto_Inputs.csv", index_col = 0)
            paretoInputs.dropna(axis='columns', inplace=True)
            paretoOutputs = pd.read_csv(simulationsFolderPath + '/' + simulationToLoad + "/Results/Pareto_Outputs.csv", index_col = 0)
            initialCosts = investmentCost(currentPath, varSimulationName.get())
            insulationMaterialResults, insulationThicknessResults, windowResults = [], [], []
            if 'Insulation material' in paretoInputs.columns:
                for insulationMaterial in paretoInputs["Insulation material"]:
                    insulationMaterialResults.append(insulationMaterials[int(insulationMaterial)])
            else:
                for insulationMaterial in range(len(paretoInputs.index)):
                    insulationMaterialResults.append("-")
                    
            if 'Insulation thickness' in paretoInputs.columns:
                for insulationThickness in paretoInputs["Insulation thickness"]:
                    insulationThicknessResults.append(insulationThickness)
            else:
                for insulationThickness in range(len(paretoInputs.index)):
                    insulationThicknessResults.append("-")
                    
            if 'Windows' in paretoInputs.columns:
                for window in paretoInputs["Windows"]:
                    windowResults.append(glazingMaterials[int(window)])
            else:
                for window in range(len(paretoInputs.index)):
                    windowResults.append("-")
                
            entries = []
            for i in range(len(paretoInputs.index)):
                args = (i, insulationMaterialResults[i], insulationThicknessResults[i], windowResults[i], round(paretoOutputs.iloc[i,0],1), round(paretoOutputs.iloc[i,4],1), round(paretoOutputs.iloc[i,1],1), round(paretoOutputs.iloc[i,5],1), round(paretoOutputs.iloc[i,2],1), round(paretoOutputs.iloc[i,3],0), round(initialCosts[i],0))
                entries.append(args)
            
            def treeview_sort_column(tv, col, reverse):
                l = [(tv.set(k, col), k) for k in tv.get_children('')]
                try:
                    l.sort(key=lambda t: float(t[0].replace(",","")), reverse=reverse)
                except:
                    l.sort(reverse=reverse)
                for index, (val, k) in enumerate(l):
                    tv.move(k, '', index)
                tv.heading(col, command=lambda _col=col: treeview_sort_column(tv, _col, not reverse))
            
            columns = ('ID', 'Insulation material','Insulation thickness', 'Glazing material', 'Heating demand [kWh m\u207b\u00B2]', 'Heating peak [W m\u207b\u00B2]', 'Cooling demand [kWh m\u207b\u00B2]', 'Cooling peak [W m\u207b\u00B2]', 'PPD [%]', 'NPV [€]', 'Initial cost [€]')
            resultTable = ttk.Treeview(mainFrameResults, columns=columns, height=10) # if you want size to change height should be len(paretoInputs.index)
            resultTable.column('#0', width=0,  stretch='no')      
            resultTable.column('ID', anchor='center', width=60)                   
            resultTable.column('Insulation material', anchor='center', width=150)
            resultTable.column('Insulation thickness', anchor='center', width=150)
            resultTable.column('Glazing material', anchor='center', width=160)
            resultTable.column('Heating demand [kWh m\u207b\u00B2]', anchor='center', width=200)
            resultTable.column('Heating peak [W m\u207b\u00B2]', anchor='center', width=180)
            resultTable.column('Cooling demand [kWh m\u207b\u00B2]', anchor='center', width=200)
            resultTable.column('Cooling peak [W m\u207b\u00B2]', anchor='center', width=180)
            resultTable.column('PPD [%]', anchor='center', width=80)
            resultTable.column('NPV [€]', anchor='center', width=80)
            resultTable.column('Initial cost [€]', anchor='center', width=120)
            resultTable.heading('#0', text='', anchor='center')
            resultTable.heading('ID', text='ID', anchor='center')
            resultTable.heading('Insulation material', text='Insulation material', anchor='center')
            resultTable.heading('Insulation thickness', text='Insulation thickness', anchor='center')
            resultTable.heading('Glazing material', text='Glazing material', anchor='center')  
            resultTable.heading('Heating demand [kWh m\u207b\u00B2]', text='Heating demand [kWh m\u207b\u00B2]', anchor='center')
            resultTable.heading('Heating peak [W m\u207b\u00B2]', text='Heating peak [W m\u207b\u00B2]', anchor='center')
            resultTable.heading('Cooling demand [kWh m\u207b\u00B2]', text='Cooling demand [kWh m\u207b\u00B2]', anchor='center')
            resultTable.heading('Cooling peak [W m\u207b\u00B2]', text='Cooling peak [W m\u207b\u00B2]', anchor='center')
            resultTable.heading('PPD [%]', text='PPD [%]', anchor='center')
            resultTable.heading('NPV [€]', text='NPV [€]', anchor='center') 
            resultTable.heading('Initial cost [€]', text='Initial cost [€]', anchor='center')
            resultTable.grid(row = 3, column = 0, columnspan = 15)
            
            yScrollbarTable = customtkinter.CTkScrollbar(mainFrameResults, command=resultTable.yview)
            yScrollbarTable.grid(row = 3, column = 14, sticky="e")
            resultTable.configure(yscrollcommand=yScrollbarTable.set)
            
            for entry in entries:
                resultTable.insert(parent = '', index = entry[0], iid = entry[0], text ='', values=(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8], entry[9], entry[10]))
                
            for col in columns:
                resultTable.heading(col, text=col, command=lambda _col=col: treeview_sort_column(resultTable, _col, False))
        def showFixedResults():
            simulationToLoad = loadSimulationMenu.get()
            simulationName = varSimulationName.get()
            fixedSimulationOutputs = pd.read_csv(simulationsFolderPath + '/' + simulationToLoad + "/Results/FixedSimulation_Outputs.csv", header = None)
            # 1st chart
            paretoImage1 = customtkinter.CTkImage(light_image=Image.open(simulationsFolderPath + '/' + simulationToLoad + "/Results/ShoeboxFixedParameters_HeatingCooling.png"),
                                                  size=(425,325))
            customtkinter.CTkLabel(mainFrameResults, image = paretoImage1, text='').grid(row = 0, column = 0, columnspan = 5)
            # 2nd chart
            paretoImage2 = customtkinter.CTkImage(light_image=Image.open(simulationsFolderPath + '/' + simulationToLoad + "/Results/ShoeboxFixedParameters_HeatingComfort.png"),
                                                  size=(425,325))
            customtkinter.CTkLabel(mainFrameResults, image = paretoImage2, text='').grid(row = 0, column = 5, columnspan = 5)
            # 3rd chart
            paretoImage3 = customtkinter.CTkImage(light_image=Image.open(simulationsFolderPath + '/' + simulationToLoad + "/Results/ShoeboxFixedParameters_HeatingNPV.png"),
                                                  size=(425,325))
            customtkinter.CTkLabel(mainFrameResults, image = paretoImage3, text='').grid(row = 0, column = 10, columnspan = 5)
            # 4th chart
            paretoImage4 = customtkinter.CTkImage(light_image=Image.open(simulationsFolderPath + '/' + simulationToLoad + "/Results/ShoeboxFixedParameters_CoolingComfort.png"),
                                                  size=(425,325))
            customtkinter.CTkLabel(mainFrameResults, image = paretoImage4, text='').grid(row = 1, column = 0, columnspan = 5)
            # 5th chart
            paretoImage5 = customtkinter.CTkImage(light_image=Image.open(simulationsFolderPath + '/' + simulationToLoad + "/Results/ShoeboxFixedParameters_CoolingNPV.png"),
                                                  size=(425,325))
            customtkinter.CTkLabel(mainFrameResults, image = paretoImage5, text='').grid(row = 1, column = 5, columnspan = 5)
            # 6th chart
            paretoImage5 = customtkinter.CTkImage(light_image=Image.open(simulationsFolderPath + '/' + simulationToLoad + "/Results/ShoeboxFixedParameters_ComfortNPV.png"),
                                                  size=(425,325))
            customtkinter.CTkLabel(mainFrameResults, image = paretoImage5, text='').grid(row = 1, column = 10, columnspan = 5)
              
            thisSimulationFolderPath = simulationsFolderPath + '/' + simulationName
            fname1 = thisSimulationFolderPath + "/ShoeboxFixedParameters_ForSimulation.idf"
            idf1 = IDF(fname1)
            surfaces = idf1.idfobjects["BuildingSurface:Detailed"]
            if surfaces[0].Construction_Name != "No_Insulation":
                entry = (0, insulationMaterials[fixedInsulationMaterialIndex], fixedInsulationThicknessSlider.get(), glazingMaterials[fixedGlazingMaterialIndex], round(fixedSimulationOutputs.iloc[0,0],1), round(fixedSimulationOutputs.iloc[5,0],1), round(fixedSimulationOutputs.iloc[1,0],1), round(fixedSimulationOutputs.iloc[6,0],1), round(fixedSimulationOutputs.iloc[2,0],1), round(fixedSimulationOutputs.iloc[3,0],0), round(fixedSimulationOutputs.iloc[4,0],0))
            else:
                entry = (0, "-", "-", glazingMaterials[fixedGlazingMaterialIndex], round(fixedSimulationOutputs.iloc[0,0],1), round(fixedSimulationOutputs.iloc[5,0],1), round(fixedSimulationOutputs.iloc[1,0],1), round(fixedSimulationOutputs.iloc[6,0],1), round(fixedSimulationOutputs.iloc[2,0],1), round(fixedSimulationOutputs.iloc[3,0],0), round(fixedSimulationOutputs.iloc[4,0],0))

            columns = ('ID', 'Insulation material','Insulation thickness', 'Glazing material', 'Heating demand [kWh m\u207b\u00B2]', 'Heating peak [W m\u207b\u00B2]', 'Cooling demand [kWh m\u207b\u00B2]', 'Cooling peak [W m\u207b\u00B2]', 'PPD [%]', 'NPV [€]', 'Initial cost [€]')
            resultTable = ttk.Treeview(mainFrameResults, columns=columns, height=10)
            columns = ('ID', 'Insulation material','Insulation thickness', 'Glazing material', 'Heating demand [kWh m\u207b\u00B2]', 'Heating peak [W m\u207b\u00B2]', 'Cooling demand [kWh m\u207b\u00B2]', 'Cooling peak [W m\u207b\u00B2]', 'PPD [%]', 'NPV [€]', 'Initial cost [€]')
            resultTable = ttk.Treeview(mainFrameResults, columns=columns, height=10) # if you want size to change height should be len(paretoInputs.index)
            resultTable.column('#0', width=0,  stretch='no')      
            resultTable.column('ID', anchor='center', width=60)                   
            resultTable.column('Insulation material', anchor='center', width=150)
            resultTable.column('Insulation thickness', anchor='center', width=150)
            resultTable.column('Glazing material', anchor='center', width=160)
            resultTable.column('Heating demand [kWh m\u207b\u00B2]', anchor='center', width=200)
            resultTable.column('Heating peak [W m\u207b\u00B2]', anchor='center', width=180)
            resultTable.column('Cooling demand [kWh m\u207b\u00B2]', anchor='center', width=200)
            resultTable.column('Cooling peak [W m\u207b\u00B2]', anchor='center', width=180)
            resultTable.column('PPD [%]', anchor='center', width=80)
            resultTable.column('NPV [€]', anchor='center', width=80)
            resultTable.column('Initial cost [€]', anchor='center', width=120)
            resultTable.heading('#0', text='', anchor='center')
            resultTable.heading('ID', text='ID', anchor='center')
            resultTable.heading('Insulation material', text='Insulation material', anchor='center')
            resultTable.heading('Insulation thickness', text='Insulation thickness', anchor='center')
            resultTable.heading('Glazing material', text='Glazing material', anchor='center')  
            resultTable.heading('Heating demand [kWh m\u207b\u00B2]', text='Heating demand [kWh m\u207b\u00B2]', anchor='center')
            resultTable.heading('Heating peak [W m\u207b\u00B2]', text='Heating peak [W m\u207b\u00B2]', anchor='center')
            resultTable.heading('Cooling demand [kWh m\u207b\u00B2]', text='Cooling demand [kWh m\u207b\u00B2]', anchor='center')
            resultTable.heading('Cooling peak [W m\u207b\u00B2]', text='Cooling peak [W m\u207b\u00B2]', anchor='center')
            resultTable.heading('PPD [%]', text='PPD [%]', anchor='center')
            resultTable.heading('NPV [€]', text='NPV [€]', anchor='center') 
            resultTable.heading('Initial cost [€]', text='Initial cost [€]', anchor='center')
            resultTable.grid(row = 3, column = 0, columnspan = 15)
            
            yScrollbarTable = customtkinter.CTkScrollbar(mainFrameResults, command=resultTable.yview)
            yScrollbarTable.grid(row = 3, column = 14, sticky="e")
            resultTable.configure(yscrollcommand=yScrollbarTable.set)
            
            
            if len(resultTable.get_children()) == 0:
                for i in resultTable.get_children():
                    resultTable.delete(i)
                resultTable.insert(parent = '', index = entry[0], iid = entry[0], text ='', values=(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8], entry[9], entry[10]))
            else:
                resultTable.insert(parent = '', index = entry[0], iid = entry[0], text ='', values=(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8], entry[9], entry[10]))

        updateButtons = customtkinter.CTkFrame(mainFrameResults, fg_color="transparent") 
        updateButtons.grid(row = 4, columnspan=15)
        updateResultsButton1 = customtkinter.CTkButton(updateButtons, text ="Update optimization results", command = showOptimizedResults)
        updateResultsButton1.grid(row = 0, columnspan=15)
        updateResultsButton2 = customtkinter.CTkButton(updateButtons, text ="Update fixed results", command = showFixedResults)
        updateResultsButton2.grid(row = 1, columnspan=15)

a = App()
a.mainloop()