# -*- coding: utf-8 -*-
"""
Created on Tue Jan 04 18:24:51 2021

@author: FBattini
"""

def createIDF(currentPath, simulationName):
    
    import os
    import sys
    import math
    import numpy as np
    import pandas as pd
    from eppy.modeleditor import IDF
    # define eppy parameters
    eppy_path = "C:/Anaconda3/Lib/site-packages/eppy"
    sys.path.append(eppy_path)
    iddfile = "C:/EnergyPlusV9-4-0/Energy+.idd"
    simulationFilesFolderPath = currentPath + "/SimulationFiles"
    thisSimulationFolderPath = currentPath + '/Simulations/' + simulationName
    thisSimulationResultsFolder = thisSimulationFolderPath + '/Results'
    if not os.path.exists(thisSimulationResultsFolder):
        os.mkdir(thisSimulationResultsFolder)
    buildingInputsDF = pd.read_csv(thisSimulationFolderPath + '/BuildingInputs.csv', index_col = 0)
    # get all building inputs
    weatherFile = buildingInputsDF.loc[0,'Weather file']
    height = buildingInputsDF.loc[0,'Height']
    adiabaticS, adiabaticW, adiabaticN, adiabaticE, adiabaticF, adiabaticR = buildingInputsDF.loc[0,'adiabaticS'], buildingInputsDF.loc[0,'adiabaticW'], buildingInputsDF.loc[0,'adiabaticN'], buildingInputsDF.loc[0,'adiabaticE'], buildingInputsDF.loc[0,'adiabaticF'], buildingInputsDF.loc[0,'adiabaticR']
    width, depth = buildingInputsDF.loc[0,'Width'], buildingInputsDF.loc[0,'Depth']
    WWRS, WWRW, WWRN, WWRE = buildingInputsDF.loc[0,'WWRS'], buildingInputsDF.loc[0,'WWRW'], buildingInputsDF.loc[0,'WWRN'], buildingInputsDF.loc[0,'WWRE']
    massiveIndex, massiveThick = buildingInputsDF.loc[0,'Massive index'], buildingInputsDF.loc[0,'Massive thickness']
    insulationPosition, insulationOptimization, insulationFixed, insulationOpt1, insulationOpt2 = buildingInputsDF.loc[0,'Insulation position'], buildingInputsDF.loc[0,'Ins optimization'], buildingInputsDF.loc[0,'Fixed insulation index'], buildingInputsDF.loc[0,'Optimized insulation index1'], buildingInputsDF.loc[0,'Optimized insulation index2']
    insulationThickOptimization, insulationThick, insulationMinThick, insulationMaxThick, insulationMStepThick = buildingInputsDF.loc[0,'Ins thick optimization'], buildingInputsDF.loc[0,'Ins thickness'], buildingInputsDF.loc[0,'Min ins thickness'], buildingInputsDF.loc[0,'Max ins thickness'], buildingInputsDF.loc[0,'Step ins thickness']
    insulationCost = buildingInputsDF.loc[0,'Insulation cost']
    glazingOptimization, glazingFixed, glazingOpt1, glazingOpt2 = buildingInputsDF.loc[0,'Glazing optimization'], buildingInputsDF.loc[0,'Fixed glazing index'], buildingInputsDF.loc[0,'Optimized glazing index1'], buildingInputsDF.loc[0,'Optimized glazing index2']
    gains, met, clo, ventilation, internalMass = buildingInputsDF.loc[0,'Gains'], buildingInputsDF.loc[0,'Met'], buildingInputsDF.loc[0,'Clo'], buildingInputsDF.loc[0,'Ventilation'], buildingInputsDF.loc[0,'Internal mass']
    heatingSetpoint = buildingInputsDF.loc[0,'Heating setpoint']
    coolingSetpoint = buildingInputsDF.loc[0,'Cooling setpoint']
    heatingSetback = buildingInputsDF.loc[0,'Heating setback']
    coolingSetback = buildingInputsDF.loc[0,'Cooling setback']
    heatingSetbackStart = buildingInputsDF.loc[0,'Heating setback start']
    heatingSetbackFinish = buildingInputsDF.loc[0,'Heating setback finish']
    coolingSetbackStart = buildingInputsDF.loc[0,'Cooling setback start']
    coolingSetbackFinish = buildingInputsDF.loc[0,'Cooling setback finish']
    heatingSeasonStartMonth = buildingInputsDF.loc[0,'Heating season start month']
    heatingSeasonStartDay = buildingInputsDF.loc[0,'Heating season start day']
    heatingSeasonEndMonth = buildingInputsDF.loc[0,'Heating season end month']
    heatingSeasonEndDay = buildingInputsDF.loc[0,'Heating season end day']  
    coolingSeasonStartMonth = buildingInputsDF.loc[0,'Cooling season start month']
    coolingSeasonStartDay = buildingInputsDF.loc[0,'Cooling season start day']
    coolingSeasonEndMonth = buildingInputsDF.loc[0,'Cooling season end month']
    coolingSeasonEndDay = buildingInputsDF.loc[0,'Cooling season end day']
    shadingPresence = buildingInputsDF.loc[0,'Shading presence']
    shadingSetpoint = buildingInputsDF.loc[0,'Shading setpoint']

    fname1 = simulationFilesFolderPath + "/ShoeboxBaseModel.idf"
    IDF.setiddname(iddfile)
    idf1 = IDF(fname1)

    """ Envelope characterization """
    # compute adiabatic and non-adiabatic lengths
    width_adS, depth_adW, width_adN, depth_adE, depth_adR, depth_adF = width*adiabaticS, depth*adiabaticW, width*adiabaticN, depth*adiabaticE, depth*adiabaticR, depth*adiabaticF
    width_nonadS, depth_nonadW, width_nonadN, depth_nonadE, depth_nonadR, depth_nonadF = width - width_adS , depth - depth_adW , width - width_adN  , depth - depth_adE, depth - depth_adR, depth - depth_adF
    
    '''Different adiabatic and non adiabatic length for the orientations'''
    # adiabatic lengths
    widthAdS = width*adiabaticS    #South
    depthAdW = depth*adiabaticW    #West   
    widthAdN = width*adiabaticN    #North   
    depthAdE = depth*adiabaticE    #East
    depthAdR = depth*adiabaticR    #Roof
    depthAdF = depth*adiabaticF    #Floor
    # non-adiabatic lengths
    widthNonadS = width - widthAdS    #South
    depthNonadW = depth - depthAdW    #West   
    widthNonadN = width - widthAdN    #North   
    depthNonadE = depth - depthAdE    #East
    depthNonadR = depth - depthAdR    #Roof
    depthNonadF = depth - depthAdF    #Floor
    
    """ Size surfaces -> order to not have problems when deleting objects """
    surfaces = idf1.idfobjects["BuildingSurface:Detailed"]
    ''' Roof sizing -> from TOP counterclock-wise top-right corner nonAd, counterclockwise bottom-left corner Ad'''
    # Non adiabatic                                                                                   
    roofNonad = surfaces[11]                                                                         
    roofNewX = [width, 0, 0, width]
    roofNewY = [depthNonadR, depthNonadR, 0, 0]
    roofNonad.Vertex_1_Xcoordinate, roofNonad.Vertex_1_Ycoordinate, roofNonad.Vertex_1_Zcoordinate = roofNewX[0], roofNewY[0], height
    roofNonad.Vertex_2_Xcoordinate, roofNonad.Vertex_2_Ycoordinate, roofNonad.Vertex_2_Zcoordinate = roofNewX[1], roofNewY[1], height
    roofNonad.Vertex_3_Xcoordinate, roofNonad.Vertex_3_Ycoordinate, roofNonad.Vertex_3_Zcoordinate = roofNewX[2], roofNewY[2], height
    roofNonad.Vertex_4_Xcoordinate, roofNonad.Vertex_4_Ycoordinate, roofNonad.Vertex_4_Zcoordinate = roofNewX[3], roofNewY[3], height
    # Adiabatic
    roofAd = surfaces[10]
    roofAdNewX = [0, width, width, 0]
    roofAdNewY = [depthNonadR, depthNonadR, depth, depth]
    roofAd.Vertex_1_Xcoordinate, roofAd.Vertex_1_Ycoordinate, roofAd.Vertex_1_Zcoordinate = roofAdNewX[0], roofAdNewY[0], height
    roofAd.Vertex_2_Xcoordinate, roofAd.Vertex_2_Ycoordinate, roofAd.Vertex_2_Zcoordinate = roofAdNewX[1], roofAdNewY[1], height
    roofAd.Vertex_3_Xcoordinate, roofAd.Vertex_3_Ycoordinate, roofAd.Vertex_3_Zcoordinate = roofAdNewX[2], roofAdNewY[2], height 
    roofAd.Vertex_4_Xcoordinate, roofAd.Vertex_4_Ycoordinate, roofAd.Vertex_4_Zcoordinate = roofAdNewX[3], roofAdNewY[3], height 
    if adiabaticR == 0:
        idf1.removeidfobject(surfaces[10])
    if adiabaticR == 1:
        idf1.removeidfobject(surfaces[11])
    ''' Floor sizing -> from TOP counterclock-wise bottom-right corner for bath nonAd and Ad '''
    # Non adiabatic
    floorNonad = surfaces[9]
    floorNewX = [width, 0, 0, width]
    floorNewY = [0, 0, depthNonadF, depthNonadF]
    floorNonad.Vertex_1_Xcoordinate, floorNonad.Vertex_1_Ycoordinate = floorNewX[0], floorNewY[0]
    floorNonad.Vertex_2_Xcoordinate, floorNonad.Vertex_2_Ycoordinate = floorNewX[1], floorNewY[1]
    floorNonad.Vertex_3_Xcoordinate, floorNonad.Vertex_3_Ycoordinate = floorNewX[2], floorNewY[2]
    floorNonad.Vertex_4_Xcoordinate, floorNonad.Vertex_4_Ycoordinate = floorNewX[3], floorNewY[3]
    # Adiabatic
    floorAd = surfaces[8]
    floorAdNewX = [width, 0, 0, width]
    floorAdNewY = [depthNonadF, depthNonadF, depth, depth]
    floorAd.Vertex_1_Xcoordinate, floorAd.Vertex_1_Ycoordinate = floorAdNewX[0], floorAdNewY[0]
    floorAd.Vertex_2_Xcoordinate, floorAd.Vertex_2_Ycoordinate = floorAdNewX[1], floorAdNewY[1]
    floorAd.Vertex_3_Xcoordinate, floorAd.Vertex_3_Ycoordinate = floorAdNewX[2], floorAdNewY[2]
    floorAd.Vertex_4_Xcoordinate, floorAd.Vertex_4_Ycoordinate = floorAdNewX[3], floorAdNewY[3]
    if adiabaticF == 0:
        idf1.removeidfobject(surfaces[8])
    if adiabaticF == 1:
        idf1.removeidfobject(surfaces[9])
    ''' East Wall sizing -> from FRONT counterclock-wise top-left corner nonAd and Ad'''
    # Non adiabatic                                                                                  
    eastNonad = surfaces[6]      
    eastNewY = [0, 0, depthNonadE, depthNonadE]
    eastNonad.Vertex_1_Xcoordinate, eastNonad.Vertex_1_Ycoordinate, eastNonad.Vertex_1_Zcoordinate = width, eastNewY[0], height
    eastNonad.Vertex_2_Xcoordinate, eastNonad.Vertex_2_Ycoordinate =  width, eastNewY[1]
    eastNonad.Vertex_3_Xcoordinate, eastNonad.Vertex_3_Ycoordinate =  width, eastNewY[2] 
    eastNonad.Vertex_4_Xcoordinate, eastNonad.Vertex_4_Ycoordinate, eastNonad.Vertex_4_Zcoordinate = width, eastNewY[3], height 
    # Adiabatic
    eastAd = surfaces[7]
    eastAdNewY = [depthNonadE, depthNonadE, depth, depth]
    eastAd.Vertex_1_Xcoordinate, eastAd.Vertex_1_Ycoordinate, eastAd.Vertex_1_Zcoordinate = width, eastAdNewY[0], height
    eastAd.Vertex_2_Xcoordinate, eastAd.Vertex_2_Ycoordinate = width, eastAdNewY[1]
    eastAd.Vertex_3_Xcoordinate, eastAd.Vertex_3_Ycoordinate = width, eastAdNewY[2]
    eastAd.Vertex_4_Xcoordinate, eastAd.Vertex_4_Ycoordinate, eastAd.Vertex_4_Zcoordinate = width, eastAdNewY[3], height
    if adiabaticE == 0:
        idf1.removeidfobject(surfaces[7])
    if adiabaticE == 1:
        idf1.removeidfobject(surfaces[6])
    ''' North Wall sizing -> from FRONT counterclock-wise top-left corner nonAd and Ad''' 
    # Non adiabatic                                                                                     
    northNonad = surfaces[4]
    northNewX = [width, width, widthAdN, widthAdN]
    northNonad.Vertex_1_Xcoordinate, northNonad.Vertex_1_Ycoordinate, northNonad.Vertex_1_Zcoordinate = northNewX[0], depth, height
    northNonad.Vertex_2_Xcoordinate, northNonad.Vertex_2_Ycoordinate = northNewX[1], depth
    northNonad.Vertex_3_Xcoordinate, northNonad.Vertex_3_Ycoordinate = northNewX[2], depth
    northNonad.Vertex_4_Xcoordinate, northNonad.Vertex_4_Ycoordinate, northNonad.Vertex_4_Zcoordinate = northNewX[3], depth, height
    # Adiabatic
    northAd = surfaces[5]
    northAdNewX = [widthAdN, widthAdN, 0, 0]
    northAd.Vertex_1_Xcoordinate, northAd.Vertex_1_Ycoordinate, northAd.Vertex_1_Zcoordinate = northAdNewX[0], depth, height
    northAd.Vertex_2_Xcoordinate, northAd.Vertex_2_Ycoordinate = northAdNewX[1], depth
    northAd.Vertex_3_Xcoordinate, northAd.Vertex_3_Ycoordinate = northAdNewX[2], depth
    northAd.Vertex_4_Xcoordinate, northAd.Vertex_4_Ycoordinate, northAd.Vertex_4_Zcoordinate = northAdNewX[3], depth, height
    if adiabaticN == 0:
        idf1.removeidfobject(surfaces[5])
    if adiabaticN == 1:
        idf1.removeidfobject(surfaces[4])
    ''' West Wall sizing -> from FRONT counterclock-wise top-left corner nonAd and Ad'''
    # Non adiabatic                                                                                     
    westNonad = surfaces[2]
    westNewY = [depth, depth, depthAdW, depthAdW]       
    westNonad.Vertex_1_Ycoordinate, westNonad.Vertex_1_Zcoordinate = westNewY[0], height
    westNonad.Vertex_2_Ycoordinate = westNewY[1]
    westNonad.Vertex_3_Ycoordinate = westNewY[2]
    westNonad.Vertex_4_Ycoordinate, westNonad.Vertex_4_Zcoordinate = westNewY[3], height
    # Adiabatic
    westAd = surfaces[3]
    westAdNewY = [depthAdW, depthAdW, 0, 0]  
    westAd.Vertex_1_Ycoordinate, westAd.Vertex_1_Zcoordinate = westAdNewY[0], height
    westAd.Vertex_2_Ycoordinate = westAdNewY[1]
    westAd.Vertex_3_Ycoordinate = westAdNewY[2]
    westAd.Vertex_4_Ycoordinate, westAd.Vertex_4_Zcoordinate = westAdNewY[3], height
    if adiabaticW == 0:
        idf1.removeidfobject(surfaces[3])
    if adiabaticW == 1:
        idf1.removeidfobject(surfaces[2]) 
    ''' South Wall sizing -> from FRONT counterclock-wise top-left corner nonAd and Ad'''
    # Non adiabatic                                                                                   
    southNonad = surfaces[0]     
    southNewX = [0, 0, widthNonadS, widthNonadS]                                                                    
    southNonad.Vertex_1_Xcoordinate, southNonad.Vertex_1_Zcoordinate = southNewX[0], height
    southNonad.Vertex_2_Xcoordinate = southNewX[1]
    southNonad.Vertex_3_Xcoordinate = southNewX[2]
    southNonad.Vertex_4_Xcoordinate, southNonad.Vertex_4_Zcoordinate = southNewX[3], height
    # Adiabatic
    southAd = surfaces[1]
    southAdNewX = [widthNonadS, widthNonadS, width, width]      
    southAd.Vertex_1_Xcoordinate, southAd.Vertex_1_Zcoordinate = southAdNewX[0], height
    southAd.Vertex_2_Xcoordinate = southAdNewX[1]
    southAd.Vertex_3_Xcoordinate = southAdNewX[2]
    southAd.Vertex_4_Xcoordinate, southAd.Vertex_4_Zcoordinate = southAdNewX[3], height
    if adiabaticS == 0:
        idf1.removeidfobject(surfaces[1])
    if adiabaticS == 1:
        idf1.removeidfobject(surfaces[0])
    
    ''' Window sizing -> order to avoid problems when deleting windows objects'''
    windows = idf1.idfobjects["FenestrationSurface:Detailed"]
    ''' East Window '''
    if not (WWRE == 0 or adiabaticE == 1):
        # Find window's points
        y_array = np.array([eastNonad.Vertex_1_Ycoordinate, eastNonad.Vertex_2_Ycoordinate, eastNonad.Vertex_3_Ycoordinate, eastNonad.Vertex_4_Ycoordinate])
        z_array = np.array([eastNonad.Vertex_1_Zcoordinate, eastNonad.Vertex_2_Zcoordinate, eastNonad.Vertex_3_Zcoordinate, eastNonad.Vertex_4_Zcoordinate])
        ymax, zmax = np.max(y_array), np.max(z_array)
        ymin, zmin = np.min(y_array), np.min(z_array)
        wall_area = (ymax-ymin)*(zmax-zmin)
        centery, centerz = ymin + (ymax-ymin)/2, zmin + (zmax-zmin)/2
        window_area = WWRE*wall_area
        findarea = window_area/wall_area
        findlength = math.sqrt(findarea)
        base_window = findlength*(ymax-ymin)
        height_window = findlength*(zmax-zmin)
        window_y1, window_z1 = centery - base_window/2, centerz - height_window/2
        window_y2, window_z2 = window_y1 + base_window, window_z1
        window_y3, window_z3 = window_y2, window_z1 + height_window
        window_y4, window_z4 = window_y1, window_z3
        east_windowy = np.array([window_y1, window_y2, window_y3, window_y4])
        east_windowz = np.array([window_z1, window_z2, window_z3, window_z4])
        # Write on idf file
        east_window = windows[3]
        east_window.Vertex_1_Xcoordinate, east_window.Vertex_1_Ycoordinate, east_window.Vertex_1_Zcoordinate = width, east_windowy[0], east_windowz[0]
        east_window.Vertex_2_Xcoordinate, east_window.Vertex_2_Ycoordinate, east_window.Vertex_2_Zcoordinate = width, east_windowy[1], east_windowz[1]
        east_window.Vertex_3_Xcoordinate, east_window.Vertex_3_Ycoordinate, east_window.Vertex_3_Zcoordinate = width, east_windowy[2], east_windowz[2]
        east_window.Vertex_4_Xcoordinate, east_window.Vertex_4_Ycoordinate, east_window.Vertex_4_Zcoordinate = width, east_windowy[3], east_windowz[3]
    else:
        idf1.removeidfobject(windows[3])
    ''' North Window '''
    if not (WWRN == 0 or adiabaticN == 1):
        # Find window's points
        x_array = np.array([northNonad.Vertex_1_Xcoordinate, northNonad.Vertex_2_Xcoordinate, northNonad.Vertex_3_Xcoordinate, northNonad.Vertex_4_Xcoordinate])
        z_array = np.array([northNonad.Vertex_1_Zcoordinate, northNonad.Vertex_2_Zcoordinate, northNonad.Vertex_3_Zcoordinate, northNonad.Vertex_4_Zcoordinate])
        xmax, zmax = np.max(x_array), np.max(z_array)
        xmin, zmin = np.min(x_array), np.min(z_array)
        wall_area = (xmax-xmin)*(zmax-zmin)
        centerx, centerz = xmin + (xmax-xmin)/2, zmin + (zmax-zmin)/2
        window_area = WWRN*wall_area
        findarea = window_area/wall_area
        findlength = math.sqrt(findarea)
        base_window = findlength*(xmax-xmin)
        height_window = findlength*(zmax-zmin)
        window_x1, window_z1 = centerx - base_window/2, centerz - height_window/2
        window_x2, window_z2 = window_x1 + base_window, window_z1
        window_x3, window_z3 = window_x2, window_z1 + height_window
        window_x4, window_z4 = window_x1, window_z3
        north_windowx = np.array([window_x1, window_x2, window_x3, window_x4])
        north_windowz = np.array([window_z1, window_z2, window_z3, window_z4])
        # Write on idf file
        north_window = windows[2]
        north_window.Vertex_1_Xcoordinate, north_window.Vertex_1_Ycoordinate, north_window.Vertex_1_Zcoordinate = north_windowx[0], depth, north_windowz[0]
        north_window.Vertex_2_Xcoordinate, north_window.Vertex_2_Ycoordinate, north_window.Vertex_2_Zcoordinate = north_windowx[3], depth, north_windowz[3]
        north_window.Vertex_3_Xcoordinate, north_window.Vertex_3_Ycoordinate, north_window.Vertex_3_Zcoordinate = north_windowx[2], depth, north_windowz[2]
        north_window.Vertex_4_Xcoordinate, north_window.Vertex_4_Ycoordinate, north_window.Vertex_4_Zcoordinate = north_windowx[1], depth, north_windowz[1]
    else:
        idf1.removeidfobject(windows[2])
    ''' West Window '''
    if not (WWRW == 0 or adiabaticW == 1):
        # Find window's points
        y_array = np.array([westNonad.Vertex_1_Ycoordinate, westNonad.Vertex_2_Ycoordinate, westNonad.Vertex_3_Ycoordinate, westNonad.Vertex_4_Ycoordinate])
        z_array = np.array([westNonad.Vertex_1_Zcoordinate, westNonad.Vertex_2_Zcoordinate, westNonad.Vertex_3_Zcoordinate, westNonad.Vertex_4_Zcoordinate])
        ymax, zmax = np.max(y_array), np.max(z_array)
        ymin, zmin = np.min(y_array), np.min(z_array)
        wall_area = (ymax-ymin)*(zmax-zmin)
        centery, centerz = ymin + (ymax-ymin)/2, zmin + (zmax-zmin)/2
        window_area = WWRW*wall_area
        findarea = window_area/wall_area
        findlength = math.sqrt(findarea)
        base_window = findlength*(ymax-ymin)
        height_window = findlength*(zmax-zmin)
        window_y1, window_z1 = centery - base_window/2, centerz - height_window/2
        window_y2, window_z2 = window_y1 + base_window, window_z1
        window_y3, window_z3 = window_y2, window_z1 + height_window
        window_y4, window_z4 = window_y1, window_z3
        west_windowy = np.array([window_y1, window_y2, window_y3, window_y4])
        west_windowz = np.array([window_z1, window_z2, window_z3, window_z4])
        # Write on idf file
        west_window = windows[1]
        west_window.Vertex_1_Ycoordinate, west_window.Vertex_1_Zcoordinate = west_windowy[0], west_windowz[0]
        west_window.Vertex_2_Ycoordinate, west_window.Vertex_2_Zcoordinate = west_windowy[3], west_windowz[3]
        west_window.Vertex_3_Ycoordinate, west_window.Vertex_3_Zcoordinate = west_windowy[2], west_windowz[2]
        west_window.Vertex_4_Ycoordinate, west_window.Vertex_4_Zcoordinate = west_windowy[1], west_windowz[1]
    else:
        idf1.removeidfobject(windows[1])
    ''' South Window '''
    if not (WWRS == 0 or adiabaticS == 1):
        # Find window's points
        x_array = np.array([southNonad.Vertex_1_Xcoordinate, southNonad.Vertex_2_Xcoordinate, southNonad.Vertex_3_Xcoordinate, southNonad.Vertex_4_Xcoordinate])
        z_array = np.array([southNonad.Vertex_1_Zcoordinate, southNonad.Vertex_2_Zcoordinate, southNonad.Vertex_3_Zcoordinate, southNonad.Vertex_4_Zcoordinate])
        xmax, zmax = np.max(x_array), np.max(z_array)
        xmin, zmin = np.min(x_array), np.min(z_array)
        wall_area = (xmax-xmin)*(zmax-zmin)
        centerx, centerz = xmin + (xmax-xmin)/2, zmin + (zmax-zmin)/2
        window_area = WWRS*wall_area
        findarea = window_area/wall_area
        findlength = math.sqrt(findarea)
        base_window = findlength*(xmax-xmin)
        height_window = findlength*(zmax-zmin)
        window_x1, window_z1 = centerx - base_window/2, centerz - height_window/2
        window_x2, window_z2 = window_x1 + base_window, window_z1
        window_x3, window_z3 = window_x2 , window_z1 + height_window
        window_x4, window_z4 = window_x1, window_z3
        south_windowx = np.array([window_x1, window_x2, window_x3, window_x4])
        south_windowz = np.array([window_z1, window_z2, window_z3, window_z4])
        # Write on idf file
        south_window = windows[0]
        south_window.Vertex_1_Xcoordinate, south_window.Vertex_1_Zcoordinate = south_windowx[0], south_windowz[0]
        south_window.Vertex_2_Xcoordinate, south_window.Vertex_2_Zcoordinate = south_windowx[1], south_windowz[1]
        south_window.Vertex_3_Xcoordinate, south_window.Vertex_3_Zcoordinate = south_windowx[2], south_windowz[2]
        south_window.Vertex_4_Xcoordinate, south_window.Vertex_4_Zcoordinate = south_windowx[3], south_windowz[3]
    else:
        idf1.removeidfobject(windows[0])
    
#%% Setpoint
    scheduleCompact = idf1.idfobjects["Schedule:Compact"]
    
    scheduleCompact[0].Field_6 = heatingSetpoint
    scheduleCompact[0].Field_14 = heatingSetpoint
    scheduleCompact[0].Field_22 = heatingSetpoint
    
    if heatingSetback != "No":
        scheduleCompact[0].Field_4 = scheduleCompact[0].Field_8 = heatingSetback
        scheduleCompact[0].Field_12 = scheduleCompact[0].Field_16 = heatingSetback
        scheduleCompact[0].Field_20 = scheduleCompact[0].Field_24 = heatingSetback
        
        scheduleCompact[0].Field_3 = scheduleCompact[0].Field_11 = scheduleCompact[0].Field_19 = "Until: {:02d}:00".format(heatingSetbackFinish)
        scheduleCompact[0].Field_5 = scheduleCompact[0].Field_13 = scheduleCompact[0].Field_21 = "Until: {:02d}:00".format(heatingSetbackStart)
    else:
        scheduleCompact[0].Field_4 = scheduleCompact[0].Field_8 = heatingSetpoint
        scheduleCompact[0].Field_12 = scheduleCompact[0].Field_16 = heatingSetpoint
        scheduleCompact[0].Field_20 = scheduleCompact[0].Field_24 = heatingSetpoint
    
    if heatingSeasonStartMonth and heatingSeasonStartDay and heatingSeasonEndMonth and heatingSeasonEndDay != "On":
        scheduleCompact[0].Field_1 = "Through: {:02d}/{:02d}".format(heatingSeasonEndMonth, heatingSeasonEndDay)
        scheduleCompact[0].Field_9 = "Through: {:02d}/{:02d}".format(heatingSeasonStartMonth, heatingSeasonStartDay)
        scheduleCompact[0].Field_12 = scheduleCompact[0].Field_14 = scheduleCompact[0].Field_16 = 5

    scheduleCompact[7].Field_6 = coolingSetpoint
    scheduleCompact[7].Field_14 = coolingSetpoint
    scheduleCompact[7].Field_22 = coolingSetpoint
       
    if coolingSetback != "No":
        scheduleCompact[7].Field_4 = scheduleCompact[7].Field_8 = coolingSetback
        scheduleCompact[7].Field_12 = scheduleCompact[7].Field_16 = coolingSetback
        scheduleCompact[7].Field_20 = scheduleCompact[7].Field_24 = coolingSetback
        
        scheduleCompact[7].Field_3 = scheduleCompact[7].Field_11 = scheduleCompact[7].Field_19 = "Until: {:02d}:00".format(coolingSetbackFinish)
        scheduleCompact[7].Field_5 = scheduleCompact[7].Field_13 = scheduleCompact[7].Field_21 = "Until: {:02d}:00".format(coolingSetbackStart)
    else:
        scheduleCompact[7].Field_4 = scheduleCompact[7].Field_8 = coolingSetpoint
        scheduleCompact[7].Field_12 = scheduleCompact[7].Field_16 = coolingSetpoint
        scheduleCompact[7].Field_20 = scheduleCompact[7].Field_24 = coolingSetpoint
    
    if coolingSeasonStartMonth and coolingSeasonStartDay and coolingSeasonEndMonth and coolingSeasonEndDay != "On":
        scheduleCompact[7].Field_1 = "Through: {:02d}/{:02d}".format(coolingSeasonStartMonth, coolingSeasonStartDay)
        scheduleCompact[7].Field_9 = "Through: {:02d}/{:02d}".format(coolingSeasonEndMonth, coolingSeasonEndDay)
        scheduleCompact[7].Field_4 = scheduleCompact[7].Field_6 = scheduleCompact[7].Field_8 = 50
        scheduleCompact[7].Field_20 = scheduleCompact[7].Field_22 = scheduleCompact[7].Field_24 = 50
#%% Daily schedule
    dailySchedule = idf1.idfobjects["Schedule:Day:Hourly"]
    dailySchedule[0].Hour_1 = buildingInputsDF.loc[0,'Schedule1']
    dailySchedule[0].Hour_2 = buildingInputsDF.loc[0,'Schedule2']
    dailySchedule[0].Hour_3 = buildingInputsDF.loc[0,'Schedule3']
    dailySchedule[0].Hour_4 = buildingInputsDF.loc[0,'Schedule4']
    dailySchedule[0].Hour_5 = buildingInputsDF.loc[0,'Schedule5']
    dailySchedule[0].Hour_6 = buildingInputsDF.loc[0,'Schedule6']
    dailySchedule[0].Hour_7 = buildingInputsDF.loc[0,'Schedule7']
    dailySchedule[0].Hour_8 = buildingInputsDF.loc[0,'Schedule8']
    dailySchedule[0].Hour_9 = buildingInputsDF.loc[0,'Schedule9']
    dailySchedule[0].Hour_10 = buildingInputsDF.loc[0,'Schedule10']
    dailySchedule[0].Hour_11 = buildingInputsDF.loc[0,'Schedule11']
    dailySchedule[0].Hour_12 = buildingInputsDF.loc[0,'Schedule12']
    dailySchedule[0].Hour_13 = buildingInputsDF.loc[0,'Schedule13']
    dailySchedule[0].Hour_14 = buildingInputsDF.loc[0,'Schedule14']
    dailySchedule[0].Hour_15 = buildingInputsDF.loc[0,'Schedule15']
    dailySchedule[0].Hour_16 = buildingInputsDF.loc[0,'Schedule16']
    dailySchedule[0].Hour_17 = buildingInputsDF.loc[0,'Schedule17']
    dailySchedule[0].Hour_18 = buildingInputsDF.loc[0,'Schedule18']
    dailySchedule[0].Hour_19 = buildingInputsDF.loc[0,'Schedule19']
    dailySchedule[0].Hour_20 = buildingInputsDF.loc[0,'Schedule20']
    dailySchedule[0].Hour_21 = buildingInputsDF.loc[0,'Schedule21']
    dailySchedule[0].Hour_22 = buildingInputsDF.loc[0,'Schedule22']
    dailySchedule[0].Hour_23 = buildingInputsDF.loc[0,'Schedule23']
    dailySchedule[0].Hour_24 = buildingInputsDF.loc[0,'Schedule24']
        
#%% Envelope
    
    """ Opaque envelope """
    constructions = idf1.idfobjects["Construction"]
    materials = idf1.idfobjects["Material"]
    # Set right massive layer properties
    structuralMaterialsDF = pd.read_csv("SimulationFiles/Structural-material.csv")
    structuralMaterials = structuralMaterialsDF.loc[:,"Material"]
    materials[0].Thickness = materials[1].Thickness = materials[2].Thickness= massiveThick/100
    if insulationPosition == "External": # external
        constructions[2].Layer_2 = structuralMaterials[massiveIndex]
        constructionName = constructions[2].Name
        for surface in surfaces:
            if not surface.Outside_Boundary_Condition == "Adiabatic":
                surface.Construction_Name = constructionName
    if insulationPosition == "Internal": # internal
        constructions[1].Outside_Layer = structuralMaterials[massiveIndex]
        constructionName = constructions[1].Name
        for surface in surfaces:
            if not surface.Outside_Boundary_Condition == "Adiabatic":
                surface.Construction_Name = constructionName
    if insulationPosition == "Non insulated": # non-insulated
        constructions[0].Outside_Layer = structuralMaterials[massiveIndex]
        constructionName = constructions[0].Name
        for surface in surfaces:
            if not surface.Outside_Boundary_Condition == "Adiabatic":
                surface.Construction_Name = constructionName           
    # Insulation material optimization
    insulationMaterialsDF = pd.read_csv("SimulationFiles/Insulation-material.csv")
    insulationMaterials = insulationMaterialsDF.loc[:,"Material"]
    if insulationOptimization == "Fixed" or insulationPosition == "Non insulated": # if insulation material fixed set the right one
        constructions[2].Outside_Layer = constructions[1].Layer_2 = insulationFixed
        insulationIndexes_GA = np.NaN
    else: # else create range of insulating material indexes
        insulationOpt1Index = insulationMaterials[insulationMaterials == insulationOpt1].index[0]
        insulationOpt2Index = insulationMaterials[insulationMaterials == insulationOpt2].index[0]
        insulationIndexes_GA = list(np.arange(insulationOpt1Index, insulationOpt2Index+1, 1)) # +1 to get the last element as well
    # Insulation thickness optimization
    if insulationThickOptimization == "Fixed" or insulationPosition == "Non insulated":
        if insulationThick == 0:
            materials[3].Thickness = materials[4].Thickness = materials[5].Thickness = materials[6].Thickness = 1/100000
        else:
            materials[3].Thickness = materials[4].Thickness = materials[5].Thickness = materials[6].Thickness = insulationThick/100
        insulationThicknesses_GA = np.NaN
    else:
        insulationThicknesses_GA = list(np.arange(insulationMinThick, insulationMaxThick+1, insulationMStepThick)) # +1 to get the last element as well
    
    """ Transparent envelope"""
    glazingMaterialsDF = pd.read_csv("SimulationFiles/Glazing-material.csv")
    glazingMaterials = glazingMaterialsDF.loc[:,"Material"]
    if glazingOptimization == "Fixed":
        for window in windows:
            window.Construction_Name = glazingFixed
        windows_GA = np.NaN
    if glazingOptimization == "Optimized":
        glazingOpt1Index = glazingMaterials[glazingMaterials == glazingOpt1].index[0]
        glazingOpt2Index = glazingMaterials[glazingMaterials == glazingOpt2].index[0]
        windows_GA = list(np.arange(glazingOpt1Index, glazingOpt2Index+1, 1)) # +1 to get the last element as well
    
    ''' Change non geometric properties such as ach, gains, heating and cooling '''
    # change variables in file
    idf1.idfobjects["ZoneInfiltration:DesignFlowRate"][0].Air_Changes_per_Hour = ventilation
    idf1.idfobjects["OtherEquipment"][0].Power_per_Zone_Floor_Area = gains
    idf1.idfobjects["ZoneCapacitanceMultiplier:ResearchSpecial"][0].Temperature_Capacity_Multiplier =  internalMass
    if met == 1:
        activity = 108
    if met == 1.2:
        activity = 126
    if met == 1.6:
        activity = 171
    if met == 2:
        activity = 207
    idf1.idfobjects["Schedule:Compact"][4].Field_4 = activity
    
    shading = idf1.idfobjects["WindowShadingControl"][0]
    if shadingPresence == 1:
        idf1.removeidfobject(shading)
    else:
        shading.Setpoint = shadingSetpoint
        if len(windows) < 4:
            idf1.newidfobject("WindowShadingControl")
            shading1 =idf1.idfobjects["WindowShadingControl"][1]
            shading1.Name = shading.Name
            shading1.Zone_Name = shading.Zone_Name
            shading1.Shading_Control_Sequence_Number = shading.Shading_Control_Sequence_Number
            shading1.Shading_Type = shading.Shading_Type
            shading1.Shading_Control_Type = shading.Shading_Control_Type
            shading1.Schedule_Name = shading.Schedule_Name
            shading1.Setpoint = shading.Setpoint
            shading1.Shading_Control_Is_Scheduled =shading.Shading_Control_Is_Scheduled
            shading1.Glare_Control_Is_Active = shading.Glare_Control_Is_Active
            shading1.Shading_Device_Material_Name = shading.Shading_Device_Material_Name
            shading1.Type_of_Slat_Angle_Control_for_Blinds = shading.Type_of_Slat_Angle_Control_for_Blinds
            shading1.Multiple_Surface_Control_Type = shading.Multiple_Surface_Control_Type
            if len(windows) == 3:
                shading1.Fenestration_Surface_1_Name = windows[0].Name
                shading1.Fenestration_Surface_2_Name = windows[1].Name
                shading1.Fenestration_Surface_3_Name = windows[2].Name
                idf1.removeidfobject(shading)
            elif len(windows) == 2:
                shading1.Fenestration_Surface_1_Name = windows[0].Name
                shading1.Fenestration_Surface_2_Name = windows[1].Name
                idf1.removeidfobject(shading)
            elif len(windows) == 1:
                shading1.Fenestration_Surface_1_Name = windows[0].Name
                idf1.removeidfobject(shading)
            elif len(windows) == 0:
                idf1.removeidfobject(shading1)
                idf1.removeidfobject(shading)

    # save file
    idf1.save(thisSimulationFolderPath + '\\ShoeboxFixedParameters.idf')
    
    # save file for optimization
    optimizationDFDict = {"Insulation material": insulationIndexes_GA, "Insulation thickness": insulationThicknesses_GA, "Windows": windows_GA}
    optimizationDF = pd.DataFrame({key:pd.Series(value) for key, value in optimizationDFDict.items() }) # to create DF with different column length
    optimizationDF.to_csv(thisSimulationFolderPath + "\\OptimizationVariables.csv")
