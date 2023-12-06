# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 10:39:30 2022

@author: FBattini
"""
def runOptimization(currentPath, simulationName, simulationStateLabel):

    # currentPath = "C:/Users/FBattini/OneDrive - Scientific Network South Tyrol (1)/Documents/GitHub/Simplified-Configurator/"
    # simulationName = "Simulation1"
    
    import sys
    import os
    from eppy import modeleditor
    from eppy.modeleditor import IDF
    import matplotlib
    import matplotlib.pyplot as plt
    from EconomicAnalysis import economicAnalysis
    import numpy as np
    import pandas as pd
    
    matplotlib.rcParams['axes.formatter.useoffset'] = False
    
    global runs
    
    # Turn interactive plotting off
    plt.ioff()
    
    def pareto(costs):
        """
        Find the pareto-efficient points
        :param costs: An (n_points, n_costs) array
        :return: A (n_points, ) boolean array, indicating whether each point is Pareto efficient
        """
        paretoPoints = np.ones(costs.shape[0], dtype=bool)
        for i, c in enumerate(costs):
            paretoPoints[i] = np.all(np.any(costs[:i] > c, axis=1)) and np.all(np.any(costs[i+1:] > c, axis=1))
        return paretoPoints
    
    
    eppy_path = "C:/Anaconda3/Lib/site-packages/eppy"
    sys.path.append(eppy_path)
    iddfile = "C:/EnergyPlusV9-4-0/Energy+.idd"
    thisSimulationFolderPath = currentPath + '/Simulations/' + simulationName
    thisSimulationResultsFolder = thisSimulationFolderPath + '/Results'
    optimizationInputDF = pd.read_csv(thisSimulationFolderPath + "/OptimizationVariables.csv", index_col=0)
    buildingInputsDF = pd.read_csv(thisSimulationFolderPath + '/BuildingInputs.csv', index_col=0)
    weatherFilesPath = currentPath + "/Weather files/"  # weather files base path
    epw = weatherFilesPath + buildingInputsDF.loc[0, 'Weather file'] + ".epw"
    floorsNumber = buildingInputsDF.loc[0, 'Floors number']
    
    fname1 = thisSimulationFolderPath + "/ShoeboxFixedParameters.idf"
    IDF.setiddname(iddfile)
    idf1 = IDF(fname1, epw)
    insulationMaterialsDF = pd.read_csv("SimulationFiles/Insulation-material.csv")
    insulationMaterials = insulationMaterialsDF.loc[:,"Material"]
    glazingMaterialsDF = pd.read_csv("SimulationFiles/Glazing-material.csv")
    glazingMaterials = glazingMaterialsDF.loc[:,"Material"]
    # empty folder from previous simulations
    # remove useless files after every run
    for file in os.listdir(thisSimulationFolderPath):
        if file.startswith("ShoeboxOptimization"):
            # current directory is another one so I have to point it
            os.remove(thisSimulationFolderPath + "\\" + file)
    
    ''' Part to make optimization indipendent by variables and order'''
    variablesNames = []
    # loop through first row and check if the element is > 1, if yes append the column name
    for item in np.arange(len(optimizationInputDF.iloc[0, :])):
        # greater or equal because I have indexes that start from zero, NaNs are anyway not included
        if optimizationInputDF.iloc[0, :][item] >= 0:
            variablesNames.append(optimizationInputDF.iloc[0, :].index[item])
    optimizationValuesPerColumns = optimizationInputDF.count().values           # for every column count non-NaNs
    # count columns without zero to get the number of variables for the optimization
    variablesNumber = np.count_nonzero(optimizationValuesPerColumns)
    
    runs = 0  # variable to name files progressively
    ''' Run if I have variables to optimize'''
    if len(optimizationInputDF.iloc[:, 0].dropna().values.tolist()) > 0:
        insulationCases = len(optimizationInputDF.iloc[:, 0].dropna().values.tolist())
    else:
        insulationCases = 1
    if len(optimizationInputDF.iloc[:, 1].dropna().values.tolist()) > 0:
        thicknessCases = len(optimizationInputDF.iloc[:, 1].dropna().values.tolist())
    else:
        thicknessCases = 1
    if len(optimizationInputDF.iloc[:, 2].dropna().values.tolist()) > 0:
        glazingCases = len(optimizationInputDF.iloc[:, 2].dropna().values.tolist())
    else:
        glazingCases = 1
    
    numberOfSimulations = insulationCases*thicknessCases*glazingCases
    if variablesNumber > 0:
        # optimize if at least one column is not full of NaNs
        combinations = np.array([])
        for insulationIndex in optimizationInputDF.iloc[:, 0].dropna().values.tolist() or [None]:
            for insulationThickness in optimizationInputDF.iloc[:, 1].dropna().values.tolist() or [None]:
                for glazingIndex in optimizationInputDF.iloc[:, 2].dropna().values.tolist() or [None]:
                    if runs == 0:
                        combinations = np.array([insulationIndex, insulationThickness, glazingIndex])
                    else:
                        combinations = np.vstack([combinations, [insulationIndex, insulationThickness, glazingIndex]])
                    
                    if 'Insulation material' in variablesNames:
                        constructions = idf1.idfobjects["Construction"]
                        constructions[0].Outside_Layer = constructions[1].Layer_2 = insulationMaterials[int(insulationIndex)]    # it must be int to pick from the list
    
                    if 'Insulation thickness' in variablesNames:
                        insulationThicknessM = insulationThickness/100
                        materials = idf1.idfobjects["Material"]
                        if insulationThicknessM == 0:
                            materials[3].Thickness = materials[4].Thickness = materials[5].Thickness = materials[6].Thickness = 1/100000
                        else:
                            materials[3].Thickness = materials[4].Thickness = materials[5].Thickness = materials[6].Thickness = insulationThicknessM
                        
                    if 'Windows' in variablesNames:
                        windows = idf1.idfobjects["FenestrationSurface:Detailed"]
                        for window in windows:
                            window.Construction_Name = glazingMaterials[int(glazingIndex)]
    
                    idf1.save(thisSimulationFolderPath + "/ShoeboxOptimization" + str(runs) + ".idf")
                    idf1.run(output_directory=thisSimulationFolderPath, 
                             readvars=True, output_prefix="/ShoeboxOptimization" + str(runs))
    
                    runs = runs + 1
                    simulationStateLabel.configure(text="Simulating... ({:d}/{:d})".format(runs, numberOfSimulations), fg_color="#FF6600", text_color="white", font=("", 13, "bold"), width=150)
        
        # remove useless files after every run
        for file in os.listdir(thisSimulationFolderPath):
            if not file.endswith(".csv") and not file.endswith(".idf") and not file.endswith("Results"):
                # current directory is another one so I have to point it
                os.remove(thisSimulationFolderPath + "/" + file)
    
        zone = idf1.idfobjects["Zone"][0]
        area = modeleditor.zonearea(idf1, zone.Name)*floorsNumber
        results, initialCosts = np.array([]), []
        hoursToExclude = []
        for i in range(24):
            if buildingInputsDF.loc[0,'Schedule{:d}'.format(i+1)] == 0:
                hoursToExclude.append(i)            
        for run in range(runs):
            resultsDF = pd.read_csv(thisSimulationFolderPath + "/ShoeboxOptimization" + str(run) + "out.csv", parse_dates=[0], index_col=0)
            annualHeating = resultsDF.iloc[:, 1].sum()/3600000/area   # already converted in kWh/m2
            heatingPeak = resultsDF.iloc[:, 1].max()/3600/area        # already converted in W/m2
            annualCooling = resultsDF.iloc[:, 2].sum()/3600000/area   # already converted in kWh/m2
            coolingPeak = resultsDF.iloc[:, 2].max()/3600/area        # already converted in W/m2
            meanPPD = resultsDF.iloc[:, 3].mean()
            if 'Insulation material' in variablesNames:
                insulationIndex = int(combinations[run, 0])
            else:
                # in case I have to consider it economically but it is not optimized
                insulationIndex = int(insulationMaterials[insulationMaterials == buildingInputsDF.loc[0, 'Fixed insulation index']].index[0])
                
            if 'Insulation thickness' in variablesNames:
                insulationThicknessM = combinations[run, 1]/100
            else:
                insulationThicknessM = buildingInputsDF.loc[0, 'Ins thickness']/100
            if 'Windows' in variablesNames:
                glazingIndex = int(combinations[run, 2])
            else:
                glazingIndex = int(glazingMaterials[glazingMaterials == buildingInputsDF.loc[0, 'Fixed glazing index']].index[0])
                
            NPV, initialCost = economicAnalysis(resultsDF, currentPath, thisSimulationFolderPath, idf1, insulationIndex, glazingIndex, insulationThicknessM)
            initialCosts.append(initialCost)
            
            # find PPD only for occupied hours
            if len(hoursToExclude) > 0:
                start_time = '2022-01-01 00:00:00'
                duration = pd.Timedelta(days=365)
                end_time = pd.to_datetime(start_time) + duration - pd.Timedelta(hours=1)
                date_range = pd.date_range(start=start_time, end=end_time, freq='H')
                resultsDF.set_index(date_range, inplace=True)
                resultsDFFiltered = resultsDF[~resultsDF.index.hour.isin(hoursToExclude)]
                meanPPD = resultsDFFiltered.iloc[:, 3].mean()
            else:
                meanPPD = resultsDF.iloc[:, 3].mean()
            
            if run == 0:
                results = np.array([annualHeating, annualCooling, meanPPD, NPV])
                peaks = np.array([heatingPeak, coolingPeak])
            else:
                results = np.vstack([results, [annualHeating, annualCooling, meanPPD, NPV]])
                peaks = np.vstack([peaks, [heatingPeak, coolingPeak]])
    
        paretoFront = pareto(results)
        results = np.hstack((results, peaks))
        indexesOnPareto = []
        for n in range(len(paretoFront)):
            if paretoFront[n] == True:
                indexesOnPareto.append(n)
        X = combinations[indexesOnPareto, :]        # inputs of pareto
        F = results[indexesOnPareto, :]             # outputs of pareto
        X_all = combinations                        # all inputs
        F_all = results                             # all output
        
        plt.figure(figsize=(7, 5))
        allPoints = plt.scatter(F_all[:, 0], F_all[:, 1], s=30, c='blue', marker='.')
        paretoPoints = plt.scatter(F[:, 0], F[:, 1], s=40, c='red', marker='o')
        plt.title("Objective Space: Heating and Cooling")
        plt.xlabel("Heating demand [kWh m\u207b\u00B2]")
        plt.ylabel("Cooling demand [kWh m\u207b\u00B2]")
        plt.legend((allPoints, paretoPoints), ('Other results', 'Optimal results'))
        plt.savefig(thisSimulationResultsFolder + '/Pareto_HeatingCooling.png')
    
        plt.figure(figsize=(7, 5))
        allPoints = plt.scatter(F_all[:, 0], F_all[:, 2], s=30, c='blue', marker='.')
        paretoPoints = plt.scatter(F[:, 0], F[:, 2], s=40, c='red', marker='o')
        plt.title("Objective Space: Heating and Comfort")
        plt.xlabel("Heating demand [kWh m\u207b\u00B2]")
        plt.ylabel("Annual average PPD [%]")
        plt.legend((allPoints, paretoPoints), ('Other results', 'Optimal results'))
        plt.savefig(thisSimulationResultsFolder + '/Pareto_HeatingComfort.png')
    
        plt.figure(figsize=(7, 5))
        allPoints = plt.scatter(F_all[:, 0], F_all[:, 3], s=30, c='blue', marker='.')
        paretoPoints = plt.scatter(F[:, 0], F[:, 3], s=40, c='red', marker='o')
        plt.title("Objective Space: Heating and Net Present Value")
        plt.xlabel("Heating demand [kWh m\u207b\u00B2]")
        plt.ylabel("Net Present Value [€]")
        plt.legend((allPoints, paretoPoints), ('Other results', 'Optimal results'))
        plt.savefig(thisSimulationResultsFolder + '/Pareto_HeatingNPV.png')
    
        plt.figure(figsize=(7, 5))
        allPoints = plt.scatter(F_all[:, 1], F_all[:, 2], s=30, c='blue', marker='.')
        paretoPoints = plt.scatter(F[:, 1], F[:, 2], s=40, c='red', marker='o')
        plt.title("Objective Space: Cooling and Comfort")
        plt.xlabel("Cooling demand [kWh m\u207b\u00B2]")
        plt.ylabel("Annual average PPD [%]")
        plt.legend((allPoints, paretoPoints), ('Other results', 'Optimal results'))
        plt.savefig(thisSimulationResultsFolder + '/Pareto_CoolingComfort.png')
    
        plt.figure(figsize=(7, 5))
        allPoints = plt.scatter(F_all[:, 1], F_all[:, 3], s=30, c='blue', marker='.')
        paretoPoints = plt.scatter(F[:, 1], F[:, 3], s=40, c='red', marker='o')
        plt.title("Objective Space: Cooling and Net Present Value")
        plt.xlabel("Cooling demand [kWh m\u207b\u00B2]")
        plt.ylabel("Net Present Value [€]")
        plt.legend((allPoints, paretoPoints), ('Other results', 'Optimal results'))
        plt.savefig(thisSimulationResultsFolder + '/Pareto_CoolingNPV.png')
    
        plt.figure(figsize=(7, 5))
        allPoints = plt.scatter(F_all[:, 2], F_all[:, 3], s=30, c='blue', marker='.')
        paretoPoints = plt.scatter(F[:, 2], F[:, 3], s=40, c='red', marker='o')
        plt.title("Objective Space: Comfort and Net Present Value")
        plt.xlabel("Annual average PPD [%]")
        plt.ylabel("Net Present Value [€]")
        plt.legend((allPoints, paretoPoints), ('Other results', 'Optimal results'))
        plt.savefig(thisSimulationResultsFolder + '/Pareto_ComfortNPV.png')
    
        paretoInputs = pd.DataFrame(X, columns=optimizationInputDF.columns)
        paretoOutputs = pd.DataFrame(F, columns=['Heating', 'Cooling', 'Comfort', 'NPV', 'Heating peak', 'Cooling peak'])
        paretoAllInputs = pd.DataFrame(X_all, columns=optimizationInputDF.columns)
        paretoAllOutputs = pd.DataFrame(F_all, columns=['Heating', 'Cooling', 'Comfort', 'NPV', 'Heating peak', 'Cooling peak'])
        paretoInputs.to_csv(thisSimulationResultsFolder + "/Pareto_Inputs.csv")
        paretoOutputs.to_csv(thisSimulationResultsFolder + "/Pareto_Outputs.csv")
        paretoAllInputs.to_csv(thisSimulationResultsFolder + "/All_Inputs.csv")
        paretoAllOutputs.to_csv(thisSimulationResultsFolder + "/All_Outputs.csv")
        np.savetxt(thisSimulationResultsFolder + "/InitialCosts.csv", np.array(initialCosts), delimiter=",")
    else:
        insulationIndex = int(insulationMaterials[insulationMaterials == buildingInputsDF.loc[0, 'Fixed insulation index']].index[0])
        glazingIndex = int(glazingMaterials[glazingMaterials == buildingInputsDF.loc[0, 'Fixed glazing index']].index[0])
        insulationThicknessM = buildingInputsDF.loc[0, 'Ins thickness']/100
        
        constructions = idf1.idfobjects["Construction"]
        constructions[2].Outside_Layer = constructions[1].Layer_2 = insulationMaterials[insulationIndex]    # it must be int to pick from the list
    
        materials = idf1.idfobjects["Material"]
        if insulationThicknessM == 0:
            materials[3].Thickness = materials[4].Thickness = materials[5].Thickness = materials[6].Thickness = 1/100000
        else:
            materials[3].Thickness = materials[4].Thickness = materials[5].Thickness = materials[6].Thickness = insulationThicknessM
    
        windows = idf1.idfobjects["FenestrationSurface:Detailed"]
        for window in windows:
            window.Construction_Name = glazingMaterials[glazingIndex]
        
        idf1.save(thisSimulationFolderPath + '\\ShoeboxFixedParameters_ForSimulation.idf')
        fname1 = thisSimulationFolderPath + "/ShoeboxFixedParameters_ForSimulation.idf"
        idf1 = IDF(fname1, epw)
        idf1.run(output_directory=thisSimulationFolderPath, readvars=True, output_prefix="\\ShoeboxFixedParameters_ForSimulation")
        resultsDF = pd.read_csv(thisSimulationFolderPath + "\\ShoeboxFixedParameters_ForSimulation" + "out.csv", index_col=0)
        zone = idf1.idfobjects["Zone"][0]
        area = modeleditor.zonearea(idf1, zone.Name)*floorsNumber
        annualHeatingFixed = resultsDF.iloc[:, 1].sum()/3600000/area   # already converted in kWh/m2
        heatingPeakFixed = resultsDF.iloc[:, 1].max()/3600/area        # already converted in W/m2
        annualCoolingFixed = resultsDF.iloc[:, 2].sum()/3600000/area   # already converted in kWh/m2
        coolingPeakFixed = resultsDF.iloc[:, 2].max()/3600/area        # already converted in W/m2
        
        NPVFixed, initialCostFixed = economicAnalysis(resultsDF, currentPath, thisSimulationFolderPath, idf1, insulationIndex, glazingIndex, insulationThicknessM)
        # find PPD only for occupied hours
        hoursToExclude = []
        for i in range(24):
            if buildingInputsDF.loc[0,'Schedule{:d}'.format(i+1)] == 0:
                hoursToExclude.append(i) 
        if len(hoursToExclude) > 0:
            start_time = '2022-01-01 00:00:00'
            duration = pd.Timedelta(days=365)
            end_time = pd.to_datetime(start_time) + duration - pd.Timedelta(hours=1)
            date_range = pd.date_range(start=start_time, end=end_time, freq='H')
            resultsDF.set_index(date_range, inplace=True)
            resultsDFFiltered = resultsDF[~resultsDF.index.hour.isin(hoursToExclude)]
            meanPPDFixed = resultsDFFiltered.iloc[:, 3].mean()
        else:
            meanPPDFixed = resultsDF.iloc[:, 3].mean()
        fixedSimulationResults = np.array([annualHeatingFixed, annualCoolingFixed, meanPPDFixed, NPVFixed, initialCostFixed, heatingPeakFixed, coolingPeakFixed])
    
        plt.figure(figsize=(7, 5))
        plt.scatter(annualHeatingFixed, annualCoolingFixed, s=20, c='red', marker='.')
        plt.title("Objective Space: Heating and Cooling")
        plt.xlabel("Heating demand [kWh m\u207b\u00B2]")
        plt.ylabel("Cooling demand [kWh m\u207b\u00B2]")
        plt.savefig(thisSimulationResultsFolder + '/ShoeboxFixedParameters_HeatingCooling.png')
    
        plt.figure(figsize=(7, 5))
        plt.scatter(annualHeatingFixed, meanPPDFixed, s=20, c='red', marker='.')
        plt.title("Objective Space: Heating and Comfort")
        plt.xlabel("Heating demand [kWh m\u207b\u00B2]")
        plt.ylabel("Annual average PPD [%]")
        plt.savefig(thisSimulationResultsFolder + '/ShoeboxFixedParameters_HeatingComfort.png')
    
        plt.figure(figsize=(7, 5))
        plt.scatter(annualHeatingFixed, NPVFixed, s=20, c='red', marker='.')
        plt.title("Objective Space: Heating and Net Present Value")
        plt.xlabel("Heating demand [kWh m\u207b\u00B2]")
        plt.ylabel("Net Present Value [€]")
        plt.savefig(thisSimulationResultsFolder + '/ShoeboxFixedParameters_HeatingNPV.png')
    
        plt.figure(figsize=(7, 5))
        plt.scatter(annualCoolingFixed, meanPPDFixed, s=20, c='red', marker='.')
        plt.title("Objective Space: Cooling and Comfort")
        plt.xlabel("Cooling demand [kWh m\u207b\u00B2]")
        plt.ylabel("Annual average PPD [%]")
        plt.savefig(thisSimulationResultsFolder + '/ShoeboxFixedParameters_CoolingComfort.png')
    
        plt.figure(figsize=(7, 5))
        plt.scatter(annualCoolingFixed, NPVFixed, s=20, c='red', marker='.')
        plt.title("Objective Space: Cooling and Net Present Value")
        plt.xlabel("Cooling demand [kWh m\u207b\u00B2]")
        plt.ylabel("Net Present Value [€]")
        plt.savefig(thisSimulationResultsFolder + '/ShoeboxFixedParameters_CoolingNPV.png')
    
        plt.figure(figsize=(7, 5))
        plt.scatter(meanPPDFixed, NPVFixed, s=20, c='red', marker='.')
        plt.title("Objective Space: Comfort and Net Present Value")
        plt.xlabel("Annual average PPD [%]")
        plt.ylabel("Net Present Value [€]")
        plt.savefig(thisSimulationResultsFolder + '/ShoeboxFixedParameters_ComfortNPV.png')
    
        np.savetxt(thisSimulationResultsFolder + "/FixedSimulation_Outputs.csv", fixedSimulationResults, delimiter=",")

    return variablesNumber
