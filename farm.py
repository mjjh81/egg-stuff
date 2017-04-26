#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 15:22:17 2017

@author: hans
"""
import uuid

class Farm(object):
    def __init__(self,name):
        self.name = name
        
    def setIncubator(self, incubator):
        self.incubator=incubator
        
    def getIncubator(self):
        return self.incubator
    
    def setBrooder(self, brooder):
        self.brooder=brooder
        
    def getBrooder(self):
        return self.brooder
    
    def setCoop(self, coop):
        self.coop=coop
        
    def getCoop(self):
        return self.coop
    

class House(object):
    """
    House is any space where chickens are stored throughout their life
    Incubator, Brooder and Coop are the subclasses for now
    They will have a price per square/ft to construct
    An area, each chicken breed/phase will have a capacity within that space
    """
    def __init__(self, size, price = 0, cons = 0):
        self.size=size
        self.occupancy=Occupancy()
        self.price=price
        self.cons=0
        
    def getArea(self):
        return self.area
    
    def getPrice(self):
        return self.price
    
    def getSize(self):
        return self.size    
            
    
    
    
class Incubator(House):
    """
    Incubator has an energy consumption, price, hatch rate factor, size
    """
    def __init__(self,hatchRate):
        self.hatchRate=hatchRate
        
    def getHatchRate(self):
        return self.hatchRate
    

    
    
class RaisingHouse(House):
    """
    specifically for brooders and coops. Death rates are more day to day
    """
    def __init__(self,name,area):
        self.name=name
        self.area=area
    
        

class Brooder(RaisingHouse):
    """
    Brooders are for raising the chicks immediately after they leave the incubator
    They have a heating efficiency, require heat, but that's defined in a heating class
    """
    def __init__(self, heatingEffeciency = 1):
        self.heatingEffeciency=heatingEffeciency
        
class Coop(RaisingHouse):
    """
    Coops are where chickens are placed after brooders and where they preside
    until they die or are sold
    """
    def __init__(self,name):
        self.name=name
        
    def setLighting(self,light):
        self.light=light    
    
    
    
    
class Occupancy(object):
    """Occupancy class helps manage the cohorts within each housing
    providing the space occupied by the various cohorts, thus, the 
    space available for more. This should mainly be used to deal
    with the scheduling of the cohorts in the incubators
    """
    def __init__(self, size = 0):
        self.size=size
        self.cohorts={}
        
    def getAvailableSpace(self):
        total=0
        for cohort in self.cohorts:
            total+=cohort.getSizeOfCohort()
        return total
    
    def addCohort(self, cohort):
        self.cohorts[cohort.uuid]=cohort
                    
    def getCohort(self, cohortUUID):
        try:
            return self.cohorts[cohortUUID]
        except KeyError:
            return None
        
        

class Cohort(object):
    def __init__(self,house):
        self.chickens={}
        self.age=1
        self.house=house
        self.uuid=uuid.uuid4()
        
    def addChicken(self,chicken):
        self.chickens[chicken.getUUID()]=chicken
                      
    def addChickens(self,chickens):
        for chicken in chickens:
            self.addChicken(chicken)
            
    def getChicken(self,chicken):
        try:
            return self.chickens.get(chicken.getuuid())
        
        except KeyError:
            return None
                      
    def removeChicken(self,chicken):
        try:
            return self.chickens.pop(chicken.getUUID())
        except KeyError:
            return None
        
    def removeChickenWithUUID(self,UUID):
        try:
            return self.chickens.pop(UUID)
        except KeyError:
            return None
    
    def removeChickens(self,chickens):
        removedChickens=[]
        for chicken in chickens:
            removedChickens.append(self.removeChicken(chicken))
        return removedChickens
    
    def removeRandomNumberOfChickens(self,numberToRemove):
        if numberToRemove <= len(self.chickens):
            return self.removeAllChickens()
        else:
            removedChickens=[]
            listOfRandomChickens=random.shuffle(self.chickens.keys())[:numberToRemove]
            for chickenUUID in listOfRandomChickens:
                removedChickens.append(self.removeChickenWithUUID(chickenUUID))
            return removedChickens
    
    def removeAllChickens(self):
        removedChickens=[]
        for key in self.chickens.keys():
            removedChickens.append(self.chickens.pop(key))
        return removedChickens
    
    def getSizeOfCohort(self):
        return len(self.chickens)
    
    def incrementAge(self):
        self.age+=1
        
    def getAge(self):
        return self.age
    
    def changeHouse(self,house):
        self.house=house
        
    def getHouse(self):
        return self.house
        
    
        
        
