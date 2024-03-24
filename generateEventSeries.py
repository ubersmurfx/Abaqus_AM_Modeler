
#--------------
# Main Function
#------------


if __name__ =="__main__":
#def main():

    import os,sys

    #---------
    #Handling arguments
    #---------
    if len(sys.argv)!=5:
        print("The python script should be called with 4 arguments - 'generateEventSeries.py toolPathFileName rollerPadDimension delayBetweenLayers powerOftheLaser' Eg generateEventSeries.py cube.gCode 0.5 10 400")
        exit()

    fileName  = sys.argv[1] 
    rollerPad = sys.argv[2] 
    userDelay = sys.argv[3] 
    userPower = sys.argv[4] 

    #fileName = 'Model-Horizontal.gcode'
    #rollerPad = .5

    #userDelay=10
    #userPower=300

    try:
        rollerPad = float(rollerPad)
    except:
        print ("The roller pad value should be a float")
        exit()

    try:
        userDelay = float(userDelay)
    except:
        print ("The delayBetweenLayers value should be a float")
        exit()

    try:
        userPower = float(userPower)
    except:
        print ("The power value should be a float")
        exit()


    if not os.path.isfile(fileName):
        print ("The file path does not exist")
        exit()
    head,onlyFileName = os.path.split(fileName)


    #-----
    #Importing the appropriate reader
    #--------
    neutralFormList = ['txt','npf','sim']
    if onlyFileName[-3:].lower() in neutralFormList:
        onlyFileName = onlyFileName[:-4]
        import LayerObjectReader as myGcode
    
    elif onlyFileName[-5:].lower() =='gcode' or gCodeFileName[-2:].lower() =='nc':
        if onlyFileName[-5:].lower() =='gcode':
            onlyFileName = onlyFileName[:-6]
        else:
            onlyFileName = onlyFileName[:-3]
        import GcodeReader as myGcode

    constWidth= 0.0
    Layers = myGcode.CreateLayers(fileName,constWidth)


    #-----------------
    #Writing the Event Series data
    #-----------------

    PowerFile = onlyFileName+"_EventSeries_Power.inp"
    RollerFile =onlyFileName+"_EventSeries_Roller.inp"
    f1=open(PowerFile,'w')
    f2= open(RollerFile,'w')
    tPrev=0.0

    #-----
    #Getting the yMin.yMax for all the layers
    #-------



    ymin,ymax=None,None
    for layer in Layers:
        if len(layer.pathPoints)==0:
            continue

        for path in layer.pathPoints:
            y = path.y                    
            ymin = y
            ymax=y
            break

    try:
        v1= float(ymin)
        v2 =float(ymax)
    except:
        raise ValueError("The minimum y value of the layers could not be determined the plugin will now exit")
        sys.exit()



    for layer in Layers:
        if len(layer.pathPoints)==0:
            continue

        for path in layer.pathPoints:
            y = path.y

            if ymin > y:
                ymin=y
            if ymax<y:
                ymax=y

    range = ymax- ymin
    ymin -= rollerPad*range
    ymax+= rollerPad*range

    modifiedlayerStartTime = 0
    prevLayerEndTime = 0
    

    #Modifying time for user delay
    for layer in Layers:
        if len(layer.pathPoints)==0:
            continue

        modifiedlayerStartTime=prevLayerEndTime+userDelay          
        originalLayerStartTime = 0.0+layer.pathPoints[0].t

        layer.pathPoints[0].t = modifiedlayerStartTime

        cnt=0
        lPathPoints = layer.pathPoints
        for path in lPathPoints[1:]:
            cnt+=1
            currTime = 0.0+path.t
            newTime = modifiedlayerStartTime+currTime-originalLayerStartTime 
            path.t= newTime
        prevLayerEndTime=lPathPoints[-1].t


    for layer in Layers:

        if len(layer.pathPoints)==0:
            continue
        
        z=layer.modifiedZpos + 0.5*layer.avgHeight
        xAv= 0.0
        tCurr = layer.pathPoints[0].t
        vecPow = []


        #--------
        #Switching the power by one row
        #---------
        lPathPoints = layer.pathPoints
        for path in lPathPoints[1:]:
            vecPow.append(path.width)
        vecPow.append(0.0)

        #for path in layer.pathPoints:
        pathCnt=-1       
        for path in layer.pathPoints:
            pathCnt+=1
            x=  path.x
            y = path.y
            t = path.t
            pow = vecPow[pathCnt] #This is used to store power for .npf file
            
            if pow>0 and userPower>0:
                pow = userPower
            f1.write(str(t)+","+str(x)+","+str(y)+","+str(z)+","+str(pow)+"\n")        

        xAv/=len(layer.pathPoints)

       
        f2.write(str(tPrev)+","+str(xAv)+","+str(ymin)+","+str(z)+",1\n")
        f2.write(str(tCurr)+","+str(xAv)+","+str(ymax)+","+str(z)+",0\n")

        tPrev = layer.pathPoints[-1].t
        
    f1.close()
    f2.close()
    #f3.close()

    print ("Successfully generated the Event Series files \n"+PowerFile +"\n"+RollerFile+"\n")

#main()