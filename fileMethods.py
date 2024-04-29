import os
import PySimpleGUI as sg

def validateFile(extension,fileLocation):
    '''
    Ensures that a file path exists
    :param extension: The extension of the file to validate
    :param fileLocation: The path to validate
    :return: True if path exists False if not
    '''
    name,ext = os.path.splitext(fileLocation)
    if ext != extension:
        return False
    else:
        return True

def getFile():
    '''
    Method to get a file using PysimpleGUI
    :return: The path of the selected file
    '''
    browsing = True
    while browsing:
        fileName = sg.popup_get_file("Select document")
        if fileName is not None:
            if sg.os.path.exists(fileName):
                return fileName
            else:
                sg.popup("Error in file path")
                return None
        else:
            return None


def getFolder():
    '''
    Method to get a folder using PysimpleGUI
    :return: The path of the selected folder
    '''
    browsing = True
    while browsing:
        folderName = sg.popup_get_folder("Select a folder")
        if sg.os.path.exists(folderName):
            return folderName
        else:
            sg.popup("Error in folder path")

def getFileName(filePath, separator ="\\"):
    '''
    Method that gets the name of a given file
    :param filePath: Path of the file to be selected
    :param separator: The seperator betweeen files/folders in the path (is default / but is sometimes \)
    :return: Returns the name of the file with no path or file extension
    '''
    splitList = filePath.split(separator)
    return splitList[-1].replace(".png","").replace(".jpg","").replace(".tif","")

def valid_file_name(fileName):

    bannedCharacters = ['\ ',"/","?","%","*",":",";","|","<",">",",","=","."]
    for character in list(fileName.replace(" ","")):
        if character in bannedCharacters:
            return False
    return True


def file_to_coord(file):
    '''
    Takes in the file with coordinates and converts to a list of tuples that can be used to cut out images
    :param file: File containing coordinates
    :return: A list of organised coordinates
    '''
    with open(file, "r") as file:
        fileList = []
        for line in file:
            coordinate = line.replace("\n", "")
            coordinate = int(coordinate)
            fileList.append(coordinate)
    dividedList = []
    for coordinate in range(0, len(fileList), 4):
        dividedList.append(fileList[coordinate:coordinate + 4])
    print(dividedList)
    twoList = []
    for i in dividedList:
        for coordinate in range(0, len(i), 2):
            twoList.append(i[coordinate:coordinate + 2])
    tupleList = []
    for coordinate in twoList:
        tupleList.append((coordinate[0], coordinate[1]))
    finalList = []
    for coordinate in range(0, len(tupleList), 2):
        finalList.append(tuple(tupleList[coordinate:coordinate + 2]))
    return finalList
