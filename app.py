import streamlit as st
import pandas as pd

st.set_page_config(page_title="FFXI 合成利潤計算機", layout="wide")
st.title("⚔️ FFXI 合成利潤即時試算")

# 1. 讀取 Excel 資料庫
file_path = 'FFXI 合成試算表 V2 (公式修正版).xlsx'
try:
    df = pd.read_excel(file_path, sheet_name='FFXI 合成試算表 V2 (公式修正版)', header=None)
    data_region = df.iloc[:, 11:].dropna(how='all')
    
    target_row_idx = data_region[data_region[11] == '合成目標'].index[0]
    item_names = data_region.loc[target_row_idx, 12:].dropna().tolist()
    
    # 側邊欄：Wiki 快速導覽
    st.sidebar.header("📚 Wiki 快速導覽")
    st.sidebar.markdown("""
    - [Alchemy (鍊金)](https://horizonffxi.wiki/Alchemy)
    - [Cooking (烹飪)](https://horizonffxi.wiki/Cooking)
    - [Woodworking (木工)](https://horizonffxi.wiki/Woodworking)
    - [Clothcraft (裁縫)](https://horizonffxi.wiki/Clothcraft)
    """)
    
    selected_item = st.sidebar.selectbox("🎯 選擇合成項目", item_names)

    if selected_item:
        col_idx = data_region.columns[data_region.loc[target_row_idx] == selected_item][0]
        item_data = data_region.set_index(11)[col_idx]
        
        # 建立 Wiki 連結 (將空白換成底線)
        wiki_url = f"https://horizonffxi.wiki/{selected_item.replace(' ', '_')}"
        
        st.subheader(f"📊 {selected_item} 成本與利潤分析")
        st.link_button(f"📖 在 Horizon Wiki 查看 {selected_item} 細節", wiki_url)

        # --- 動態材料偵測 ---
        st.write("### 💰 即時市價調整")
        materials_to_show = []
        for i in range(1, 5):
            m_name = item_data.get(f'材料 {i}')
            if pd.notna(m_name) and str(m_name).strip() != "":
                materials_to_show.append({
                    "id": i, "name": m_name,
                    "cost": float(item_data.get(f'材料 {i} 成本', 0)),
                    "count": item_data.get(f'材料 {i} 數量', 0)
                })

        cols = st.columns(len(materials_to_show) + 1)
        updated_costs = []
        for idx, mat in enumerate(materials_to_show):
            with cols[idx]:
                new_val = st.number_input(f"{mat['name']} (x{mat['count']})", value=mat['cost'], key=f"mat_{mat['id']}")
                updated_costs.append(new_val)
        
        with cols[-1]:
            new_crystal = st.number_input(f"{item_data.get('水晶類型', '水晶')}", value=float(item_data.get('水晶單價', 0)))

        st.divider()
        sell_price = st.number_input("市場預期售價 (請手動輸入官網價格)", value=2000.0)

        total_cost = sum(updated_costs) + new_crystal
        profit = sell_price - total_cost
        
        res_col1, res_col2 = st.columns(2)
        res_col1.metric("即時總成本", f"{total_cost:,.0f} Gil")
        res_col2.metric("預期利潤", f"{profit:,.0f} Gil", delta=f"{profit:,.0f}")
        
        if profit > 0:
            st.success("✅ 利潤為正")
        else:
            st.error("❌ 虧損中")

except Exception as e:
    st.error(f"讀取失敗：{e}")
