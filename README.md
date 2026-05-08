# 5G 信号可视化看板

基于 Streamlit 的 5G 路测数据交互式 Web 看板，支持 2D/3D 地图、多维度联动筛选与实时统计图表。

---

## 功能一览

基础关卡

- 数据加载与清洗（pandas）
- 信号点散点地图，按 RSRP 强度三色显示（绿/橙/红）
- 频段基站数量柱状图 + 终端类型占比饼图

进阶关卡

- 侧边栏多维度联动筛选（频段、RSRP 范围、终端类型）
- 3D 柱状地图，柱高映射下载速率，颜色仍反映 RSRP
- 核心函数单元测试（pytest）+ 规范注释
- 额外 KPI 卡片、SINR-RSRP 关系散点图

---

## 文件结构
app.py # 主应用入口
requirements.txt # Python 依赖
test_app.py # 单元测试
README.md # 本说明文档
AI_PROMPTS.md # AI 交互日志
data/
signal_samples.csv # 5G 路测数据集

使用说明
左侧边栏可筛选频段、RSRP 信号强度范围和终端类型，地图与图表实时响应
主页顶部切换 2D 散点或 3D 柱状地图，3D 模式下可旋转和缩放视角
鼠标悬停于地图点可查看详细指标（CellID、RSRP、SINR、下载速率）
下方图表展示频段分布、终端占比以及 SINR-RSRP 关系
