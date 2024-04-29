import cv2
import random
import numpy as np

class Cluster:

    def __init__(self,contour,image):

        self.image = image
        self.contour = contour
        self.perimeterLength = round(cv2.arcLength(contour,False),1)
        self.area = round(cv2.contourArea(self.contour))
        self.center = self.find_center(self.contour)
        self.colour = (random.randint(1,255),random.randint(1,255),random.randint(1,255))
        self.meanIntensity = None
        self.points = None


    def __str__(self):
        return f"Cluster object at {self.center}"

    def find_center(self,cont):

        # M is a dictionary of information about the contour generates by cv2
        M = cv2.moments(cont)
        # In M dictionary these values correspond to the y,x values of the center of the countour
        if (M['m01'] != 0) or  (M['m00'] != 0) or (M['m10'] !=0 ) or (M['m00'] !=0):
            clusterCenter = (int(M['m01'] / M['m00']), int(M['m10'] / M['m00']))  # (y,x)
            return clusterCenter
        else:
            return False

    def calculate_intensity(self):

        # np.zeroes sets all values to 0
        mask = np.zeros(self.image.shape, np.uint8)
        #drawContours then draws the contour onto the mask, only pixels in the contour are changed
        maskImage = cv2.drawContours(mask, [self.contour], 0, 255, -1)
        self.points = cv2.findNonZero(mask)
        #Calculates mean intensity [0] index gives intensity of first channel as other channels not used in B and W image
        self.meanIntensity = round(cv2.mean(self.image,mask=mask)[0])


