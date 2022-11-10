
'''
Try to validate a cityGML file.
Reference:
Hugo Ledoux, https://github.com/tudelft3d/val3dity;
Hugo Ledoux, http://geovalidation.bk.tudelft.nl/val3dity/docs/errors

 Validation error code:
 LinearRing Level:
    101 TOO_FEW_POINTS
    102 CONSECUTIVE_POINTS_SAME ??==>?? check all the points repeated
    103 NOT_CLOSED
    104 RING_SELF_INTERSECTION

Polygon Level:
    201 INTERSECTION_RINGS:  For those polygons only has one linearing, skip this. 
    


Current progress:
    Only get where the invalid building is, don't know the exact ID for the invalid polygon.
Maybe later on, we will try to delete the invalid building from the xml (build a new xml that is 100% valid)
'''

import xml.etree.ElementTree as ET
import numpy as np
from pyproj import Proj, transform
import multiprocessing as mp
from multiprocessing import Process, Manager, Queue, Pool
import time
import sys
import math


# Classes for storing data extracted from xml and transformation made by pyproj;
# Use the ".name" property as a reference to find the right place in the original XML file.
class _Edge:
    def __init__(self,head,tail):
        self.head = head
        self.tail = tail
#end class _Edge, we don't care the direction (who is head\tail). Just two points there.

# LinearRing/posList, the most basic shape
# name refers to the ID of roof/ground/wall surface. Might be better to use the ID of linearRing...
class _Geometry:
    def __init__(self,name,posList):
        self.name = name
        self.posList = posList
        self.cmt = "Valid"

# A polygon may contains one linearRing, or multiple ones (one external and mutilple inner linearRings)
# Normally roof/ground/wall surface only contains one polygon.
class _Polygon:
    def __init__(self,name):
        self.name = name
        # ring is a list of _Geometry; ring[0] is the exterior. rest for interior ring(s).
        self.ring = []
        #ring[0] => exterior, ring[1] =Interior
        self.cmt = "Valid"

# Building/boundedby/**surface/lod2MultiSurface/MultiSurface/Polygon/LinearRing/posList
class _Building:
    def __init__(self,name):
        self.name = name
        # roof/foot/wall are lists of all the surfaces belong to the building.
        # e.g. roof = [roof1,roof2,roof3,...]
        # each single roof, e.g. roof1, is a  _Polygon. 
        # to get the posList, use ".roof[i].ring[j].posList"
        self.roof = []
        self.foot = []
        self.wall = []  
        self.cmt = "Valid"  
#end class _Building

# read xml and save it to cityObjs
def v_readCityGML(fileName,_nameSpace):
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
            for Poly in roof.findall('.//gml:Polygon',_nameSpace):
                newPoly = _Polygon(Poly.attrib)
                for Pts in Poly.findall('.//gml:posList',_nameSpace):
                    posList = np.array(str(Pts.text).split(' '))
                    posList = posList.astype(np.float)
                    newGeometry = _Geometry(roof.attrib, posList)
                    newPoly.ring.append(newGeometry)
                Building.roof.append(newPoly)   
        for foot in bldg.findall('.//bldg:GroundSurface',_nameSpace):
            for Poly in foot.findall('.//gml:Polygon',_nameSpace):
                newPoly = _Polygon(Poly.attrib)
                for Pts in Poly.findall('.//gml:posList',_nameSpace):
                    posList = np.array(str(Pts.text).split(' '))
                    posList = posList.astype(np.float)
                    newGeometry = _Geometry(foot.attrib,posList)
                    newPoly.ring.append(newGeometry)
                Building.foot.append(newPoly)
        for wall in bldg.findall('.//bldg:WallSurface',_nameSpace):
            for Poly in wall.findall('.//gml:Polygon',_nameSpace):
                newPoly = _Polygon(Poly.attrib)
                for Pts in Poly.findall('.//gml:posList',_nameSpace):
                    posList = np.array(str(Pts.text).split(' '))
                    posList = posList.astype(np.float)
                    newGeometry = _Geometry(wall.attrib,posList)
                    newPoly.ring.append(newGeometry)
                Building.wall.append(newPoly)
        # Append the object Building to our reserved list.
        buildingList.append(Building)
    # end loop of XML searching
    return buildingList

# 102: check if there is consecutive same points (CPS)?? 
# Actually it checks for all points (except the last point) in a ring that are repeated.
# Thus, it should be called as REPEATED_POINTS
def isPolyCPS(polypoints):
    points = polypoints[:-1] # take out the last point, which is same as the first.
    seen = []
    for pt in points:
        if pt in seen:
            return True
        else:
            seen.append(pt)
    return False

# Orientation determination
# from Jonathan Richard Schewchuk, http://www.cs.cmu.edu/~quake/robust.html
# Evaluating the sign of a determinant:
#     | A.x-C.x   A.y-C.y |
#     | B.x-C.x   B.y-C.y |
# which is the volume of vector CA, and CB.
# if the vloume is ZERO, then C is on line AB;
# if the volume is positive, then C is on the left side of line AB; negative for the right side.
def orientation(A,B,C,demension,tol):
    if demension == "x":
        res = (A[1]-C[1])*(B[2]-C[2])-(B[1]-C[1])*(A[2]-C[2])
    elif demension == "y":
        res = (A[0]-C[0])*(B[2]-C[2])-(B[0]-C[0])*(A[2]-C[2])
    elif demension == "z":
        res = (A[0]-C[0])*(B[1]-C[1])-(B[0]-C[0])*(A[1]-C[1])
    if np.abs(res) < tol:
        #print("Third point on the line.")
        return 0
    elif res > 0:
        #print("Third point on the left of line")
        return -1
    else:
        #print("Third point on the right of line")
        return 1

# check if the third point is on the segment of AB
def onSegment(A,B,C,demension):
    if demension == "x":
        if (C[1] <= max(A[1], B[1]) and C[1] >= min(A[1], B[1])) and \
        (C[2] <= max(A[2], B[2]) and C[2]>= min(A[2], B[2])): 
            return True; 
    elif demension == "y":
        if (C[0] <= max(A[0], B[0]) and C[0] >= min(A[0], B[0])) and \
        (C[2] <= max(A[2], B[2]) and C[2]>= min(A[2], B[2])): 
            return True; 
    elif demension == "z":
        if (C[0] <= max(A[0], B[0]) and C[0] >= min(A[0], B[0])) and \
        (C[1] <= max(A[1], B[1]) and C[1]>= min(A[1], B[1])): 
            return True; 
    return False

# >> Line Segment Intersection Algorithm,\
# from Bryce Boe https://bryceboe.com/2006/10/23/line-segment-intersection-algorithm
# Segment AB and segment CD intersected, if and only if
# A and B are on different side of line CD, and at the same time, C and D are seperated by line AB as well.
# Additionally, pay attention to tht extreme circumstance, that AB and CD are on a same line.
# That is an invalid case (intersected), if they overlap (valid if not).
# But the results of orientation() give ZERO for both cases.

# Unfortunately, points are in 3-demension, so we have to check the intersection at xy, yz, xz planes.
# [Important] Assume our points are on a same plane (pass the planar test), then
# true intersection happens to all three planes "xy,yz,xz" at the same time.
def isSegIntersected(A,B,C,D,demension,tol):
    orientation_CD_A = orientation(C,D,A,demension,tol)
    orientation_CD_B = orientation(C,D,B,demension,tol)
    orientation_AB_C = orientation(A,B,C,demension,tol)
    orientation_AB_D = orientation(A,B,D,demension,tol)
    # Normal cases: A&B are seperated by CD, while C&D are seperated by AB.
    if (orientation_CD_A != orientation_CD_B) and (orientation_AB_C != orientation_AB_D):
        return True
    # for special cases, some points are alighed in a same line.
    elif orientation_CD_A==0 and onSegment(C,D,A,demension):
        return True
    elif orientation_CD_B==0 and onSegment(C,D,B,demension):
        return True
    elif orientation_AB_C==0 and onSegment(A,B,C,demension):
        return True
    elif orientation_AB_D==0 and onSegment(A,B,D,demension):
        return True
    else:
        return False

# Check two edges if they are joint
def isEdgeConnected(edge1,edge2):
    # Normally adjacent edges will follow eg1.tail = eg2.head, only except for the pair (i=0, j=last one)
    # where edge_i.head = edge_j.tail
    if edge1.tail == edge2.head or edge2.tail == edge1.head:
        return True
    else:
        return False
# Check two edges if they are identical
def isEdgeSame(edge1,edge2):
    if edge1.head == edge2.head and edge1.tail == edge2.tail:
        return True
    else:
        return False

# Check two edges if they are intersected, using function isSegIntersected(A,B,C,D):
def isEdgeIntersected(edge1,edge2,tol):
    if isSegIntersected(edge1.head,edge1.tail,edge2.head,edge2.tail,"x",tol) and \
    isSegIntersected(edge1.head,edge1.tail,edge2.head,edge2.tail,"y",tol) and \
    isSegIntersected(edge1.head,edge1.tail,edge2.head,edge2.tail,"z",tol):
        return True
    else:
        return False

# 104: check self intersection
def isPolySelfIntersected(polypoints,tol):
    edgeList = []
    for i in range(len(polypoints)-1):
        newEdge = _Edge(polypoints[i],polypoints[i+1])
        edgeList.append(newEdge)

    for i in range(len(edgeList)-1):
        edge = edgeList[i]
        # Ususally, each edge should be connected to other 2 edges.
        # Thus, 1 means not_closed. More than 2 means trouble
        connected_count = 0
        for j in range(i+1,len(edgeList)):
            #print("current = ",i," and ",j)
            another_edge = edgeList[j]
            if isEdgeConnected(edge,another_edge):
                # check the connection of the edge. skip its adjacent two edges.
                #print("Connect [i,j] = ",i," and ",j)
                continue
            elif isEdgeIntersected(edge,another_edge,tol):
                # check the edge intersection issues.
                print("Intersected at [i,j]",i," and ",j)
                return True
        #end loop of another_edge
    #end loop of edge in edgeList
    return False
# 203: NON_PLANAR_POLYGON_DISTANCE_PLANE
def isPolyPlanar_DSTP(polypoints,tol):
    distance = 0.0
    tempDis = 0.0
    p0 = np.array(polypoints[0])
    p1 = np.array(polypoints[1])
    #ensure the three points are not aligned
    for i in range(2,len(polypoints)-1):
        p2 = np.array(polypoints[i])
        tol_ori = 0.001
        if orientation(p0,p1,p2,'x',tol_ori) != 0 or\
            orientation(p0,p1,p2,'y',tol_ori) !=0 or\
            orientation(p0,p1,p2,'z',tol_ori) !=0:
            break
    # test for the rest of points
    for t in range(i+1,len(polypoints)-1):
        pt = np.array(polypoints[t])
        distance = calculateDistanceToPlane(p0,p1,p2,pt)
        if distance > tol:
            if tempDis < distance:
                tempDis = distance

    distance = tempDis
    return distance

# Calculate the distance from point pt to plane p0p1p2.
def calculateDistanceToPlane(p0,p1,p2,pt):
    normal = np.cross(p1-p0,p2-p0)
    magnitude = np.linalg.norm(normal)

    normal = np.true_divide(normal,magnitude)
    distance = np.absolute(np.dot(normal,pt-p0))
    return distance

# 204: NON_PLANAR_POLYGON_NORMALS_DEVIATION, return the max angel deviation in degree.
def isPolyPlanar_NORMAL(polypoints,tol):
    #-- Normal of the polygon from the first three points
    AngleDeviation = 0
    tempDev = 0
    #-- Number of points, last point is as same as the first.
    npolypoints = len(polypoints)
    # after filtering by Error code 101, a polygon at least has 4 point: p0 p1 p2 ~ p3
    p0 = np.array(polypoints[0])
    p1 = np.array(polypoints[1])   
    #ensure the three points are not aligned
    for i in range(2,len(polypoints)-1):
        p2 = np.array(polypoints[i])
        tol_ori = 0.01
        if orientation(p0,p1,p2,'x',tol_ori) != 0 or\
            orientation(p0,p1,p2,'y',tol_ori) !=0 or\
            orientation(p0,p1,p2,'z',tol_ori) !=0:
            break

    # test for the rest of points
    for nt in range(i+1,npolypoints-1):
        p3 = np.array(polypoints[nt])
        AngleDeviation = calculateAngleDeviation(p0,p1,p2,p3)
        if AngleDeviation > tol:
            if tempDev < AngleDeviation:
                tempDev = AngleDeviation

    AngleDeviation = tempDev
    return AngleDeviation

# calculate the angle between p3p0 and the normal of plane p0p1p2, 
# then calculate the deviation to 90 degree.
def calculateAngleDeviation(p0,p1,p2,p3):
    # get the normal of plane p0p1p2
    normal = np.cross(p1-p0,p2-p0)
    magnitude = np.linalg.norm(normal)
    
    normal = np.true_divide(normal,magnitude)
    # get the vector p3p0
    vector = p3-p0
    magnitude = np.linalg.norm(vector)
    vector = np.true_divide(vector,magnitude)
    # get angle and deviation to 90 degree
    AngleDeviation = np.arccos(np.clip(np.dot(vector,normal), -1.0, 1.0))/np.pi*180
    AngleDeviation = np.absolute(AngleDeviation-90)
    return AngleDeviation

# Convert a poslist to a 3d-coordinate array, which is Like, [[x,y,z],...]
def ringConverter(posList):
    polypoints = []
    for i in range(int(len(posList)/3)):
        pt = [posList[3*i],posList[3*i+1],posList[3*i+2]]
        polypoints.append(pt)
    return polypoints

# Error 201: INTERSECTION_RINGS
# it also includes the error 205, where interior ring's vertex fall on the edges of exterior. 
# Error 205 sure is a case of edge intersection
def areRingsIntersected(polygon):
    for i in range(len(polygon.ring)-1):
        ring_i = polygon.ring[i]
        edgeList_i = []
        for it in range(len(ring_i)-1):
            newEdge = _Edge(ring_i[it],ring_i[it+1])
            edgeList_i.append(newEdge)
        # now pick another ring
        for j in range(i+1,len(polygon.ring)):
            ring_j = polygon.ring[j]
            edgeList_j = []
            for jt in range(len(ring_j)-1):
                newEdge = _Edge(ring_j[jt],ring_j[jt+1])
                edgeList_j.append(newEdge)

            # now pick one edge from ring_i, and one edge from ring_j
            for egi in edgeList_i:
                for egj in edgeList_j:
                    tol_intersection = 0.001
                    if isEdgeIntersected(egi,egj,tol_intersection):
                        return True
    #end loop
    return False

# Error 202: DUPLICATED_RINGS
def areRingsDuplicated(polygon):
    for i in range(len(polygon.ring)-1):
        ring_i = polygon.ring[i]
        for j in range(i+1,len(polygon.ring)):
            ring_j = polygon.ring[j]
            if ring_i == ring_j:
                return True
    #end loop
    return False

# Ray Casting
# http://philliplemons.com/posts/ray-casting-algorithm
def ray_casting(point,polypoints,demension):
    inside = False

    if demension == "x":
        p1 = [polypoints[0][1],polypoints[0][2]]
        pt = [point[1],point[2]]
    elif demension == "y":
        p1 = [polypoints[0][0],polypoints[0][2]]
        pt = [point[0],point[2]]
    elif demension == "z":
        p1 = [polypoints[0][0],polypoints[0][1]]
        pt = [point[0],point[1]]
    else:
        print("Demension error.")
        return -1

    # p1 and p2 to form an edge. A ray is cast from right to the pt, parallel to the x-axis.
    for i in range(len(polypoints)):
        if demension == "x":
            p2 = [polypoints[i][1],polypoints[i][2]]
        elif demension == "y":
            p2 = [polypoints[i][0],polypoints[i][2]]
        elif demension == "z":
            p2 = [polypoints[i][0],polypoints[i][1]]

        # Impossible for the ray to go across an edge too hign or too low 
        # Only need to consider pt[1] between them
        if pt[1] >= min(p1[1],p2[1]) and pt[1] <= max(p1[1],p2[1]):
            # also, only need to consider pt[0] when it is less than the max x-coordinates
            if pt[0] <= max(p1[0],p2[0]):
                # when the slope exists
                if p1[1] != p2[1]:
                    # this a line passing p1 and p2.
                    # point [xints,pt[1]] is the intersection point as result of the ray's crossing edge p1p2.
                    # Again, the ray is travelling from x=infinite(rightest) to the pt.
                    # Ray-casting algorithm is to count 
                    # the number of intersection points that this ray goes across the polygon
                    xints = (pt[1]-p1[1])*(p2[0]-p1[0])/(p2[1]-p1[1])+p1[0]
                    # if slope does not exist (p1.y=p2.y), it is parallel to the ray, skip it.
                    if pt[0] <= xints:
                        # x <= xints ensures pt is on the left of the segment p1p2. Intersection happens.
                        # "not inside" means the odd-even switch for the number of intersection points 
                        # same as count one more intersection point
                        inside = not inside
                
        # update p1
        p1 = p2
    #end loop. Odd=Inside=True; Even=Outdise=False
    return inside

# Error 206: INNER_RING_OUTSIDE
# this is error 206, as well as error 207, requires to check a polygon-in-polygon problem. 
# Check the following site:
# https://stackoverflow.com/questions/4833802/check-if-polygon-is-inside-a-polygon
# Basically it takes TWO steps:
# Firstly, check whether theses two rings intersected or not
# (We have done this in error 201, unnecessary to do it again here)
# Secondly, what we do here in this function, is to check if any one point of the interior ring falls in/out of
# the exterior ring. 
# "In" means polygon-in-polygon, "Out" means polygon-outside-polygon.
# Just need to use point-in-polygon algorithm: ray-tracing. Simple enough.

def areInnerRingsOutside(polygon):
    # After checking Error 201, we ensure that all rings are not intersected (No intersected pair of edges)
    # Just pick a point from each Interior ring
    exteriorRing = polygon.ring[0]
    for i in range(1,len(polygon.ring)):
        pt = polygon.ring[i][0]
        if ray_casting(pt,exteriorRing,"x") and\
            ray_casting(pt,exteriorRing,"y") and\
            ray_casting(pt,exteriorRing,"z"):
            # only when all projections return INSIDE, then pt is inside of polygon
            continue
        else:
            return True
    return False

# Error 207: INNER_RINGS_NESTED
# same thing as error 206. Only need to check the point-in-polygon problem.
def areInnerRingsNested(polygon):
    # First we have ensured they are not intersected in Error 201.
    # too few interior rings
    if len(polygon.ring)<3:
        return False

    for i in range(1,len(polygon.ring)-1):
        ring_i = polygon.ring[i]
        for j in range(i+1,len(polygon.ring)):
            ring_j = polygon.ring[j]

            # now check if pt from ring i is inside ring j. INSIDE=>Nested.
            if ray_casting(ring_i[0],ring_j,"x") and\
                ray_casting(ring_i[0],ring_j,"y") and\
                ray_casting(ring_i[0],ring_j,"z"):
                return True

            if ray_casting(ring_j[0],ring_i,"x") and\
                ray_casting(ring_j[0],ring_i,"y") and\
                ray_casting(ring_j[0],ring_i,"z"):
                return True

    return False


# calculate the direction of the normal vector of the LineaRing (orientation)
# this orientation is different from the function "orientation", which solve the problem for Error 104.
# Just two kinds of result for the direction of a normal: "in" or "out"
# counterclockwise order of posList means "out". 
# clockwise order means "in"
# We can calculate the enclosed area to see whether it's ccw or cw. 
# sum up the  (x[i+1] - x[i])(y[i+1] + y[i]).  ccw = negative, cw = positive, aligned = zero
#   
def getRingOrientation(polypoints):
    area_sum_xy = 0
    area_sum_yz = 0
    area_sum_xz = 0
    for i in range(len(polypoints)-1):
        area_sum_xy += (polypoints[i+1][0]-polypoints[i][0])*(polypoints[i+1][1]+polypoints[i][1])
        area_sum_yz += (polypoints[i+1][1]-polypoints[i][1])*(polypoints[i+1][2]+polypoints[i][2])
        area_sum_xz += (polypoints[i+1][0]-polypoints[i][0])*(polypoints[i+1][2]+polypoints[i][2])
    
    #convert to their signs. e.g. [-1,-1,1]
    return np.sign([area_sum_xy,area_sum_yz,area_sum_xz])

# Error 208: ORIENTATION_RINGS_SAME. 
# Exterior and Interior rings are with same orientation. Taht is, the order of posList are both counterclockwise 
# or clockwise.
def areRingsOrientationSame(polygon):
    extRing = getRingOrientation(polygon.ring[0])
    for j in range(1,len(polygon.ring)):
        intRing = getRingOrientation(polygon.ring[j])
        if extRing == intRing:
            return True
    #end loop
    return False

# Check all Errors
def isPolyValid(polygon):
    #-- Assume that it is valid, and try to disprove the assumption
    valid = ""
    # usually, one polygon only contains one rings. 
    # But still possible to have one external and multiple inner rings
    for i in range(len(polygon.ring)):
        polypoints = ringConverter(polygon.ring[i].posList)
        #-- Number of points of the polygon (including the doubled first/last point)
        npolypoints = len(polypoints)      
        # 101 - TOO_FEW_POINTS
        # Four because the first point is doubled as the last one in the ring
        if npolypoints < 4:
            valid += "Invalid: 101 TOO_FEW_POINTS.\n"
        # 102 – CONSECUTIVE_POINTS_SAME: Points in a ring should not be repeated 
        if isPolyCPS(polypoints):
            valid += "Invalid: 102 CONSECUTIVE_POINTS_SAME.\n"

        # 103 – RING_NOT_CLOSED: Check if last point equal
        if polypoints[0] != polypoints[-1]:
            valid += "Invalid: 103 NOT_CLOSED.\n"
        
        # 104 – RING_SELF_INTERSECTION
        tol_intersection = 0.001
        if isPolySelfIntersected(polypoints,tol_intersection):
            valid += "Invalid: 104: RING_SELF_INTERSECTION.\n"
            pass
        # -- Check if the points are planar, 203 and 204:
        # 203 – NON_PLANAR_POLYGON_DISTANCE_PLANE
        tol_in_degree = 0.1
        distance_deviation = isPolyPlanar_DSTP(polypoints,tol_in_degree)
        if distance_deviation > tol_in_degree:
            valid += "Invalid: 203 NON_PLANAR_POLYGON_DISTANCE_PLANE. \nDistance_Deviation_in_meter = "+\
            str(distance_deviation)+"\n"
        # 204 – NON_PLANAR_POLYGON_NORMALS_DEVIATION
        tol_in_degree = 9
        angle_deviation = isPolyPlanar_NORMAL(polypoints,tol_in_degree) 
        if angle_deviation > tol_in_degree:
            valid += "Invalid: '204 NON_PLANAR_POLYGON_NORMALS_DEVIATION. \nAngle_Deviation_in_Degree = "+\
            str(angle_deviation)+"\n"
    # end loop of searching rings from the polygon

    # check the validation for multiple-ring cases
    if len(polygon.ring) > 1:
        if areRingsIntersected(polygon):
            valid += "Invalid 201: INTERSECTION_RINGS.\n"
        if areRingsDuplicated(polygon):
            valid += "Invalid 202: DUPLICATED_RINGS.\n"
        if areInnerRingsOutside(polygon):
            valid += "Invalid 206: INNER_RING_OUTSIDE.\n"
        if areInnerRingsNested(polygon):
            valid += "Invalid 207: INNER_RINGS_NESTED.\n"
        if areRingsOrientationSame(polygon):
            valid += "Invalid 208: ORIENTATION_RINGS_SAME.\n"
    # -----------------
    # Without issues.
    if valid == "":
        valid += "Valid"
    return valid

# Polygon_level Validation for each building (multiprocessing purpose)
def validation(buildingList,invalidResult,loc):
    print("process starts = ",loc)
    proxy = buildingList[loc]
    # roof
    for rj in range(len(proxy.roof)):
        polygon = proxy.roof[rj]
        res = isPolyValid(polygon)
        if res != "Valid":
            proxy.cmt = "Invalid"
        proxy.roof[rj].cmt = res        
    # foot
    for fj in range(len(proxy.foot)):
        polygon = proxy.foot[fj]
        res = isPolyValid(polygon)
        if res != "Valid":
            proxy.cmt = "Invalid"
        proxy.foot[fj].cmt = res
    # wall
    for wj in range(len(proxy.wall)): 
        polygon = proxy.wall[wj]
        res = isPolyValid(polygon)
        if res != "Valid":
            proxy.cmt = "Invalid"
        proxy.wall[wj].cmt = res

    invalidResult.append(proxy)
    print("process ends = ",loc)
    return 0

def main():
    # deal with fileNames
    if len(sys.argv) == 1:
        # Default fileNames
        fileName = "DUSSELDORF-5-building-test.xml"
        #fileName = "LoD2_354_5667_1_NW.gml.xml"
        fileName_exported = "report.txt"
    elif len(sys.argv) == 2:
        if sys.argv[1] == "-H" or sys.argv[1] == "--help":
            print("-----------------------------------------------------")
            print("python xmlParser_Process.py [input.xml] [report.txt]")
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
        print("python xmlParser_Process.py [input.xml] [report.txt]")
        print("-----------------------------------------------------")
        return 0

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
    buildingList = v_readCityGML(fileName,_nameSpace)
    print("Number buildings = ",len(buildingList))


    # prepare for multiprocessing
    # manager.list() is one of several ways that are only available for exchanging data between multple processes. 
    manager = Manager()
    invalidResult = manager.list()

    # You may try Pool(), see more details in xmlParser_Process.py
    pool = Pool()
    pool.starmap(validation,[(buildingList,invalidResult,loc) for loc in range(len(buildingList))])
    pool.close()
    pool.join()

    # About results
    report_str = ""
    num_invalid_geometry = 0
    num_invalid_building = 0
    for i in range(len(invalidResult)):
        invalidOne = invalidResult[i]
        if invalidOne.cmt == "Valid":
            continue
        else:
            num_invalid_building += 1
            for roof in invalidOne.roof:
                if roof.cmt != "Valid":
                    num_invalid_geometry += 1
                    newInvalidStr = str(num_invalid_geometry)+". In Building = "+str(invalidOne.name)+\
                    ";\n Roof Issue = "+str(roof.name)+"\n"+str(roof.cmt)+"\n"   
                    #print("Building No ",i,">>",newInvalidStr)
                    report_str += newInvalidStr
            for foot in invalidOne.foot:
                if foot.cmt != "Valid":
                    num_invalid_geometry += 1
                    newInvalidStr = str(num_invalid_geometry)+". In Building = "+str(invalidOne.name)+\
                    ";\n Foot Issue = "+str(foot.name)+"\n"+str(foot.cmt)+"\n"   
                    #print("Building No ",i,">>",newInvalidStr)
                    report_str += newInvalidStr
            for wall in invalidOne.wall:
                if wall.cmt != "Valid":
                    num_invalid_geometry += 1
                    newInvalidStr = str(num_invalid_geometry)+". In Building = "+str(invalidOne.name)+\
                    ";\n Wall Issue = "+str(wall.name)+"\n"+str(wall.cmt)+"\n"   
                    #print("Building No ",i,">>",newInvalidStr)
                    report_str += newInvalidStr


    print("number of invalid LinearRings = ",num_invalid_geometry)
    print("cpu_count = ",mp.cpu_count())
    print("number of invalid Buildings = ",num_invalid_building,"/",len(invalidResult))
        
    if num_invalid_building == 0:
        report_str = "All buildings are valid!"
    else:
        report_str += "---------------------------------------------------------------------------"
        report_str += "\n Number of invalid LinearRings = "+str(num_invalid_geometry)+"\n"
        report_str += "\n Number of invalid Buildings = "+str(num_invalid_building)+"/"+str(len(invalidResult))+"\n"
    

    with open(fileName_exported,'a+') as f_handle:
        f_handle.write(report_str)

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %.6f seconds ---" % (time.time() - start_time))