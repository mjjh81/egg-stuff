#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 15:22:17 2017

@author: hans
"""
import uuid
import random
import loadBreedsFromTxt
import math


"""
*******************************************************************************
*******************************************************************************
FARM CLASS TO MANAGE INDIVIDUAL SIMULATIONS
*******************************************************************************
*******************************************************************************
"""
class Simulation(object):
    """
    Keeps a dictionary of the farms and batches created so can easily mix and
    match the two
    """
    def __init__(self,name):
        self.name=name
        self.farms={}
        self.batches={}
        
    def addFarm(self,farm):
        self.farms[farm.name]=farm
    
    def getFarm(self,farm):
        return self.farms[farm.name]
        
    def addBatch(self,batch):
        self.batches[batch.name]=batch
    
    def getBatch(self,batch):
        return self.batches[batch.name]
    


"""
*******************************************************************************
*******************************************************************************
FARM CLASS TO MANAGE INDIVIDUAL SIMULATIONS
*******************************************************************************
*******************************************************************************
"""
class Farm(object):
    """
    The farm class is used to define the housing structures that the chickens
    will be processed through
    """
    def __init__(self,name):
        self.name = name
        self.loadBreeds()
        
    def loadBreeds(self):
        path=None
        loaded_breeds=loadBreedsFromTxt.load_breeds(path)
        self.breeds=Breed.dictsToBreed(loaded_breeds) 
        
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
    


"""
*******************************************************************************
*******************************************************************************
HOUSING CLASSES TO SETUP STRUCTURE FOR CHICKENS TO TRAVEL THROUGH
*******************************************************************************
*******************************************************************************
"""

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
    Incubator has an energy consumption, price, hatch rate, size
    """
    def __init__(self,hatchRate, size, price, cons):
        super().__init__(size, price, cons)
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
    
    
    
    
"""
*******************************************************************************
*******************************************************************************
CLASSES TO HELP MANAGE CHICKENS TRAVELING THROUGH THE STRUCTURES
*******************************************************************************
*******************************************************************************
"""    
    
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
    """
    Cohort is used to group chickens together and track them acroos the types
    housing. Each chicken is an item in a dictionary with the uuid acting as
    the key and the chicken object itself acting as the value
    
    Cohorts too have a uuid that used to track them across time and the housing
    units. The cohorts have a single age for each chicken within it.
    
    A cohort is first created with the max size that cohort will be. Afterwards
    the cohort can only decrease in size according to deathrates and when the
    chickens are sold.
    """
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
    
    
class Batch(object):
    def __init__(self, name, farm):
        self.name=name
        self.farm=farm
        self.cohorts={}
        self.setIncubatorSize()
        
    def setIncubatorSize(self):
        self.incubatorSize=self.farm.getIncubator().size
        
    def setBreeds(self,breeds):
        """
        breeds is a dictionary with the breeds as the key, and the 
        proportion of that batch that is the breed as the value
        
        the value of the dictionary can either be a % or a integer value
        representing the number of eggs in that batch of that breed
        """
        self.setProportion(breeds)
        
    def testPrintCohort(self, breeds):
        for key in breeds.keys():
            print("breed name: " + key.name + ", number: " + str(breeds[key]))
        
    def setProportion(self, breeds):
        """
        sets number of chickens per breed for the batch
        
        if only 1 breed then it will take all available space
        
        otherwise, a list is created based on descending values
        -if the largest value is greater than 1 then number of chickens
        per breed is set by those integer values with 0's in the list
        evenly splitting the remaining space
        -if the largest value is between 1 and 0 then number of chickens
        per breed is set by that proportion*self.incubatorSize with the
        0's in the list evenly splitting the remaining space
        
        both of these methods change the values in the dictionary to 
        integers that will be used to create the cohorts
        """
        self.breeds=breeds
        if len(breeds) == 1:
            self.breeds[self.breeds.key()[0]]=self.incubatorSize
            self.testPrintCohort(self.breeds)
            ##TODO: add to cohort method
        else:
            self.addCohortsWithDescendingValuesList(
                    sorted(breeds, key=breeds.get, reverse=True), self.incubatorSize)
                
    def addCohortsWithDescendingValuesList(self, keysOfDescendingValues, remaining):
        value=self.breeds[keysOfDescendingValues[0]]
        if len(keysOfDescendingValues)==1:
            self.breeds[keysOfDescendingValues[0]]=remaining
            ##TODO: add to cohort method
            self.testPrintCohort(self.breeds)
        elif value < 1 and value >0:
            self.convertProportionToInteger(keysOfDescendingValues, remaining)
            
        elif value > 1:
            self.addCohortsWithDescendingValuesList(keysOfDescendingValues[1:], remaining-value)
            
        elif value == 0:
            self.convertProportionToInteger(keysOfDescendingValues, remaining)
            
    
    def convertProportionToInteger(self, keysOfDescendingValues, remaining):
         number=round(self.breeds[keysOfDescendingValues[0]]*self.incubatorSize)
         delta=remaining-number
         if len(keysOfDescendingValues) == 1:
            self.breeds[keysOfDescendingValues.pop(0)]=remaining
            ##TODO: add to cohort method
            self.testPrintCohort(self.breeds)
         elif number == 0:
            number=round((1/len(keysOfDescendingValues))*remaining)
            self.breeds[keysOfDescendingValues.pop(0)]=number
            self.convertProportionToInteger(keysOfDescendingValues, remaining-number)
         elif delta >= 0:
            self.breeds[keysOfDescendingValues.pop(0)]=number
            self.convertProportionToInteger(keysOfDescendingValues,remaining-number)

             
             
            
              
          
    


"""
*******************************************************************************
*******************************************************************************
CLASSES ALL PERTRAINING TO CHICKENS AND THEIR ATTRIBUTES
*******************************************************************************
*******************************************************************************
"""   

    
class Breed(object):
    """
    Breed is the base class for any chicken
    All breed information is read in from txt files
    """
    
    def __init__(self, name, incubatorTime, incubatorDeathRate, brooderTime,
                 brooderDeathRate, coopReadyTime, coopReadyDeathRate,
                 coopDeathRate, lifeTime, eggPrice, sellingPrice):
        """
        Initializes a position with coordinates (x, y).
        """
        self.name=name
        self.incubatorTime=incubatorTime
        self.incubatorDeathRate=incubatorDeathRate
        self.brooderTime=brooderTime
        self.brooderDeathRate=brooderDeathRate
        self.coopReadyTime=coopReadyTime
        self.coopReadyDeathRate=coopReadyDeathRate
        self.coopDeathRate=coopDeathRate
        self.lifeTime=lifeTime
        self.eggPrice=eggPrice
        self.sellingPrice=sellingPrice
        
    @classmethod
    def dictToBreed(cls,breedDict):
        return cls(breedDict['name'], breedDict['incubatorTime'],breedDict['incubatorDeathRate'],
                      breedDict['brooderTime'], breedDict['brooderDeathRate'], 
                      breedDict['coopReadyTime'], breedDict['coopReadyDeathRate'], 
                      breedDict['coopDeathRate'], breedDict['lifeTime'],
                      breedDict['eggPrice'], breedDict['sellingPrice'])
        
    @classmethod
    def dictsToBreed(cls,listOfBreedDicts):
        listOfBreeds=[]
        for breedDict in listOfBreedDicts:
            listOfBreeds.append(Breed.dictToBreed(breedDict))
        return listOfBreeds
        
    """
    example reading in information...
    Path=None
    loaded_breeds=loadBreedFromTxt.load_breeds(Path)
    breeds=Breed.dictsToBreed(loaded_breeds) 
    """
    
class Chicken(Breed):
    """
    each instance of chicken for a specific breed is created once
    assigned a uuid then added to a cohort to be processed
    """
    def __init__(self):
        self.createUUID()
        
    def createUUID(self):
        self.uuid=uuid.uuid4()
        
    def getUUID(self):
        return self.uuid
    
        
        
