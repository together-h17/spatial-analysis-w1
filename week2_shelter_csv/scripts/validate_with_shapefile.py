import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

def validate_with_taiwan_boundary():
    import os
    # 設定工作目錄
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(script_dir))
    
    # 讀取避難收容所數據
    csv_files = [f for f in os.listdir('data') if f.endswith('.csv') and '避難收容處所點位檔案v9' in f and '邊界驗證版' not in f]
    if not csv_files:
        print("未找到避難收容所CSV檔案")
        return
    
    shelter_df = pd.read_csv(f'data/{csv_files[0]}')
    print(f"讀取檔案: {csv_files[0]}")
    
    # 讀取台灣縣市邊界shapefile
    shapefile_path = 'data/縣市界線(TWD97經緯度)/COUNTY_MOI_1090820.shp'
    taiwan_boundary = gpd.read_file(shapefile_path)
    
    print("=== 台灣邊界資訊 ===")
    print(f"座標系統: {taiwan_boundary.crs}")
    print(f"縣市數量: {len(taiwan_boundary)}")
    print(f"邊界範圍: {taiwan_boundary.total_bounds}")
    
    # 將避難收容所轉換為GeoDataFrame
    geometry = []
    valid_indices = []
    
    for idx, row in shelter_df.iterrows():
        try:
            lon, lat = float(row['經度']), float(row['緯度'])
            
            # 跳過(0,0)點
            if lon == 0 or lat == 0:
                print(f"跳過(0,0)點: 序號{row['序號']}")
                continue
                
            point = Point(lon, lat)
            geometry.append(point)
            valid_indices.append(idx)
            
        except (ValueError, TypeError):
            print(f"無效座標: 序號{row['序號']}")
            continue
    
    # 創建避難收容所GeoDataFrame
    shelters_gdf = gpd.GeoDataFrame(
        shelter_df.loc[valid_indices],
        geometry=geometry,
        crs='EPSG:4326'  # WGS84經緯度
    )
    
    print(f"\n=== 避難收容所統計 ===")
    print(f"原始資料數量: {len(shelter_df)}")
    print(f"有效座標數量: {len(shelters_gdf)}")
    
    # 確保座標系統一致
    if taiwan_boundary.crs != shelters_gdf.crs:
        taiwan_boundary = taiwan_boundary.to_crs(shelters_gdf.crs)
    
    # 空間連接：檢查哪些避難所在台灣邊界內
    shelters_within_boundary = gpd.sjoin(shelters_gdf, taiwan_boundary, how='inner', predicate='within')
    
    print(f"台灣邊界內數量: {len(shelters_within_boundary)}")
    print(f"邊界外數量: {len(shelters_gdf) - len(shelters_within_boundary)}")
    
    # 找出邊界外的避難所
    shelters_outside = shelters_gdf[~shelters_gdf.index.isin(shelters_within_boundary.index)]
    
    if len(shelters_outside) > 0:
        print(f"\n=== 邊界外避難所 ===")
        for idx, row in shelters_outside.iterrows():
            print(f"序號{row['序號']}: ({row['經度']}, {row['緯度']}) - {row['避難收容處所名稱']}")
    
    # 保存清理後的數據
    cleaned_data = shelters_within_boundary.drop(columns=['geometry', 'index_right'])
    cleaned_data.to_csv('output/避難收容處所點位位檔案v9_邊界驗證版.csv', index=False, encoding='utf-8-sig')
    
    print(f"\n=== 輸出結果 ===")
    print(f"清理後數據已保存為: 避難收容處所點位位檔案v9_邊界驗證版.csv")
    print(f"保留數量: {len(cleaned_data)}")
    print(f"移除數量: {len(shelter_df) - len(cleaned_data)}")
    
    return shelters_within_boundary, shelters_outside

if __name__ == "__main__":
    validate_with_taiwan_boundary()
