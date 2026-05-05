import streamlit as st
import pandas as pd

# 設定網頁標題與寬度
st.set_page_config(page_title="FFXI 合成利潤計算機", layout="wide")

# 主標題
st.title("⚔️ FFXI 全項目合成試算助手")
st.caption("連動檔案：FFXI 合成試算表 V2 (公式修正版).xlsx | 目前 Rank: 3")

# 1. 讀取 Excel 資料庫
file_path = 'FFXI 合成試算表 V2 (公式修正版).xlsx'

try:
    # 讀取 Excel，不設標題以利手動定位
    df = pd.read_excel(file_path, sheet_name='FFXI 合成試算表 V2 (公式修正版)', header=None)
    
    # 定位右側計算區：從第 12 欄 (Index 11) 開始
    data_region = df.iloc[:, 11:].dropna(how='all')
    
    # 找出「合成目標」那一行作為選單來源
    target_row_selector = data_region[data_region[11] == '合成目標']
    
    if not target_row_selector.empty:
        target_row_idx = target_row_selector.index[0]
        # 抓取該行所有成品名稱作為下拉選單
        item_names = data_region.loc[target_row_idx, 12:].dropna().tolist()
        
        # --- 側邊欄：功能分區 ---
        st.sidebar.header("🎯 操作面板")
        selected_item = st.sidebar.selectbox("請選擇合成項目", item_names)
        
        st.sidebar.divider()
        st.sidebar.header("📚 Wiki 快速導覽")
        
        # 根據圖片整理的 Crafts 類別
        with st.sidebar.expander("🛠️ Crafts (合成技能)", expanded=True):
            st.markdown("""
            - [Alchemy (鍊金)](https://horizonffxi.wiki/Alchemy)
            - [Bonecraft (骨工)](https://horizonffxi.wiki/Bonecraft)
            - [Clothcraft (裁縫)](https://horizonffxi.wiki/Clothcraft)
            - [Cooking (烹飪)](https://horizonffxi.wiki/Cooking)
            - [Fishing (釣魚)](https://horizonffxi.wiki/Fishing)
            - [Goldsmithing (彫金)](https://horizonffxi.wiki/Goldsmithing)
            - [Leathercraft (革工)](https://horizonffxi.wiki/Leathercraft)
            - [Smithing (鍛冶)](https://horizonffxi.wiki/Smithing)
            - [Woodworking (木工)](https://horizonffxi.wiki/Woodworking)
            """)
            
        # 根據圖片整理的 Hobbies 類別
        with st.sidebar.expander("🌿 Hobbies (生活嗜好)", expanded=False):
            st.markdown("""
            - [Digging (挖掘)](https://horizonffxi.wiki/Chocobo_Digging)
            - [Clamming (採蛤)](https://horizonffxi.wiki/Clamming)
            - [Excavation (坑道發掘)](https://horizonffxi.wiki/Excavation)
            - [Gardening (園藝)](https://horizonffxi.wiki/Gardening)
            - [Harvesting (收穫)](https://horizonffxi.wiki/Harvesting)
            - [Logging (伐木)](https://horizonffxi.wiki/Logging)
            - [Mining (採礦)](https://horizonffxi.wiki/Mining)
            """)
        
        st.sidebar.divider()
        st.sidebar.link_button("🌐 查看所有 Hobbies 分類", "https://horizonffxi.wiki/Category:Hobbies")

        # --- 主畫面邏輯 ---
        if selected_item:
            # 根據選中的名字，定位到正確的直欄 (Column)
            col_idx = data_region.columns[data_region.loc[target_row_idx] == selected_item][0]
            item_data = data_region.set_index(11)[col_idx]
            
            # 顯示標題與 Wiki 按鈕
            st.subheader(f"📊 {selected_item} 成本利潤即時試算")
            wiki_url = f"https://horizonffxi.wiki/{selected_item.replace(' ', '_')}"
            st.link_button(f"📖 開啟 {selected_item} Wiki 頁面", wiki_url)

            # --- 全動態材料偵測 ---
            st.write("### 💰 即時成本調整 (可手動修改數值)")
            materials = []
            # 自動偵測材料 1 到材料 4
            for i in range(1, 5):
                m_name = item_data.get(f'材料 {i}')
                if pd.notna(m_name) and str(m_name).strip() != "":
                    materials.append({
                        "name": m_name,
                        "cost": float(item_data.get(f'材料 {i} 成本', 0)),
                        "qty": item_data.get(f'材料 {i} 數量', 0)
                    })

            # 動態產生材料與水晶的輸入框
            m_cols = st.columns(len(materials) + 1)
            new_costs = []
            for idx, m in enumerate(materials):
                with m_cols[idx]:
                    val = st.number_input(f"{m['name']} (x{m['qty']})", value=m['cost'], key=f"m_{idx}")
                    new_costs.append(val)
            
            # 水晶輸入框
            with m_cols[-1]:
                crystal = item_data.get('水晶類型', '水晶')
                c_val = st.number_input(f"{crystal}", value=float(item_data.get('水晶單價', 0)), key="c_val")

            st.divider()
            
            # 售價試算區
            st.write("### 💸 利潤計算")
            # 預設抓取 Excel 的「單個價格」，若無則預設 2000
            default_sell = 2000.0
            sell_price = st.number_input("當前市場預期售價 (請參考官網/拍賣場輸入)", value=default_sell, step=100.0)
            
            # 計算結果總結
            total_cost = sum(new_costs) + c_val
            profit = sell_price - total_cost
            
            res_col1, res_col2 = st.columns(2)
            res_col1.metric("即時總成本", f"{total_cost:,.0f} Gil")
            res_col2.metric("預期淨利", f"{profit:,.0f} Gil", delta=f"{profit:,.0f}")
            
            if profit > 0:
                st.success(f"✅ 目前合成 {selected_item} 是獲利的！")
            else:
                st.error(f"❌ 目前處於虧損狀態，請確認材料價格。")

            # 配方備註展開
            with st.expander("📋 查看完整配方與 Excel 原始數據"):
                st.write(f"**水晶：** {item_data.get('水晶類型')}")
                for m_idx, m in enumerate(materials):
                    st.write(f"**材料 {m_idx+1}：** {m['name']} x {m['qty']}")
                st.write("---")
                st.write("該欄位所有 Excel 原始內容：")
                st.write(item_data)
                
    else:
        st.warning("在 Excel 的第 11 欄找不到『合成目標』標籤，請確認 Excel 格式。")

except Exception as e:
    st.error(f"程式執行出錯：{e}")
    st.info("請檢查 GitHub 上的 Excel 檔名與程式碼內設定是否一致。")
