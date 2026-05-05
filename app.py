import streamlit as st
import pandas as pd

# 設定網頁標題與圖示
st.set_page_config(page_title="FFXI 合成計算器", page_icon="⚔️")

st.title("FFXI 合成試算助手 V2")
st.write("目前 Rank: 3") # 根據你的修正紀錄

# 讀取 Excel 檔案
# 注意：請確保 app.py 與 Excel 放在同一個資料夾
file_path = 'FFXI 合成試算表 V2 (公式修正版).xlsx'
try:
    df = pd.read_excel(file_path, sheet_name='FFXI 合成試算表 V2 (公式修正版)')
    
    # 建立搜尋選單
    # 根據你的表格結構提取「合成目標」
    targets = df['內容/公式'].dropna().unique()
    selected_item = st.selectbox("請選擇要合成的項目：", targets)

    # 顯示該項目的合成細節 (這邊可以根據你的表格欄位做更細的抓取)
    st.subheader(f"🔍 {selected_item} 的合成資訊")
    
    # 範例：顯示該項目的數據
    item_data = df[df['內容/公式'] == selected_item]
    st.table(item_data[['項目', '內容/公式']]) 

except Exception as e:
    st.error(f"讀取檔案失敗，請檢查檔名是否正確：{e}")

st.info("提示：你可以在手機瀏覽器直接操作此介面。")