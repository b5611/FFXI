import streamlit as st
import pandas as pd

st.set_page_config(page_title="FFXI 合成利潤計算機", layout="wide")
st.title("⚔️ FFXI 合成利潤即時試算")
st.caption("連動檔案：FFXI 合成試算表 V2 (公式修正版).xlsx | 目前 Rank: 3")

# 1. 讀取 Excel 資料庫
file_path = 'FFXI 合成試算表 V2 (公式修正版).xlsx'
try:
    df = pd.read_excel(file_path, sheet_name='FFXI 合成試算表 V2 (公式修正版)', header=None)
    data_region = df.iloc[:, 11:].dropna(how='all')
    
    target_row_idx = data_region[data_region[11] == '合成目標'].index[0]
    item_names = data_region.loc[target_row_idx, 12:].dropna().tolist()
    
    selected_item = st.sidebar.selectbox("🎯 選擇合成項目", item_names)

    if selected_item:
        col_idx = data_region.columns[data_region.loc[target_row_idx] == selected_item][0]
        item_data = data_region.set_index(11)[col_idx]
        
        st.subheader(f"📊 {selected_item} 成本與利潤分析")
        
        # --- 動態材料偵測核心邏輯 ---
        st.write("### 💰 即時市價調整")
        
        # 建立材料清單 (最多檢查到材料 4)
        materials_to_show = []
        for i in range(1, 5):
            m_name = item_data.get(f'材料 {i}')
            if pd.notna(m_name) and str(m_name).strip() != "":
                materials_to_show.append({
                    "id": i,
                    "name": m_name,
                    "cost": float(item_data.get(f'材料 {i} 成本', 0)),
                    "count": item_data.get(f'材料 {i} 數量', 0)
                })

        # 動態產生輸入框 (每行顯示 3 個)
        cols = st.columns(len(materials_to_show) + 1) # 材料加水晶
        updated_costs = []

        # 產生材料輸入框
        for idx, mat in enumerate(materials_to_show):
            with cols[idx]:
                new_val = st.number_input(f"{mat['name']} (x{mat['count']})", value=mat['cost'], key=f"mat_{mat['id']}")
                updated_costs.append(new_val)
        
        # 產生水晶輸入框 (放在最後一個 Column)
        with cols[-1]:
            crystal_name = item_data.get('水晶類型', '水晶')
            default_crystal = float(item_data.get('水晶單價', 0))
            new_crystal = st.number_input(f"{crystal_name}", value=default_crystal, key="crystal")

        # 售價輸入
        st.divider()
        sell_price = st.number_input("市場預期售價 (請參考官網手動輸入)", value=2000.0, step=100.0)

        # --- 計算結果 ---
        total_cost = sum(updated_costs) + new_crystal
        profit = sell_price - total_cost
        
        res_col1, res_col2 = st.columns(2)
        res_col1.metric("即時總成本", f"{total_cost:,.0f} Gil")
        res_col2.metric("預期利潤", f"{profit:,.0f} Gil", delta=f"{profit:,.0f}")
        
        if profit > 0:
            st.success(f"✅ 利潤為正：建議製作")
        else:
            st.error(f"❌ 虧損中：請評估材料來源")

        with st.expander("查看配方完整細節"):
            st.write(f"水晶：{item_data.get('水晶類型')}")
            for mat in materials_to_show:
                st.write(f"材料 {mat['id']}：{mat['name']} x {mat['count']}")

except Exception as e:
    st.error(f"讀取失敗：{e}")
