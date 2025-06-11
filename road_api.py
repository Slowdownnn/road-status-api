from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from road_heatmap import RoadHeatmap
from fastapi.openapi.utils import get_openapi
import yaml

app = FastAPI()
road = RoadHeatmap("hongshan_roads_with_quality.geojson")

# 接收字段结构
class UpdateByNameRequest(BaseModel):
    keyword: str
    quality: int

class UpdateByLocationRequest(BaseModel):
    lat: float
    lon: float
    quality: int

# 添加静态文件访问（HTML地图）
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/update_by_name")
def update_by_name(req: UpdateByNameRequest):
    count = road.update_by_name(req.keyword, req.quality)
    road.save_geojson("hongshan_roads_with_quality.geojson")
    road.save_map("static/map.html")
    return {
        "status": "success",
        "updated": count,
        "message": f"成功更新 {count} 条道路状态",
        "map_url": "/static/map.html"
    }

@app.post("/update_by_location")
def update_by_location(req: UpdateByLocationRequest):
    success = road.update_by_location(req.lat, req.lon, req.quality)
    road.save_geojson("hongshan_roads_with_quality.geojson")
    road.save_map("static/map.html")
    return {
        "status": "success" if success else "failed",
        "message": "成功更新" if success else "未找到附近道路",
        "map_url": "/static/map.html"
    }

@app.get("/preview_map")
def preview_map():
    return {
        "url": "/static/map.html",
        "message": "打开链接以查看最新的道路热力图"
    }
