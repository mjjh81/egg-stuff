#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 15:22:17 2017

@author: hans
"""
import uuid
import random
import loadTxtFile
import math

import tkinter as tk

"""
*******************************************************************************
*******************************************************************************
FARM CLASS TO MANAGE INDIVIDUAL SIMULATIONS
*******************************************************************************
*******************************************************************************
"""
class Simulation(object):
    """
    Simulation begins with this class. First all of the information is loaded
    from txt files for the breeds, incubators, brooders, coops and farm setups.
    
    The simulation then creates a GUI so that users can specify their simulation.
    A MVC scheme is used for the GUI retreive parameters for the simulation
    then display the results. To the controller, the simulation is a blackbox
    which gives the entire output of the simulation.
    """
    def __init__(self,name):
        self.name=name
        self.loadBreeds()
        self.loadIncubators()
        self.loadBrooders()
        self.loadCoops()
        self.loadFarmParms()
        
        self.addFarm()
        
    def loadBreeds(self):
        loaded_breeds=loadTxtFile.loadBreeds()
        self.breeds=Breed.dictsToBreed(loaded_breeds) 
        
    def loadIncubators(self):
        loaded_incubators=loadTxtFile.loadIncubators()
        self.incubators=Incubator.dictsToIncubator(loaded_incubators)
        
    def loadBrooders(self):
        loaded_brooders=loadTxtFile.loadBrooders()
        self.brooders=Brooder.dictsToBrooder(loaded_brooders)
        
    def loadCoops(self):
        loaded_coops=loadTxtFile.loadCoops()
        self.coops=Coop.dictsToCoop(loaded_coops)
        
    def loadFarmParms(self):
        loaded_farm_parms=loadTxtFile.loadFarms()
        self.farm_parms=FarmParm.dictsToFarmParm(loaded_farm_parms)
        
    def addMCV(self,name):
        root = tk.Tk()
        self.view = Application(master=root)
        self.model = GUIModel()
        
        self.controller = GUIController(self.model, self.view)
        self.controller.registerSim(self)
        self.controller.upload_to_model(self.breeds, self.incubators,
                                        self.brooders, self.coops, 
                                        self.farm_parms)
        
    """
    checks if the request has all fo the necessary information to build
    a "farm" and start the simulation process. Once the simulation has
    occured then all information is sent back to the controller to be
    displayed to the user
    """    
    def receiveRequestFromController(self,request):
        """
        checking for infomration of request if it checks out then
        create farm and start sim
        """
        
    """add 'request' to method as to come from GUI"""
    def addFarm(self):
        #farm name
        name = "test farm"
        #breed
        breed = self.breeds[0]
        #starting number of chickens
        starting_number = 12
        #age of chickens
        starting_age = 20
        #incubator
        incubator = self.incubators[0]
        #brooder
        brooder = self.brooders[0]
        #coop
        coop = self.coops[0]
        #farm parameters
        farm_parm = self.farm_parms[0]
        #sales strategy
            #eggs 0
            #meat 1
            #chicks 2
        sales = 2      
        #time to run simulation
        sim_time = 365
        
        farm = Farm(name, breed, starting_number, starting_age, incubator, brooder, coop,
                    farm_parm, sales, sim_time)
        
        self.farm=farm
        
        
    def getIncubators(self):
        return self.incubators
        
    def getCoops(self):
        return self.coops
    



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
    def __init__(self, name, breed, starting_number, starting_age, incubator, brooder, coop,
                    farm_parm, sales, sim_time):
        self.name = name
        self.breed = breed
        self.starting_number = starting_number
        self.starting_age = starting_age 
        self.incubator = incubator
        self.brooder = brooder
        self.coop = coop
        self.farm_parm = farm_parm
        self.sales = sales
        self.sim_time = sim_time
        self.chickens={}
        self.day=0
        
        self.dead = Dead("testDeath",100000000)
        self.setDeathRates()
        
        self.sold = Sold("testSold",100000000)
        
        self.eggBasket = EggBasket("testBasket",100000)
        
        self.account=Accounting(self)

        self.createStartingCohort()
        
    def setDeathRates(self):
        self.deathRates = {}
        
        self.deathRates["Incubator"] = math.pow(self.breed.incubatorDeathRate,
                                                (1/self.breed.incubatorTime))
        self.deathRates["Brooder"] = math.pow(self.breed.brooderDeathRate,
                                              (1/self.breed.brooderTime))
        self.deathRates["CoopReady"] = math.pow(self.breed.coopReadyDeathRate,
                                                (1/self.breed.coopReadyTime))
        self.deathRates["Coop"] = math.pow(self.breed.coopDeathRate,
                                          (1/(self.breed.lifeTime-self.breed.brooderTime-
                                              self.breed.coopReadyTime)))
        self.deathRates["Sold"] = None
        self.deathRates["Dead"] = None
                      
        
    def createStartingCohort(self):
        numberOfMales=math.ceil((1/self.breed.maleToFemaleRatio)*self.starting_number)
        maleCount=0
        
        for number in range(0,self.starting_number):
            chicken=Chicken(self.breed,self.day-self.starting_age)
            chicken.setLocationByAge(self.starting_age,self.incubator,self.brooder,
                                     self.coop, self.dead)
            if maleCount<numberOfMales:
                chicken.setSex(1)
                maleCount+=1
            else:
                chicken.setSex(0)
            self.chickens[chicken.getUUID()]=chicken
                          
        self.updateChickensLocationLog()
        self.dailyHappenings()
        
    def updateChickensLocationLog(self):
        for chicken in self.chickens.values():
            self.updateChickenLocationLog(chicken.updateLocationLog(self.day))
            
    def updateChickenLocationLog(self, chicken):
        chicken.updateLocationLog(self.day)
        
    def dailyHappenings(self):
        
        for chicken in self.chickens.values():
            sex=chicken.getSex()
            self.dailyDeath(chicken)
            self.dailyFeeding(chicken, sex)
            self.dailyLaying()
            
            #Vaccinating
            #TODO: add in vaccines and effect on death rate
            
        ##Sales specific management
        if self.sales=="Eggs":
            print("")
        elif self.sales=="Chicks":
            print("")
        elif self.sales=="Meat":
            print("")


        #Update day then go to next
        
    def dailyDeath(self, chicken):
        deathRate = self.deathRates[chicken.getLocationName()]
        print(deathRate)
        if type(deathRate) is float:
            if random.random() > deathRate:
                chicken.transferLocation("Dead",self.dead,self.day)
                print('chicken died')
                    
    def dailyFeeding(self, chicken, sex):
        locationName=chicken.getLocationName()
        if locationName == "Brooder":
            expense=self.breed.dailyStarterFood*self.farm_parm.foodStarterPrice
            self.account.expeneses.addExpense(expense, 'food', self.day)
            print("")
        elif locationName == "CoopReady":
            if sex == 0:
                expense=self.breed.dailyGrowerFood*self.farm_parm.foodGrowerPrice
                self.account.expeneses.addExpense(expense, 'food', self.day)
                print("")
            else:
                expense=self.breed.dailyHenFood*self.farm_parm.foodHenPrice
                self.account.expeneses.addExpense(expense, 'food', self.day)
                print("")
        elif locationName == "Coop":
            if sex == 0:
                expense=self.breed.dailyMashFood*self.farm_parm.foodMashPrice
                self.account.expeneses.addExpense(expense, 'food', self.day)
                print("")
            else:
                expense=self.breed.dailyHenFood*self.farm_parm.foodHenPrice
                self.account.expeneses.addExpense(expense, 'food', self.day)
                print("")
                    
    def dailyLaying(self, chicken, sex):
        if sex == 0:
            if chicken.getLocationName() == "Coop":
                if random.random() < (self.breed.eggProductionRate/365):
                    #TODO: add in fertility probability
                    egg=Chicken(self.breed,None)
                    egg.setLocationName("EggBasket")
                    self.chickens[egg.getUUID()]=egg
    
    
    def eggSalesManagement(self):
                            
            
                    


            
                
        
        
        
        
#    def loadBreeds(self):
#        loaded_breeds=loadTxtFile.loadBreeds()
#        self.breeds=Breed.dictsToBreed(loaded_breeds) 
#        
#    def loadIncubator(self):
#        loaded_incubator=loadTxtFile.loadIncubator()
#        self.setIncubator(Incubator.dictToIncubator(loaded_incubator[0]))
#        
#    def loadBrooder(self):
#        loaded_brooder=loadTxtFile.loadBrooder()
#        self.setBrooder(Brooder.dictToBrooder(loaded_brooder[0]))
#        
#    def loadCoop(self):
#        loaded_coop=loadTxtFile.loadCoop()
#        self.setCoop(Coop.dictToCoop(loaded_coop[0]))
#        
#    def setIncubator(self, incubator):
#        self.incubator=incubator
#        
#    def getIncubator(self):
#        return self.incubator
#    
#    def setBrooder(self, brooder):
#        self.brooder=brooder
#        
#    def getBrooder(self):
#        return self.brooder
#    
#    def setCoop(self, coop):
#        self.coop=coop
#        
#    def getCoop(self):
#        return self.coop
    
class Accounting(object):
    def __init__(self,farm):
        self.farm=farm
        self.revenues=Revenues(self)
        self.expeneses=Expenses(self)
        

class Revenues(object):
    def __init__(self, account):
        self.account=account
        self.revenues={}
        
    def addRevenue(self, amount, source, day):
        try:
            self.revenues[day].append(amount,source)
        except KeyError:
            self.revenues[day]=[(amount,source)]
            
class Expenses(object):
    def __init__(self, account):
        self.account=account
        self.expenses={}
        
    def addExpense(self, amount, source, day):
        try:
            self.expenses[day].append(amount,source)
        except KeyError:
            self.expenses[day]=[(amount,source)]
            
    
        

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
    def __init__(self, name, size, price = 0, cons = 0):
        self.name=name
        self.size=size
        self.occupancy=Occupancy()
        self.price=price
        self.cons=0
    
    def getPrice(self):
        return self.price
    
    def getSize(self):
        return self.size    
    
    
class Dead(House):
    def __init__(self,name, size):
        super().__init__(name, size)
        
class Sold(House):
    def __init__(self, name, size):
        super().__init__(name, size)
            
class EggBasket(House):
    def __init__(self,name,size):
        super().__init__(name, size)
    
class Incubator(House):
    """
    Incubator has an energy consumption, price, hatch rate, size
    """
    def __init__(self,hatchRate, name, size, price, cons):
        super().__init__(name, size, price, cons)
        self.hatchRate=hatchRate
        
    @classmethod
    def dictToIncubator(cls,incubatorDict):
        return cls(incubatorDict['hatchrate'],incubatorDict['name'],
                   incubatorDict['size'],incubatorDict['price'],
                   incubatorDict['cons'])
        
    @classmethod
    def dictsToIncubator(cls,listOfIncubatorDicts):
        listOfIncubators=[]
        for incubatorDict in listOfIncubatorDicts:
            listOfIncubators.append(Incubator.dictToIncubator(incubatorDict))
        return listOfIncubators
        
    def getHatchRate(self):
        return self.hatchRate
    
    
    
class RaisingHouse(House):
    """
    specifically for brooders and coops. Death rates are more day to day
    """
    def __init__(self,area, name, size, price, cons):
        super().__init__(name, size, price, cons)
        self.area=area
    
        

class Brooder(RaisingHouse):
    """
    Brooders are for raising the chicks immediately after they leave the incubator
    They have a heating efficiency, require heat, but that's defined in a heating class
    """
    def __init__(self, heatingEffeciency, area, name, size, price, cons):
        super().__init__(area, name, size, price, cons)
        self.heatingEffeciency=heatingEffeciency
        
    @classmethod
    def dictToBrooder(cls,brooderDict):
        return cls(brooderDict['heatingEfficiency'],brooderDict['area'],
                   brooderDict['name'],brooderDict['size'],brooderDict['price'],
                   brooderDict['cons'])
        
    @classmethod
    def dictsToBrooder(cls,listOfBrooderDicts):
        listOfBrooders=[]
        for brooderDict in listOfBrooderDicts:
            listOfBrooders.append(Brooder.dictToBrooder(brooderDict))
        return listOfBrooders
        
class Coop(RaisingHouse):
    """
    Coops are where chickens are placed after brooders and where they preside
    until they die or are sold
    """
    def __init__(self,partitions, area, name, size, price, cons):
        super().__init__(area, name, size, price, cons)
        self.partitions=partitions
        
    @classmethod
    def dictToCoop(cls,coopDict):
        return cls(coopDict['partitions'],coopDict['area'],
                   coopDict['name'],coopDict['size'],coopDict['price'],
                   coopDict['cons'])
        
    @classmethod
    def dictsToCoop(cls,listOfCoopDicts):
        listOfCoops=[]
        for coopDict in listOfCoopDicts:
            listOfCoops.append(Coop.dictToCoop(coopDict))
        return listOfCoops
    
    def setLighting(self,light):
        self.light=light   
        
    
class FarmParm(object):
    def __init__(self, marketDemandEggs, marketDemandChicks, marketDemandMeat,
                 foodStarterPrice, foodGrowerPrice, foodMashPrice,
                 foodHenPrice):
        self.marketDemandEggs=marketDemandEggs
        self.marketDemandChicks=marketDemandChicks
        self.marketDemandMeat=marketDemandMeat
        self.foodStarterPrice=foodStarterPrice
        self.foodGrowerPrice=foodGrowerPrice
        self.foodMashPrice=foodMashPrice
        self.foodHenPrice=foodHenPrice
        
    @classmethod
    def dictToFarmParm(cls,farmParmDict):
        return cls(farmParmDict['marketDemandEggs'], farmParmDict['marketDemandChicks'],
                   farmParmDict['marketDemandMeat'], farmParmDict['foodStarterPrice'],
                   farmParmDict['foodGrowerPrice'], farmParmDict['foodMashPrice'],
                   farmParmDict['foodHenPrice'])
        
    @classmethod
    def dictsToFarmParm(cls,listOfFarmParmDicts):
        listOfFarmParms=[]
        for farmParmDict in listOfFarmParmDicts:
            listOfFarmParms.append(FarmParm.dictToFarmParm(farmParmDict))
        return listOfFarmParms
    
    
    
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
        
        
class CohortHelper(object):
    
    def __init__(self, batchBreeds):
        self.cohortDict={}
        for batchItem in batchBreeds.items():
            tempCohort=Cohort(batchItem)
            self.cohortDict[tempCohort.getUUID()]=tempCohort
    
    def getCohortDict(self):
        return self.cohortDict
            

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
    def __init__(self, batchItem = None, house = None):
        if house is not None:
            self.house=house
        if batchItem is not None:
            self.initializeCohortFromBatchBreed(batchItem)
        self.chickens={}
        self.age=1
        self.uuid=uuid.uuid4()
        
    def initializeCohortFromBatchBreed(self, batchItem):
        for i in range(0,batchItem[1]):
            tempChicken=Chicken(batchItem[0])
            self.chickens[tempChicken.getUUID()]=tempChicken
    
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
    
    def getUUID(self):
        return self.uuid
    
    
class Batch(object):
    def __init__(self, name, farm):
        self.name=name
        self.farm=farm
        self.cohorts={}
        self.setIncubatorSize()
        self.breeds=self.farm.breeds
        
    def setIncubatorSize(self):
        self.incubatorSize=self.farm.getIncubator().size
        
    def setBreeds(self,breeds):
        """
        breeds is a dictionary with the breeds as the key, and the 
        proportion of that batch that is the breed as the value
        
        the value of the dictionary can either be a % or a integer value
        representing the number of eggs in that batch of that breed
        """
        self.breeds=breeds
        self.setProportion(breeds)
        
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
        
        TODO: setup an option to have a variable batch size
        """
        helper=ProportionHelper(self.breeds,self.incubatorSize)
        self.breeds=helper.getUpdatedBreeds()
        
        self.createCohortsFromBatchAmounts()
        
    def createCohortsFromBatchAmounts(self):
        self.cohorts=CohortHelper(self.breeds).getCohortDict()
            
                
            


class ProportionHelper(object):
    """
    Helper class taking in the breeds of the batch along with the predetermined
    proportions and total size of the batch to determine amounts for each breed
    
    The proportions can come as integers, float decimal proportions, or 0's in
    which case all of the 0's evenly split the remaining space in the batch
    
    If there is only 1 breed then it occupies the entire space
    
    With 2 or more breeds the keys are sorted in descending order according to
    their values. The integer values are kept while the float values are
    replaced with a round number of the float*batchSize. The remaining space
    is tracked so that the trailing 0's can evenly split the space
    """
    def __init__(self, breeds, batchSize):
        if len(breeds)==1:
            self.breeds[self.breeds.key()[0]]=batchSize
        else:
            self.breeds=breeds
            self.batchSize=batchSize
            self.keysOfDescendingValues=sorted(breeds, key=breeds.get, reverse=True)
            self.addCohortsWithDescendingValuesList(self.keysOfDescendingValues,batchSize)                    
        
    def addCohortsWithDescendingValuesList(self, keysOfDescendingValues, remaining):
        value=self.breeds[keysOfDescendingValues[0]]
        if len(keysOfDescendingValues)==1:
            self.breeds[keysOfDescendingValues[0]]=remaining
        elif value < 1 and value >0:
            self.convertProportionToInteger(keysOfDescendingValues, remaining)
            
        elif value > 1:
            self.addCohortsWithDescendingValuesList(keysOfDescendingValues[1:], remaining-value)
            
        elif value == 0:
            self.convertProportionToInteger(keysOfDescendingValues, remaining)
      
    def convertProportionToInteger(self, keysOfDescendingValues, remaining):
         number=round(self.breeds[keysOfDescendingValues[0]]*self.batchSize)
         delta=remaining-number
         if len(keysOfDescendingValues) == 1:
            self.breeds[keysOfDescendingValues.pop(0)]=remaining
         elif number == 0:
            number=round((1/len(keysOfDescendingValues))*remaining)
            self.breeds[keysOfDescendingValues.pop(0)]=number
            self.convertProportionToInteger(keysOfDescendingValues, remaining-number)
         elif delta >= 0:
            self.breeds[keysOfDescendingValues.pop(0)]=number
            self.convertProportionToInteger(keysOfDescendingValues,remaining-number)
              
    def getUpdatedBreeds(self):
        return self.breeds
          
    def testPrintCohort(self, breeds):
        for key in breeds.keys():
            print("breed name: " + key.name + ", number: " + str(breeds[key]))    


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
                 coopDeathRate, lifeTime, eggPrice, sellingPrice, eggCost,
                 chickPrice, maleToFemaleRatio, fertilityRate, eggProductionRate,
                 sellingFertilePrice, sellingSexed, sexedAge, brooderSpace,
                 kibandaSpace,dailyStarterFood,dailyGrowerFood,dailyMashFood,
                 dailyHenFood):
        """
        Initializes a position with coordinates (x, y).
        """
        self.name=name
        self.incubatorTime=float(incubatorTime)
        self.incubatorDeathRate=float(incubatorDeathRate)
        self.brooderTime=float(brooderTime)
        self.brooderDeathRate=float(brooderDeathRate)
        self.coopReadyTime=float(coopReadyTime)
        self.coopReadyDeathRate=float(coopReadyDeathRate)
        self.coopDeathRate=float(coopDeathRate)
        self.lifeTime=float(lifeTime)
        self.eggPrice=float(eggPrice)
        self.sellingPrice=float(sellingPrice)
        self.eggCost=float(eggCost)
        self.chickPrice=float(chickPrice)
        self.maleToFemaleRatio=float(maleToFemaleRatio)
        self.fertilityRate=float(fertilityRate)
        self.eggProductionRate=float(eggProductionRate)
        self.sellingFertilePrice=float(sellingFertilePrice)
        self.sellingSexed=float(sellingSexed)
        self.sexedAge=float(sexedAge)
        self.brooderSpace=float(brooderSpace)
        self.kibandaSpace=float(kibandaSpace)
        self.dailyStarterFood=float(dailyStarterFood)
        self.dailyGrowerFood=float(dailyGrowerFood)
        self.dailyMashFood=float(dailyMashFood)
        self.dailyHenFood=float(dailyHenFood)
        
        
    @classmethod
    def dictToBreed(cls,breedDict):
        return cls(breedDict['name'], breedDict['incubatorTime'],breedDict['incubatorDeathRate'],
                      breedDict['brooderTime'], breedDict['brooderDeathRate'], 
                      breedDict['coopReadyTime'], breedDict['coopReadyDeathRate'], 
                      breedDict['coopDeathRate'], breedDict['lifeTime'],
                      breedDict['eggPrice'], breedDict['sellingPrice'],
                      breedDict['eggCost'], breedDict['chickPrice'],
                      breedDict['maleToFemaleRatio'], breedDict['fertilityRate'],
                      breedDict['eggProductionRate'], breedDict['sellingFertilePrice'],
                      breedDict['sellingSexed'], breedDict['sexedAge'],
                      breedDict['brooderSpace'], breedDict['kibandaSpace'],
                      breedDict['dailyStarterFood'], breedDict['dailyGrowerFood'],
                      breedDict['dailyMashFood'], breedDict['dailyHenFood'])
        
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
    
class Chicken(object):
    """
    each instance of chicken for a specific breed is created once
    assigned a uuid then added to a cohort to be processed
    """
    def __init__(self, breed, birthday):
        self.breed=breed
        self.birthday=birthday
        self.createUUID()
        self.locationByDay={}
        
    def createUUID(self):
        self.uuid=uuid.uuid4()
        
    def setSex(self,sex):
        #female: 0, male: 1
        self.sex=sex
        
    def getSex(self):
        return self.sex
        
    def getUUID(self):
        return self.uuid
    
    def setLocation(self, location):
        self.location=location
        
    def setLocationName(self, name):
        self.locationName=name
        
    def getLocation(self):
        return self.location
    
    def getLocationName(self):
        return self.locationName
    
    def getBirthday(self):
        return self.birthday
    
    def setLocationByAge(self, day, incubator, brooder, coop, dead):
        age = day - self.birthday
        if age < self.breed.incubatorTime:
            self.locationName="Incubator"
            self.location=incubator
        elif age < (self.breed.brooderTime + self.breed.incubatorTime):
            self.locationName="Brooder"
            self.location=Brooder
        elif age < (self.breed.coopReadyTime + self.breed.brooderTime + 
                    self.breed.incubatorTime):
            self.locationName="CoopReady"
            self.location=coop
        elif age < (self.lifeTime - self.breed.incubatorTime):
            self.locationName="Coop"
            self.location=coop
        else:
            self.locationName="Dead"
            self.location=dead
        
        self.updateLocationLog(day)
        
    def updateLocationLog(self,currentDay):
        if currentDay == 0:
            self.locationByDay[currentDay]=(self.location,self.locationName)
        else:
            try:
                if self.location[currentDay-1] is not None:
                    self.locationByDay[currentDay]=(self.location,self.locationName)
            except KeyError:
                self.locationByDay[currentDay]=(self.location,self.locationName)
                self.updateLocationLog(currentDay-1)
                
            
    def transferLocation(self,locationName, location, day):
        self.locationName=locationName
        self.location=location
        self.updateLocationLog(day)
        
    

"""
*******************************************************************************
*******************************************************************************
GUI CLASSES
*******************************************************************************
*******************************************************************************
"""

class GUIModel(object):
    def __init__(self):
        self.loaded_information = {
                "breeds" : []}
        self.GUI_information = {
                "chicken_number_entry" : [],
                "breed_entry" : [],
                }

class GUIController(object):
    def __init__(self, model, view):
        self.model=model
        self.view=view
        
        self.view.register(self)
        
    def registerSim(self,sim):
        self.sim=sim
        
    def upload_to_model(self):
        for breed in farm.breeds:
            self.model.loaded_information["breeds"].append(breed)
            
    def get_breeds(self):
        breed_list = []
        for breed in self.model.loaded_information["breeds"]:
            breed_list.append(breed)
            
        return breed
        
        
        
"""
Welcome window to introduce model. Capabilities, limitations, etc.
"""
class Welcome(tk.Frame):
    def __init__(self,master=None):
        tk.Frame.__init__(self,master)
        self.root=master
        self.setup_window()
        
    def setup_window(self):
        
        welcome_text="Hello. This is a temporary introduction. Click Continue"
        continue_button_text="continue"
        quit_button_text="quit"
        
        self.welcome_label = tk.Label(self.root)
        self.welcome_label["text"] = welcome_text
        self.welcome_label.grid(row=0)
        
        self.continue_button = tk.Button(self.root)
        self.continue_button["text"] = continue_button_text
#        self.continue_button["command"] = self.continue_from_welcome
        self.continue_button.grid(row=1)
        
        self.quit_button = tk.Button(self.root)
        self.quit_button["text"] = quit_button_text
        self.quit_button.grid(row=2)      
        
#    def continue_from_welcome(self):
#        try:
#            self.welcome_label.destroy()
#            self.continue_button.destroy()
#            self.quit_button.destroy()
#            print("about to try continue method")
#            
#        except:
#            print("Something Went Wrong")
            
"""
Typical Toolbar setup
"""        
class Toolbar(tk.Frame):
    def __init__(self,frame):
#        super().__init__(master)
#        self.root=master
        self.frame=frame
        self.setup_menu()
        
    def setup_menu(self):
        save_button_text = "save"
        reset_button_text = "reset"
        quit_button_text = "quit"
    
        self.save_button = tk.Button(self.frame)
        self.save_button["text"] = save_button_text
        self.save_button.pack(side="left")
                        
        self.reset_button = tk.Button(self.frame)
        self.reset_button["text"] = reset_button_text
        self.reset_button.pack(side="left")
                        
        self.quit_button = tk.Button(self.frame)
        self.quit_button["text"] = quit_button_text
        self.quit_button.pack(side="left")
                        


"""
Displaying informaiton, area for user to input information
"""        
class Main(tk.Frame):
    def __init__(self,frame):
#        super().__init__(master)
#        self.root=master
        self.frame=frame
        
        self.setup_sub_frames()
        
    def setup_sub_frames(self):
        self.chicken_sub_frame=tk.Frame(self.frame)
        self.chicken_sub_frame.pack(side = "left")
        
        
        
        self.chicken_frame(self.chicken_sub_frame)
        
        
        
    def chicken_frame(self,frame):
        heading_label_text = "Choose Starting Number Of Chickens and Breed"
        self.heading_label=tk.Label(frame)
        self.heading_label["text"] = heading_label_text
        self.heading_label.pack(side = "top")
        
        chicken_number_title_text = "Starting Number Of Chickens"
        self.chicken_number_title = tk.Label(frame)
        self.chicken_number_title["text"] = chicken_number_title_text
        self.chicken_number_title.pack(side = "left")
        
                          
        default_chicken_number = 6
        self.chicken_number_entry = tk.Entry(frame)
        self.chicken_number_entry.pack(side = "right")
        self.chicken_number_entry.insert(0, default_chicken_number)
        
        
        
    
"""
Help flip through tabs of information in the main window
"""    
class Navigation(tk.Frame):
    def __init__(self,frame):
#        super().__init__(master)
#        self.root=master
        self.frame=frame
        
        self.text=tk.Label(frame,text="example text")
        self.text.pack(side="left")
        
"""
controlling all of the subwindows 
"""
class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self,master)
#        self.pack()
        self.root=master
#        self.size_window()
        self.welcome=Welcome(self.root)
        self.welcome.continue_button.bind("<Button>",self.continue_from_welcome)
        self.welcome.quit_button.bind("<Button>",self.quit_from_welcome)
        ##self.create_widgets()\   
        
    def register(self,controller):
        self.controller=controller
        
    def continue_from_welcome(self, event):
        self.welcome.welcome_label.destroy()
        self.welcome.continue_button.destroy()
        self.welcome.quit_button.destroy()
        
        toolbarFrame = tk.Frame(self.root, bd=2)
        toolbarFrame.pack(side="top", padx=5, pady=5)
        navFrame = tk.Frame(self.root, bd=2)
        navFrame.pack(side="left", fill="y", padx=5, pady=5)        
        mainFrame = tk.Frame(self.root, bd=2)
        mainFrame.pack(side="right",fill="both",expand=True, padx=5, pady=5)
        
        self.setup_toolbar(toolbarFrame)
        self.setup_nav(navFrame)
        self.setup_main(mainFrame)
        
#        self.toolbar.pack(side="top", fill="x") 
#        self.nav.pack(side="left", fill="y")
#        self.main.pack(side="right",fill="both",expand=True)  
        
    def setup_toolbar(self,frame):
        self.toolbar = Toolbar(frame)
#        self.toolbar.save_button.bind("<Button>",self.save_from_toolbar)
#        self.toolbar.reset_button.bind("<Button>",self.reset_from_toolbar)
#        self.toolbar.quit_button.bind("<Button>",self.quit_from_toolbar)
        
       
    def setup_nav(self,frame):
        self.nav = Navigation(frame)
        
        
    def setup_main(self,frame):
        self.main = Main(frame)
              
    
    def quit_from_welcome(self, event):
        self.root.destroy()

    def register(self,controller):
        self.controller = controller



    """
    adding different tabs depending on the information to be displayed...
    perhaps change to all information being displayed on a single page.
    """
    
    def set_tabs(self):
        self.tabs={}
        self.tabs['breeds']=0
        self.tabs['housing']=1
        self.tabs['simulation']=2
                 
        self.set_tab_buttons()
                 
    def set_tab_buttons(self):
#        self.create_tab_button("tab1",0)
        colNum=0
        for tab_name in self.tabs.keys():
            self.create_tab_button(tab_name,colNum)
            colNum+=1
            
    def create_tab_button(self,tab_name,colNum):
        self.tab_button=tk.Button(self)
        self.tab_button["text"]=tab_name
        self.tab_button.grid(row=0,column=colNum)
    
    def size_window(self):
#        window_width=500
#        window_height=500
        self.root.geometry('{}x{}'.format(500,500))
        
    def add_simulation(self, sim):
        self.simulations[sim.name]=sim
        
    def create_breed_display(self,farm):
        self.loadedBreeds=farm.breeds
        
#        self.checkbox=tk.Checkbutton(self,text=self.loadedBreeds[0].name).grid(row=0)
        
#        self.hi_there = tk.Button(self)
#        self.hi_there["text"] = self.loadedBreeds[0].name
#        self.hi_there["command"] = self.say_hi
#        self.hi_there.pack(side="top")

        rowNum=1
        for breed in self.loadedBreeds:
            self.add_breed_checkbox(breed,rowNum)
            rowNum+=1
            
        self.quit = tk.Button(self, text="QUIT", fg="red", command=self.root.destroy)
        self.quit.grid(row=rowNum)
            
        
    def add_breed_checkbox(self, breed, rowNum):
        self.checkbox=tk.Checkbutton(self,text=breed.name).grid(row=rowNum)

    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.destroy)
        self.quit.pack(side="bottom")

    def say_hi(self):
        print("hi there, everyone!")


class Tab(object):
    def __init__(self,name):
        self.name=name
        self.row={}
        self.col={}
        
class BreedTab(Tab):
    def __init__(self,tab_name,breeds):
        super.__init__(tab_name)
        self.breeds=breeds
        self.heading="Select breeds for Simulation"
        
#root = tk.Tk()
#app = Application(master=root)
#app.mainloop()
    
        
        
