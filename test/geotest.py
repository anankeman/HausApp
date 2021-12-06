# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 12:32:43 2019

@author: Cami
"""

import geopandas as gpd

# Clean geoshapes
geo_df = gpd.read_file('./shp/NSW_LOCALITY_POLYGON_shp.shp')
geo_df['neigh'] = geo_df.NSW_LOCA_2.str.lower()
geo_df['neigh'] = geo_df.neigh.str.replace("-"," ")

print geo_df.head()