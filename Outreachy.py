from io import BytesIO
import os
from osm_fieldwork.basemapper import create_basemap_file

basepath = os.path.dirname(os.path.abspath(__file__))
filepath = f"{basepath}\\tests\\testdata\\Sample.geojson"
sampletest = f"{basepath}\\tests\\testdata\\testingdata.geojson"


with open(filepath, "rb") as geojson_file:
    boundary = geojson_file.read()  # read as a `bytes` object.
    boundary_bytesio = BytesIO(boundary)   # add to a BytesIO wrapper


create_basemap_file(
    verbose=True,
    boundary=boundary_bytesio,
    outfile="toogood.mbtiles",
    zooms="15-17",
    source="esri",
)