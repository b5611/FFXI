import streamlit as st
import pandas as pd

st.set_page_config(page_title="FFXI 合成利潤計算機", layout="wide")
st.title("⚔️ FFXI 合成利潤即時試算")
st.caption("連動檔案：FFXI 合成試算表 V2 (公式修正版).xlsx | 目前 Rank: 3")

# 1. 讀取 Excel 資料庫
file_path = 'FFXI 合成試算表 V2 (公式修正版).xlsx'
try:
    # 讀取全部資料，不設 header 方便定位
    df = pd.read_excel(file_path, sheet_name='FFXI 合成試算表 V2 (公式修正版)', header=None)
    data_region = df.iloc[:, 11:].dropna(how='all')
    
    # 定位「合成目標」列與項目清單
    target_row_idx = data_region[data_region[11] == '合成目標'].index[0]
    item_names = data_region.loc[target_row_idx, 12:].dropna().tolist()
    
    # 側邊欄：選擇目標
    selected_item = st.sidebar.selectbox("🎯 選擇合成項目", item_names)

    if selected_item:
        # 抓取該成品的欄位資料
        col_idx = data_region.columns[data_region.loc[target_row_idx] == selected_item][0]
        item_data = data_region.set_index(11)[col_idx]
        
        st.subheader(f"📊 {selected_item} 成本與利潤分析")
        
        # --- 互動輸入區 ---
        st.write("### 💰 即時市價調整 (修改下方數值可直接試算)")
        c_col1, c_col2, c_col3 = st.columns(3)
        
        with c_col1:
            # 獲取 Excel 中的預設成本
            default_c1 = float(item_data.get('材料 1 成本', 0))
            new_c1 = st.number_input(f"{item_data.get('材料 1', '材料1')} 成本", value=default_c1, step=100.0)
            
        with c_col2:
            default_c2 = float(item_data.get('材料 2 成本', 0))
            new_c2 = st.number_input(f"{item_data.get('材料 2', '材料2')} 成本", value=default_c2, step=100.0)
            
        with c_col3:
            default_crystal = float(item_data.get('水晶單價', 0))
            new_crystal = st.number_input("水晶單價 (單個)", value=default_crystal, step=10.0)

        # 售價輸入
        st.divider()
        sell_price = st.number_input("市場預期售價 (每疊/每個)", value=2000.0, step=100.0)

        # --- 計算結果 ---
        total_cost = new_c1 + new_c2 + new_crystal
        profit = sell_price - total_cost
        
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("即時總成本", f"{total_cost:,.0f} Gil")
        res_col2.metric("預期利潤", f"{profit:,.0f} Gil", delta=f"{profit:,.0f}")
        
        if profit > 0:
            st.success(f"✅ 目前利潤為正！建議合成。")
        else:
            st.error(f"❌ 目前虧損中，請重新評估材料價格。")

        # 顯示配方細節備查
        with st.expander("查看原始配方細節"):
            st.write(f"水晶：{item_data.get('水晶類型')}")
            st.write(f"材料 1：{item_data.get('材料 1')} x {item_data.get('材料 1 數量')}")
            st.write(f"材料 2：{item_data.get('材料 2')} x {item_data.get('材料 2 數量')}")

except Exception as e:
    st.error(f"讀取失敗：{e}")
