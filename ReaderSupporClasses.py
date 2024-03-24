
#This file contains different support classes required for the translator..


############################################################################################################
#Class 1 -> State Class
###########################################################################################################
import copy
class StateObject(object):
    """description of class"""
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self,IdleTime= None,X=None,Y=None,Z=None,Rate=None,Acceleration=None,PumpState=None,ExtrudeRate=None,Time=None):
        self.idleTime= IdleTime
        self.x = X
        self.y = Y
        self.z = Z
        self.rate=Rate #This is the F parameter
        self.acceleration = Acceleration
        self.pumpSwitch=PumpState
        self.extrudeRate = ExtrudeRate #This is the E parameter..
        self.time=Time
        self.width = None
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def printState(self):        
        
        print "\nx = ",self.point.x,"  y = ",self.point.y," z = ",self.point.z," Feed Rate = ",self.rate, "Is pump On = ",self.pumpSwitch,\
            "ExtrudeRate = ",self.extrudeRate 

    ###################################################################################
    # GET FUNCTIONS 
    #######################

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getIdleTime(self):
        return self.idleTime

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getX(self):
        return self.x
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getY(self):
        return self.y
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getZ(self):
        return self.z
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getF(self):
        return self.rate
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getAcceleration(self):
        return self.acceleration
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getPumpState(self):
        return copy.deepcopy(self.pumpSwitch)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getE(self):
        return self.extrudeRate
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getTime(self):
        return self.time


    ###################################################################################
    # SET FUNCTIONS 
    #######################
    def setIdleTime(self,IdleTime):
        self.idleTime = IdleTime
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setX(self,xval):
        self.x = xval
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setY(self,yval):
        self.y = yval
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setZ(self,zval):
        self.z = zval
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setF(self,frate):
        self.rate = frate
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setAcceleration(self,Acceleration):
        self.acceleration = Acceleration
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    def setPumpState(self,pumpSw):
        self.pumpSwitch = pumpSw
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    def setE(self,ExtrudeRate):
        self.extrudeRate = ExtrudeRate
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    def setTime(self,Time):
        self.time = Time
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    
    ###################################################################################
    # SUPPORT FUNCTIONS 
    #######################    
    
    #This is only for setting up the x,y,z,f and E paramters .. with the idea that in future the I,J parameters will be added.
    #This will retrun the appropriate set functions ..and the arguments will be passed by the client code...
    #The input argument has to be a string of the form shown in the dictionary key .. 
    def updateParam(self,arg):
        paramDict={}
        paramDict['X']=self.setX
        paramDict['Y']=self.setY
        paramDict['Z']=self.setZ
        paramDict['F']=self.setF
        paramDict['E']=self.setE
        paramDict['IT']=self.setIdleTime
        paramDict['PS']=self.setPumpState
        return paramDict[arg]
        

        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #String representation.
    def __str__(self):
            
        str2return = "\n"+ "IdleT= "+str(self.idleTime).ljust(10)+ "  ,  "+"X= "+str(self.x).ljust(10)+ "  ,  " +"Y= "+str(self.y).ljust(10)+ "  ,  "+"Z= "+str(self.z).ljust(10) \
                +"  ,  "+"F= "+str(self.rate).ljust(10)+ "  ,  "+"IsA= "+str(self.acceleration)+"  ,  "+"Pump = "+str(self.pumpSwitch)+"  ,  "+"E= "+str(self.extrudeRate)+\
                "  ,  "+"W= "+str(self.width)+"  ,  "+"Time= "+str(self.time)
        
        return str2return
    



############################################################################################################
#Class 2 -> Layer Class
###########################################################################################################




#from stateObject import StateObject as myState
#from point import Point as myPoint
#from PathPoint import PathPoint as myPath

tol =0.001

class Layer(object):
    """description of class"""
    def __init__(self,LayerNumber):
        self.layerNumber = LayerNumber
        self.origin = None
        
        self.avgHeight=None        
        self.zPos = None
        self.modifiedZpos= None
        self.minWidth = None
        self.pathPoints=[]

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setOrigin(self,point):
        self.origin = point
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #The modified Zpos is requried to make the tip head travel through the thickness of the layer instead of being at the top
    #This is done by subtracting the half of the layer height from the zposition
    def setModifiedZpos(self,Zmodified):
        self.modifiedZpos = Zmodified

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setZpos(self,Z):
        self.zPos = Z
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setAvgHeight(self,height):
        self.avgHeight = height

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setOrigin(self,point):
        self.origin = point

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def appendState(self,state):
        self.motionStates.append(state)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def appendPathPoints(self,pathPoint):
        self.pathPoints.append(pathPoint)
    


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #def __repr__(self):
    #    print "\n\n\n----------------------------------------------------------------------"
    #    print "\n                  Layer Number = ", self.layerNumber
    #    print "\n----------------------------------------------------------------------"

    #    print "\n Layer Number = ",self.layerNumber
    #    print "\n\n  x  ,   y  ,  z  ,  F ,  pump\n"
    #    for m in self.motionStates:
    #        print "\n",m.getX,m.getY,m.getZ,m.getF,m.getPumpState            

        #        self.origin = None
        
        #self.avgHeight=None        
        #self.zPos = None
        #self.modifiedZpos= None
        #self.pathPoints=[]
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):

        if self.origin:
            origString = "\n Layer Origin = "+ str(self.origin.x)+ " , " + str(self.origin.y)+ " , " + str(self.origin.z)
        else:
            origString = ''

        str1=\
            "\n\n\n----------------------------------------------------------------------"+\
            "\n                  Layer Number = " + str(self.layerNumber) + \
            "\n----------------------------------------------------------------------"+\
            "\n Layer Number = "+str(self.layerNumber) + origString + \
            "\n Layer Zpos = "+ str(self.zPos) + \
            "\n Layer Modified zPos = "+str(self.modifiedZpos) + \
            "\n Layer height = " +str(self.avgHeight) +\
            "\n Layer Min Width = " +str(self.minWidth) +\
            "\n\n Path Points are ...... \n"+\
            "\nx                   y           Time              width"
        

        str2=''
        for paths in self.pathPoints:
            str2+="\n"+str(paths.x).ljust(10)+ "  ,  "+str(paths.y).ljust(10)+ "  ,  " +str(paths.t).ljust(10)+"  ,  " +str(paths.width).ljust(10)
        strRep = str1+str2

        return strRep


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setZPosFromLayer(self):

        if len(self.motionStates)==0:
            print 'The motion States are empty and Z position cannot be set'
            return
                
        for motionStates in self.motionStates:
            if motionStates.pumpSwitch:
                zPos = motionStates.getZ()
                self.setZpos(zPos)
                break
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setPathPoints(self,X,Y,T,Width):

        #The idea of Time Modifier is to subtract a certain value from the time..
        #normally the start time is not when the machine starts but a later value after the machine checks for readines..
        #This time is there in the motionStates object which is not useful from an analysis standPoint..
        x = X
        y=  Y
        t= T
        w = Width
        myPathPt = PathPoint(x,y,t,w)
        self.appendPathPoints(myPathPt)
        



    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # GET Functions ............
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getZpos(self):
        return float(self.zPos)

        


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Support Functions ............
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def setUnits(self,scaleFactor):
        
        if self.origin:
            self.origin.scale(scaleFactor)        
        self.avgHeight *=scaleFactor
        self.zPos *=scaleFactor
        self.modifiedZpos *=scaleFactor
        
        for pathPoints in self.pathPoints:
            pathPoints.x *=scaleFactor
            pathPoints.y *=scaleFactor

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setMinWidth(self): #This functions sets the minimum width for the layer.. this has to be used by the Translator code for Wgrid creation..
        wmin = self.pathPoints[1].width #the first path point width is 0.. assuming the second path point width as minimum..
        if wmin<tol:
            raise ValueError, "The minimum width cannot be 0....."

        for i in range(1,len(self.pathPoints)):
            w = self.pathPoints[i].width
            if wmin > w and w>tol:
                wmin =w

        if wmin<tol:
            raise ValueError, "The minimum width cannot be 0....."

        self.minWidth = wmin
        pass
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setWidthScale(self,scaleFactor):   #This is to scale the width of the path..

        if scaleFactor<=0.0:
            raise ValueError, "The scale factor for width should be positivie"
            return None
        for paths in self.pathPoints:
            paths.width*=scaleFactor

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setTimeScale(self,scaleFactor):  #This is to scale the time factor of the path...

        if scaleFactor<=0.0:
            raise ValueError, "The scale factor for width should be positivie"
            return None
        for paths in self.pathPoints:
            paths.t*=scaleFactor
      
            
############################################################################################################
#Class 3 -> PathPoint Class
###########################################################################################################      
class PathPoint(object):
    """description of class"""

    def __init__(self,X,Y,T,W):
        self.x = X
        self.y = Y
        self.t = T
        self.width = W
        





############################################################################################################
#Class 4 -> Point Class
###########################################################################################################     

class Point(object):
    """description of class"""

    def __init__(self,X,Y,Z):
        self.x = X
        self.y = Y
        self.z = Z

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def scale(self,Scale):
        self.x *= Scale
        self.y *= Scale
        self.z *= Scale
    #At some point add checks for floats...
