#!/usr/bin/python
# -*- coding: utf-8 -*-
#******************************************************************************
# RosegardenBankGeneration: sf2banks.py
#
# Main Program for FluidSynth bank generation
#
# Copyright (C) 2021 Jan Vlietland <j.vlietland@ziggo.nl>
#
#******************************************************************************
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For a full copy of the GNU General Public License see the LICENSE.txt file.
#
#******************************************************************************

import sys
import os
import glob
import xml.etree.ElementTree as ET
import subprocess

COM_SF2 = 'fluidsynth -i -f config.txt -a pulseaudio '
roseGardenFile = ""
soundfontsDir = ""
msbValue = ""
roseGardenFile = ""
deviceName = ""

def getSoundFileList(location):
    fileArray = []
    for file in glob.glob(location + "*.sf2"):
        fileArray.append(file)
    return sorted(fileArray)

def getInstrumentList(file):
    stringArray = []
    cmd = COM_SF2 + "'" + file + "'"
    fsOutput = str(subprocess.run(cmd, capture_output=True, shell=True))
    if (not "inst: invalid font number" in fsOutput):
        startList = fsOutput.find("stdout=b") + len("stdout=b")+1
        endList = fsOutput.find("\\ncheers!")
        substring = fsOutput[startList:endList]
        stringArray = substring.split("\\n")
        for i, string in enumerate(stringArray):
            stringArray[i] = string[8:]
    return stringArray

def getBankName(soundfontsDir, file):
    string = file.replace(soundfontsDir,"")
    endList = string.find(".sf2")
    return string[:endList]
    
def addBank(tree, bankName, instrumentList, msbValue, lsbValue):
    root = tree.getroot()
    fsTree = root.find("studio/device[@name='"+deviceName+"']")
    bankTree = ET.SubElement(fsTree, "bank", name=bankName, percussion="false", msb=msbValue, lsb=lsbValue)
    for i, instrument in enumerate(instrumentList):
        ET.SubElement(bankTree, "program", id=str(i), name=instrumentList[i])
    return tree

#---------------------------------------reading input---------------------------------

try:
    if (len(sys.argv) == 2) and (sys.argv[1] == '--help') :
        print("sf2banks runtime version 0.1 \n\
Copyright (C) 2021 Jan Vlietland. \n\
Distributed under the LGPL license. \n \n\
Usage: \n \
  sf2banks [options | source file] [destination file] [soundfonts path] [msb value] [device name]\n \n\
Possible options: \n\
  --help : Shows this help \n \n\
Remark: Rosegarden file are gzipped. sf2banks cannot read these gzipped file. Therefore\
first gunzip the file with the 'gunzip -S .rg [rosegarden filename]'.\
sf2banks is able to read the unencrypted file.\n")
        exit()
    elif (len(sys.argv) == 6) :
        roseGardenFile = sys.argv[1]
        targetFile = sys.argv[2]
        soundfontsDir = sys.argv[3]
        msbValue = sys.argv[4]
        deviceName = sys.argv[5]
except Exception as err:
    print("No valid command provided, exception: "+str(err))
    exit()

#---------------------------------------testing input---------------------------------

if (not os.path.isdir(soundfontsDir)):
    print("soundfont path: "+soundfontsDir+" is not valid.")
    exit()

print("\nparsing: '"+roseGardenFile+"' XML-based file")    
tree = ET.parse(roseGardenFile)

#---------------------------------------executing command-----------------------------

print("reading: '"+soundfontsDir+"', the soundfont directory")
fileList = getSoundFileList(soundfontsDir)

print("generating banks")
for i, string in enumerate(fileList):
    bankName = getBankName(soundfontsDir, fileList[i])
    print("reading SoundFonts file: "+fileList[i])
    instrumentList = getInstrumentList(fileList[i])
    addBank(tree, bankName, instrumentList, msbValue, str(i))

#print(ET.dump(tree))
print("writing file to: '"+targetFile+"'")
tree.write(targetFile)
print("done !")