#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 18:04:03 2017

@author: hans
"""

import farm as farmLibrary

farmName="Test Farm Setup"
farm= farmLibrary.Farm(farmName)

breedAttributes=["name", "incubatorTime", "incubatorDeathRate", "brooderTime",
                 "brooderDeathRate", "coopReadyTime", "coopReadyDeathRate",
                 "coopDeathRate", "lifeTime", "eggPrice", "sellingPrice"]


###test print to see if all breeds/attributes have been loaded
#for breed in farm.breeds:
#    print(breed.name)
#    for att in breedAttributes:
#        print(att + ": " + getattr(breed,att))

incubator = farmLibrary.Incubator(0.9,100,0,0)
farm.setIncubator(incubator)  
##testing batch definition

batchTest=farmLibrary.Batch("batchTest",farm)
breeds={}

testproportions=[]
testproportions.append([.5,0,0])
testproportions.append([.5,0.25,0.25])
testproportions.append([25,0,0])
testproportions.append([50,5,5])
testproportions.append([float(1/3),float(1/3),0])


breeds=farm.breeds
print(type(breeds))
for testproportion in testproportions:
    breedsUsed={}
    print("test proportion: " + str(testproportion))
    for breed in breeds:
        breedsUsed[breed]=testproportion.pop(0)
    batchTest.setProportion(breedsUsed)
