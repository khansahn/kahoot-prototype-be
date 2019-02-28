from flask import json

def writeFile(fileLocation,toBeWritten):
    writeFile = open(fileLocation,'w')
    writeFile.write(toBeWritten)
    # return json.load(writeFile)

def readFile(fileLocation):
    readFile = open(fileLocation,'r')
    readData = json.load(readFile)
    return readData

def createFile(fileLocation):
    createFile = open(fileLocation, 'x')
    return createFile

def checkFileExistence():
    return "exist"
