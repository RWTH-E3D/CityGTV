![E3D - Institute of Energy Efficiency and Sustainable Building, RWTH Aachen University](./pictures/e3dHeader__1_.png)

# CityGTV - CityGML Geometrical Transformation and Validation Tool 

[![License](http://img.shields.io/:license-mit-blue.svg)](http://doge.mit-license.org)

The CityGML Geometrical Transformation and Validation Tool (CityGTV) is developed by members of the "Institute of Energy Efficiency and Sustainable Building (e3D), RWTH Aachen University" using Python 3.5+.
This tool can be used to transform building geometries for unavailable building models based on user inputs and further validate the models within the tool.
The CityGTV aims to help urban planners and simulation scientists to facilitate CityGML model developments for energy performance simulations.


This GitLab page will be used to further develop the package and make it available under the [MIT License](https://gitlab.e3d.rwth-aachen.de/e3d-software-tools/citygtv/citygtv/-/blob/master/License/LICENSE).

If you have any questions regarding CityGTV feel free to contact us at: [cityatb@e3d.rwth-aachen.de](mailto:cityatb@e3d.rwth-aachen.de)


## Description

Emerging technologies, computational algorithms and simulation environments enable users, facility managers and occupants to achieve a good estimation of the energy demands of their buildings, districts and cities.
This is a huge step forward towards the realization of the 7th United Nations Sustainable Goal of ensuring an affordable, reliable, sustainable and modern energy for the population of our planet.
The availability of 3D building models has been increasing in the last few years. CityGML LoD1-2 datasets are also available for some countries, states and cities. However, there is still a lack of open source information for many city districts which would be beneficial for the industrial and research community. In order to bridge the gap between the availability of data models and its application, CityGTV can be used to create missing building models where less or no data exists. 


## Version

The CityGTV is currently being developed. Currently the CityGTV is available in the version 0.1.


## How to use CityGTV

### Dependencies

CityGTV is currently being developed using Python 3.5+ and PySide6 python bindings. However in future, the developers will make it usable with other versions of python 3. 
Futhermore, the following external libraries/python packages are used in the different functionalities of CityGTV:
1. PySide6
2. numpy
3. matplotlib
4. pandas
5. pyproj

### Installation

The CityGTV can be used by cloning or downloading the whole CityGTV package from the GIT Repository. Moreover, the user needs to run the "PyQt5_mainUI.py" for loading the GUI.  

### How to contribute to the development of CityGTV

You are invited to contribute to the development of CityGTV. You may report any issues by using the [Issues](https://gitlab.e3d.rwth-aachen.de/e3d-software-tools/citygtv/citygtv/-/issues) button.

## How to cite CityGTV

Geometrical Interoperability of 3D CityGML Building Models for Urban Energy Use Cases. Avichal Malhotra, Yue Pan, Jérôme Frisch, Christoph van Treeck. IBPSA Building Simulation 2021, September 2021, Brugge. (in press)

## License

CityGTV is released by RWTH Aachen University, E3D - Institute of Energy Efficiency and Sustainable Building, under the [MIT License](https://gitlab.e3d.rwth-aachen.de/e3d-software-tools/citygtv/citygtv/-/blob/master/License/LICENSE).
