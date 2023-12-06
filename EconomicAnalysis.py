# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 16:20:50 2022

@author: FBattini
"""
def economicAnalysis(resultsDF, currentPath, thisSimulationFolderPath, idf1, insulationIndex, glazingIndex, insulationThickness):
    import pandas as pd
    buildingInputsDF = pd.read_csv(thisSimulationFolderPath + '/BuildingInputs.csv', index_col = 0)
    glazingMaterialsDF = pd.read_csv(currentPath + '/SimulationFiles/Glazing-material.csv')
    insulationMaterialsDF = pd.read_csv(currentPath + '/SimulationFiles/Insulation-material.csv')
    insulationCost, glazingCost = buildingInputsDF.loc[0,'Insulation cost'], buildingInputsDF.loc[0,'Glazing cost']
    insulationPosition = buildingInputsDF.loc[0,'Insulation position']
    heatingLoad = resultsDF.iloc[:,1].sum()/3600000
    coolingLoad = resultsDF.iloc[:,2].sum()/3600000
    
    ''' Prametri di input assunti costanti '''
    dr     = 0.03      # dr   é il discount rate; 
    hh     = 9.09      # hh   é il potere calorifico del GAS [kW/Sm3]
    hc     = buildingInputsDF.loc[0,'Natural gas price']       # hc   é il costo del gas [EUR/Sm3]
    icg    = 0.028     # icg  é l'incremento annuo del costo del GAS
    elc    = buildingInputsDF.loc[0,'Electricity price']       # elc   é il costo dell'energia elettrica [EUR/kWhe]
    icel   = 0.0171    # icel  é l'incremento annuo del costo dell'elettricitá
    
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
    
    if insulationThickness == 1/100000:
        insulationThickness = 0
    
    if insulationCost == "No" or insulationThickness == 0 or insulationPosition == "Non insulated":
        ICe = 0
    elif insulationCost == "Yes":
            ICe = (insulationMaterialCostIncrease[insulationIndex]*insulationThickness + insulationMaterialCostBase[insulationIndex])*envelopeArea
        
    if glazingCost == "No":
        ICw = 0
    elif glazingCost == "Yes":
        ICw = glazingMaterialPrices[glazingIndex]*windowsArea
    ''' Costo di investimento complessivo '''
    IC = ICe + ICw
    
    ''' COSTI DI ESERCIZIO '''
    tG = ((1 + dr) / (1 + icg)) - 1                 # tG   é il tasso libero di crescita del gas
    GCy = ((heatingLoad*hc)/ hh) * (1 + icg)        # GCy  é il costo per il Gas in un anno
    GC =  (GCy / (1 + icg)) * (1 /(1 + tG) + 1/(1+tG)**2 + 1/(1+tG)**3 + 1/(1+tG)**4 + 1/(1+tG)**5 + 1/(1+tG)**6 + 1/(1+tG)**7 + 1/(1+tG)**8+ 1/(1+tG)**9 + 1/(1+tG)**10 + 1/(1+tG)**11 + 1/(1+tG)**12 + 1/(1+tG)**13 + 1/(1+tG)**14 + 1/(1+tG)**15 + 1/(1+tG)**16 + 1/(1+tG)**17 + 1/(1+tG)**18 + 1/(1+tG)**19 + 1/(1+tG)**20 + 1/(1+tG)**21 + 1/(1+tG)**22 + 1/(1+tG)**23 + 1/(1+tG)**24 + 1/(1+tG)**25 + 1/(1+tG)**26 + 1/(1+tG)**27 + 1/(1+tG)**28 + 1/(1+tG)**29 + 1/(1+tG)**30)
    
    tEl = ((1 + dr) / (1 + icel)) - 1 
    ElCy = (coolingLoad * elc) * (1 + icel)
    ElC = (ElCy / (1 + icel)) * (1 /(1 + tEl) + 1/(1+tEl)**2 + 1/(1+tEl)**3 + 1/(1+tEl)**4 + 1/(1+tEl)**5 + 1/(1+tEl)**6 + 1/(1+tEl)**7 + 1/(1+tEl)**8 + 1/(1+tEl)**9 + 1/(1+tEl)**10 + 1/(1+tEl)**11 + 1/(1+tEl)**12 + 1/(1+tEl)**13 + 1/(1+tEl)**14 + 1/(1+tEl)**15 + 1/(1+tEl)**16 + 1/(1+tEl)**17 + 1/(1+tEl)**18 + 1/(1+tEl)**19 + 1/(1+tEl)**20 + 1/(1+tEl)**21 + 1/(1+tEl)**22 + 1/(1+tEl)**23 + 1/(1+tEl)**24 + 1/(1+tEl)**25 + 1/(1+tEl)**26 + 1/(1+tEl)**27 + 1/(1+tEl)**28 + 1/(1+tEl)**29 + 1/(1+tEl)**30)
   
    ''' Costi di esercizio complessivi '''
    ExC = GC + ElC
    ''' VALORE ATTUALE NETTO NPV '''
    NPV = IC + ExC
    return NPV, IC