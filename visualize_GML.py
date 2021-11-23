#!/usr/bin/env python
# coding: utf-8

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib import cm

import xml.etree.ElementTree as ET
import numpy as np
from pyproj import Proj, transform
import re
import math
import sys
import time

'''
Just Draw a gml, no CRS transformation included.
'''
def drawXML(fileName,figureName,myDPI):
    # change the font size here if needed
    plt.rcParams.update({'font.size': 14})

    # read xml
    tree = ET.parse(fileName)
    root = tree.getroot()

    # nameSpace used for ElementTree's search function
    # CityGML 1.0
    _nameSpace1 = {'core':"http://www.opengis.net/citygml/1.0",
    'gen':"http://www.opengis.net/citygml/generics/1.0",
    'grp':"http://www.opengis.net/citygml/cityobjectgroup/1.0",
    'app':"http://www.opengis.net/citygml/appearance/1.0",
    'bldg':"http://www.opengis.net/citygml/building/1.0",
    'gml':"http://www.opengis.net/gml",
    'xal':"urn:oasis:names:tc:ciq:xsdschema:xAL:2.0",
    'xlink':"http://www.w3.org/1999/xlink",
    'xsi':"http://www.w3.org/2001/XMLSchema-instance"}

    # CityGML 2.0
    _nameSpace2 = {'core':"http://www.opengis.net/citygml/2.0",
    'gen':"http://www.opengis.net/citygml/generics/2.0",
    'grp':"http://www.opengis.net/citygml/cityobjectgroup/2.0",
    'app':"http://www.opengis.net/citygml/appearance/2.0",
    'bldg':"http://www.opengis.net/citygml/building/2.0",
    'gml':"http://www.opengis.net/gml",
    'xal':"urn:oasis:names:tc:ciq:xsdschema:xAL:2.0",
    'xlink':"http://www.w3.org/1999/xlink",
    'xsi':"http://www.w3.org/2001/XMLSchema-instance"}

    # check the version of CityGML
    with open(fileName,"r") as fileHandle:
        version = 0
        for line in fileHandle.readlines():
            #print("current line = ",line)
            if str(line).find("citygml/1.0")!= -1:
                _nameSpace = _nameSpace1
                version = 1
                print("CityGml Version = 1.0")
                break
            elif str(line).find("citygml/2.0")!= -1:
                _nameSpace = _nameSpace2
                version = 2
                print("CityGML Version = 2.0")
                break
        # end loop 
        if version == 0:
            print("CityGML Version Not Supported.")
            return -1

    roof_list = []
    foot_list = []
    wall_list = []

    num_building = 0
    for bldg in root.findall('.//bldg:Building',_nameSpace):
        num_building += 1
        for pts in bldg.findall('.//bldg:RoofSurface//gml:posList',_nameSpace):
            posList = np.array(str(pts.text).split(' '))
            posList = posList.astype(np.float)
            roof = []
            for j in range(int(len(posList)/3)):
                pt = [posList[3*j],posList[3*j+1],posList[3*j+2]]
                roof.append(pt)
            roof_list.append(roof)
        for pts in bldg.findall('.//bldg:GroundSurface//gml:posList',_nameSpace):
            posList = np.array(str(pts.text).split(' '))
            posList = posList.astype(np.float)
            foot = []
            for j in range(int(len(posList)/3)):
                pt = [posList[3*j],posList[3*j+1],posList[3*j+2]]
                foot.append(pt)
            foot_list.append(foot)
        for pts in bldg.findall('.//bldg:WallSurface//gml:posList',_nameSpace):
            posList = np.array(str(pts.text).split(' '))
            posList = posList.astype(np.float)
            wall = []
            for j in range(int(len(posList)/3)):
                pt = [posList[3*j],posList[3*j+1],posList[3*j+2]]
                wall.append(pt)
            wall_list.append(wall)

    print("Extracted " + str(num_building) + " Buildings.")
    print("Extracted " + str(len(roof_list)) + " roof surfaces.")
    print("Extracted " + str(len(foot_list)) + " foot prints.")
    print("Extracted " + str(len(wall_list))+ " wall surfaces.")


    minRange = np.array([0,0,0])
    maxRange = np.array([0,0,0])

    totalPts = []
    for roof in roof_list:
        for pt in roof:
            totalPts.append(pt)
    for foot in foot_list:
        for pt in roof:
            totalPts.append(pt)
    for wall in wall_list:
        for pt in roof:
            totalPts.append(pt)
    
    totalPts = np.array(totalPts)

    minRange = [np.amin(totalPts[:,0]),np.amin(totalPts[:,1]),np.amin(totalPts[:,2])]
    maxRange = [np.amax(totalPts[:,0]),np.amax(totalPts[:,1]),np.amax(totalPts[:,2])]

    #---------------------------------------------------------------------------------------
    # Drawings
    fig = plt.figure(dpi=myDPI, figsize=(16,9))
    ax1 = fig.add_subplot(111,projection='3d')
    lineWidth = 0.5

    axLabelSign = 0
    for roof in roof_list:
        xs = []
        ys = []
        zs = []
        for pt in roof:
            xs.append(pt[0])
            ys.append(pt[1])
            zs.append(pt[2])
        xs = np.asarray(xs)
        ys = np.asarray(ys)
        zs = np.asarray(zs)
        if axLabelSign == 0:
            ax1.plot(xs,ys,zs,color='firebrick',lw=lineWidth,label='Roofedges')
            axLabelSign = 1
        else:
            ax1.plot(xs,ys,zs,color='firebrick',lw=lineWidth)
        # polygon
        verts = [list(zip(xs,ys,zs))]
        ax1.add_collection(Poly3DCollection(verts,alpha=0.6,facecolor='red'))
        
    axLabelSign = 0
    for foot in foot_list:
        xs = []
        ys = []
        zs = []
        for pt in foot:
            #ax1.scatter(pt[0],pt[1],pt[2],marker='^',color='indigo')
            xs.append(pt[0])
            ys.append(pt[1])
            zs.append(pt[2]) 
        xs = np.asarray(xs)
        ys = np.asarray(ys)
        zs = np.asarray(zs)
        if axLabelSign == 0:
            ax1.plot(xs,ys,zs,color='navy',lw=lineWidth,label='Footprints')
            axLabelSign = 1
        else:
            ax1.plot(xs,ys,zs,color='navy',lw=lineWidth)
        # polygon
        verts = [list(zip(xs,ys,zs))]
        ax1.add_collection(Poly3DCollection(verts,alpha=0.6,facecolor='royalblue'))

    axLabelSign = 0
    for wall in wall_list:
        xs = []
        ys = []
        zs = []
        for pt in wall:
            xs.append(pt[0])
            ys.append(pt[1])
            zs.append(pt[2]) 
        xs = np.asarray(xs)
        ys = np.asarray(ys)
        zs = np.asarray(zs)
        if axLabelSign == 0:
            ax1.plot(xs,ys,zs,color='darkorange',lw=lineWidth,label='Walls')
            axLabelSign = 1
        else:
            ax1.plot(xs,ys,zs,color='darkorange',lw=lineWidth)
        #polygon
        verts = [list(zip(xs,ys,zs))]
        ax1.add_collection(Poly3DCollection(verts,alpha=0.6,facecolor='gold'))

                
    # Set Equal Boundaries for xyz axis, using exact range of coordinates
    # To fool the matplotlib's automatic setting of the scales of xyz-axis
    rangeDiff = np.subtract(maxRange,minRange)
    print("rangeDiff = ",rangeDiff)
    maxDiff = np.max(rangeDiff)


    Xb_1 = 0.5*maxDiff*np.mgrid[-1:1:0.5,-0.5:1.5:0.5,-0.5:1.5:0.5][0].flatten() + 0.5*(maxRange[0]+minRange[0])
    Yb_1 = 0.5*maxDiff*np.mgrid[-1:1:0.5,-0.5:1.5:0.5,-0.5:1.5:0.5][1].flatten() + 0.5*(maxRange[1]+minRange[1])
    Zb_1 = 0.5*maxDiff*np.mgrid[-1:1:0.5,-0.5:1.5:0.5,-0.5:1.5:0.5][2].flatten() + 0.5*(maxRange[2]+minRange[2])

    for xb1, yb1, zb1 in zip(Xb_1, Yb_1, Zb_1):
        #print(xb1,yb1,zb1)
        ax1.plot([xb1], [yb1], [zb1], 'w')

    #plt.grid()

    #polygon: horizon
    xmin,xmax,ymin,ymax = plt.axis()
    print(ax1.get_xlim())
    print(ax1.get_ylim())
    p1 = [xmin,ymin,minRange[2]]
    p2 = [xmin,ymax,minRange[2]]
    p3 = [xmax,ymax,minRange[2]]
    p4 = [xmax,ymin,minRange[2]]
    xh = [p1[0],p2[0],p3[0],p4[0],p1[0]]
    yh = [p1[1],p2[1],p3[1],p4[1],p1[1]]
    zh = [p1[2],p2[2],p3[2],p4[2],p1[2]]
    verts = [list(zip(xh,yh,zh))]
    ax1.add_collection(Poly3DCollection(verts,alpha=0.2,facecolor='springgreen'))
        
        
    # Labels
    ax1.set_xlabel('$X$')
    ax1.set_ylabel('$Y$')
    ax1.set_zlabel('$Z$')
    #ax1.legend()
    ax1.legend(bbox_to_anchor=(0.9, 1))

    #fig.suptitle('CityGML Plotting',fontsize=16,fontweight="bold")
    fig.savefig(figureName)

def main():
    '''
    Deal with your gml file input:
    '''
    if len(sys.argv) == 1:
        print("Use deaulft files.")
        # default name settings
        fileName = "testing5.xml"
        #fileName = "DUSSELDORF-5-building-test.xml"
        figureName = "testing_Just_draw_the_GML.png"
    elif len(sys.argv) == 2:
        if sys.argv[1] == "-H" or sys.argv[1] == "--help":
            print("-------------------------------------------------")
            print("python visualize_GML.py [input.xml] [output.png]")
            print("-------------------------------------------------")
            return 0
        else:
            print("Use \"-H\" or \"--help\" for more information")
            return 0
    elif len(sys.argv) == 3:
        fileName = sys.argv[1]
        figureName = sys.argv[2]
        if figureName.split(".")[-1] != "png":
            print("Only accept png format.")
            return 0
    else:
        print(">>>ERROR: TOO MANY ARGUMENTS.")
        print("-------------------------------------------------")
        print("python visualize_GML.py [input.xml] [output.png]")
        print("-------------------------------------------------")
        return 0

    myDPI = 500
    drawXML(fileName,figureName,myDPI)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))





