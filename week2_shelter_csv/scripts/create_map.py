import pandas as pd
import folium
import numpy as np

def create_intersection_map():
    # 讀取避難收容所數據
    shelter_df = pd.read_csv(r'week2_shelter_csv\output\避難收容處所點位位檔案v9_邊界驗證版.csv')
    
    # 創建地圖，以台灣中心為基準
    m = folium.Map(location=[23.8, 121], zoom_start=8, tiles='OpenStreetMap')
    
    # Layer A: 避難收容所
    shelter_group = folium.FeatureGroup(name="避難收容所")
    
    for idx, row in shelter_df.iterrows():
        try:
            lon, lat = float(row['經度']), float(row['緯度'])
            
            # 跳過異常點
            if lon == 0 or lat == 0:
                continue
                
            # 檢查是否在海洋中 (簡單驗證)
            if not (118 <= lon <= 124 and 20 <= lat <= 26):
                print(f"警告: 序號{row['序號']}可能在海洋中: ({lon}, {lat})")
                continue
            
            # 根據室內/室外選擇圖標
            if row['室內'] == '是':
                icon_color = 'blue'
                icon_symbol = 'home'
            else:
                icon_color = 'green'
                icon_symbol = 'tree'
            
            folium.Marker(
                location=[lat, lon],
                popup=f"{row['避難收容處所名稱']}<br>收容人數: {row['預計收容人數']}<br>類型: {'室內' if row['室內'] == '是' else '室外'}",
                icon=folium.Icon(color=icon_color, icon=icon_symbol, prefix='fa')
            ).add_to(shelter_group)
            
        except (ValueError, TypeError):
            continue
    
    # Layer B: AQI站點 (模擬數據)
    aqi_group = folium.FeatureGroup(name="AQI站點")
    
    # 模擬AQI站點數據
    aqi_stations = [
        {'name': '台北站', 'lat': 25.03, 'lon': 121.56, 'aqi': 85},
        {'name': '新北站', 'lat': 25.27, 'lon': 121.46, 'aqi': 65},
        {'name': '桃園站', 'lat': 24.99, 'lon': 121.30, 'aqi': 45},
        {'name': '新竹站', 'lat': 24.81, 'lon': 120.96, 'aqi': 35},
        {'name': '台中站', 'lat': 24.14, 'lon': 120.67, 'aqi': 75},
        {'name': '嘉義站', 'lat': 23.48, 'lon': 120.45, 'aqi': 55},
        {'name': '台南站', 'lat': 22.99, 'lon': 120.20, 'aqi': 95},
        {'name': '高雄站', 'lat': 22.62, 'lon': 120.31, 'aqi': 105},
        {'name': '宜蘭站', 'lat': 24.69, 'lon': 121.77, 'aqi': 40},
        {'name': '花蓮站', 'lat': 23.97, 'lon': 121.60, 'aqi': 30}
    ]
    
    for station in aqi_stations:
        # 根據AQI值決定顏色
        if station['aqi'] <= 50:
            color = 'green'
            severity = '良好'
        elif station['aqi'] <= 100:
            color = 'orange'
            severity = '普通'
        else:
            color = 'red'
            severity = '不良'
        
        folium.CircleMarker(
            location=[station['lat'], station['lon']],
            radius=8,
            popup=f"{station['name']}<br>AQI: {station['aqi']}<br>等級: {severity}",
            color='black',
            fillColor=color,
            fillOpacity=0.7
        ).add_to(aqi_group)
    
    # 添加圖層到地圖
    shelter_group.add_to(m)
    aqi_group.add_to(m)
    
    # 添加圖層控制
    folium.LayerControl().add_to(m)
    
    # 添加圖例
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 200px; height: 140px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>圖例</h4>
    <p><i class="fa fa-home" style="color:blue"></i> 室內避難所</p>
    <p><i class="fa fa-tree" style="color:green"></i> 室外避難所</p>
    <p><span style="display:inline-block;width:12px;height:12px;background-color:green"></span> AQI良好(≤50)</p>
    <p><span style="display:inline-block;width:12px;height:12px;background-color:orange"></span> AQI普通(51-100)</p>
    <p><span style="display:inline-block;width:12px;height:12px;background-color:red"></span> AQI不良(>100)</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # 儲存地圖
    m.save('shelter_aqi_intersection_map.html')
    print("地圖已儲存為 shelter_aqi_intersection_map.html")
    
    return m

if __name__ == "__main__":
    create_intersection_map()
