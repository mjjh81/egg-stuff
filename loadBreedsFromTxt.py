#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 14:38:10 2017

@author: hans

Creates a list of dictionaries each with attributes of their respective breeds
A path to the breeds folder can be given otherwise, the default is the
current path + '/breeds'
"""

import os


def load_breeds(path=None):
    loaded_breeds=[]
    if path is None:
        path=os.getcwd()+'/breeds'
        
    for filename in os.listdir(path):
            if filename.split('.')[1] == 'txt':
                loaded_breeds.append(convertFileToDict(path+'/'+filename))
                
    return loaded_breeds
                
def convertFileToDict(filename):
    f = open(filename, 'r')
    breedDict=dict()
    for line in f:
        line_data=line.split(',')
        print(line_data)
        breedDict[line_data[0]] = line_data[1].rstrip()
        
    return breedDict
