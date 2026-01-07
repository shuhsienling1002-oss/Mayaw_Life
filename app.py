import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 系統配置 ---
st.set_page_config(page_title="人生建築師 - 未來財富模擬", layout="wide")

# --- CSS樣式優化 (讓手機版更好看) ---
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .highlight { color: #FF4B4B; font-weight: bold; }
    .success { color: #00CC96; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 核心運算函數 (Layer 1: Physics Kernel) ---
def calculate_wealth(
    years, 
    start_salary, 
    monthly_living_cost, 
    shadow_rent, 
    skill_investment, 
    invest_return_rate, 
    salary_growth_rate
):
    """
    模擬未來的資產累積
    """
    wealth_path = []
    salary_path = []
    passive_income_path = []
    
    current_assets = 0
    current_salary = start_salary
    
    for i in range(years):
        # 每年薪資成長 (技能投資越高，薪資成長潛力越高)
        current_salary = current_salary * (1 + salary_growth_rate)
        salary_path.append(current_salary)
        
        # 計算年度淨現金流
        # 收入 - 生活費 - 影子房租(強制儲蓄) - 技能投資(消耗但換取未來薪資)
        annual_income = current_salary * 12
        annual_living = monthly_living_cost * 12
        annual_skill_cost = skill_investment * 12
        annual_shadow_rent = shadow_rent * 12 # 這是投入投資帳戶的錢
        
        # 剩餘可自由支配或額外儲蓄的錢 (假設這部分隨性花掉或存一點點，這裡簡化處理)
        disposable = annual_income - annual_living - annual_skill_cost - annual_shadow_rent
        
        # 假設可支配所得中，只有 10% 被額外存下來 (真實人性)
        extra_savings = disposable * 0.1 if disposable > 0 else 0
        
        # 總投資本金增加
        annual_contribution = annual_shadow_rent + extra_savings
        
        # 資產複利滾動
        current_assets = current_assets * (1 + invest_return_rate) + annual_contribution
        wealth_path.append(current_assets)
        
        # 估算被動收入 (假設 4% 殖利率)
        passive_income_path.append((current_assets * 0.04) / 12)
        
    return wealth_path, salary_path, passive_income_path

# --- APP 介面 (Layer 0 & Shell) ---

st.title("🏗️ 人生建築師：你的未來藍圖")
st.markdown("不用記帳，只需「選對模式」。看看 10 年後，不同的選擇會讓你的身價差多少？")

# 側邊欄：基礎設定
with st.sidebar:
    st.header("1. 你的現狀")
    age = st.number_input("現在年齡", 20, 50, 30)
    salary = st.number_input("月薪收入 (元)", 20000, 150000, 55000, step=1000)
    current_savings = st.number_input("目前存款 (元)", 0, 5000000, 100000)
    
    st.header("2. 環境參數")
    simulate_years = st.slider("模擬未來幾年?", 5, 30, 15)
    market_rent = st.slider("如果租房，市價多少? (影子房租)", 5000, 30000, 15000)

# 主畫面：模式選擇
st.subheader("請選擇一種生活模式：")

mode = st.radio(
    "選擇策略模式",
    ["🐢 模式 A：隨性舒適 (現狀)", 
     "🏠 模式 B：影子房東 (強制存房租)", 
     "🚀 模式 C：技能狂人 (投資大腦)", 
     "🛡️ 模式 D：黃金混合 (FP-CRF 推薦)"],
    index=3,
    horizontal=True
)

# 根據模式設定參數
if "模式 A" in mode:
    # 隨性：不存房租，不投資技能，薪資成長低，投資回報低(放活存)
    p_shadow_rent = 0
    p_skill_invest = 0
    p_invest_return = 0.01 # 銀行利息
    p_salary_growth = 0.01 # 僅抗通膨
    desc = "住家裡免房租，錢主要拿來吃喝玩樂。舒服，但資產累積極慢。"
    
elif "模式 B" in mode:
    # 影子房東：存下房租買 ETF，不投資技能
    p_shadow_rent = market_rent
    p_skill_invest = 0
    p_invest_return = 0.06 # ETF 平均報酬
    p_salary_growth = 0.015 # 體力勞工自然增長
    desc = "假裝自己要付房租，把這筆錢存入投資帳戶。資產成長快，但薪水天花板低。"

elif "模式 C" in mode:
    # 技能狂人：錢拿去上課考照，存錢較少，但薪水成長高
    p_shadow_rent = 0 # 錢拿去學費
    p_skill_invest = 5000
    p_invest_return = 0.03 # 保守投資
    p_salary_growth = 0.05 # 技能帶來加薪
    desc = "把錢投資在「自己的大腦」與「證照」。前期資產少，但後期收入爆發力強。"

else: # 模式 D (混合)
    # 混合：存房租 + 小額技能投資 + 穩健投資
    p_shadow_rent = market_rent
    p_skill_invest = 3000 # 每月拿一點錢升級裝備/考照
    p_invest_return = 0.06
    p_salary_growth = 0.035 # 溫和成長
    desc = "【推薦】同時執行「影子房租」與「適度自我投資」。平衡了風險與成長。"

st.info(f"💡 策略分析：{desc}")

# --- 執行運算 ---
wealth, salary_flow, passive = calculate_wealth(
    simulate_years, salary, 20000, p_shadow_rent, p_skill_invest, p_invest_return, p_salary_growth
)

# 加上初始存款
total_wealth = [w + current_savings for w in wealth]
final_amount = total_wealth[-1]
final_passive_monthly = passive[-1] + (current_savings * 0.04 / 12) # 加上原本存款的利息

# --- 結果展示區 ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label=f"{age + simulate_years} 歲時的總資產", value=f"${int(final_amount):,}")
with col2:
    st.metric(label="那時候每個月的「被動收入」", value=f"${int(final_passive_monthly):,}", delta="不工作也有錢領")
with col3:
    st.metric(label="那時候的預估月薪", value=f"${int(salary_flow[-1]):,}", delta=f"比現在成長 {((salary_flow[-1]/salary)-1)*100:.1f}%")

# --- 圖表區 ---
st.subheader("📈 資產成長曲線模擬")

# 為了比較，我們同時算出四種模式 (背景運算)
w_a, _, _ = calculate_wealth(simulate_years, salary, 20000, 0, 0, 0.01, 0.01)
w_b, _, _ = calculate_wealth(simulate_years, salary, 20000, market_rent, 0, 0.06, 0.015)
w_c, _, _ = calculate_wealth(simulate_years, salary, 20000, 0, 5000, 0.03, 0.05)
w_d, _, _ = calculate_wealth(simulate_years, salary, 20000, market_rent, 3000, 0.06, 0.035)

chart_data = pd.DataFrame({
    '隨性舒適 (模式A)': [x + current_savings for x in w_a],
    '影子房東 (模式B)': [x + current_savings for x in w_b],
    '技能升級 (模式C)': [x + current_savings for x in w_c],
    '黃金混合 (模式D)': [x + current_savings for x in w_d]
})

st.line_chart(chart_data)

st.markdown("""
---
### 🛠️ 行動指令 (Action Plan)
1. **去開兩個戶頭**：一個薪轉戶(生存用)，一個證券戶(影子房東用)。
2. **設定自動轉帳**：發薪日當天，自動轉 **${:,}** 到證券戶。
3. **忘記密碼**：證券戶的錢只進不出，把它當作「消失的房租」。
""".format(market_rent))