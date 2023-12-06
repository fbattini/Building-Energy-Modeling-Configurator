# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 16:20:50 2022

@author: FBattini
"""
def investmentCost(currentPath, simulationName):
    
    import sys
    import pandas as pd
    from eppy.modeleditor import IDF
    # define eppy parameters
    eppy_path = "C:/Anaconda3/Lib/site-packages/eppy"
    sys.path.append(eppy_path)
    iddfile = "C:/EnergyPlusV9-4-0/Energy+.idd"
    thisSimulationFolderPath = currentPath + '/Simulations/' + simulationName
    fname1 = thisSimulationFolderPath + "/ShoeboxFixedParameters.idf"
    IDF.setiddname(iddfile)
    idf1 = IDF(fname1)
        
    buildingInputsDF = pd.read_csv(thisSimulationFolderPath + '/BuildingInputs.csv', index_col = 0)
    glazingMaterialsDF = pd.read_csv(currentPath + '/SimulationFiles/Glazing-material.csv')
    insulationMaterialsDF = pd.read_csv(currentPath + '/SimulationFiles/Insulation-material.csv')
    paretoInputsDF = pd.read_csv(thisSimulationFolderPath + '/Results/Pareto_Inputs.csv', index_col = 0)
    paretoInputsDF.dropna(axis='columns', inplace=True)
    insulationCost, glazingCost = buildingInputsDF.loc[0,'Insulation cost'], buildingInputsDF.loc[0,'Glazing cost']
    insulationPosition, insulationThicknessFixed, insulationMaterialFixed = buildingInputsDF.loc[0,'Insulation position'], buildingInputsDF.loc[0,'Ins thickness'], buildingInputsDF.loc[0,'Fixed insulation index']
    glazingFixed = buildingInputsDF.loc[0,'Fixed glazing index']
    glazingMaterials = glazingMaterialsDF.loc[:,"Material"]
    
    glazingMaterialPrices = glazingMaterialsDF.loc[:,"Price"]
    insulationMaterialCostBase = insulationMaterialsDF.loc[:,"Cost base"]
    insulationMaterialCostIncrease = insulationMaterialsDF.loc[:,"Cost increase"]
    
    surfaces = idf1.idfobjects["BuildingSurface:Detailed"]
    envelopeArea = 0
    for surface in surfaces:
        if surface.Surface_Type == 'WALL' and surface.Outside_Boundary_Condition == 'Outdoors':
            envelopeArea += surface.area
        if surface.Surface_Type == 'FLOOR' and surface.Outside_Boundary_Condition == 'Ground':
            envelopeArea += surface.area 
        if surface.Surface_Type == 'ROOF' and surface.Outside_Boundary_Condition == 'Outdoors':
            envelopeArea += surface.area
    
    windows = idf1.idfobjects["FenestrationSurface:Detailed"]
    windowsArea = 0
    for window in windows:
        windowsArea += window.area
        
    ICs = []
    for ind in paretoInputsDF.index:
        if insulationCost == "No" or insulationPosition == "Non insulated":
            ICe = 0
        elif insulationCost == "Yes" and insulationPosition != "Non insulated":
            if 'Insulation material' in paretoInputsDF.columns:
                insulationIndex = int(paretoInputsDF['Insulation material'][ind])
            else:
                insulationIndex = int(insulationMaterialFixed)
            if 'Insulation thickness' in paretoInputsDF.columns:
                insulationThickness = paretoInputsDF['Insulation thickness'][ind]/100
            else:
                insulationThickness = insulationThicknessFixed/100
            
            if insulationThickness == 1/100000:
                insulationThickness = 0
            
            ICe = (insulationMaterialCostIncrease[insulationIndex]*insulationThickness + insulationMaterialCostBase[insulationIndex])*envelopeArea
            if insulationThickness == 0:
                ICe = 0
                
        if glazingCost == "No":
            ICw = 0
        elif glazingCost == "Yes":
            if 'Windows' in paretoInputsDF.columns:
                glazingIndex = int(paretoInputsDF['Windows'][ind])
            else:
                glazingIndex = int(glazingMaterials[glazingMaterials == glazingFixed].index[0])
                
            ICw = glazingMaterialPrices[glazingIndex]*windowsArea
        
        ''' Costo di investimento complessivo '''
        IC = ICe + ICw
        ICs.append(IC)
    return ICs