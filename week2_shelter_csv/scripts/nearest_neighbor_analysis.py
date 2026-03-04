import pandas as pd
import numpy as np
import math
import os

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    使用Haversine公式計算兩點間的距離（公里）
    """
    R = 6371  # 地球半徑（公里）
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def find_nearest_aqi_station(shelter_lat, shelter_lon, aqi_stations):
    """
    找到最近的AQI站點
    """
    min_distance = float('inf')
    nearest_station = None
    
    for station in aqi_stations:
        distance = haversine_distance(shelter_lat, shelter_lon, station['lat'], station['lon'])
        if distance < min_distance:
            min_distance = distance
            nearest_station = station.copy()
            nearest_station['distance_km'] = distance
    
    return nearest_station

def nearest_neighbor_analysis():
    # 讀取避難收容所數據
    output_files = [f for f in os.listdir('output') if f.endswith('.csv') and '邊界驗證版' in f]
    if not output_files:
        print("未找到邊界驗驗證版CSV檔案")
        return
    
    shelter_df = pd.read_csv(f'output/{output_files[0]}')
    print(f"讀取檔案: {output_files[0]}")
    
    # AQI站點數據（包含情境模擬）
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
    
    print("=== 情境模擬前AQI狀況 ===")
    good_air_count = sum(1 for s in aqi_stations if s['aqi'] < 50)
    print(f"AQI < 50的站點數量: {good_air_count}/{len(aqi_stations)}")
    
    # 情境注入：如果空氣品質都很好，手動設定高雄站AQI為150
    if good_air_count == len(aqi_stations):
        print("檢測到所有站點AQI < 50，執行情境模擬...")
        # 將高雄站AQI設為150
        for station in aqi_stations:
            if station['name'] == '高雄站':
                station['aqi'] = 150
                print(f"情境模擬：將{station['name']} AQI設為 {station['aqi']}")
                break
    
    print("\n=== 開始最近鄰居分析 ===")
    
    results = []
    
    for idx, row in shelter_df.iterrows():
        try:
            shelter_lat = float(row['緯度'])
            shelter_lon = float(row['經度'])
            
            # 跳過無效座標
            if shelter_lat == 0 or shelter_lon == 0:
                continue
            
            # 找到最近的AQI站點
            nearest_station = find_nearest_aqi_station(shelter_lat, shelter_lon, aqi_stations)
            
            if nearest_station is None:
                continue
            
            # 風險標記
            nearest_aqi = nearest_station['aqi']
            is_outdoor = row['室內'] != '是'
            
            if nearest_aqi > 100:
                risk_level = 'High Risk'
            elif nearest_aqi > 50 and is_outdoor:
                risk_level = 'Warning'
            else:
                risk_level = 'Low Risk'
            
            # 保存結果
            result = {
                '序號': row['序號'],
                '避難收容處所名稱': row['避難收容處所名稱'],
                '縣市及鄉鎮市區': row['縣市及鄉鎮市區'],
                '村里': row['村里'],
                '避難收容處所地址': row['避難收容處所地址'],
                '經度': shelter_lon,
                '緯度': shelter_lat,
                '預計收容人數': row['預計收容人數'],
                '室內': row['室內'],
                '室外': row['室外'],
                '最近AQI站點': nearest_station['name'],
                '最近AQI站點經度': nearest_station['lon'],
                '最近AQI站點緯度': nearest_station['lat'],
                '距離(km)': round(nearest_station['distance_km'], 2),
                '最近AQI值': nearest_aqi,
                '風險等級': risk_level
            }
            
            results.append(result)
            
        except (ValueError, TypeError) as e:
            print(f"處理序號{row.get('序號', 'unknown')}時發生錯誤: {e}")
            continue
    
    # 轉換為DataFrame
    result_df = pd.DataFrame(results)
    
    # 統計結果
    print(f"\n=== 分析結果統計 ===")
    print(f"總避難所數量: {len(result_df)}")
    risk_counts = result_df['風險等級'].value_counts()
    for risk_level, count in risk_counts.items():
        print(f"{risk_level}: {count}個")
    
    # 顯示High Risk案例
    high_risk_cases = result_df[result_df['風險等級'] == 'High Risk']
    if len(high_risk_cases) > 0:
        print(f"\n=== High Risk案例 (前5個) ===")
        for idx, row in high_risk_cases.head().iterrows():
            print(f"序號{row['序號']}: {row['避難收容處所名稱']} - 最近AQI: {row['最近AQI值']} ({row['最近AQI站點']})")
    
    # 保存結果
    output_path = 'output/shelter_aqi_analysis.csv'
    result_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n結果已保存至: {output_path}")
    
    return result_df

if __name__ == "__main__":
    nearest_neighbor_analysis()
