import mbsModel
import sys
from pathlib import Path


myModel = mbsModel.mbsModel()

#read fdd file path from input arguments
fdd_path = Path("E:\\9.Semester\\Digitalisierung-Visualisierung-Uebung\\VIS_2024\\Aufgabe_3\\test.fdd")
myModel.importFddFile(fdd_path)
#create path for solver input file (fds)
fds_path = fdd_path.with_suffix(".fds")
myModel.exportFdsFile(fds_path)
#create path for model database file (json)
json_path = fdd_path.with_suffix(".json")
myModel.saveDatabase(json_path)

