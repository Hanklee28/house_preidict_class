from flask import Flask, render_template, request
from layer.data_preprocessing import HouseObject
import pandas as pd
import geopandas as gpd
import numpy as np


app = Flask(__name__)



#----------practice start------------
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def index2():
    return render_template("about.html")

@app.route('/model')
def index3():
    return render_template("model.html")    

@app.route('/analysis')
def index4():
    return render_template("analysis.html")


#----------practice end-------------- 
#----------post-------------- 
@app.route('/model', methods=['GET', 'POST'])
def get_form():
    if request.method == "GET":
        return render_template('model.html', page_header="Form")
    elif request.method == "POST":# 以post的形式傳出去
        #print(f'req_value:{request.values}')

        address = request.values['county'] + \
                  request.values['district'] + \
                  request.values['street']
        
        house = HouseObject(address)
        # User輸入地址的經緯度
        house_lon, house_lat = house.get_current_location()
        # 空間資訊處理
        house.create_buffer()
        
        # 醫療設施
        target_layer = gpd.read_file('./layer/medical_facilities/hospital.geojson', encoding = 'utf-8')
        hospital = house.sjoin_point_layer(target_layer, 'near_hospital', '機構名稱', 'near')
        target_layer = gpd.read_file('./layer/medical_facilities/clinic.geojson', encoding = 'utf-8')
        clinic = house.sjoin_point_layer(target_layer, 'clinic_count', '機構名稱', 'count')        
        target_layer = gpd.read_file('./layer/medical_facilities/dentist.geojson', encoding = 'utf-8')
        dentist = house.sjoin_point_layer(target_layer, 'dentist_count', '機構名稱', 'count')
        target_layer = gpd.read_file('./layer/medical_facilities/pharmacy.geojson', encoding = 'utf-8')
        pharmacy = house.sjoin_point_layer(target_layer, 'pharmacy_count', '機構名稱', 'count')

        # 經濟指標
        target_layer = gpd.read_file('./layer/economic_indicators/conveniencestore.geojson', encoding = 'utf-8')
        conveniencestore = house.sjoin_point_layer(target_layer, 'conveniencestore_count', '分公司名稱', 'count')
        target_layer = gpd.read_file('./layer/economic_indicators/fastfood.geojson', encoding = 'utf-8')
        fastfood = house.overlay_polygon_layer(target_layer, 'fastfood_count', 'full_id', 'count')

        # 文教機構
        target_layer = gpd.read_file('./layer/educational_resources/library.geojson', encoding = 'utf-8')
        library = house.overlay_polygon_layer(target_layer, 'library_count', 'full_id', 'count')
        target_layer = gpd.read_file('./layer/educational_resources/school.geojson', encoding = 'utf-8')
        school = house.overlay_polygon_layer(target_layer, 'near_school', 'full_id', 'near')
        target_layer = gpd.read_file('./layer/educational_resources/university.geojson', encoding = 'utf-8')
        university = house.overlay_polygon_layer(target_layer, 'near_university', 'full_id', 'near')

        # 公共安全
        target_layer = gpd.read_file('./layer/public_safety/firestation.geojson', encoding = 'utf-8')
        firestation = house.sjoin_point_layer(target_layer, 'near_firestation', '消防隊名稱', 'near')
        target_layer = gpd.read_file('./layer/public_safety/fuel.geojson', encoding = 'utf-8')
        fuel = house.overlay_polygon_layer(target_layer, 'fuel_count', 'full_id', 'count')
        target_layer = gpd.read_file('./layer/public_safety/market.geojson', encoding = 'utf-8')
        market = house.overlay_polygon_layer(target_layer, 'market_count', 'full_id', 'count')
        target_layer = gpd.read_file('./layer/public_safety/police.geojson', encoding = 'utf-8')
        police = house.sjoin_point_layer(target_layer, 'near_police', '中文單位名稱', 'near')
        target_layer = gpd.read_file('./layer/public_safety/placeofworkship.geojson', encoding = 'utf-8')
        placeofworkship = house.overlay_polygon_layer(target_layer, 'placeofworkship_count', 'full_id', 'count')

        # 自然環境
        target_layer = gpd.read_file('./layer/natural_environment/cemetery.geojson', encoding = 'utf-8')
        cemetery = house.overlay_polygon_layer(target_layer, 'cemetery_area', 'full_id', 'area')
        target_layer = gpd.read_file('./layer/natural_environment/park.geojson', encoding = 'utf-8')
        park = house.overlay_polygon_layer(target_layer, 'park_area', 'full_id', 'area')
        target_layer = gpd.read_file('./layer/natural_environment/river_TW.geojson', encoding = 'utf-8')
        river_TW = house.overlay_polygon_layer(target_layer, 'river_TW_area', 'full_id', 'area')

        # 交通運輸
        target_layer = gpd.read_file('./layer/transportation/parking.geojson', encoding = 'utf-8')
        parking = house.overlay_polygon_layer(target_layer, 'parking_area', 'full_id', 'area')
        target_layer = gpd.read_file('./layer/transportation/busstop.geojson', encoding = 'utf-8')
        busstop = house.sjoin_point_layer(target_layer, 'busstop_count', 'full_id', 'count')
        target_layer = gpd.read_file('./layer/transportation/LRT.geojson', encoding = 'utf-8')
        LRT = house.sjoin_point_layer(target_layer, 'near_LRT', 'MARKID', 'near')
        target_layer = gpd.read_file('./layer/transportation/MRT.geojson', encoding = 'utf-8')
        MRT = house.sjoin_point_layer(target_layer, 'near_MRT', 'MARKID', 'near')
        target_layer = gpd.read_file('./layer/transportation/TRA.geojson', encoding = 'utf-8')
        TRA = house.sjoin_point_layer(target_layer, 'near_TRA', 'MARKID', 'near')

        result = house.return_geo_dataframe()
        result.to_csv('codeCheckFile.csv')
        

        
        #print(lon, lat)

        return render_template('model.html', page_header="Form")
# @app.route('/form_result', methods=['POST']) # default methods is "GET"
# def form_result():
#     data = [["method:", request.method],
#             ["base_url:", request.base_url],
#             ["form data:", request.form]]
#     return render_template('model.html', page_header="Form data", data=data)



if __name__=="__main__":
    app.run(debug=True)
