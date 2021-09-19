#!/usr/bin/python

import sys
import os
import glob
import xml.etree.ElementTree as ET
import subprocess

COM_SF2 = 'fluidsynth -i -f config.txt -a pulseaudio '
TARGET_FILE = 'generated.rg'
roseGardenFile = "autoload.rg"
systemSfDir = "systemSf/"
userSfDir = "userSf/"
systemMsb = "0"
userMsb = "1"

def getSoundFileList(location):
    return [f for f in glob.glob(location + "*.sf2")]

def getInstrumentList(file):
    cmd = COM_SF2 + "'" + file + "'"
    fsOutput = str(subprocess.run(cmd, capture_output=True, shell=True))
    startList = fsOutput.find("stdout=b'") + len("stdout=b'")
    endList = fsOutput.find("\\ncheers!")
    substring = fsOutput[startList:endList]
    stringArray = substring.split("\\n")
    for i, string in enumerate(stringArray):
        stringArray[i] = string[8:]
    return stringArray

def getBankName(file):
    startList = file.find("/") + len("/")
    endList = file.find(".sf2")
    return file[startList:endList]    
    
def addBank(tree, bankName, instrumentList, msbValue, lsbValue):
    root = tree.getroot()
    fsTree = root.find("studio/device[@name='FluidSynth']")
    bankTree = ET.SubElement(fsTree, "bank", name=bankName, percussion="false", msb=msbValue, lsb=lsbValue)
    for i, instrument in enumerate(instrumentList):
        ET.SubElement(bankTree, "program", id=str(i), name=instrumentList[i])
    return tree


print("Hello! 'Extinst' creates instrument banks for Rose garden. First the program asks for entering \
two locations (directories) where your soundbanks are stored. After entering these locations Extinst \
asks for the rosegarden file that needs to be used for generating the banks. After entering the input \
Extinst walks through your Sound files one by one, creates the banks in the rosegarden file and stores \
the result in the file 'generated.rg'. That file can be directly loaded into Rosegarden. ")

print("\nExtinst generates the banks in the first soundfonts location with msb value '0' and the second \
with msb value '1'. For each location the banks are sequentially uniquely numbered with the lsb value.")

print("\nRemark: The rosegarden file is gzipped. Extinst cannot read these file. Therefor first gunzip the file \
with the 'gunzip -S .rg <rosegarden filename>' command. Extinst is albe to read the unencrypted file.")

roseGardenFile = "autoload.rg"

userInput = input("\nEnter the path of your file (default: 'systemSf/'): ")
if (os.path.isdir(userInput)):
    systemSfDir = userInput
else:
    print("path not found, using default")
    
userInput = input("\nEnter the path of your file (default: 'userSf/'): ")
if (os.path.isdir(userInput)):
    userSfDir = userInput
else:
    print("path not found, using default")
    
userInput = input("\nEnter the path of your file (default: 'autoload.rg'): ")
if (os.path.isdir(userInput)):
    roseGardenFile = userInput
else:
    print("file not found, using default")

print("\nparsing: '"+roseGardenFile+"' XML-based file")    
tree = ET.parse(roseGardenFile)

print("\nreading: '"+systemSfDir+"', the first soundfont directory")
fileList = getSoundFileList(systemSfDir)
print("generating banks")
for i, string in enumerate(fileList):
    bankName = getBankName(fileList[i])
    instrumentList = getInstrumentList(fileList[i])
    addBank(tree, bankName, instrumentList, systemMsb, str(i))
    
print("\nreading: '"+userSfDir+"', the second soundfont directory")
fileList = getSoundFileList(userSfDir)
print("generating banks")
for i, string in enumerate(fileList):
    bankName = getBankName(fileList[i])
    instrumentList = getInstrumentList(fileList[i])
    addBank(tree, bankName, instrumentList, userMsb, str(i))

#print(ET.dump(tree))
print("\nwriting file to: '"+TARGET_FILE+"'")
tree.write(TARGET_FILE)
print("\n done !")