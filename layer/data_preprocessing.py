import requests as req
import json

import pandas as pd
import geopandas as gpd
import numpy as np

from scipy.spatial import cKDTree
from pyproj import CRS
from shapely.geometry import Point

class HouseObject:

    def __init__(self, address):
        self.address = address
        self.lst = [250, 500, 750]

    def get_current_location(self):
        my_place = self.address
        google_url = f'https://www.google.com.tw/search?tbm=map&authuser=0&hl=zh-TW&gl=tw&q={my_place}'
        res = req.get(google_url)
        google_data = json.loads(res.text[5:])
        self.x = google_data[1][0][1]
        self.y = google_data[1][0][2]
        return self.x, self.y

    def ckdnearest(gdA, gdB, columnName):
        nA = np.array(list(gdA.geometry.apply(lambda x: (x.x, x.y))))
        nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))
        btree = cKDTree(nB)
        dist, idx = btree.query(nA, k=1)
        gdf = pd.concat(
            [
                gdA.reset_index(drop=True),
                pd.Series(dist, name=f'{columnName}_dist')
            ], 
            axis=1)

        return gdf

    def create_buffer(self):
        d = {'idx': [1], 'lon': [self.x], 'lat': [self.y]}
        df = pd.DataFrame(data=d)
        geom = [Point(xy) for xy in zip(df.lon, df.lat)]
        crs = CRS('epsg:4326')
        self.gf = gpd.GeoDataFrame(df, crs=crs, geometry=geom)
        self.gf = self.gf.to_crs(epsg=3826)  


        self.gf250 = gpd.GeoDataFrame(df, crs=crs, geometry=geom)
        self.gf250 = self.gf250.to_crs(epsg=3826)  
        self.gf250['geometry'] = self.gf250['geometry'].buffer(250)

        self.gf500 = gpd.GeoDataFrame(df, crs=crs, geometry=geom)
        self.gf500 = self.gf500.to_crs(epsg=3826) 
        self.gf500['geometry'] = self.gf500['geometry'].buffer(500)

        self.gf750 = gpd.GeoDataFrame(df, crs=crs, geometry=geom)
        self.gf750 = self.gf750.to_crs(epsg=3826) 
        self.gf750['geometry'] = self.gf750['geometry'].buffer(750)


    def intersect_hospital():
        near_hospital = gpd.read_file('./medical_facilities/hospital.geojson', encoding = 'utf-8') # point