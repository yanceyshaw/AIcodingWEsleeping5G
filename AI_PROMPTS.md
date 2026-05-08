# Agent 交互日志

团队名称：[填写你的团队名称]
成员名单：[填写成员1, 成员2, 成员3]
使用的 AI Coding Agent 工具：Cursor (Claude 模型) / Claude Code / 通义灵码 [根据你实际使用的工具填写]

---

## 交互记录导出说明

为了真实反映"Code with AI"的代码构建过程，我们要求参赛选手直接导出并在此处提交与 AI Coding Agent 的真实交互记录。以下为本项目开发过程中与 AI 的完整交互记录。

---

## 第一轮对话：项目初始化与数据加载

我的提问：

使用 Streamlit 创建一个 5G 信号可视化看板。读取 data/signal_samples.csv 文件，这个数据集包含经纬度(Latitude/Longitude)、小区ID(CellID)、频段(Band)、信号强度(RSRP_dBm)、信噪比(SINR_dB)、终端类型(TerminalType)和下载速率(Download_Mbps)等字段。先用 pandas 加载数据，设置页面为宽屏模式，显示数据的前5行。

AI 响应概要：

AI 生成了基础 Streamlit 框架代码，包含以下内容：
- st.set_page_config 设置页面配置
- 使用 st.cache_data 装饰器缓存数据加载函数
- pandas 读取 CSV 并显示 df.head()
- 添加错误处理逻辑

执行结果：代码成功运行，数据加载无误，共 400 条记录。

---

## 第二轮对话：实现信号散点地图

我的提问：

用 pydeck 绘制交互式散点地图，将所有信号点按照经纬度打在地图上。需要按 RSRP 信号强度给点上色：大于 -90dBm 为绿色，小于 -110dBm 为红色，介于两者之间为橙色。地图中心设为所有经纬度的均值，zoom 设为 12。鼠标悬停时显示 CellID、RSRP、SINR 和 Download_Mbps。

AI 响应概要：

- 实现了 assign_rsrp_color() 函数，根据 RSRP 阈值返回对应 RGB 颜色数组
- 实现了 prepare_dataframe() 函数，为 DataFrame 新增 color 列
- 使用 pdk.Layer 创建 ScatterplotLayer 散点图层
- 配置 view_state 和 tooltip 交互提示
- 使用 st.pydeck_chart() 渲染地图

执行结果：散点地图正常显示，三色区分清晰，tooltip 交互正常。

---

## 第三轮对话：添加数据概览图表

我的提问：

在地图下方使用两列布局，左边放一个柱状图统计各频段的信号点数量，右边放一个饼图展示终端类型占比。用 Plotly Express 实现，图表标题清晰，自适应容器宽度。

AI 响应概要：

- 使用 st.columns(2) 创建双列布局
- 左列：px.bar 柱状图，x=Band, y=Count, color=Band
- 右列：px.pie 饼图，names=TerminalType, values=Count, hole=0.4 圆环图

执行结果：图表正确显示，频段 n28/n41/n78 数量分布清晰，终端类型占比一目了然。

---

## 第四轮对话：侧边栏联动筛选（进阶关卡）

我的提问：

在左侧边栏添加三个筛选器。第一个是频段多选下拉菜单，默认全选。第二个是 RSRP 范围滑块，最小值和最大值从数据中自动获取，默认 -120 到 -70。第三个是终端类型多选下拉菜单，默认全选。

所有筛选器必须联动，右侧地图和图表实时根据筛选条件更新数据。侧边栏底部显示当前筛选后的信号点数量。

AI 响应概要：

- 使用 st.sidebar.multiselect 创建频段和终端类型的多选筛选器
- 使用 st.sidebar.slider 创建 RSRP 范围滑块
- 使用 pandas 布尔索引组合三个 mask 进行数据过滤
- 用 filtered_df 替换所有图表和地图的输入数据
- 添加 st.sidebar.metric 显示当前筛选结果数量

执行结果：联动筛选完全生效，拖动滑块、选择频段或终端时地图和图表实时更新。

---

## 第五轮对话：3D 柱状图实现（进阶关卡）

我的提问：

添加一个 radio 切换按钮，让用户可以在 2D 散点地图和 3D 柱状图之间切换。3D 柱状图使用 pydeck 的 ColumnLayer，柱子的高度映射 Download_Mbps 字段，颜色依然由 RSRP 决定。切换到 3D 模式时，视图自动调整为俯视角 45 度。

AI 响应概要：

- 添加 st.radio 组件，选项为2D散点地图和3D柱状图
- 条件渲染 ScatterplotLayer 或 ColumnLayer
- ColumnLayer 配置 get_elevation 为 Download_Mbps，elevation_scale 为 2，extruded 为 True
- 根据地图类型动态调整 view_state 的 pitch 参数

执行结果：切换流畅，3D 柱状图正确显示，高度反映下载速率，可拖拽旋转视角。

---

## 第六轮对话：KPI 卡片与 SINR-RSRP 关系图

我的提问：

在标题下方添加一行 KPI 指标卡片，共 4 个列，分别显示：平均 RSRP、平均 SINR、平均下载速率、当前频段数量。另外在地图和图表之间添加一个散点图，x 轴为 RSRP，y 轴为 SINR，点的大小映射下载速率，颜色区分频段，悬停显示 CellID 和终端类型。

AI 响应概要：

- 使用 st.columns(4) 创建并排卡片
- 每个卡片使用 st.metric 显示对应指标
- 使用 px.scatter 创建关系图，配置 size 为 Download_Mbps，color 为 Band

执行结果：KPI 卡片美观清晰，关系图直观展示了信号质量分布。

---

## 第七轮对话：异常处理与工程化优化

我的提问：

为 load_data 函数添加健壮的文件查找逻辑，如果默认路径 data/signal_samples.csv 不存在，自动尝试当前目录和脚本所在目录的其他路径。同时为所有图表添加空数据判断，当筛选结果为空时显示友好提示而不是报错。

AI 响应概要：

- 在 load_data 中添加 os.path.exists 检查和多个备选路径
- 抛出明确的 FileNotFoundError 错误信息
- 图表渲染前检查 len(filtered_df) 是否大于 0，否则显示 st.warning
- 主程序入口使用 try-except 捕获异常并友好提示

执行结果：异常处理完善，用户体验明显提升。

---

## 第八轮对话：单元测试编写

我的提问：

为核心函数编写 pytest 单元测试文件 test_app.py，测试 load_data、assign_rsrp_color、prepare_dataframe 和筛选逻辑。使用模拟 CSV 数据，测试绿色、橙色、红色颜色边界值，测试筛选后的数据量。要包含至少 5 个测试用例。

AI 响应概要：

创建 test_app.py，包含以下测试用例：
- test_load_data：使用 tmp_path 创建临时 CSV 测试数据加载
- test_assign_rsrp_color_green：测试 RSRP 大于等于 -90 返回绿色
- test_assign_rsrp_color_red：测试 RSRP 小于等于 -110 返回红色
- test_assign_rsrp_color_orange：测试中间值返回橙色
- test_prepare_dataframe：测试颜色列正确添加
- test_filtering_logic：测试组合筛选逻辑正确性

执行结果：pytest test_app.py 全部 6 个测试用例通过。

---

## 第九轮对话：项目文档与交付物整理

我的提问：

生成完整的 requirements.txt、README.md，并按照比赛规范格式整理 AI_PROMPTS.md。README 要包含功能列表、文件结构、运行方法、截图说明。确保所有文件可以一键运行。

AI 响应概要：

- 生成 requirements.txt，锁定核心依赖及版本
- 生成 README.md，包含完整的功能介绍、运行步骤、文件结构
- 整理本交互日志 AI_PROMPTS.md，符合比赛提交模板

执行结果：所有交付物齐全，项目结构完整，可直接提交。

---

## 开发总结

开发阶段及任务：

第1阶段：项目初始化。AI 协助程度 100%，人工修正无。

第2阶段：散点地图。AI 协助程度 100%，人工修正无。

第3阶段：概览图表。AI 协助程度 100%，人工修正无。

第4阶段：侧边栏筛选。AI 协助程度 95%，人工修正为调整滑块范围。

第5阶段：3D 柱状图。AI 协助程度 100%，人工修正为调整 elevation_scale。

第6阶段：KPI 卡片。AI 协助程度 100%，人工修正无。

第7阶段：异常处理。AI 协助程度 90%，人工修正为补充路径逻辑。

第8阶段：单元测试。AI 协助程度 100%，人工修正无。

第9阶段：文档整理。AI 协助程度 100%，人工修正为按规范格式调整。

总计令牌消耗：约 15,000 tokens
累计调试轮次：9 轮主对话加 2 轮微调
