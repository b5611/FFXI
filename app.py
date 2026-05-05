import streamlit as st
import pandas as pd

st.set_page_config(page_title="FFXI 合成利潤計算機", layout="wide")
st.title("⚔️ FFXI 全項目合成試算助手")

# 1. 讀取 Excel 資料庫
file_path = 'FFXI 合成試算表 V2 (公式修正版).xlsx'
try:
    # 讀取 Excel，不設標題
    df = pd.read_excel(file_path, sheet_name='FFXI 合成試算表 V2 (公式修正版)', header=None)
    
    # 定位右側計算區：從第 12 欄 (Index 11) 開始是「項目」欄位
    data_region = df.iloc[:, 11:].dropna(how='all')
    
    # 找出「合成目標」那一行作為選單來源
    # 這裡會掃描第 11 欄，找到寫著「合成目標」的那一列
    target_row_selector = data_region[data_region[11] == '合成目標']
    
    if not target_row_selector.empty:
        target_row_idx = target_row_selector.index[0]
        # 抓取該行從第 12 欄開始的所有成品名稱 (Shihei, Acid Bolt, Echo Drops...)
        item_names = data_region.loc[target_row_idx, 12:].dropna().tolist()
        
        # 側邊欄：選擇項目 (這裡現在會顯示你 Excel 裡所有的綠色格子目標)
        selected_item = st.sidebar.selectbox("🎯 選擇合成項目", item_names)
        
        # 側邊欄：Wiki 快速連結
        st.sidebar.divider()
        st.sidebar.markdown("### 📚 快速導覽\n- [Hobbies (技能總覽)](https://horizonffxi.wiki/Category:Hobbies)\n- [Alchemy (鍊金)](https://horizonffxi.wiki/Alchemy)\n- [Cooking (烹飪)](https://horizonffxi.wiki/Cooking)")

        if selected_item:
            # 根據選中的名字，定位到正確的直欄 (Column)
            col_idx = data_region.columns[data_region.loc[target_row_idx] == selected_item][0]
            item_data = data_region.set_index(11)[col_idx]
            
            # 顯示標題與 Wiki 連結
            st.subheader(f"📊 {selected_item} 成本利潤試算")
            wiki_url = f"https://horizonffxi.wiki/{selected_item.replace(' ', '_')}"
            st.link_button(f"📖 開啟 {selected_item} Wiki 頁面", wiki_url)

            # --- 動態材料輸入區 ---
            st.write("### 💰 即時成本調整")
            materials = []
            for i in range(1, 5): # 檢查材料 1-4
                m_name = item_data.get(f'材料 {i}')
                if pd.notna(m_name) and str(m_name).strip() != "":
                    materials.append({
                        "name": m_name,
                        "cost": float(item_data.get(f'材料 {i} 成本', 0)),
                        "qty": item_data.get(f'材料 {i} 數量', 0)
                    })

            # 動態產生輸入框
            m_cols = st.columns(len(materials) + 1)
            new_costs = []
            for idx, m in enumerate(materials):
                with m_cols[idx]:
                    val = st.number_input(f"{m['name']} (x{m['qty']})", value=m['cost'])
                    new_costs.append(val)
            
            with m_cols[-1]:
                crystal = item_data.get('水晶類型', '水晶')
                c_val = st.number_input(f"{crystal}", value=float(item_data.get('水晶單價', 0)))

            st.divider()
            
            # 售價試算
            sell_price = st.number_input("💸 當前市場售價 (手動輸入)", value=2000.0, step=100.0)
            
            # 計算結果
            total_cost = sum(new_costs) + c_val
            profit = sell_price - total_cost
            
            r1, r2 = st.columns(2)
            r1.metric("總成本", f"{total_cost:,.0f} Gil")
            r2.metric("預期利潤", f"{profit:,.0f} Gil", delta=f"{profit:,.0f}")
            
            if profit > 0:
                st.success("✅ 有利潤")
            else:
                st.error("❌ 虧損中")
    else:
        st.warning("在 Excel 中找不到『合成目標』字樣，請檢查格式。")

except Exception as e:
    st.error(f"讀取失敗：{e}")
