from flask import Flask, render_template, request, redirect, url_for
from layer.data_preprocessing import HouseObject
from model.house_price_MLP import HousePriceModel
import pandas as pd
import geopandas as gpd
import numpy as np


app = Flask(__name__)



# 主頁：網頁使用說明
@app.route('/')
def index():
    return render_template("index.html")

# 組員資料頁
@app.route('/about')
def index2():
    return render_template("about.html")

# 地圖圖表分析頁
@app.route('/analysis')
def analysis():
    return render_template("analysis.html")

# 模型訓練頁
@app.route('/model', methods=['GET', 'POST'])  # type: ignore
def get_form():
    # GET 方法
    if request.method == "GET":
        return render_template('model.html', page_header="Form")
    
    # POST 方法
    elif request.method == "POST":
        print(f'req_value:{request.values}')
        d1 = {
            '交易標的':[int(request.values['target'])],
            '建物現況格局-房':[int(request.values['bedroom'])],
            '建物現況格局-廳':[int(request.values['livingroom'])],
            '建物現況格局-衛':[int(request.values['bathroom'])],
            '有無管理組織':[int(request.values['manage_org'])],
            '主建物面積':[float(request.values['main_area'])],
            '附屬建物面積':[float(request.values['sub_area'])],
            '陽台面積':[float(request.values['balcony'])],
            '電梯':[int(request.values['elevator'])],
            '屋齡':[int(request.values['age'])],
            '交易年份':[111],
            'floor':[int(request.values['floor'])],
            'total_floor':[int(request.values['total_floor'])],
            '車位類別_一樓平面':[0],
            '車位類別_其他':[0],
            '車位類別_升降平面':[0],
            '車位類別_升降機械':[0],
            '車位類別_坡道平面':[0],
            '車位類別_坡道機械':[0],
            '車位類別_塔式車位':[0],
            '建物型態-公寓':[0],
            '建物型態-華廈':[0],
            '建物型態-住宅大樓':[0],
            '建物型態-套房':[0]
        }
        df = pd.DataFrame(data=d1)
        if request.values['parking'] == '1':
            df['車位類別_一樓平面'] = 1
        elif request.values['parking'] == '2':
            df['車位類別_升降平面'] = 1
        elif request.values['parking'] == '3':
            df['車位類別_升降機械'] = 1
        elif request.values['parking'] == '4':
            df['車位類別_坡道平面'] = 1
        elif request.values['parking'] == '5':
            df['車位類別_坡道機械'] = 1
        elif request.values['parking'] == '6':
            df['車位類別_塔式車位'] = 1
        elif request.values['parking'] == '7':
            df['車位類別_其他'] = 1

        if request.values['type'] == '1':
            df['建物型態-公寓'] = 1
        elif request.values['type'] == '2':
            df['建物型態-華廈'] = 1
        elif request.values['type'] == '3':
            df['建物型態-住宅大樓'] = 1
        elif request.values['type'] == '4':
            df['建物型態-套房'] = 1

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
        fuel = house.overlay_polygon_layer(target_layer, 'near_fuel', 'full_id', 'near')
        target_layer = gpd.read_file('./layer/public_safety/market.geojson', encoding = 'utf-8')
        market = house.overlay_polygon_layer(target_layer, 'near_market', 'full_id', 'near')
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
        result = df.join(result)

        if request.values['county'] == '台北市':
            d2 = {
                '中山區':[0],
                '中正區':[0],
                '信義區':[0],
                '內湖區':[0],
                '北投區':[0],
                '南港區':[0],
                '士林區':[0],
                '大同區':[0],
                '大安區':[0],
                '文山區':[0],
                '松山區':[0],
                '萬華區':[0]
            }
            df2 = pd.DataFrame(data=d2)
            df2[request.values['district']] = 1
            result.drop(['idx','lon','lat','geometry','near_fuel_dist','near_market_dist','near_LRT_250','near_LRT_500','near_LRT_750'],axis=1,inplace=True)
            result = result.join(df2)
            lst = result.values.tolist()
            print(lst[0])

            TPE_model = HousePriceModel('TPE')
            price = TPE_model.predictPrice(lst[0]) * 3.3058
            print(price)

        if request.values['county'] == '新北市':
            d2 = {
                '三峽區':[0],
                '三芝區':[0],
                '三重區':[0],
                '中和區':[0],
                '五股區':[0],
                '八里區':[0],
                '土城區':[0],
                '新店區':[0],
                '新莊區':[0],
                '板橋區':[0],
                '林口區':[0],
                '樹林區':[0],
                '永和區':[0],
                '汐止區':[0],
                '泰山區':[0],
                '淡水區':[0],
                '深坑區':[0],
                '烏來區':[0],
                '瑞芳區':[0],
                '石碇區':[0],
                '石門區':[0],
                '萬里區':[0],
                '蘆洲區':[0],
                '貢寮區':[0],
                '金山區':[0],
                '雙溪區':[0],
                '鶯歌區':[0]
            }
            df2 = pd.DataFrame(data=d2)
            df2[request.values['district']] = 1
            result.drop(['idx','lon','lat','geometry','near_fuel_dist','near_market_dist'],axis=1,inplace=True)
            result = result.join(df2)
            lst = result.values.tolist()
            print(lst[0])

            TPE_model = HousePriceModel('NTPC')
            price = TPE_model.predictPrice(lst[0]) * 3.3058
            print(price)
            
        if request.values['county'] == '基隆市':
            d2 = {
                '七堵區':[0],
                '中山區':[0],
                '中正區':[0],
                '仁愛區':[0],
                '信義區':[0],
                '安樂區':[0],
                '暖暖區':[0]
            }
            df2 = pd.DataFrame(data=d2)
            df2[request.values['district']] = 1
            result.drop(['idx','lon','lat','geometry','near_fuel_dist','near_market_dist','near_hospital_dist','near_university','near_LRT_250','near_LRT_500','near_LRT_750','near_LRT_dist','near_MRT_250','near_MRT_500','near_MRT_750','near_MRT_dist'],axis=1,inplace=True)
            result = result.join(df2)
            lst = result.values.tolist()
            print(lst[0])

            TPE_model = HousePriceModel('TPE')
            price = TPE_model.predictPrice(lst[0]) * 3.3058
            print(price)

        
        #print(lon, lat)

        return redirect("analysis")
        # return render_template('model.html', page_header="Form", hospital = hospital)


#功能測試頁：完成後需移除
@app.route('/test')  # type: ignore
def test():
    if request.method == "GET":
        return render_template('test.html', page_header="Form")
    
    # POST 方法
    elif request.method == "POST":
        return redirect("analysis.html")



if __name__=="__main__":
    app.run(debug=True)
