#!/usr/bin/python3

# Copyright (c) 2022, 2023 Humanitarian OpenStreetMap Team
#
# This file is part of osm_fieldwork.
#
#     Underpass is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Underpass is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with osm_fieldwork.  If not, see <https:#www.gnu.org/licenses/>.
#
"""Test functionalty of basemapper.py."""

import logging
import os
import shutil
from io import BytesIO

from osm_fieldwork.basemapper import BaseMapper
from osm_fieldwork.sqlite import DataFile

log = logging.getLogger(__name__)

rootdir = os.path.dirname(os.path.abspath(__file__))
boundary = f"{rootdir}/testdata/Rollinsville.geojson"
outfile = f"{rootdir}/testdata/rollinsville.mbtiles"
base = "./tiles"

with open(boundary,"rb") as geofile:
    boundary= BytesIO(geofile.read())


# boundary = open(infile, "r")
# poly = geojson.load(boundary)
# if "features" in poly:
#    geometry = shape(poly["features"][0]["geometry"])
# elif "geometry" in poly:
#    geometry = shape(poly["geometry"])
# else:
#    geometry = shape(poly)


def test_create():
    """See if the file got loaded."""
    hits = 0
    basemap = BaseMapper(boundary, base, "topo", False)
    tiles = list()
    for level in [8, 9, 10, 11, 12]:
        basemap.getTiles(level)
        tiles += basemap.tiles

    if len(tiles) == 5:
        hits += 1

    if tiles[0].x == 52 and tiles[1].y == 193 and tiles[2].x == 211:
        hits += 1

    outf = DataFile(outfile, basemap.getFormat())
    outf.writeTiles(tiles, base)

    os.remove(outfile)
    shutil.rmtree(base)

    assert hits == 2


def test_usingEsri():
    # creating a base image using esri as the source
    basemap = BaseMapper(boundary, base, "esri", False)
    tiles = list()
    for level in [12, 13, 14, 15, 16,17]: #getting zoom level from 12-17
        basemap.getTiles(level)
        tiles += basemap.tiles

    # Inserting data content into the database
    outf = DataFile(outfile, basemap.getFormat()) 
    outf.writeTiles(tiles, base) # writing out datafile in sqlite database file.

    os.remove(outfile)
    shutil.rmtree(base)


if __name__ == "__main__":
    test_usingEsri()


