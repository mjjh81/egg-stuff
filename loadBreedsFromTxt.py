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

breed_path=os.getcwd()+'/breeds'
incubator_path=os.getcwd()+'/incubator'
brooder_path=os.getcwd()+'/brooder'
coop_path=os.getcwd()+'/coop'
farm_path=os.getcwd()+'/farm_parms'
ignoreTheseFiles=['.DS_Store']

def loadFromPath(path):
    fileTuples=[(None,None,path)]
    return LoadFilesFromTuples(fileTuples).getListOfListOfDicts()[0]

def loadBreeds():
    return loadFromPath(breed_path)

def loadIncubators():
    return loadFromPath(incubator_path)

def loadBrooders():
    return loadFromPath(brooder_path)

def loadCoops():
    return loadFromPath(coop_path)

def loadFarms():
    return loadFromPath(farm_path)


class LoadFilesFromTuples(object):
    def __init__(self, fileTuples=None):
        self.files=[]
        self.listoflistofdicts=[]
        if fileTuples is None:
            self.fileTuples=[]
        else:
            self.fileTuples=fileTuples
            self.getDictListsFromTuples()
                
    def getDictListsFromTuples(self):
        for fileTuple in self.fileTuples:
            self.files.append(TupleToFiles(fileTuple[0],fileTuple[1],fileTuple[2]).getFiles())
            
        self.convertFilesListToDictsList()
        
    def convertFilesListToDictsList(self):
        for fileList in self.files:
            tempDictList=[]
            for file in fileList:
                print(str(file))
                if file.split('/')[-1] in ignoreTheseFiles:
                    pass
                else:
                    tempDictList.append(self.convertFileToDict(file))
            self.listoflistofdicts.append(tempDictList)
                
    def convertFileToDict(self,filename):
        f = open(filename, 'r')
        d=dict()
        for line in f:
            line_data=line.split(',')
            d[line_data[0]] = line_data[1].rstrip()   
        return d
    
    def getListOfListOfDicts(self):
        return self.listoflistofdicts
        
class TupleToFiles(object):
    def __init__(self,filename=None, filetype=None, path=os.getcwd()):
        self.filename=filename
        self.filetype=filetype
        self.path=path
        self.files=[]
        self.createFilesFromTuple()
        
    def createFilesFromTuple(self):
        if self.filename is not None:
            if self.filetype is not None:
                for file in os.listdir(self.path):
                    if file.split('.')[0] == self.filename and file.split('.')[1]==self.filetype:
                        self.files.append(self.path + '/' + file)
            else:
                for file in os.listdir(self.path):
                    if file.split('.')[0]==self.filename:
                        self.files.append(self.path + '/' + file)             
        else:
            if self.filetype is not None:
                for file in os.listdir(self.path):
                    if file.split('.')[1] == self.filetype:
                        self.files.append(self.path + '/' + file)
            else:
                for file in os.listdir(self.path):
                    self.files.append(self.path + '/' + file)
                    
        
    def getFiles(self):
        return self.files
            
