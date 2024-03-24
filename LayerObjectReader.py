
import re
from ReaderSupporClasses import Layer as myLayer
from ReaderSupporClasses import Point as myPoint


def CreateLayers(fileName,constWidth):

    constWidth=None #This width is not used. This argument is added so as to have consistency between the CreateLayer function in Gcode reader and Layer object reader


    f=open(fileName,'r')
    sLayer = f.read()
    Layers=[]
    srcStr1 =r"^                  Layer Number ="
    reLayerNums = re.compile(srcStr1,re.I|re.DOTALL|re.M)
    #lsLayers =re.findall(reLayerNums,sLayer)
    lSplitLayers = re.split(reLayerNums,sLayer)

    #---------
    #Getting the layer height
    #--------
    srcStr2 =r"step between layer =(.*)\n"
    reLayerNums = re.compile(srcStr2,re.I|re.M)
    srcStepSize = re.search(reLayerNums,sLayer)
    sStepSize =  srcStepSize.groups()[0]
    sStepSize = sStepSize.strip()
    steplayerHeight = float(sStepSize)


    LzPositions=[]
    avgLayerHeight=0.0
    cnt=0

    for layer in lSplitLayers[1:]:
    
        #Improvement .. Get the string till path points...
    
        #Get the layer number... 
        srcLayNum = r"^ Layer Number = (\d+)"
        reLayerNum = re.compile(srcLayNum,re.M|re.I)
        reLaySrch = re.search(reLayerNum,layer)
        layNum= int(reLaySrch.groups(1)[0])
        layNum-=1
        #print layNum
       

        #Get the layer position...
        srcLayPos = r"^ Layer Zpos = ([-+]?\d+\.?\d*)"
        reLayerZPos = re.compile(srcLayPos,re.M|re.I)
        reLayZpos = re.search(reLayerZPos,layer)
        layerZpos= float(reLayZpos.groups(1)[0])
        LzPositions.append(layerZpos)
        #print layerZpos


        #Get the main data block...
        sreBlock = r"power\n(.*?)\n\n"
        reBlock = re.compile(sreBlock,re.I|re.M|re.DOTALL)
        sBlock = re.search(reBlock,layer)
        #dataBlock = sBlock.groups(1)[0]
        #listDataBlocks = dataBlock.split("\n")
    
        currLayer= myLayer(layNum)
        currLayer.setZpos(layerZpos)
        currLayer.setAvgHeight(steplayerHeight)
        currLayer.setModifiedZpos(layerZpos)

        if sBlock==None:
            Layers.append(currLayer)
            continue
        else:
        
            dataBlock = sBlock.groups(1)[0]
            listDataBlocks = dataBlock.split("\n")
    
            for datalines in listDataBlocks:
                path = datalines.split(",")
                try:
                    x = float(path[0])
                    y = float(path[1])
                    t = float(path[2])
                    w = float(path[4])
                except:                    
                    break


                #

                currLayer.setPathPoints(x,y,t,w)

            try:
                currLayer.setMinWidth()           
            except:
                print currLayer.layerNumber,"Is the layer number"
                print currLayer

            Layers.append(currLayer)


    #Determining the layer height and average layer height..

    #f=open("NewLayerObject.txt",'w')
    #for layer in Layers:
    #    f.write(str(layer))
    #f.close()
    return Layers

#Ignore the first layer.. the split is based on that ..
#for layers in lsplitLayers[1:]:

















