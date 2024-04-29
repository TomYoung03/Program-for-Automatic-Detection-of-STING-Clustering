import cv2 as cv2
from statistics import median, mean
import PySimpleGUI as sg
import shutil
import numpy as np
import datetime
from fileMethods import *
from pathlib import Path
from ClusterClass import Cluster
from CellClass import Cell
import pandas as pd

'''

Program written to detect clustering events in cells and assign them to the nearest cell
Created by Thomas Young at Leonie Unterholzner lab at Lancaster University
Use at your own risk no guarantee is made for the accuracy of the results given 

'''


def find_clusters(colourImage,minimumClusterPerimeter,maximumClusterPerimeter,thresholdIntensity,blur):
    """
    :param colourImage: should be a COLOUR image
    :param minimumClusterPerimeter:
    :param maximumClusterPerimeter:
    :param thresholdIntensity:
    :param blur:
    :return:
    """
    colourImage = colourImage.copy()
    #Ensures that blur is an odd number
    if int(blur) % 2 == 0:
        blur = blur+1

    image = cv2.GaussianBlur(colourImage, (blur, blur), 0)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


    # Thresholds cluster image to find clusters
    ret, clusterThresh = cv2.threshold(colourImage, thresholdIntensity, 255, cv2.THRESH_TOZERO)
    clusterThresh = cv2.cvtColor(clusterThresh, cv2.COLOR_BGR2GRAY)
    clusterThresh = cv2.GaussianBlur(clusterThresh, (blur, blur), 0)
    # Finding the sting clusters
    clusterFoundContours, _ = cv2.findContours(clusterThresh ,  cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # Creates a list of all found clusters, then filters them that fit within max and minimum perimeter length
    clusterList = []
    foundClusterList = []
    for i, cnt in enumerate(clusterFoundContours):
        foundClusterList.append(Cluster(cnt, image))
    for cluster in foundClusterList:
        if (cluster.perimeterLength >= minimumClusterPerimeter) and (
                cluster.perimeterLength <= maximumClusterPerimeter):
            clusterList.append(Cluster(cluster.contour, image))

    print(f"Number of clusters found:{len(clusterList)}")

    clusterContImg = cv2.drawContours(colourImage, [cluster.contour for cluster in clusterList], -1, (255, 255, 255),1)
    threshDisplayImage = cv2.merge([clusterThresh,clusterThresh,clusterThresh])
    clusterDisplayImage = np.hstack((threshDisplayImage,clusterContImg))
    cv2.namedWindow("Cluster Detection", cv2.WINDOW_NORMAL)
    cv2.imshow("Cluster Detection", clusterDisplayImage)

    return clusterList,clusterContImg

def find_cells (colourImage,minimumCellPerimeter,maximumCellPerimeter,intensityThreshold,blur):

    """

    :param colourImage:
    :param minimumCellPerimeter:
    :param maximumCellPerimeter:
    :param intensityThreshold:
    :param blur:
    :return:
    """

    colourImage = colourImage.copy()
    # Ensures that blur is an odd number
    if int(blur) % 2 == 0:
        blur = blur + 1

    image = cv2.GaussianBlur(colourImage, (blur, blur), 0)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    dapiRet, dapiThresh = cv2.threshold(image, intensityThreshold, 255, cv2.THRESH_TOZERO)
    dapiFoundContours, _, = cv2.findContours(dapiThresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # Finds the contours of the nuclei
    cellList = []
    for i, cnt in enumerate(dapiFoundContours):
        perimeter = cv2.arcLength(cnt, False)
        perimeter = round(perimeter, 1)

        if (perimeter >= minimumCellPerimeter) and (perimeter <= maximumCellPerimeter):
            cellList.append(Cell(cnt))

    print(f"Number of Cells found:{len(cellList)}")
    #dapiContImg = cv2.drawContours(colourImage, [cluster.contour for cluster in cellList], -1, (255, 255, 255), 1)
    for cell in cellList:
        cv2.circle(colourImage, cell.center, cell.radius, cell.colour, 2)
    threshDisplayImage = cv2.merge([dapiThresh, dapiThresh, dapiThresh])
    cellDisplayImage = np.hstack((threshDisplayImage, colourImage))
    cv2.namedWindow("Cell Detection", cv2.WINDOW_NORMAL)
    cv2.imshow("Cell Detection", cellDisplayImage)
    #Returns a list of cells and an image of the detected cells circled
    return cellList,colourImage

def link_cell_clusters(listOfClusters,listOfCells,clusterImage,cellImage):

    maxClusterDistance = 500000000000

    # finds the closest nucleus to each cluster
    for cluster in listOfClusters:

        clusterCenterX = cluster.center[0]
        clusterCenterY = cluster.center[1]

        # Determines 3 closest nuclei
        distanceDict = {}
        closestCoordinates = []
        for cell in listOfCells:
            distance = (clusterCenterY - cell.center[0]) ** 2 + (clusterCenterX - cell.center[1]) ** 2
            distanceDict[distance] = cell
        for key in sorted(distanceDict)[0:3]:
            closestCoordinates.append(distanceDict[key])
        shortestDistanceDict = {}
        # Determines closest point of nuclei
        for cell in closestCoordinates:
            distanceList = []
            for point in cell.perimeter:
                pointDistance = (clusterCenterY - point[0]) ** 2 + (clusterCenterX - point[1]) ** 2
                distanceList.append(pointDistance)
            shortestDistanceDict[sorted(distanceList)[0]] = cell
        # If shortest distance is too large then does not count it
        if sorted(shortestDistanceDict)[0] < maxClusterDistance:
            # Only calculates intensity of clusters being counted
            cluster.calculate_intensity()
            # Sorts based on values (distance) then first value is shortest
            closestNuclei = shortestDistanceDict[sorted(shortestDistanceDict)[0]]
            closestNuclei.add_cluster(cluster)

    clusterB,clusterG,clusterR = cv2.split(clusterImage)
    cellB,cellG,cellR = cv2.split(cellImage)

    clusterLinkImg = cv2.merge([cellB,np.zeros(cellG.shape, np.uint8),clusterR])
    for cell in listOfCells:
        if len(cell.clusters) >= 1 :
            cv2.circle(clusterLinkImg,cell.center,cell.radius,cell.colour,2)
            for cluster in cell.clusters:
                cv2.drawContours(clusterLinkImg, cluster.contour, -1, cluster.colour, 1)
    cv2.namedWindow("Linked Clusters",cv2.WINDOW_NORMAL)
    cv2.imshow("Linked Clusters",clusterLinkImg)

    return clusterLinkImg

def analyse_image(fileName,clusterList, cellList, clusterImageColour, cellImageColour):
    global clusterLinkImage
    #Fucntion returns image as well as adding clusters to cells in list
    clusterLinkImage = link_cell_clusters(clusterList, cellList, clusterImageColour, cellImageColour)
    withClustersNameList = []
    withClustersDataList = []
    withoutClustersNameList = []
    withoutClustersDataList = []

    meanIntensityList = []
    medianIntensityList = []
    meanAreaList = []
    medianAreaList = []
    numCellsWithClusters = 0

    # Creates a list of all relevant data per cell, sorted into if the cell has any associated clusters
    for cell in cellList:
        if len(cell.clusters) >= 1:
            numCellsWithClusters += 1
            clusterIntensities = [cluster.meanIntensity for cluster in cell.clusters]
            clusterAreas = [cluster.area for cluster in cell.clusters]
            withClustersNameList.append(f"Cell: {cell.center}")
            # Calculates all values needed and adds them to a list for all cells
            meanIntensity = mean(clusterIntensities)
            medianIntensity = median(clusterIntensities)
            meanIntensityList.append(meanIntensity)
            medianIntensityList.append(medianIntensity)
            meanArea = mean(clusterAreas)
            medianArea = median(clusterAreas)
            meanAreaList.append(meanArea)
            medianAreaList.append(medianArea)

            withClustersDataList.append([len(cell.clusters),
                                         meanIntensity,
                                         medianIntensity,
                                         meanArea,
                                         medianArea])
        else:
            # If the cell has no associated clusters
            clusterIntensities = [0]
            clusterAreas = [0]
            withoutClustersNameList.append(f"Cell: {cell.center}")
            withoutClustersDataList.append([len(cell.clusters),
                                            mean(clusterIntensities),
                                            median(clusterIntensities),
                                            mean(clusterAreas),
                                            median(clusterAreas)])

    # Data for all cells with clusters
    withClustersDF = pd.DataFrame(withClustersDataList,
                                  columns=["Number of clusters",
                                           "Mean Cluster Intensity",
                                           "Median Cluster Intensity",
                                           "Mean Cluster Area",
                                           "Median Cluster Intensity"],
                                  index=withClustersNameList)
    # Data for all cells without clusters
    withoutClustersDF = pd.DataFrame(withoutClustersDataList,
                                     columns=["Number of clusters",
                                              "Mean Cluster Intensity",
                                              "Median Cluster Intensity",
                                              "Mean Cluster Area",
                                              "Median Cluster Intensity"],
                                     index=withoutClustersNameList)

    # Creates a dataframe of all the parameters used to detect clusters and cells
    detectionParameters = [[int(values["minimumClusterSelection"]),
                            int(values["maximumClusterSelection"]),
                            int(values["clusterThresholdIntensitySelection"]),
                            int(values["clusterBlurSelection"])],
                           [int(values["minimumCellSelection"]),
                            int(values["maximumCellSelection"]),
                            int(values["cellThresholdIntensitySelection"]),
                            int(values["cellBlurSelection"])]]

    detectionParameterNames = ["Minimum Length", "Maximum Length", "Threshold Intensity", "Blur Intensity"]

    detectionParametersDF = pd.DataFrame(detectionParameters, columns=detectionParameterNames,
                                         index=["Cluster Parameters", "Cell Parameters"])

    # Creates a dataframe of the mean/median area/intensity of all cells
    print(numCellsWithClusters)
    print(len(cellList))
    percentCellsWithCluster = round(numCellsWithClusters / len(cellList), 2) * 100
    print(percentCellsWithCluster)
    overallValues = [[percentCellsWithCluster, mean(meanIntensityList), median(medianIntensityList), mean(meanAreaList),
                      median(medianAreaList)]]

    overallValuesDF = pd.DataFrame(overallValues, columns=["% Cells with Clustering ",
                                                           "Total Mean Intensity",
                                                           "Total Median Intensity",
                                                           "Total Mean Area",
                                                           "Total Median Area"], index=["Total"])
    # Tries to save with file name given, if there is an error then will try instead with RECOVERED DATA file name
    try:
        with pd.ExcelWriter(f"{fileName}.xlsx", engine="openpyxl") as writer:

            detectionParametersDF.to_excel(excel_writer=writer, sheet_name=f"{fileName}", startcol=1, startrow=1)
            overallValuesDF.to_excel(excel_writer=writer, sheet_name=f"{fileName}", startcol=1, startrow=5)
            withClustersDF.to_excel(excel_writer=writer, sheet_name=f"{fileName}", startcol=1, startrow=8)
            withoutClustersDF.to_excel(excel_writer=writer, sheet_name=f"{fileName}", startcol=8, startrow=8)
    except:
        fileName = "RECOVERED DATA"
        with pd.ExcelWriter(f"{fileName}.xlsx", engine="openpyxl") as writer:

            detectionParametersDF.to_excel(excel_writer=writer, sheet_name=f"{fileName}", startcol=1, startrow=1)
            overallValuesDF.to_excel(excel_writer=writer, sheet_name=f"{fileName}", startcol=1, startrow=5)
            withClustersDF.to_excel(excel_writer=writer, sheet_name=f"{fileName}", startcol=1, startrow=8)
            withoutClustersDF.to_excel(excel_writer=writer, sheet_name=f"{fileName}", startcol=8, startrow=8)
        sg.popup(f"Error in saving file, data has been stored as {fileName}")

    window["analysisImageSaveButton"].update(disabled=False)


windowSize = (650,275)
mainWindowTab = [
                [sg.Button("Select File",key="nucleusImageSelectButton"),sg.Text("Select Nucleus Image",key="nucleusImageSelectText")],
                [sg.Button("Select File",key="proteinImageSelectButton"),sg.Text("Select Fluorescent Label Image",key="proteinImageSelectText")],
                [sg.Text("Fluorescent protein colour:"),sg.Combo(["Red","Green"],readonly=True,default_value="Red",key="fluorescenceSelection")],
                [sg.Button("Add Data to Existing File",key="existingFileButton"),sg.Text("",key="excelFileSelectionText")],
                [sg.Text("Image Analysis Experiment Name:"),sg.InputText("",key="experimentName")],
                [sg.Button("Analyse Images",key="analyseImagesButton",disabled=True),sg.Button("Save Analysis Image",key="analysisImageSaveButton",disabled=True)],]


clusterDetectionTab = [[sg.Text("Minimum Cluster Perimeter"),sg.Spin([i for i in range(1,100000)],initial_value=15,size=(5,10),key="minimumClusterSelection")],
                       [sg.Text("Maximum Cluster Perimeter"),sg.Spin([i for i in range(1,100000)],initial_value=500,size=(5,10),key="maximumClusterSelection")],
                       [sg.Text("Intensity Threshold"),sg.Spin([i for i in range(1,255)],initial_value=25,size=(5,10),key="clusterThresholdIntensitySelection")],
                       [sg.Text("Blur Intensity"),sg.Spin([i for i in range(1,100,2)],initial_value=3,size=(5,10),key="clusterBlurSelection")],
                       [sg.Button("Show Cluster Detection",key="displayClustersButton"),sg.Button("Save Image",key="clusterImageSaveButton")]]

cellDetectionTab = [[sg.Text("Minimum Cell Perimeter"),sg.Spin([i for i in range(1,100000)],initial_value=200,size=(5,10),key="minimumCellSelection")],
                   [sg.Text("Maximum Cell Perimeter"),sg.Spin([i for i in range(1,100000)],initial_value=2000,size=(5,10),key="maximumCellSelection")],
                   [sg.Text("Intensity Threshold"),sg.Spin([i for i in range(1,255)],initial_value=3,size=(5,10),key="cellThresholdIntensitySelection")],
                   [sg.Text("Blur Intensity"),sg.Spin([i for i in range(1,100,2)],initial_value=3,size=(5,10),key="cellBlurSelection")],
                   [sg.Button("Show Cell Detection",key="displayCellsButton"),sg.Button("Save Image",key="cellImageSaveButton")]]

helpText = open("howToText.txt","r")

howToTab = [[sg.Multiline(helpText.read(),size=windowSize,horizontal_scroll=True,disabled=True)]]

windowLayout = [[sg.TabGroup([[sg.Tab("Main Window",mainWindowTab)],
                              [sg.Tab("Cluster Detection",clusterDetectionTab)],
                              [sg.Tab("Nucleus Detection",cellDetectionTab)],
                              [sg.Tab("How To Guide",howToTab)]])]]

selectionWindowLayout = [[sg.Button("Open Image")],
                         [sg.Text("Select cells by left clicking and dragging to draw a box around the cell\n"
                                  "To undo a selection press the Z key\n"
                                  "To reset all selections press the R key\n"
                                  "To finish selections and save them as images press the X key\n"
                                  "To close the window press the Q key"),],
                         ]

bannedCharacters = [r"\ ", "/", "?", "%", "*", ":", ";", "|", "<", ">", ",", "="]
numberList = ["1","2","3","4","5","6","7","8","9","0"]
window = sg.Window("Nuclear Localisation Analysis",windowLayout,resizable=True,size=windowSize)
nucleusImageSelected = False
clusterImageSelected = False
excelFile = None
cellsDictionary = {}
clusterDetectionImage = None
cellDetectionImage = None
clusterLinkImage = None
cellImagePath = None
clusterImagePath = None


while True:
    event,values = window.read()

    if event == sg.WIN_CLOSED or event == 'Cancel':  # If user closes window or clicks cancel
        break

    if event == "nucleusImageSelectButton":
        #Selects the image of the nucleus (DAPI stained)
        cellFile = getFile()
        if cellFile is not None:
            cellImagePath = Path(cellFile).__str__() #Path object ensures that uses correct /

            if os.path.splitext(cellImagePath)[-1] == ".tif":
                window["nucleusImageSelectText"].update(f"Nucleus file selected: {getFileName(cellImagePath)}")
                print(f"Selected image: {getFileName(cellImagePath)}")
                cellImageColour = cv2.imread(cellImagePath)
                cellImage = cv2.cvtColor(cellImageColour, cv2.COLOR_BGR2GRAY)
                nucleusImageSelected = True
            else:
                cellImagePath = None
                sg.popup("Selected image must be a .tif file")

    if event == "proteinImageSelectButton":
        #Selects the image of the protein to determine the localisation of
        clusterFile = getFile()
        if clusterFile is not None:
            clusterImagePath = Path(clusterFile).__str__() #Path object ensures that uses correct /
            if os.path.splitext(clusterImagePath)[-1] == ".tif":
                window["proteinImageSelectText"].update(f"Fluorescent labelled file selected: {getFileName(clusterImagePath)}")
                print(f"Selected image: {getFileName(clusterImagePath)}")
                folderName = f"{getFileName(clusterImagePath)}"
                clusterImageSelected = True
                clusterImageColour = cv2.imread(clusterImagePath)
                clusterImage = cv2.cvtColor(clusterImageColour, cv2.COLOR_BGR2GRAY)
            else:
                clusterImagePath = None
                sg.popup("Selected image must be a .tif file")

    if (nucleusImageSelected is True) and (clusterImageSelected is True):
        #Ensures buttons can only be used if cell images have been selected
        window["analyseImagesButton"].update(disabled=False)


    if event == "displayClustersButton":

        clusterList,clusterDetectionImage = find_clusters(clusterImageColour,
                      int(values["minimumClusterSelection"]),
                      int(values["maximumClusterSelection"]),
                      int(values["clusterThresholdIntensitySelection"]),
                      int(values["clusterBlurSelection"]))

    if event == "clusterImageSaveButton":

        if clusterDetectionImage is not None:

            if values["experimentName"]:
                experimentName = values["experimentName"]
            else:
                time = datetime.datetime.now()
                experimentName = f"{time.strftime('%d')}.{time.strftime('%m')}.{time.strftime('%y')}"


            fileName = f"Cluster Detection {experimentName} "\
                        f"Min {int(values['minimumClusterSelection'])} "\
                        f"Max {int(values['maximumClusterSelection'])} "\
                        f"Thresh {int(values['clusterThresholdIntensitySelection'])} "\
                        f"Blur {int(values['clusterBlurSelection'])}.tif"

            sg.popup(f"Image Saved as {fileName} ")

            cv2.imwrite(fileName,clusterDetectionImage)

    if event == "displayCellsButton":

        cellList,cellDetectionImage = find_cells(cellImageColour,
                                    int(values["minimumCellSelection"]),
                                    int(values["maximumCellSelection"]),
                                    int(values["cellThresholdIntensitySelection"]),
                                    int(values["cellBlurSelection"]))

    if event == "cellImageSaveButton":

        if cellDetectionImage is not None:

            if values["experimentName"]:
                experimentName = values["experimentName"]
            else:
                time = datetime.datetime.now()
                experimentName = f"{time.strftime('%d')}.{time.strftime('%m')}.{time.strftime('%y')}"

            fileName = f"Cell Detection {experimentName} " \
                       f"Min {int(values['minimumCellSelection'])} " \
                       f"Max {int(values['maximumCellSelection'])} " \
                       f"Thresh {int(values['cellThresholdIntensitySelection'])} " \
                       f"Blur {int(values['cellBlurSelection'])}.tif"

            cv2.imwrite(fileName,cellDetectionImage)
            sg.popup(f"Image Saved as {fileName} ")





    if event == "analyseImagesButton":

        analyse_image(values["experimentName"],clusterList, cellList, clusterImageColour, cellImageColour)
        window.perform_long_operation(lambda: analyse_image(values["experimentName"],clusterList, cellList, clusterImageColour, cellImageColour), 'analysisComplete')

    if event == "analysisComplete":

        sg.popup("Analysis Complete!")


    if event == "analysisImageSaveButton":

        if clusterLinkImage is not None:

            if values["experimentName"]:
                experimentName = values["experimentName"]
            else:
                time = datetime.datetime.now()
                experimentName = f"{time.strftime('%d')}.{time.strftime('%m')}.{time.strftime('%y')}"

            fileName = f"Cluster and Cell links {experimentName} " \
                       f"Min cell {int(values['minimumCellSelection'])} cluster {int(values['minimumClusterSelection'])} " \
                       f"Max cell {int(values['maximumCellSelection'])} cluster {int(values['maximumClusterSelection'])} " \
                       f"Thresh cell {int(values['cellThresholdIntensitySelection'])} cluster {int(values['clusterThresholdIntensitySelection'])} " \
                       f"Blur cell {int(values['cellBlurSelection'])} cluster {int(values['clusterBlurSelection'])}.tif"

            cv2.imwrite(fileName,clusterLinkImage)
            sg.popup(f"Image Saved as {fileName} ")

        else:
            sg.popup("No linked image of clusters and cells found")

