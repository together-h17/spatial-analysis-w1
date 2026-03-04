import pandas as pd
import numpy as np

def check_coordinate_system():
    import os
    # 取得目前目錄中的CSV檔案
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if not csv_files:
        print("未找到CSV檔案")
        return
    
    csv_file = csv_files[0]  # 使用第一個CSV檔案
    print(f"分析檔案: {csv_file}")
    
    df = pd.read_csv(csv_file)
    
    # 檢查座標範圍
    lons = df['經度'].dropna()
    lats = df['緯度'].dropna()
    
    print("=== 座標分析 ===")
    print(f"經度範圍: {lons.min():.6f} ~ {lons.max():.6f}")
    print(f"緯度範圍: {lats.min():.6f} ~ {lats.max():.6f}")
    
    # 判斷座標系統
    if (118 <= lons.min() and lons.max() <= 124 and 
        20 <= lats.min() and lats.max() <= 26):
        print("座標系統: 經緯度 (EPSG:4326)")
    elif (lons.min() > 1000 or lats.min() > 1000):
        print("座標系統: 二度分帶 (EPSG:3826)")
    else:
        print("座標系統: 無法確定")
    
    # 檢查異常點
    print("\n=== 異常點檢查 ===")
    
    # (0,0)點
    zero_points = df[(df['經度'] == 0) | (df['緯度'] == 0)]
    print(f"(0,0)異常點數量: {len(zero_points)}")
    
    # 台灣邊界外點 (經緯度範圍)
    taiwan_bounds = (118, 124, 20, 26)  # (min_lon, max_lon, min_lat, max_lat)
    outside_points = df[
        (df['經度'] < taiwan_bounds[0]) | (df['經度'] > taiwan_bounds[1]) |
        (df['緯度'] < taiwan_bounds[2]) | (df['緯度'] > taiwan_bounds[3])
    ]
    print(f"台灣邊界外點數量: {len(outside_points)}")
    
    if len(outside_points) > 0:
        print("\n邊界外點位:")
        for idx, row in outside_points.iterrows():
            print(f"序號{row['序號']}: ({row['經度']}, {row['緯度']}) - {row['避難收容處所名稱']}")
    
    # 空值統計
    print(f"\n空值統計:")
    print(f"經度空值: {df['經度'].isnull().sum()}")
    print(f"緯度空值: {df['緯度'].isnull().sum()}")

if __name__ == "__main__":
    check_coordinate_system()
