import geopandas as gpd
import folium
import branca.colormap as cm
import random
import os
from shapely.geometry import Point

class RoadHeatmap:
    def __init__(self, geojson_path):
        self.geojson_path = geojson_path
        self.gdf = gpd.read_file(geojson_path)

        # 创建初始评分字段
        if 'surface_quality' not in self.gdf.columns:
            self.gdf['surface_quality'] = [random.randint(70, 100) for _ in range(len(self.gdf))]

        self.colormap = cm.LinearColormap(colors=['red', 'yellow', 'green'], vmin=30, vmax=100)

    def update_by_name(self, keyword, quality):
        matches = self.gdf[self.gdf.get('name', '').fillna('').str.contains(keyword)]
        self.gdf.loc[matches.index, 'surface_quality'] = quality
        return len(matches)

    def update_by_location(self, lat, lon, quality, tolerance=0.001):
        point = Point(lon, lat)
        nearby = self.gdf[self.gdf.geometry.distance(point) < tolerance]
        if len(nearby) == 0:
            return False
        self.gdf.loc[nearby.index, 'surface_quality'] = quality
        return True

    def save_geojson(self, out_path):
        self.gdf.to_file(out_path, driver='GeoJSON')

    def save_map(self, html_path):
        os.makedirs(os.path.dirname(html_path), exist_ok=True)
        m = folium.Map(location=[30.5, 114.4], zoom_start=13)

        for _, row in self.gdf.iterrows():
            quality = row['surface_quality']
            color = self.colormap(quality)

            if row.geometry.geom_type == 'LineString':
                coords = [(lat, lon) for lon, lat in row.geometry.coords]
                folium.PolyLine(coords, color=color, weight=4, opacity=0.8).add_to(m)
            elif row.geometry.geom_type == 'MultiLineString':
                for line in row.geometry:
                    coords = [(lat, lon) for lon, lat in line.coords]
                    folium.PolyLine(coords, color=color, weight=4, opacity=0.8).add_to(m)

        self.colormap.caption = '道路路面质量（surface_quality）'
        self.colormap.add_to(m)
        m.save(html_path)