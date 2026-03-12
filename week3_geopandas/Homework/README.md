## AI Debugging & Development Log

在完成作業的過程中，實際遇到不少技術問題，以下為開發紀錄。

### Buffer 計算效能問題

在進行 river buffer 計算時，由於河川 shapefile 的 geometry 較大且複雜，電腦長時間無法成功產生結果。

嘗試過的解決方式：

1.直接在本地電腦執行
→ 結果電腦效能不足，運算時間過長超過一個半小時，都沒有輸出結果。

2️. 嘗試使用 Google Colab
→ 因為 RAM 使用量過高，導致 kernel crash。

當時一度懷疑：

buffer 程式寫錯

CRS 投影設定錯誤

geometry 過大

甚至考慮不使用 buffer 方法完成作業，改為直接使用 最短距離計算（mindiff）。

最後：

借用其他電腦重新執行成功完成 buffer 計算，但仍花費不少時間。

### matplotlib 中文顯示錯誤

在繪製統計圖時：

中文行政區名稱出現 方框或亂碼

負號顯示錯誤

解決方式：

設定 matplotlib 字型：

matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
### Folium 地圖資訊缺失

最初 folium 地圖出現問題：
popup 沒有顯示完整資訊
layer 無法切換
buffer 未顯示

解決方式：
將 popup 改為 HTML
新增 LayerControl
將 geometry 轉換為 EPSG:4326

### GeoDataFrame 欄位錯誤

在資料處理時曾遇到 KeyError 欄位名稱不一致。因為原始資料包含 中文欄位名稱。

後續統一改名
'''
rename(columns={
    '預計收容人數':'capacity',
    '避難收容處所名稱':'name'
})
'''
### Shelter 點位資料清理問題

資料清理時發現一個問題：

部分 shelter 點位位於海上。

只做了刪除 (0,0) 座標及 NULL geometry，但沒有進一步檢查是否落在台灣陸地範圍內。

因此仍有部分 shelter 落在海上，這是資料清理時的疏失。

若重新處理資料，應增加
'point within Taiwan polygon'或 'distance from coastline'來過濾不合理點位。

### Summary

本次作業的主要挑戰包括：
- 大型 geometry buffer 計算效能問題
- GIS 套件版本衝突
- 中文資料處理
- folium 地圖整合
- 空間資料清理

透過多次嘗試與除錯後，最終成功完成：

- 河川 buffer 風險分析
- shelter 空間關聯
- 互動式地圖與統計圖輸出