#!/usr/bin/python
# -*- coding: utf-8 -*-
#******************************************************************************
# RosegardenBankGeneration: zyn2banks.py
#
# Main Program for ZynAddSubFX bank generation
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
from operator import itemgetter, attrgetter, methodcaller

roseGardenFile = ""
soundfontsDir = ""
msbValue = ""
roseGardenFile = ""
deviceName = ""

def getBankList(banksDir):
    bankArray = glob.glob(banksDir+"/*/")
    for i, bank in enumerate(bankArray):
        bankArray[i] = getBankName(banksDir, bankArray[i])+";"+bankArray[i]
    return sorted(bankArray)

def getBankName(banksDir, bankDir):
    bankName = bankDir.replace(banksDir,"")[:-1]
    return bankName

def getInstrumentList(bankDir):
    stringArray = []
    for file in sorted(glob.glob(bankDir+"*.xiz")):
        string = file.replace(bankDir,"")
        endString = string.find(".xiz")
        stringArray.append(string[5:endString])
    return stringArray
    
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
        print("zyn2banks runtime version 0.1 \n\
Copyright (C) 2021 Jan Vlietland. \n\
Distributed under the LGPL license. \n \n\
Usage: \n \
  zyn2banks [options | source file] [destination file] [soundfonts path] [msb value] \n \n\
Possible options: \n\
  --help : Shows this help \n \n\
Remark: Rosegarden file are gzipped. zyn2banks cannot read these gzipped file. Therefore\
first gunzip the file with the 'gunzip -S .rg [rosegarden filename]'.\
zyn2banks is able to read the unencrypted file.\n")
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

print("\nreading: '"+soundfontsDir+"', the soundfont directory")
directoryList = getBankList(soundfontsDir+"zynbanks/")
directoryList.append(getBankList(soundfontsDir+"presets/zynaddsubfx/")[0])
directoryListSorted = sorted(directoryList)

print("generating banks")
for i, string in enumerate(directoryListSorted):
    dirSplitArray = directoryListSorted[i].split(";")
    bankName = dirSplitArray[0]
    instrumentList = getInstrumentList(dirSplitArray[1])
    addBank(tree, bankName, instrumentList, msbValue, str(i))

print(ET.dump(tree))
print("\nwriting file to: '"+targetFile+"'")
tree.write(targetFile)
print("\n done !")

