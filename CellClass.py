import cv2
import math
import random


class Cell:

    def __init__(self,contour):

        self.contour = contour
        self.perimeter,self.center,self.radius = self.generate_perimeter(self.contour)
        self.clusters = []
        self.colour = (random.randint(1,255),random.randint(1,255),random.randint(1,255))

    def __str__(self):
        return f"Cell object at {self.center}"

    def generate_perimeter(self,cnt):

        circleAngles = 360
        (centerX, centerY), radius = cv2.minEnclosingCircle(cnt)
        radius = int(radius)
        centerX = round(centerX)
        centerY = round(centerY)
        perimeterCoords = []
        for angle in range(0, circleAngles):
            x = round(radius * math.sin(angle))
            y = round(radius * math.cos(angle))
            perimeterCoords.append((centerX + x, centerY + y))
            perimeterCoords.append((centerX + x, centerY - y))
            perimeterCoords.append((centerX - x, centerY + y))
            perimeterCoords.append((centerX - x, centerY - y))

        return perimeterCoords,(centerX,centerY),radius

    def add_cluster(self,cluster):

        cluster.colour = self.colour
        self.clusters.append(cluster)

