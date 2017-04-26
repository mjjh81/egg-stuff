#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 18:04:03 2017

@author: hans
"""

import farm

farmName="Test Farm Setup"
farm= farm.Farm(farmName)

breedAttributes=["name", "incubatorTime", "incubatorDeathRate", "brooderTime",
                 "brooderDeathRate", "coopReadyTime", "coopReadyDeathRate",
                 "coopDeathRate", "lifeTime", "eggPrice", "sellingPrice"]

for breed in farm.breeds:
    print(breed.name)
    for att in breedAttributes:
        print(att + ": " + getattr(breed,att))
    
