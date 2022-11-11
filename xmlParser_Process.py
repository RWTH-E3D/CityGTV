'''
Transform gml coordinates from one CRS to another;
and export to a new gml file.

transfromation of 1 building consumes a time between 1~2 seconds.
'''

import xml.etree.ElementTree as ET
import numpy as np
from pyproj import Proj, transform
import multiprocessing as mp
from multiprocessing import Process, Manager, Queue, Pool
import time
import sys
from math import sin,cos

# A Class for storing data extracted from xml and transformation made by pyproj;
# Use the name property as a reference to find the right place in the original XML file.
class _Building:
    def __init__(self,name):
        self.name = name
        self.roof = []
        self.foot = []
        self.wall = []
#end class _Building



def getPosListOfSurface(surface_E, namespace):
    """extracts a numpy array of coordinates from a surface"""
    for polygon_E in surface_E.findall('.//gml:Polygon',namespace):
        Pts = polygon_E.find('.//gml:posList',namespace)
        if Pts != None:
            posList = np.array(str(Pts.text).split(' '))
        else:
            points = []
            for Pt in polygon_E.findall('.//gml:pos', namespace):
                points.extend([float(i) for i in Pt.split(' ')])
            posList = np.array(points)
    return posList.astype(np.float)



# read xml and save it to cityObjs
def readCityGML(fileName,_nameSpace):
    buildingList = []
    tree = ET.parse(fileName)
    root = tree.getroot()
    for bldg in root.findall('.//bldg:Building',_nameSpace):
        # find the cityObjectMember's name and create an object of Class _Building
        kiminonamae = bldg.attrib
        #print("kiminonamae = ",kiminonamae)
        # The name is the entire attribute of <bldg:Building>, 
        # for example, {'{http://www.opengis.net/gml}id': 'DENW20AL00006aAC'}

        Building = _Building(kiminonamae)
        # seearch the XML file using the XPath format, provided by ElementTree.
        # and change the string into float arrays, stored in the Building object.
        for roof in bldg.findall('.//bldg:RoofSurface',_nameSpace):
            posList = getPosListOfSurface(roof, _nameSpace)
            Building.roof.append(posList)
        for foot in bldg.findall('.//bldg:GroundSurface',_nameSpace):
            posList = getPosListOfSurface(foot, _nameSpace)
            Building.foot.append(posList)
        for wall in bldg.findall('.//bldg:WallSurface',_nameSpace):
            posList = getPosListOfSurface(wall, _nameSpace)
            Building.wall.append(posList)
        # Append the object Building to our reserved list.
        buildingList.append(Building)
    # end loop of XML searching
    return buildingList

# find the REF point and transform it. 
# In this example, we take the first point in the first GroundSurface as the Reference point.
def getREF(root,_nameSpace,inProj,outProj):
    for obj in root.findall('core:cityObjectMember',_nameSpace):
        for foot in obj.findall('.//bldg:GroundSurface',_nameSpace):
            posList = getPosListOfSurface(foot, _nameSpace)
            pt_REF = np.array([posList[0],posList[1],posList[2]])
            pt_REF[0],pt_REF[1] = transform(inProj,outProj,pt_REF[0],pt_REF[1])
            return pt_REF
    return 0

def getCenter(building):
    center = [0,0]
    min_x = building.foot[0][0]
    max_x = building.foot[0][0]
    min_y = building.foot[0][1]
    max_y = building.foot[0][1]
    
    for foot in building.foot:
        for i in range(int(len(foot)/3)):
            if foot[3*i]< min_x:
                min_x = foot[3*i]
            elif foot[3*i]> max_x:
                max_x = foot[3*i]
            if foot[3*i+1]< min_y:
                min_y = foot[3*i+1]
            elif foot[3*i+1]> max_y:
                max_y = foot[3*i+1]
    center[0] = float((min_x + max_x)/2)
    center[1] = float((min_y + max_y)/2)
    return center

# export the xml file
def treeWriter(fileName_exported,tree,buildingList,_nameSpace):
    root = tree.getroot()
    seperator = ' '
    for bldg in root.findall(".//bldg:Building",_nameSpace):
        for building in buildingList:
            if str(bldg.attrib) == str(building.name):
                # roof
                roof_mark = 0
                for roof in bldg.findall('.//bldg:RoofSurface',_nameSpace):
                    for Poly in roof.findall('.//gml:Polygon',_nameSpace):
                        Pts = Poly.find('.//gml:posList',_nameSpace)
                        if Pts == None:
                            linearRing = Poly.find('.//gml:LinearRing',_nameSpace)
                            for Pt in linearRing.findall('.//gml:pos',_nameSpace):
                                linearRing.remove(Pt)
                            Pts = ET.SubElement(linearRing, ET.QName(_nameSpace["gml"], "posList"))
                        transformedList = ['{:.8f}'.format(x) for x in building.roof[roof_mark]]
                        Pts.text = seperator.join(transformedList)
                        roof_mark += 1
                # foot
                foot_mark = 0
                for foot in bldg.findall('.//bldg:GroundSurface',_nameSpace):
                    for Poly in foot.findall('.//gml:Polygon',_nameSpace):
                        Pts = Poly.find('.//gml:posList',_nameSpace)
                        if Pts == None:
                            linearRing = Poly.find('.//gml:LinearRing',_nameSpace)
                            for Pt in linearRing.findall('.//gml:pos',_nameSpace):
                                linearRing.remove(Pt)
                            Pts = ET.SubElement(linearRing, ET.QName(_nameSpace["gml"], "posList"))
                        transformedList = ['{:.8f}'.format(x) for x in building.foot[foot_mark]]
                        Pts.text = seperator.join(transformedList)
                        foot_mark += 1
                # wall
                wall_mark = 0
                for wall in bldg.findall('.//bldg:WallSurface',_nameSpace):
                    for Poly in wall.findall('.//gml:Polygon',_nameSpace):
                        Pts = Poly.find('.//gml:posList',_nameSpace)
                        if Pts == None:
                            linearRing = Poly.find('.//gml:LinearRing',_nameSpace)
                            for Pt in linearRing.findall('.//gml:pos',_nameSpace):
                                linearRing.remove(Pt)
                            Pts = ET.SubElement(linearRing, ET.QName(_nameSpace["gml"], "posList"))
                        transformedList = ['{:.8f}'.format(x) for x in building.wall[wall_mark]]
                        Pts.text = seperator.join(transformedList)
                        wall_mark += 1      
        # end loop of searching for the building with same name, and go for the next building.
    # end loop of all buildings

    # ElementTree has to register all the nameSpaces(xmlns) manually. Otherwise, the export'll be wrong.
    for key in _nameSpace.keys():
        ET.register_namespace(str(key),str(_nameSpace[key]))

    # change the output file name here:
    tree.write(fileName_exported,xml_declaration=True,encoding='utf-8', method="xml")
    return 0

def crsTransformPool(buildingList,buildingResult,loc,OFFSET,inProj,outProj,angle,elevation,selectionReference):
    print("process starts = ",loc)  
    #single_start_time = time.time()
    proxy = buildingList[loc]
    angle = angle/180*(np.pi)
    
    # selection Reference, to determine whether it is necessary to do the rotation and elevation transformation.
    buildingName = str(proxy.name).split("'")[-2]

    # pivot in the original CRS
    pivot = getCenter(proxy)
    resX, resY = transform(inProj,outProj,pivot[0],pivot[1])
    pivot = [resX+OFFSET[0], resY+OFFSET[1]]

    # roof
    for rj in range(len(proxy.roof)):
        # select the j_th roof in ".roof" 
        posList = proxy.roof[rj]
        for k in range(int(len(posList)/3)):
            res_x,res_y = transform(inProj,outProj,posList[3*k], posList[3*k+1])
            res_x = res_x + OFFSET[0]
            res_y = res_y + OFFSET[1]
            if buildingName in selectionReference:
                dx = (res_x - pivot[0])*cos(angle)-(res_y - pivot[1])*sin(angle)
                dy = (res_x - pivot[0])*sin(angle)+(res_y - pivot[1])*cos(angle)
                proxy.roof[rj][3*k] = dx+ pivot[0]
                proxy.roof[rj][3*k+1] = dy + pivot[1]
                proxy.roof[rj][3*k+2]+= elevation       
            else:
                proxy.roof[rj][3*k] = res_x
                proxy.roof[rj][3*k+1] = res_y  
    # foot
    for fj in range(len(proxy.foot)):
        posList = proxy.foot[fj]
        for k in range(int(len(posList)/3)):
            res_x,res_y = transform(inProj,outProj,posList[3*k], posList[3*k+1])
            res_x = res_x + OFFSET[0]
            res_y = res_y + OFFSET[1]
            if buildingName in selectionReference:
                dx = (res_x - pivot[0])*cos(angle)-(res_y - pivot[1])*sin(angle)
                dy = (res_x - pivot[0])*sin(angle)+(res_y - pivot[1])*cos(angle)
                proxy.foot[fj][3*k] = dx+ pivot[0]
                proxy.foot[fj][3*k+1] = dy + pivot[1]
                proxy.foot[fj][3*k+2]+= elevation
            else:
                proxy.foot[fj][3*k] = res_x
                proxy.foot[fj][3*k+1] = res_y
    # wall
    for wj in range(len(proxy.wall)): 
        posList = proxy.wall[wj]
        for k in range(int(len(posList)/3)):
            res_x,res_y = transform(inProj,outProj,posList[3*k], posList[3*k+1])
            res_x = res_x + OFFSET[0]
            res_y = res_y + OFFSET[1]
            if buildingName in selectionReference:
                dx = (res_x - pivot[0])*cos(angle)-(res_y - pivot[1])*sin(angle)
                dy = (res_x - pivot[0])*sin(angle)+(res_y - pivot[1])*cos(angle)
                proxy.wall[wj][3*k] = dx+ pivot[0]
                proxy.wall[wj][3*k+1] = dy + pivot[1]
                proxy.wall[wj][3*k+2]+= elevation
            else:
                proxy.wall[wj][3*k] = res_x
                proxy.wall[wj][3*k+1] = res_y
    # save the transformed results 
    buildingResult.append(proxy)
    #print("---In a single loop: %s seconds ---" % (time.time() - single_start_time))
    print("process ends = ",loc)
    return 0


def main():
    # target location: values are in target CRS
    # this is a location in London:
    targetLoc = [522901.810984, 179591.260805, 0]

    # in&out projected CRS
    inProj = Proj('epsg:5555')
    outProj = Proj('epsg:27700')

    # deal with fileNames
    if len(sys.argv) == 1:
        # Default fileNames
        fileName = "DUSSELDORF-5-building-test.xml"
        #fileName = "LoD2_354_5667_1_NW.gml.xml"
        fileName_exported = "testing5.xml"
    elif len(sys.argv) == 2:
        if sys.argv[1] == "-H" or sys.argv[1] == "--help":
            print("-----------------------------------------------------")
            print("python xmlParser_Process.py [input.xml] [output.xml]")
            print("-----------------------------------------------------")
            return 0
        else:
            print("Use \"-H\" or \"--help\" for more information")
            return 0
    elif len(sys.argv) == 3:
        fileName = sys.argv[1]
        fileName_exported = sys.argv[2]
    else:
        print(">>>Error: TOO MANY ARGUMENTS.")
        print("-----------------------------------------------------")
        print("python xmlParser_Process.py [input.xml] [output.xml]")
        print("-----------------------------------------------------")
        return 0

    # nameSpace used for ElementTree's search function
    # CutyGMl 1.0
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
    version = 0
    with open(fileName,"r") as fileHandle:
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

    # save the xml data into buildingList. To call the building inside it, 
    # use buildingList[x].name or buildingList[x].roof (.foor or .wall) 
    buildingList = readCityGML(fileName,_nameSpace)
    print("Number buildings = ",len(buildingList))

    #Rotation&Elevation
    angle = 90
    #assume the ratation pivot is the "center" point of the building's GroundSurface.
    elevation = 100

    tree = ET.parse(fileName)

    # find the REF point and OFFSET vector.
    pt_REF = getREF(tree.getroot(),_nameSpace,inProj,outProj)
    OFFSET = np.subtract(np.array(targetLoc),np.array(pt_REF))
    OFFSET[2] = 0

    # selection reeference. Now assume we select all the buildings.
    selectionReference = []
    for building in buildingList:
        itemName = str(building.name).split("'")[-2]
        selectionReference.append(itemName)

    selectionReference = ["DENW20AL00006aAC"]

    # prepare for multiprocessing
    # manager.list() is one of several ways that are only available for exchanging data between multple processes. 
    manager = Manager()
    buildingResult = manager.list()
    
    #'''
    # You may try Pool(), another method in multiprocessing. No improvement in the performance, 
    # but much simpler in code.
    pool = Pool()
    # use .apply_async()
    #for loc in range(len(buildingList)):
    #   pool.apply_async(crsTransformPool, args=(buildingList,buildingResult,loc,OFFSET,inProj,outProj,))
    # or use starmap(), no difference in the performance.
    pool.starmap(crsTransformPool,[(buildingList,buildingResult,loc,OFFSET,inProj,outProj,angle,elevation,\
        selectionReference) for loc in range(len(buildingList))])
    pool.close()
    pool.join()
    #'''
    # Update buildingList with the buildingResult, which contains the transformation results.
    print("number of results",len(buildingResult))
    print("cpu_count = ",mp.cpu_count())
    for i in range(len(buildingList)):
        building_transformed = buildingResult[i]
        buildingList[i].name = building_transformed.name
        buildingList[i].roof = building_transformed.roof
        buildingList[i].foot = building_transformed.foot
        buildingList[i].wall = building_transformed.wall

    # export the List to an XML
    treeWriter(fileName_exported,tree,buildingList,_nameSpace)

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %.6f seconds ---" % (time.time() - start_time))