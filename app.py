"""
5G 信号可视化看板 - Code with AI 挑战赛
使用 Streamlit + Pydeck + Plotly 展示 5G 路测数据。
基础功能：颜色映射散点地图、频段/终端类型统计图表。
进阶功能：侧边栏多维度联动筛选、3D 信号柱状图、KPI 卡片。
"""
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

# -------------------------- 页面配置 --------------------------
st.set_page_config(
    page_title="5G 信号可视化看板",
    page_icon="📶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------- 数据加载与缓存 --------------------------
@st.cache_data
def load_data(path: str = "data/signal_samples.csv") -> pd.DataFrame:
    """加载 CSV 数据并执行基础清洗。"""
    df = pd.read_csv(path)
    # 确保必要的列为数值类型
    numeric_cols = ["Latitude", "Longitude", "RSRP_dBm", "SINR_dB", "Download_Mbps"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["Latitude", "Longitude", "RSRP_dBm"])

def assign_rsrp_color(rsrp: float) -> list:
    """
    根据 RSRP 信号强度返回 RGB 颜色。
    > -90 dBm : 绿色 (优秀)
    -110 ~ -90 dBm : 橙色 (中等)
    < -110 dBm : 红色 (差)
    """
    if rsrp >= -90:
        return [0, 255, 0]
    elif rsrp <= -110:
        return [255, 0, 0]
    else:
        return [255, 165, 0]

def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """为数据帧添加颜色列，供图层使用。"""
    df = df.copy()
    df["color"] = df["RSRP_dBm"].apply(assign_rsrp_color)
    return df

# -------------------------- 初始化数据 --------------------------
df = load_data()
df = prepare_dataframe(df)

# -------------------------- 侧边栏联动筛选器 --------------------------
st.sidebar.title("📊 筛选控制面板")
st.sidebar.markdown("通过以下条件动态筛选信号点，地图和图表将实时更新。")

# 频段筛选
all_bands = sorted(df["Band"].unique())
selected_bands = st.sidebar.multiselect(
    "选择频段 (Band)",
    options=all_bands,
    default=all_bands,
    help="可多选，默认全选"
)

# RSRP 范围滑块
rsrp_min = float(df["RSRP_dBm"].min())
rsrp_max = float(df["RSRP_dBm"].max())
rsrp_range = st.sidebar.slider(
    "RSRP 信号强度范围 (dBm)",
    min_value=rsrp_min,
    max_value=rsrp_max,
    value=(-120.0, -70.0),
    step=1.0,
    help="拖动两端滑块调整 RSRP 范围"
)

# 终端类型筛选
all_terminals = sorted(df["TerminalType"].unique())
selected_terminals = st.sidebar.multiselect(
    "终端类型 (TerminalType)",
    options=all_terminals,
    default=all_terminals,
    help="可多选，默认全选"
)

# -------------------------- 数据过滤 --------------------------
mask_band = df["Band"].isin(selected_bands)
mask_rsrp = (df["RSRP_dBm"] >= rsrp_range[0]) & (df["RSRP_dBm"] <= rsrp_range[1])
mask_terminal = df["TerminalType"].isin(selected_terminals)

filtered_df = df[mask_band & mask_rsrp & mask_terminal].copy()

# 侧边栏底部显示当前筛选结果数量
st.sidebar.metric("当前显示信号点", len(filtered_df))
st.sidebar.markdown("---")
st.sidebar.info("💡 右上角可切换 2D 散点 / 3D 柱状地图")

# -------------------------- 主页内容 --------------------------
st.title("📶 5G 信号路测数据可视化看板")
st.markdown("基于 `signal_samples.csv` 的动态交互式分析面板，支持 2D/3D 地图、多维度筛选与实时统计。")

# KPI 卡片
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📡 平均 RSRP (dBm)", f"{filtered_df['RSRP_dBm'].mean():.2f}")
with col2:
    st.metric("📶 平均 SINR (dB)", f"{filtered_df['SINR_dB'].mean():.2f}")
with col3:
    st.metric("⚡ 平均下载速率 (Mbps)", f"{filtered_df['Download_Mbps'].mean():.2f}")
with col4:
    st.metric("🧩 基站频段数", filtered_df["Band"].nunique())

# -------------------------- 地图区域 --------------------------
st.subheader("📍 信号点地理分布")

# 地图类型切换
map_type = st.radio(
    "选择地图样式",
    ["🌍 2D 散点地图", "🏗️ 3D 柱状图 (高度 = 下载速率)"],
    horizontal=True,
    help="2D 为彩色散点；3D 柱的高度反映下载速率，颜色仍由 RSRP 决定"
)

# 视图状态配置
view_state = pdk.ViewState(
    latitude=filtered_df["Latitude"].mean(),
    longitude=filtered_df["Longitude"].mean(),
    zoom=12,
    pitch=45 if "3D" in map_type else 0,
    bearing=0
)

if "2D" in map_type:
    # 基础关卡要求：散点地图，按 RSRP 变色
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position=["Longitude", "Latitude"],
        get_radius=25,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
    )
    deck = pdk.Deck(
        layers=[scatter_layer],
        initial_view_state=view_state,
        tooltip={"text": "CellID: {CellID}\nRSRP: {RSRP_dBm} dBm\nSINR: {SINR_dB} dB\n下载: {Download_Mbps} Mbps"}
    )
else:
    # 进阶关卡：3D 柱状图，高度 = 下载速率
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=filtered_df,
        get_position=["Longitude", "Latitude"],
        get_elevation="Download_Mbps",
        elevation_scale=2,  # 放大高度可视化效果
        radius=30,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
        extruded=True,
    )
    deck = pdk.Deck(
        layers=[column_layer],
        initial_view_state=view_state,
        tooltip={"text": "CellID: {CellID}\n下载速率: {Download_Mbps} Mbps\nRSRP: {RSRP_dBm} dBm"}
    )

st.pydeck_chart(deck, use_container_width=True)

# -------------------------- 数据概览图表 --------------------------
st.subheader("📊 数据概览统计")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # 各频段基站数量（柱状图）
    band_counts = filtered_df["Band"].value_counts().reset_index()
    band_counts.columns = ["Band", "Count"]
    fig_bar = px.bar(
        band_counts,
        x="Band",
        y="Count",
        color="Band",
        title="各频段信号点数量",
        labels={"Band": "频段", "Count": "数量"},
        text="Count"
    )
    fig_bar.update_traces(textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    # 终端类型占比饼图
    terminal_counts = filtered_df["TerminalType"].value_counts().reset_index()
    terminal_counts.columns = ["TerminalType", "Count"]
    fig_pie = px.pie(
        terminal_counts,
        names="TerminalType",
        values="Count",
        title="终端类型占比",
        color="TerminalType",
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# 额外：SINR vs RSRP 散点图，展示信号质量关系（差异化内容）
st.subheader("📈 信号质量关系 (SINR vs RSRP)")
fig_scatter = px.scatter(
    filtered_df,
    x="RSRP_dBm",
    y="SINR_dB",
    color="Band",
    size="Download_Mbps",
    hover_data=["CellID", "TerminalType"],
    title="RSRP 与 SINR 关系散点图 (点大小 = 下载速率)"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# -------------------------- 页脚 --------------------------
st.markdown("---")
st.caption("🚀 由 Streamlit + Pydeck + Plotly 驱动 | Code with AI 挑战赛作品")