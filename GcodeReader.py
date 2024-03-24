import re
from ReaderSupporClasses import Point as myPoint
from ReaderSupporClasses import StateObject as myState
from ReaderSupporClasses import Layer as myLayer
from ReaderSupporClasses import PathPoint as myPath
import sys,math

tol = 1e-5

###################################################################################################################################################
#Support Functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def updateX(inpString):
    reX = re.compile(r" X([-+]?\d+\.?\d*)",re.I)
    
  
    match=reX.search(inpString)        

    if match:
        val = match.group(1)
        fval=float(val)
        endPos=match.end() #Gives the end position in the string...
        return ('X',True,fval,endPos)
    else:
        return ('X',False,None,None)
           
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updateY(inpString):
    #reY = re.compile(r" Y([-+]?\d+\.?\d*?)[ /b]+",re.I|re.M)
    reY = re.compile(r"Y([-+]?\d+\.?\d*)",re.I)
    
    match=reY.search(inpString)        

    if match:
        val = match.group(1)
        fval=float(val)
        endPos=match.end() #Gives the end position in the string...    
        return ('Y',True,fval,endPos)
    else:
        return ('Y',False,None,None)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updateZ(inpString):
    reZ = re.compile(r" Z([-+]?\d+\.?\d*)",re.I)
    
    match=reZ.search(inpString)        
    
    if match:
        val = match.group(1)
        fval=float(val)
        endPos=match.end() #Gives the end position in the string...    
        return ('Z',True,fval,endPos)
    else:
        return ('Z',False,None,None)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updateF(inpString):

    reF = re.compile(r" F([-+]?\d+\.?\d*)",re.I)
    reW = re.compile(r" W([-+]?\d+\.?\d*)",re.I)
    
    
    match=reF.search(inpString)            
    
    if not match:
        return ('F',False,None,None)

    tableMatch = reW.search(inpString) #if F and W comes together then the F represents the motion of the table..
    if tableMatch:
        return ('F',False,None,None)               #which is ignored..
    

    val = match.group(1)
    fval=float(val)
    endPos=match.end() #Gives the end position in the string...    
    return ('F',True,fval,endPos)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updateE(inpString):
    reE = re.compile(r" E([-+]?\d+\.?\d*)",re.I)
    
    match=reE.search(inpString)        
    
    if match:
        val = match.group(1)
        fval=float(val)
        endPos=match.end() #Gives the end position in the string...    
        return ('E',True,fval,endPos)
    else:
        return ('E',False,None,None)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updatePumpSwitch(inpString):
    
    rePumpOn = re.compile(r"M101\b",re.I)
    rePumpOn2 = re.compile(r"M102\b",re.I) #This paramter has to be understoood For time being (4/19/2015) this is assumed to be turning the pump on....
    rePumpOff = re.compile(r"M103\b",re.I)

    matchOn1 = rePumpOn.search(inpString)
    matchOn2 = rePumpOn.search(inpString)
    matchOff = rePumpOff.search(inpString)

    #pumpSwitch = existingPumpState
    if matchOn1 or matchOn2:
        pumpSwitch = True
    elif matchOff:
        pumpSwitch = False

    #didItSwitch = existingPumpState ^ pumpSwitch
    return ('PS',True,pumpSwitch,0) #Improve

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updatePumpSwitchNL(inpString):
    #This code is for the national lab... they work with M62 and m64 for pumps and not m101 and m103 (which are extruders)

    #This function takes in both the existing pumpState checks whether the pump has been turned on or off...
    #This is added to fix the discrepancy in the ORNL path.. in which the pump still oozes out material even after it is turned off..
    #This lead to some materials not being activated...

    #The idea now is to understand whether the pump is switched on or off ..which is done using an exclusive or..
    #Once it is determined then if the pump is turned on .. then it is updated otherwise
    #The pump is only turned off when the next F is encountered..
    #This is a fix ..entirely specific to the ORNL data...
    
    rePumpOn = re.compile(r"\(Turn Pump ON\)",re.I)
    rePumpOff = re.compile(r"\(Turn Pump OFF\)",re.I)

    match1 = rePumpOn.search(inpString)
    match2 = rePumpOff.search(inpString)

    #pumpSwitch = existingPumpState
    if match1:
        pumpSwitch = True
    elif match2:
        pumpSwitch = False

    #didItSwitch = existingPumpState ^ pumpSwitch
    return ('PS',True,pumpSwitch,0) #Improve

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getDistanceCoords(x1,y1,x2,y2):
    d = (x1-x2)**2 + (y1-y2)**2
    dist = d**.5
    return dist
#main()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getDistance(P1,P2):
    d = (P1.x-P2.x)**2 + (P1.y-P2.y)**2 + (P1.z-P2.z)**2
    dist = d**.5
    return dist    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updateIdleTime(inpString):
    #This function matches the P values ...which represents the dead state...
    reDeadStP = re.compile(r" P(\d+\.?\d*?) ",re.I|re.M)
    reDeadStS = re.compile(r" S(\d+\.?\d*?) ",re.I|re.M)
    
    matchP=reDeadStP.search(inpString)            
    matchS=reDeadStS.search(inpString)

    if matchP:
        val = matchP.group(1)
        fval=float(val) #this value represents the time in milliSeconds..
        fval /= 1000.0
        endPos=matchP.end() #Gives the end position in the string... 
        return ('IT',True,fval,endPos)
    elif matchS:
        val = matchS.group(1)
        fval=float(val) #this value represents the time in seconds..        
        endPos=matchS.end() #Gives the end position in the string... 
        return ('IT',True,fval,endPos)
    else:
        return ('IT',False,None,None)


###################################################################################################################################################
# Main Function
###################################################################################################################################################

def CreateLayers(fileName,constWidth):


    print("Starting GCode Translator")
    
    if not fileName:
        return None

    #-----------------------
    #Input data
    #-----------------------
    f=open(fileName,'r')
    #f2=open("MotionStates.txt",'w')
    GcodeTxt= f.read()

    #-----------------------------------------------
    #Creting the GCommand dictionary 
    #The reader is the main dictionary with the information on what to to do after reading the first parameter....
    #The key will be the first field like G0,G01 or G11 .. which will be pointing to the appropriate read function...
    #-----------------------------------------------
    reader={}    
    reader['G01'] =  [updateX,updateY,updateZ,updateF,updateE]
    reader['G1']  =  [updateX,updateY,updateZ,updateF,updateE]
    reader['G0']  =  [updateX,updateY,updateZ,updateF,updateE]
    reader['M62'] =  [updatePumpSwitchNL,updateIdleTime] #This is for the pump to turn on... ORNL thing..
    reader['M63'] =  [updatePumpSwitchNL,updateIdleTime] #This is for the pump to turn off... ORNL thing..
    reader['M101'] = [updatePumpSwitch,updateIdleTime]
    reader['M103'] = [updatePumpSwitch,updateIdleTime]
    reader['G4'] = [updateIdleTime]


    #------
    #Globals
    #------ 
    Layers=[] #list of layers            
    


    #-----------------------------------------------------------------------
    #Getting the first point from the GCode data....
        #The code will be starting to look for the line with the first material deposit.    
        #The idea is to match code 64 or 101 and then look for the last state in the strings before the first match..
        #This will get the last point before the machine starts depositing material .. this is deemed as the first point before the material deposition starts
    #-----------------------------------------------------------------------

    repumpStart  = re.compile(r"M101\b.*?\n",re.I|re.M|re.DOTALL)
    rePumpSt2 = re.compile(r"M64\b",re.I)    
    pumpStMatch = repumpStart.search(GcodeTxt)
    pumpStMatch2=  rePumpSt2.search(GcodeTxt)
    
    
    if pumpStMatch: #Depending on various machines, the search code could be expanded
        pumpStindex =  pumpStMatch.start()
    elif pumpStMatch2:
        pumpStindex =  pumpStMatch2.start()
    else:
        raise ValueError,"The Gcode data is not found as expected when looking for the first instance for the extruder/pump start"

    x=None
    y=None
    z=None
    f=None
    
    MachineReadiness = GcodeTxt[:pumpStindex]
    reXval = re.compile(r" X([-+]?\d+\.?\d*)",re.I|re.M)
    reYval = re.compile(r" Y([-+]?\d+\.?\d*)",re.I|re.M)
    reZval = re.compile(r" Z([-+]?\d+\.?\d*)",re.I|re.M)
    reFval = re.compile(r" F([-+]?\d+\.?\d*)",re.I|re.M)
    reEval = re.compile(r" E([-+]?\d+\.?\d*)",re.I|re.M)
    ReValPos=[reXval,reYval,reZval]
    ReValRate = [reFval,reEval]
    firstPoint =[]

    for res in ReValPos:
        matches = res.findall(MachineReadiness)
        if matches:
            val = matches[-1]
            fval=float(val)
            firstPoint.append(fval)
        else:
            raise ValueError,"The Translator could not determine the x,y,z position before the Extruder was turned on"

    x,y,z=firstPoint[0],firstPoint[1],firstPoint[2]

    for res in ReValRate:
        matches = res.findall(MachineReadiness)
        if matches:
            val = matches[-1]
            fval=float(val)
            firstPoint.append(fval)
        else:
            firstPoint.append(0.0) #In case initial F and E are missing it is set to 0

    #startPoint = myPoint(x,y,z)
    startSpeed = firstPoint[3]    
    startPumpState = False
    startExtrudeRate = firstPoint[4]
    startIdleTime=0.0
    startAcceleration = False
    startState = myState(startIdleTime,x,y,z,startSpeed,startAcceleration,startPumpState,startExtrudeRate)


    #------------------------------------------------------------
    #Finding the Units....
        #G20 - inches
        #G21 - mm 
    #------------------------------------------------------------
    ReUnit = re.compile(r"^G20 ",re.I|re.M) 
    UnitMatch = re.search(ReUnit,MachineReadiness)
    if UnitMatch:
        print "\tUnits are in Inches"
        unitScale = 25.4
    else:
        print "\tUnits are in mm"
        unitScale = 1.0 # Not sure what to do with these now..




    #---------------------------------------
    #Finding the filament diameter..
        #Determining the cross section of the filament.
    #---------------------------------------
    if constWidth <=0.0:
        reFilDia = re.compile(r'Filament_Diameter.*: (\d*\.\d*)',re.I|re.M)
        fildiaMatch  = reFilDia.search(GcodeTxt)
        if fildiaMatch:
            filDia = fildiaMatch.group(1)
            filDia = float(filDia)
            print "\tthe filament dia was found to be  = ",filDia
        else:
            raise ValueError," The Gcode reader could not find the filament diameter\nAdd a comment of the form 'Filament_Diameter_(mm): 1.82' to the gCode file or use the constant width option"
        filXsection = 0.25*filDia*filDia*(math.pi)
    


    #-----------------------------------
    #Geting the rest of the Gcode block..
    #-----------------------------------

    ActiveGcodeTxt = GcodeTxt[pumpStindex:]
    linesinGcode = ActiveGcodeTxt.splitlines()
    motionStates = []
    motionStates.append(startState)


    # This is going to grasp the first line parameter...
    StartcodeRe=re.compile(r'(^\w*)')
    import copy
    
    for line in linesinGcode:

        line+="\n" #this is to match the end of line ..
        GcodeMatch = StartcodeRe.search(line)
        
        if GcodeMatch:
            command = GcodeMatch.group(1)
            command =command.upper()
        
        if not reader.has_key(command):
            continue

        FuncTocheck = reader[command] #this will give a list of function to match for...
        newState=copy.deepcopy(motionStates[-1]) #Only when the Gcode matches and the state has to be updated ..then the copy operation is done..

        # Idletime should be reverted back to 0...
        newState.setIdleTime(0.0)

        #This is still expensive.. should think about something better ... #Improve..        
        paramPos={} #This is a dictionary of parameter and position and is needed for determining acceleration.. Might have to be changed later..
        for funcs in FuncTocheck:

            #Fupdate = False
            #layer=myLayer(cnt)
            param,isNew,newVal,pos = funcs(line)

            #Now to get the appropriate update function from the motionState object
            if isNew :
                updateFunc = newState.updateParam(param)
            else:
                continue

            if param=='E'and constWidth<=0.0:
                newVal*=filXsection


            updateFunc(newVal)
            paramPos[param]=pos
        
                    
        if paramPos.has_key('F'):
            fpos= paramPos['F']
            newState.setAcceleration(False)
            keyList = paramPos.keys()
            keyList.remove('F')

            for ps in keyList:
                position = paramPos[ps]

                if position < fpos:
                    newState.setAcceleration(True)
                    break
        motionStates.append(newState)
    

    #Now to get the material deposition width for each pass..
    motionStates[0].width = 0.0
    motionStates[0].time = 0.0
    cumTime = 0.0

    #layerHeight = 1.0
    layerHeight = 1.0
    widthScaleFactor=1.0    

    for i in range(1,len(motionStates)):
        preState = motionStates[i-1]
        currState = motionStates[i]
        x1,y1 = currState.x,currState.y
        x2,y2 = preState.x,preState.y
        dist = getDistanceCoords(x1,y1,x2,y2)
        matDeposited =  currState.getE() - preState.getE()


        if dist and constWidth<=0.0:
            width = widthScaleFactor*matDeposited /(dist*layerHeight)
            currState.width = width
        elif dist and constWidth>0.0:
            width = constWidth
            currState.width = width
        elif not dist:
            currState.width = 0.0

        #Time Calculations..
        DeadState = currState.getIdleTime()
        Accel = currState.getAcceleration()

        if DeadState: #Dead state ..then add the necessary time
            cumTime +=DeadState
            currState.setTime(cumTime)
            continue
        
        if dist<=tol:
            prevTime = preState.getTime()
            currState.setTime(prevTime)
            continue
        
        v=currState.getF()
        u=preState.getF() 

        if Accel: #If acceleration found .. add the time for acceleration                   
            
            if abs(v - u) > tol:
                a = (v**2 - u**2)/(2*dist)
                t = (v - u)/a
                t*=60 #to change it to s
                cumTime+=t
                currState.setTime(cumTime)
            else: #constant velocity motion...
                t= dist/v #assuming that v is always going to be there ..
                t*=60 #To get time in 
                cumTime+=t
                currState.setTime(cumTime)

        else:  #constant velocity motion..
            t= dist/v #assuming that v is always going to be there ..
            t*=60 #To get time in 
            cumTime+=t
            currState.setTime(cumTime)
    
    #for mStates in motionStates:
    #    f2.write(str(mStates))
    #f2.close
    #----------------------------------------------------------------------------------------------------------------------------------------------    
    #The assumption is that when E changes that is where the model starts ...All other points are ignored...
    #Creating the layer object...
    Layers=[]
    
    heightNew=None
    bNewLayer = False


    #Creating the layers
    cnt=0
    totHeight=0.0
    for mStates in motionStates:
       MatWidth = mStates.width
       height = mStates.z

       if cnt==0 and MatWidth>tol:           
           newLayer = myLayer(0)
           newLayer.zPos = height           
           Layers.append(newLayer)          
           cnt+=1
           continue

       elif cnt>0 : 
           prevLayerHeight = Layers[cnt-1].zPos

           if prevLayerHeight < height and MatWidth>tol:
               newLayer = myLayer(cnt)
               newLayer.zPos = height
               newLayer.avgHeight = height-prevLayerHeight
               newLayer.modifiedZpos = height - 0.5*(height-prevLayerHeight)
               totHeight+= newLayer.avgHeight
               Layers.append(newLayer)          
               cnt+=1
               continue

    avgHeight = totHeight/(cnt-1)
        
    #Populating the layer with path points..
    for layer in Layers:
        
        height = layer.zPos
        for i in range(1,len(motionStates)):
            currState = motionStates[i]
            prevState = motionStates[i-1]


            if currState.width>tol and abs(currState.z-height)<tol:
                #Set the first path Point
                lenPaths = len(layer.pathPoints)
                if lenPaths==0:

                    if layer.layerNumber ==0:
                        timeToSubtract = prevState.time

                    X = prevState.x
                    Y = prevState.y
                    T = prevState.time - timeToSubtract
                    layer.setPathPoints(X,Y,T,0.0)

                    
                    XCurr= currState.x
                    YCurr= currState.y
                    TCurr= currState.time - timeToSubtract
                    WCurr= currState.width
                    layer.setPathPoints(XCurr,YCurr,TCurr,WCurr)

                #This is another important bug fix..
                #The issue was that while looking for only paths with positive width .. the start points were not being recognized
                # These are points which could be determined in two ways
                #Checking if the pumps were turned on or off at that point .. This method is not good becuase sometimes the pump turns on and does not move..
                #The other method is to see if the previous state has a width =0.0 then the previous point is added to the path..#More brainstorming needed..
                elif( lenPaths > 0 and prevState.width <tol):

                    X = prevState.x
                    Y = prevState.y
                    T = prevState.time - timeToSubtract
                    W = prevState.width 
                    layer.setPathPoints(X,Y,T,W)

                    #Adding data from the current path
                    X = currState.x
                    Y = currState.y
                    T = currState.time-timeToSubtract
                    W = currState.width
                    layer.setPathPoints(X,Y,T,W)
                
                
                elif( lenPaths > 0 and prevState.width >tol):
                    X = currState.x
                    Y = currState.y
                    T = currState.time-timeToSubtract
                    W = currState.width
                    layer.setPathPoints(X,Y,T,W)


    #Scaling the width to adjust for layer height..
    #The width for each path was determined by using unit layer height.
     
    if constWidth<=0.0:   
        for layer in Layers:
            for paths in layer.pathPoints:
                currWidthVal = paths.width
                
                if currWidthVal<tol:
                    paths.width = 0.0

                if currWidthVal > tol:     
                    a=math.pi*avgHeight*avgHeight*0.25                                   
                    newWidth = currWidthVal - a
                    newWidth /= avgHeight 
                    newWidth = newWidth + avgHeight
                    paths.width = newWidth


    print "\tnumber of layers = ",len(Layers)
    print "\tAverage height of layers = ",avgHeight
    print "Gcode Reader successful"
    
    
    #-------------------------------------------------------------------------------------------------------------------------------------------------    
    
    #Before beginning the origin has to be found out
    #And the start time has to be scaled...
    #All this data is obtained from the first Layer..


    #Determining the origin of the model..
        
    layer0 = Layers[0]
    modelOrigX = layer0.pathPoints[0].x
    modelOrigY = layer0.pathPoints[0].y
    modelOrigZ = layer0.zPos -avgHeight    
    layer0.modifiedZpos = modelOrigZ + 0.5* avgHeight
    
    modelOrigin = myPoint(modelOrigX,modelOrigY,modelOrigZ)
    
    layer0.setOrigin(modelOrigin)
    layer0.setAvgHeight(avgHeight)

    #Scaling the VAlues to mm...
    #for layer in Layers:
    #    layer.setUnits(unitScale)
        
    

    #--------
    #Writing the layer object dump
    #--------
    f2 = open('LayerObjectDump.txt','w')
    for layer in Layers:
        layer.setMinWidth() 
        f2.write(str(layer))    
    f2.close()

    
    return Layers


##################################################################################################################################################

