import cv2 as cv2
import numpy as np
import math
import random
from ClusterClass import Cluster
from CellClass import Cell

dapiImgColour = cv2.imread(r"Clustering test images/HaCaT HtDNA TILESCAN DAPI.tif")
clusterImgColour = cv2.imread(r"Clustering test images/HaCaT HtDNA TILESCAN STING.tif")
clusterImg = cv2.cvtColor(clusterImgColour, cv2.COLOR_BGR2GRAY)
dapiImg = cv2.cvtColor(dapiImgColour, cv2.COLOR_BGR2GRAY)

dapiImgOriginal = dapiImg.copy()

minimumNucleusPerimeter = 200
maximumNucleusPerimeter = 1000

minimumClusterPerimeter = 25
maximumClusterPerimeter = 1000000

#Thresholds cluster image to find clusters
ret, clusterThresh = cv2.threshold(clusterImg, 25, 255, cv2.THRESH_TOZERO)
cv2.imshow("STINGThresh",clusterThresh)
#Finding the sting clusters
clusterFoundContours, _ = cv2.findContours(clusterThresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

#Creates a list of all found clusters, then filters them that fit within max and minimum perimeter length
clusterList = []
foundClusterList = []
for i, cnt in enumerate(clusterFoundContours):
    foundClusterList.append(Cluster(cnt,clusterImg))
for cluster in foundClusterList:
    if (cluster.perimeterLength >= minimumClusterPerimeter) and (cluster.perimeterLength <= maximumClusterPerimeter):
        clusterList.append(Cluster(cluster.contour,clusterImg))

print(f"Number of clusters found:{len(foundClusterList)}\n"
      f"number of clusters removed: {len(foundClusterList)-len(clusterList)}")

clusterContImg = cv2.drawContours(clusterThresh, [cluster.contour for cluster in clusterList], -1, (255, 255, 255), 1)
cv2.imshow("STING edges", clusterContImg)


#Find the nuclei
dapiRet,dapiThresh = cv2.threshold(dapiImg,6,255,cv2.THRESH_TOZERO)
dapiFoundContours, _, = cv2.findContours(dapiThresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
#Finds the contours of the nucleus
dapiContours = []
dapiLengthList =[]
cellList = []
for i, cnt in enumerate(dapiFoundContours):
    perimeter = cv2.arcLength(cnt,False)
    perimeter = round(perimeter, 1)

    if (perimeter >= minimumNucleusPerimeter) and (perimeter <= maximumNucleusPerimeter):
        cellList.append(Cell(cnt))


dapiContImg = cv2.drawContours(dapiImg, [cell.contour for cell in cellList], -1, (255,255,255), 1)
cv2.imshow("DAPI Thresh",dapiThresh)
cv2.imshow("DAPI edges",dapiContImg)


cv2.imshow("DAPI Centers",dapiContImg)
cv2.imshow("Cluster centers",clusterContImg)

lineImage = dapiImg

maxClusterDistance = 200

#finds the closest nucleus to each cluster
for cluster in clusterList:

    clusterCenterX = cluster.center[0]
    clusterCenterY = cluster.center[1]

    #Determines 3 closest nuclei
    distanceDict = {}
    closestCoordinates = []
    for cell in cellList:
        distance = (clusterCenterY - cell.center[0]) ** 2 + (clusterCenterX - cell.center[1]) ** 2
        distanceDict[distance] = cell
    for key in sorted(distanceDict)[0:3]:
        closestCoordinates.append(distanceDict[key])
    shortestDistanceDict = {}
    #Determines closest point of nuclei
    for cell in closestCoordinates:
        distanceList = []
        for point in cell.perimeter:
            pointDistance = (clusterCenterY - point[0]) ** 2 + (clusterCenterX - point[1]) ** 2
            distanceList.append(pointDistance)

        shortestDistanceDict[sorted(distanceList)[0]] = cell

    #If shortest distance is too large then does not count it
    if sorted(shortestDistanceDict)[0] < maxClusterDistance:
        #Only calculates intensity of clusters being counted
        cluster.calculate_intensity()
        # Sorts based on values (distance) then first value is shortest
        closestNuclei = shortestDistanceDict[sorted(shortestDistanceDict)[0]]
        closestNuclei.add_cluster(cluster)
        #Creates image of lines between clusters and nuclei
        lineImage = cv2.line(lineImage,closestNuclei.center,(clusterCenterY,clusterCenterX),255,2)

    #print(f"Shortested distance dict: {shortestDistanceDict}")
    #print(f"Shortest distance is {closestNuclei}")

for cell in cellList:
    print(f"{cell} Clusters: {[cluster.meanIntensity for cluster in cell.clusters]}")


clusterB,clusterG,clusterR = cv2.split(clusterImgColour)
dapiB,dapiG,dapiR = cv2.split(dapiImgColour)
#Creates image of cell circles and clusters, any clusters will have the same colour as the cell they are linked to
clusterLinkImg = cv2.merge([dapiB,np.zeros(dapiImgOriginal.shape, np.uint8),clusterR])
cellsWithClusters = []
for cell in cellList:
    cv2.circle(clusterLinkImg,cell.center,cell.radius,cell.colour,2)
    for cluster in cell.clusters:
        cv2.drawContours(clusterLinkImg, cluster.contour, -1, cluster.colour, 1)

    if len(cell.clusters) >= 1:
        cellsWithClusters.append(cell)

print(f"Number of cells {len(cellList)} \n"
      f"Number of cells with clusters {len(cellsWithClusters)}")

cv2.namedWindow("Colour",cv2.WINDOW_NORMAL)
cv2.imshow("Colour",clusterLinkImg)

cv2.namedWindow("merge",cv2.WINDOW_NORMAL)
mergeImg = cv2.merge([dapiImgOriginal,lineImage,clusterContImg])
cv2.imshow("merge",mergeImg)
cv2.waitKey(0)