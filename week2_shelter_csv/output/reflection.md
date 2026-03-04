## **Reflection / 每週反思**

### 原始資料發現的問題 (屬於本周課程EX1 的內容)

1. **座標異常值**
    - (0,0)座標點：3個完全無效的座標
    - 超出合理範圍：45個點位經緯度超出台灣邊界
    - 精度不一致：部分座標精度達小數點後6位，部分僅3位
2. **屬性資料缺失**
    - **村里欄位空值**：209個避難所缺乏村里資訊
    - **地址格式混亂**：混用數字格式（12-1號 vs 十二之一號）
    - **預計收容人數**：部分設施標示為0，可能為未填寫或實際無收容能力
3. **聯絡資訊問題**
    - **電話號碼格式**：混用不同分隔符號（03-5851001 vs 03 585 1001）
    - **管理人姓名**：包含職稱混雜（張兒 vs 張經理）

### 室內/室外屬性缺失的處理困境

在原始csv檔案中，原本就有’室內’及’室外’欄位，可透過欄位直接初步判斷是內外情形，如果原始資料欄位沒有提供，才會根據設施名稱判斷。

```python
# 邏輯處理優先順序
if row['室內'] == '是':
    facility_type = '室內'
elif row['室外'] == '是':
    facility_type = '室外'
else:
    # 根據設施名稱推斷
    if '學校' in name or '教室' in name:
        facility_type = '室內'
    elif '操場' in name or '廣場' in name:
        facility_type = '室外'
    else:
        facility_type = '未知'
```

**處理結果**：

- 成功分類85%的設施
- 15%設施標記為「未知」，需人工確認
- 建立設施類型推斷規則庫

### AI協作Cascade表現優異的方面

1. **程式碼生成與除錯**
    - 快速生成Haversine距離計算函數
    - 自動處理中文編碼問題
    - 有效解決環境配置問題
2. **空間分析邏輯**
    - 正確識別座標系統轉換需求
    - 準確實作空間連接演算法
    - 建立完整的風險評估框架

### CRS座標系統的「幻覺」問題

坐標系統經郭簡單判斷沒有出現幻覺問題，但是對於位置點是否在台灣範圍外出現許多判斷錯誤。

1. **初始誤判**：最初誤將部分邊界外點判定為海洋中的異常點
2. **座標範圍假設**：過度依賴簡單的矩形範圍(118-124, 20-26)
3. **離島處理盲點**：未考慮金門、馬祖等離島的特殊性

**修正**：

- 主動給予 shapefile 進行精確邊界判定
- 建立離島地區的特殊處理邏輯
- 考慮不同座標系統的實際覆蓋範圍

### 空間推理指標評估

### 「最近測站」指標的合理性分析

**優點**：

1. **簡單直觀**：易於理解和實作
2. **計算效率**：O(n)時間複雜度，適合大規模資料
3. **初步篩選**：可快速識別潛在風險區域

**限制性**：

1. **忽略空間異質性**：空氣品質在空間上並非均勻分布
2. **距離權重缺失**：未考慮距離衰減效應
3. **地形因素忽略**：未考慮山脈、河谷等地形影響

### 身為主導**開發**者可考慮的額外變數

基於課程主題的AQI，我認為可以增加其他相關類型的資料，如風向風速、地形、人口、季節(時序)等。

**— 地形因素**

- **海拔高度**：空氣品質隨高度變化
- **地形遮蔽**：山脈阻擋污染物傳播
- **海岸效應**：海陸風影響污染物擴散

**— 時間因素**

- **季節變化**：不同季節風向模式
- **日夜差異**：海陸風日夜變化
- **特殊天氣**：颱風、鋒面影響

### **— AI 根據人工主導開發者提供的建議 改進的評估模型**

**多因子綜合評估**：

```python
# 風向影響模型
def calculate_wind_effect(aqi_station, shelter, wind_direction, wind_speed):
    angle = calculate_angle(aqi_station, shelter, wind_direction)
    if abs(angle) < 45:  # 順風方向
        distance_factor = 0.8  # 順風傳播距離增加
    elif abs(angle) > 135:  # 逆風方向
        distance_factor = 1.5  # 逆風傳播距離減少
    else:
        distance_factor = 1.0
    return adjusted_distance * distance_factor
```

```python
# 人口加權風險評估
def calculate_population_weighted_risk(shelter_capacity, nearby_population):
    base_risk = aqi_level / 100
    population_factor = nearby_population / 10000
    return base_risk * (1 + population_factor * 0.3)
```

```python
def comprehensive_risk_assessment(shelter, aqi_stations, weather_data):
    # 1. 基礎距離計算
    nearest_station = find_nearest_with_wind(shelter, aqi_stations, weather_data)

    # 2. 風向調整
    wind_adjusted_distance = apply_wind_correction(nearest_station, weather_data)

    # 3. 地形調整
    terrain_adjusted_aqi = apply_terrain_correction(nearest_station.aqi, shelter)

    # 4. 人口加權
    population_weight = calculate_population_weight(shelter)

    # 5. 時間因子
    temporal_factor = get_temporal_adjustment()

    # 綜合風險分數
    risk_score = (terrain_adjusted_aqi * population_weight *
                  temporal_factor / wind_adjusted_distance)

    return classify_risk(risk_score)
```

### 學到的經驗

1. **使用shapefile作為邊界判斷標準**：提升邊界判定準確性
2. **空間資料品質**：原始資料清理
3. **座標系統重要性**：CRS錯誤會導致整個分析失效
4. **情境模擬價值**：測試案例驗證系統穩健性
5. **學會使用 Markdown 語法進行報告書寫**：讓文字有比較結構化的排版