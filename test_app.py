"""
单元测试：验证数据加载、颜色映射、筛选逻辑等核心函数。
运行方式：pytest test_app.py
"""
import pandas as pd
import numpy as np
import sys
from io import StringIO
import pytest

# 导入待测模块（调整路径确保能找到 app）
# 假设 app.py 在同一目录下
from app import load_data, assign_rsrp_color, prepare_dataframe

# 模拟 CSV 数据
MOCK_CSV = """Latitude,Longitude,CellID,Band,RSRP_dBm,SINR_dB,TerminalType,Download_Mbps
31.209,121.482,1926,n28,-94.94,5.44,Smartphone,138.21
31.214,121.484,1457,n78,-105.47,20.67,CPE,837.84
31.249,121.453,1941,n28,-82.27,18.28,Smartphone,36.23
31.201,121.468,1200,n28,-119.18,27.56,IoT,482.91
"""

def test_load_data(tmp_path):
    """测试 load_data 能否正确读取 CSV 并清洗数据。"""
    # 创建临时 CSV
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(MOCK_CSV)
    df = load_data(str(csv_file))
    assert len(df) == 4
    assert "RSRP_dBm" in df.columns
    assert df["RSRP_dBm"].dtype == float

def test_assign_rsrp_color_green():
    """RSRP >= -90 应返回绿色"""
    assert assign_rsrp_color(-85) == [0, 255, 0]
    assert assign_rsrp_color(-90) == [0, 255, 0]

def test_assign_rsrp_color_red():
    """RSRP <= -110 应返回红色"""
    assert assign_rsrp_color(-112) == [255, 0, 0]
    assert assign_rsrp_color(-110) == [255, 0, 0]

def test_assign_rsrp_color_orange():
    """RSRP 在 -110 到 -90 之间返回橙色"""
    assert assign_rsrp_color(-100) == [255, 165, 0]

def test_prepare_dataframe():
    """测试颜色列是否正确添加。"""
    df = pd.read_csv(StringIO(MOCK_CSV))
    df = prepare_dataframe(df)
    assert "color" in df.columns
    # 第一条记录 RSRP=-94.94 应在橙色区间
    assert df.loc[0, "color"] == [255, 165, 0]
    # 第三条 RSRP=-82.27 应为绿色
    assert df.loc[2, "color"] == [0, 255, 0]

def test_filtering_logic():
    """模拟筛选逻辑，确保 mask 计算正确。"""
    df = pd.read_csv(StringIO(MOCK_CSV))
    bands = ["n78"]
    rsrp_min, rsrp_max = -120, -70
    terminals = ["CPE"]
    mask_band = df["Band"].isin(bands)
    mask_rsrp = (df["RSRP_dBm"] >= rsrp_min) & (df["RSRP_dBm"] <= rsrp_max)
    mask_terminal = df["TerminalType"].isin(terminals)
    filtered = df[mask_band & mask_rsrp & mask_terminal]
    # 只有第二条记录符合 n78、CPE，且 RSRP=-105.47 在范围内
    assert len(filtered) == 1
    assert filtered.iloc[0]["CellID"] == 1457