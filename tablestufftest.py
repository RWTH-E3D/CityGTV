import glob
import os
import CityGTV_gui_func as gtvgf
import lxml.etree as ET
from PySide2 import QtWidgets
import pandas as pd



def get_files(self, path):
    """func to loop through all the files and buildings and add them to the table widget for selection"""
    resultsDict = {}
    if os.path.isfile(path):
        # case for single file
        resultsDict[os.path.basename(path)] = get_lods(path)
        pass
    elif os.path.isdir(path):
        # case for multiple files
        filenames = glob.glob(os.path.join(path, "*.gml")) + glob.glob(os.path.join(path, "*.xml"))
        for i, filename in enumerate(filenames):
            resultsDict[os.path.basename(filename)] = get_lods(filename)
        pass
    else:
        gtvgf.messageBox(self, "ERROR!", "Input path is neither file or directory.\nPlease reselect input data.")

    display_file_lod(self, resultsDict)
    if self.buildingDict != {}:
        # self.btn_next.setEnabled(True)
        pass
    else:
        gtvgf.messageBox(self, "Important", "No files found!")



def get_lod(element, nss):
    """returns the first LoD found in an building or buildingPart"""
    lodFlags = {'bldg:lod0FootPrint': 0, 'bldg:lod1Solid': 1, 'bldg:lod2Solid': 2, 'bldg:lod3MultiSurface': 3, 'bldg:lod4MultiSurface': 4}
    for flag in lodFlags:
        if element.find('./' + flag, nss) != None:
            return lodFlags[flag]
    return -1



def get_info_from_building(element, nss):
    """gathers necessary info on building"""
    # bHeight, rHeight, rHeading, rType, bFunction, YOC, SAG, SBG
    data = {}
    gS_list = getGroundSurfaceCoorOfBuild(element, nss)
    # getting coordinates of groundSurface of the building
    if gS_list == '':
        # no geometry found -> skipping building
        return {}
    else:
        # found geometry of building -> can continue
        pass

    lod = get_lod(element, nss)
    if lod == -1:
        # lod is not defined -> can't continue with building
        return {}
    else:
        # found LoD -> can continue
        data["LoD"] = lod

    return data



def get_lods(filename):
    """gets all files in a building"""
    # parsing file
    print("parsing", filename)
    tree = ET.parse(filename)
    root = tree.getroot()
    nss = root.nsmap

    buildings = {}

    # getting all buildings in file
    buildings_in_file = root.findall('core:cityObjectMember/bldg:Building', nss)

    # iterating all buildings
    for building_E in buildings_in_file:
        buildingName = building_E.attrib['{http://www.opengis.net/gml}id']
        info = get_info_from_building(building_E, nss)
        if info != {}:
            buildings[buildingName] = info
        else:
            # no ground coordinates or LoD found -> can't work with building
            pass
        bps_in_bldg = building_E.findall('./bldg:consistsOfBuildingPart', nss)
        for co_bp_E in bps_in_bldg:
            bp_E = co_bp_E.find('bldg:BuildingPart', nss)
            buildingParIDJoinded = buildingName + '/' + bp_E.attrib['{http://www.opengis.net/gml}id']
            info = get_info_from_building(bp_E, nss)
            if info != {}:
                buildings[buildingParIDJoinded] = info
            else:
                # no ground coordinates or LoD found -> can't work with building
                pass
    
    return buildings



def getGroundSurfaceCoorOfBuild(element, nss):
    """returns the ground surface coor form element"""

    # LoD0
    for tagName in ['bldg:lod0FootPrint', 'bldg:lod0RoofEdge']:
        LoD_zero_E = element.find(tagName, nss)
        if LoD_zero_E != None:
            posList_E = LoD_zero_E.find('.//gml:posList', nss)
            
            if posList_E != None:
                return get_3dPosList_from_str(posList_E.text)

            else:                           # case hamburg lod2 2020
                pos_Es = LoD_zero_E.findall('.//gml:pos', nss)
                polygon = []
                for pos_E in pos_Es:
                    polygon.append(pos_E.text)
                polyStr = ' '.join(polygon)
                return get_3dPosList_from_str(polyStr)

    groundSurface_E = element.find('bldg:boundedBy/bldg:GroundSurface', nss)
    if groundSurface_E != None:
        posList_E = groundSurface_E.find('.//gml:posList', nss)       # searching for list of coordinates

        if posList_E != None:           # case aachen lod2
            return get_3dPosList_from_str(posList_E.text)
            
        else:                           # case hamburg lod2 2020
            pos_Es = groundSurface_E.findall('.//gml:pos', nss)
            polygon = []
            for pos_E in pos_Es:
                polygon.append(pos_E.text)
            polyStr = ' '.join(polygon)
            return get_3dPosList_from_str(polyStr)

    #  checking if no groundSurface element has been found
    else:               # case for lod1 files
        geometry = element.find('bldg:lod1Solid', nss)
        if geometry != None:
            poly_Es = geometry.findall('.//gml:Polygon', nss)
            all_poylgons = []
            for poly_E in poly_Es:
                polygon = []
                posList_E = element.find('.//gml:posList', nss)       # searching for list of coordinates
                if posList_E != None:
                    polyStr = posList_E.text
                else:
                    pos_Es = poly_E.findall('.//gml:pos', nss)        # searching for individual coordinates in polygon
                    for pos_E in pos_Es:
                        polygon.append(pos_E.text)
                    polyStr = ' '.join(polygon)
                coor_list = get_3dPosList_from_str(polyStr)
                all_poylgons.append(coor_list)
            
            # to get the groundSurface polygon, the average height of each polygon is calculated and the polygon with the lowest average height is considered the groundsurface
            averages = []
            for polygon in all_poylgons:
                # need to get polygon with lowest z coordinate here
                average = 0
                for i in range(len(polygon)-1):
                    average -=- polygon[i][2]
                averages.append(average/(len(polygon)-1))

            return all_poylgons[averages.index(min(averages))]
        else:
            return ''



def get_3dPosList_from_str(text):
    coor_list = [float(x) for x in text.split()]
    coor_list = [list(x) for x in zip(coor_list[0::3], coor_list[1::3], coor_list[2::3])]  # creating 2d coordinate array from 1d array
    return coor_list



def display_file_lod(self, filesDict):
    """adds results from get_files to table"""
    self.tbl_buildings.setRowCount(0)
    self.tbl_buildings.horizontalHeader().show()
    self.cBoxes = []

    self.buildingDict = {}

    # iterating over files
    for filename in filesDict:
        buildings = filesDict[filename]

        # checking if buildings have been found in file
        if buildings == {}:
            continue

        for i, entry in enumerate(buildings):
            rowCount = self.tbl_buildings.rowCount()
            self.tbl_buildings.insertRow(rowCount)
            if i == 0:
                # with filename
                newItem = QtWidgets.QTableWidgetItem(str(filename))
                self.tbl_buildings.setItem(rowCount, 0, newItem)
            else:
                # without filename
                newItem = QtWidgets.QTableWidgetItem("")
                self.tbl_buildings.setItem(rowCount, 0, newItem)
                pass
            

            newItem = QtWidgets.QTableWidgetItem(str(entry))
            self.tbl_buildings.setItem(rowCount, 1, newItem)

            newItem = QtWidgets.QTableWidgetItem(str(buildings[entry]["LoD"]))
            self.tbl_buildings.setItem(rowCount, 2, newItem)

            self.cBoxes.append(QtWidgets.QCheckBox(parent= self.tbl_buildings))
            self.cBoxes[-1].clicked.connect(self.onStateChanged)
            self.tbl_buildings.setCellWidget(rowCount, 3, self.cBoxes[-1])

            self.buildingDict[rowCount] = {"filename": filename, 'buildingname': entry, 'values': buildings[entry], "selected": False}

    self.tbl_buildings.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
    self.tbl_buildings.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
    self.tbl_buildings.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
    return


def prepForExport(self):
    # get data
    dataForFrame = []
    for index in self.buildingDict:
        splits = self.buildingDict[index]["buildingname"].split('/')
        if len(splits) > 1:
            bpname = splits[1]
        else:
            bpname = ''
        row = [self.buildingDict[index]["filename"], splits[0], bpname, self.buildingDict[index]["selected"]]
        sets = self.buildingDict[index]["values"]
        row.append(sets["LoD"])

        dataForFrame.append(row)

    df = pd.DataFrame(dataForFrame, columns=['filename', 'buildingID', 'bpID', 'selected', 'LoD'])

    # remove not selected buildings
    if any(df['selected'].tolist()):
        df = df.loc[df["selected"] == True]
    else:
        # all files and buildings
        pass
    
    print(df)
    if df.empty:
        msg = 'No buildings to transform'
        gtvgf.messageBox(self, 'Error', msg)
        return 0

    return df
    



def runningOverDatatSet(self, df):
    # help for running filewise tasks
    filesToWorkOn = list(dict.fromkeys(df["filename"].to_list()))
    for i, filename in enumerate(filesToWorkOn):
        dfFile = df.loc[df["filename"] == filename]
        # dfFile is a subset of df, only containing buildings within the current file
        someOperation(self, filename, dfFile)



def someOperation(self, filename, dfFile):
    # parsing file
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(os.path.join(self.inpDir, filename), parser)
    root_E = tree.getroot()
    nss = root_E.nsmap

    # get envelope elements
    envelope_E = root_E.find('./gml:boundedBy/gml:Envelope', nss)
    nLcorner_E = envelope_E.find('gml:lowerCorner', nss)
    nUcorner_E = envelope_E.find('gml:upperCorner', nss)
    print(nLcorner_E.text)
    print(envelope_E.attrib['srsName'])
    

    # iterate over all buildings in the file
    num_of_buildings = len(root_E.findall('core:cityObjectMember/bldg:Building', nss))
    i = 0
    while i < num_of_buildings:
        building_E = root_E.findall('core:cityObjectMember/bldg:Building', nss)[i]
        building_ID = building_E.attrib['{http://www.opengis.net/gml}id']
        dfBuild = dfFile.loc[dfFile["buildingID"] == building_ID]


        dfMain = dfBuild.loc[dfBuild['bpID'] == '']


        # check if building is selected (dfBuild has an entry -> the file should be transformed)
        # if the statement below is true, the building has been selected
        if len(dfBuild.index) != 0:
            pass
            # getting groundSurface of building
            print(getGroundSurfaceCoorOfBuild(building_E, nss))

            # adding new element
            description_E = ET.SubElement(building_E, ET.QName(nss["gml"], 'description'), nsmap={'gml': nss["gml"]}, )
            description_E.text = 'demo only'
            building_E.insert(0, description_E)

            # alter existing elements
            creationDate_E = building_E.find('core:creationDate', nss)
            creationDate_E.text = '2021-11-25'
            
            # check if the current building is a main building (parent of building parts)
            if len(dfMain.index>1):
                pass
            
            # building part stuff here
            for co_bp_E in building_E.findall('./bldg:consistsOfBuildingPart', nss):
                bp_E = co_bp_E.find('bldg:BuildingPart', nss)
                bpID = bp_E.attrib['{http://www.opengis.net/gml}id']

                dfBP = dfBuild.loc[dfBuild["bpID"] == bpID]
            

        else:
            # df is empty skipping building transformation
            com_to_delete_E = building_E.getparent()
            # deleting cityObjectMember (including building)
            com_to_delete_E.getparent().remove(com_to_delete_E)
            num_of_buildings -= 1
            continue

        i -=- 1


    # creating new tree from root
    tree = ET.ElementTree(root_E)  

    # writing new file 
    tree.write(os.path.join(self.inpDir, "test" + ".gml"), pretty_print = True, xml_declaration=True, 
                encoding='utf-8', standalone='yes', method="xml")


