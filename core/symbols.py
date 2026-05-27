"""
给排水标准符号库 (GB/T 50106-2010)
用 ezdxf Block 定义符号，支持轴测图插入
"""
import math
import ezdxf
from ezdxf.enums import TextEntityAlignment
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ezdxf.document import Drawing


def create_all_symbols(doc, scale: float = 1.0):
    """在文档中创建所有标准符号 Block 定义"""
    s = scale

    # === 阀门 ===
    _gate_valve(doc, s)
    _globe_valve(doc, s)
    _check_valve(doc, s)
    _ball_valve(doc, s)
    _butterfly_valve(doc, s)
    _pressure_reducing_valve(doc, s)
    _float_valve(doc, s)

    # === 卫生器具 ===
    _washbasin(doc, s)
    _toilet_sitting(doc, s)
    _toilet_squatting(doc, s)
    _urinal(doc, s)
    _bathtub(doc, s)
    _shower(doc, s)
    _mop_sink(doc, s)
    _faucet(doc, s)

    # === 排水附件 ===
    _floor_drain(doc, s)
    _cleanout(doc, s)
    _vent_cap(doc, s)
    _p_trap(doc, s)
    _s_trap(doc, s)

    # === 设备 ===
    _water_meter(doc, s)
    _water_heater(doc, s)
    _water_tank(doc, s)
    _pump(doc, s)

    # === 消防 ===
    _hydrant_indoor(doc, s)
    _sprinkler_head(doc, s)


# ============================================================
# 阀门符号
# ============================================================

def _gate_valve(doc, s):
    """闸阀：两个三角形 + 手轮"""
    b = doc.blocks.new('闸阀')
    # 左三角形
    b.add_lwpolyline([(-80*s, -50*s), (0, 50*s), (0, -50*s)], close=True)
    # 右三角形
    b.add_lwpolyline([(80*s, -50*s), (0, 50*s), (0, -50*s)], close=True)
    # 阀杆
    b.add_line((0, 50*s), (0, 90*s))
    # 手轮
    b.add_circle((0, 90*s), radius=25*s)
    # 管道连接线
    b.add_line((-80*s, 0), (-120*s, 0))
    b.add_line((80*s, 0), (120*s, 0))


def _globe_valve(doc, s):
    """截止阀：三角形 + 封底 + 手轮"""
    b = doc.blocks.new('截止阀')
    # 三角形（左尖右平）
    b.add_lwpolyline([(-80*s, 0), (0, 50*s), (0, -50*s)], close=True)
    # 封底线
    b.add_line((0, -50*s), (0, 50*s))
    # 阀杆 + 手轮
    b.add_line((0, 50*s), (0, 90*s))
    b.add_circle((0, 90*s), radius=25*s)
    # 管道连接线
    b.add_line((-80*s, 0), (-120*s, 0))
    b.add_line((0, 0), (120*s, 0))


def _check_valve(doc, s):
    """止回阀：三角形 + 摆线"""
    b = doc.blocks.new('止回阀')
    # 三角形指向流动方向
    b.add_lwpolyline([(-80*s, -50*s), (80*s, 0), (-80*s, 50*s)], close=True)
    # 摆线（弧形）
    b.add_arc((20*s, 0), radius=60*s, start_angle=90, end_angle=270)
    # 管道连接线
    b.add_line((-80*s, 0), (-120*s, 0))
    b.add_line((80*s, 0), (120*s, 0))


def _ball_valve(doc, s):
    """球阀：圆 + 横线 + 手柄"""
    b = doc.blocks.new('球阀')
    b.add_circle((0, 0), radius=40*s)
    # 管道通过线
    b.add_line((-40*s, 0), (40*s, 0))
    # 阀杆
    b.add_line((0, 40*s), (0, 70*s))
    # 手柄
    b.add_line((-30*s, 70*s), (30*s, 70*s))
    # 管道连接线
    b.add_line((-40*s, 0), (-120*s, 0))
    b.add_line((40*s, 0), (120*s, 0))


def _butterfly_valve(doc, s):
    """蝶阀：圆 + 直径线"""
    b = doc.blocks.new('蝶阀')
    b.add_circle((0, 0), radius=40*s)
    # 阀板（直径线）
    b.add_line((0, -40*s), (0, 40*s))
    # 管道连接线
    b.add_line((-40*s, 0), (-120*s, 0))
    b.add_line((40*s, 0), (120*s, 0))


def _pressure_reducing_valve(doc, s):
    """减压阀：三角形 + 对角箭头"""
    b = doc.blocks.new('减压阀')
    b.add_lwpolyline([(-80*s, -50*s), (80*s, 0), (-80*s, 50*s)], close=True)
    # 减压箭头
    b.add_line((-30*s, -30*s), (30*s, 30*s))
    b.add_line((30*s, 30*s), (10*s, 30*s))
    b.add_line((30*s, 30*s), (30*s, 10*s))
    # 管道连接线
    b.add_line((-80*s, 0), (-120*s, 0))
    b.add_line((80*s, 0), (120*s, 0))


def _float_valve(doc, s):
    """浮球阀：圆 + 浮球"""
    b = doc.blocks.new('浮球阀')
    b.add_line((-60*s, 0), (0, 0))
    b.add_line((0, 0), (0, -50*s))
    # 浮球
    b.add_circle((40*s, -50*s), radius=30*s)
    b.add_line((0, -50*s), (10*s, -50*s))
    # 管道连接线
    b.add_line((-60*s, 0), (-120*s, 0))


# ============================================================
# 卫生器具符号
# ============================================================

def _washbasin(doc, s):
    """洗脸盆：半圆 + 矩形台面"""
    b = doc.blocks.new('洗脸盆')
    # 台面矩形
    b.add_lwpolyline([(-80*s, 0), (80*s, 0), (80*s, 30*s), (-80*s, 30*s)], close=True)
    # 盆体半圆
    b.add_arc((0, 0), radius=50*s, start_angle=180, end_angle=360)
    # 下水口
    b.add_circle((0, -20*s), radius=10*s)


def _toilet_sitting(doc, s):
    """坐便器：椭圆 + 水箱"""
    b = doc.blocks.new('坐便器')
    # 水箱
    b.add_lwpolyline([(-40*s, 40*s), (40*s, 40*s), (40*s, 80*s), (-40*s, 80*s)], close=True)
    # 坐圈椭圆
    b.add_ellipse((0, 0), major_axis=(60*s, 0), ratio=0.6)
    # 连接线
    b.add_line((-30*s, 40*s), (-30*s, 10*s))
    b.add_line((30*s, 40*s), (30*s, 10*s))


def _toilet_squatting(doc, s):
    """蹲便器：矩形 + 脚踏"""
    b = doc.blocks.new('蹲便器')
    # 外框
    b.add_lwpolyline([(-70*s, -40*s), (70*s, -40*s), (70*s, 40*s), (-70*s, 40*s)],
                     close=True)
    # 内圈（椭圆）
    b.add_ellipse((0, 0), major_axis=(45*s, 0), ratio=0.5)
    # 脚踏指示线
    b.add_line((-50*s, 30*s), (-30*s, 30*s))
    b.add_line((30*s, 30*s), (50*s, 30*s))


def _urinal(doc, s):
    """小便器：锥形/碗形"""
    b = doc.blocks.new('小便器')
    # 外轮廓
    b.add_lwpolyline([(-30*s, -40*s), (-40*s, 30*s), (40*s, 30*s), (30*s, -40*s)])
    # 内轮廓
    b.add_lwpolyline([(-20*s, -30*s), (-25*s, 20*s), (25*s, 20*s), (20*s, -30*s)])
    # 冲水管
    b.add_line((0, 30*s), (0, 60*s))
    b.add_line((-20*s, 60*s), (20*s, 60*s))


def _bathtub(doc, s):
    """浴缸：矩形 + 倾斜端"""
    b = doc.blocks.new('浴缸')
    # 外框
    b.add_lwpolyline([(-120*s, -50*s), (100*s, -50*s), (120*s, 50*s),
                       (-100*s, 50*s)], close=True)
    # 内框
    b.add_lwpolyline([(-100*s, -35*s), (85*s, -35*s), (100*s, 35*s),
                       (-85*s, 35*s)], close=True)
    # 水龙头位置
    b.add_line((-90*s, 0), (-110*s, 0))


def _shower(doc, s):
    """淋浴器：圆 + 喷头"""
    b = doc.blocks.new('淋浴器')
    # 喷头圆
    b.add_circle((0, -40*s), radius=30*s)
    # 管段
    b.add_line((0, 0), (0, -10*s))
    # 喷头连接
    b.add_line((0, -10*s), (0, -40*s))
    # 水滴示意
    for dx in [-15*s, 0, 15*s]:
        b.add_line((dx, -70*s), (dx, -85*s))


def _mop_sink(doc, s):
    """拖布池：矩形盆"""
    b = doc.blocks.new('拖布池')
    b.add_lwpolyline([(-60*s, -40*s), (60*s, -40*s), (60*s, 40*s), (-60*s, 40*s)],
                     close=True)
    b.add_lwpolyline([(-45*s, -28*s), (45*s, -28*s), (45*s, 28*s), (-45*s, 28*s)],
                     close=True)
    # 下水口
    b.add_circle((0, 0), radius=8*s)


def _faucet(doc, s):
    """水龙头：管段 + 弯头"""
    b = doc.blocks.new('水龙头')
    # 水平管段
    b.add_line((-50*s, 0), (0, 0))
    # 垂直段
    b.add_line((0, 0), (0, -50*s))
    # 弯头
    b.add_arc((0, -50*s), radius=20*s, start_angle=0, end_angle=180)
    # 出水
    b.add_line((0, -70*s), (20*s, -70*s))


# ============================================================
# 排水附件符号
# ============================================================

def _floor_drain(doc, s):
    """地漏：同心圆 + 十字网格"""
    b = doc.blocks.new('地漏')
    b.add_circle((0, 0), radius=50*s)
    b.add_circle((0, 0), radius=35*s)
    # 十字
    b.add_line((-35*s, 0), (35*s, 0))
    b.add_line((0, -35*s), (0, 35*s))
    # 下水管
    b.add_line((0, -50*s), (0, -80*s))


def _cleanout(doc, s):
    """清扫口：圆 + 螺栓"""
    b = doc.blocks.new('清扫口')
    b.add_circle((0, 0), radius=35*s)
    # 螺栓十字
    b.add_line((-20*s, -20*s), (20*s, 20*s))
    b.add_line((-20*s, 20*s), (20*s, -20*s))


def _vent_cap(doc, s):
    """通气帽：伞形"""
    b = doc.blocks.new('通气帽')
    # 管段
    b.add_line((0, 0), (0, 40*s))
    # 伞
    b.add_lwpolyline([(-40*s, 40*s), (0, 60*s), (40*s, 40*s)])
    # 伞顶
    b.add_line((-40*s, 40*s), (40*s, 40*s))


def _p_trap(doc, s):
    """P型存水弯"""
    b = doc.blocks.new('P型存水弯')
    # 入口
    b.add_line((0, 60*s), (0, 30*s))
    # 弯曲部分
    b.add_arc((20*s, 30*s), radius=20*s, start_angle=180, end_angle=0)
    # 底部水平
    b.add_line((40*s, 30*s), (40*s, 0))
    # 出口弯头
    b.add_arc((20*s, 0), radius=20*s, start_angle=0, end_angle=180)
    # 出口
    b.add_line((0, 0), (0, -30*s))


def _s_trap(doc, s):
    """S型存水弯"""
    b = doc.blocks.new('S型存水弯')
    # 入口
    b.add_line((0, 80*s), (0, 50*s))
    # 上弯
    b.add_arc((20*s, 50*s), radius=20*s, start_angle=180, end_angle=0)
    # 中间段
    b.add_line((40*s, 50*s), (40*s, 20*s))
    # 下弯
    b.add_arc((20*s, 20*s), radius=20*s, start_angle=0, end_angle=180)
    # 出口
    b.add_line((0, 20*s), (0, -10*s))


# ============================================================
# 设备符号
# ============================================================

def _water_meter(doc, s):
    """水表：矩形 + 刻度盘"""
    b = doc.blocks.new('水表')
    # 外框
    b.add_lwpolyline([(-60*s, -35*s), (60*s, -35*s), (60*s, 35*s), (-60*s, 35*s)],
                     close=True)
    # 刻度盘
    b.add_circle((0, 0), radius=20*s)
    b.add_line((0, 0), (15*s, 10*s))
    # 管道连接线
    b.add_line((-60*s, 0), (-120*s, 0))
    b.add_line((60*s, 0), (120*s, 0))


def _water_heater(doc, s):
    """热水器：矩形 + 波浪线"""
    b = doc.blocks.new('热水器')
    # 外框
    b.add_lwpolyline([(-70*s, -80*s), (70*s, -80*s), (70*s, 80*s), (-70*s, 80*s)],
                     close=True)
    # 波浪线（表示热水）
    pts = []
    for i in range(8):
        x = -50*s + i * 14*s
        y = (10*s if i % 2 == 0 else -10*s)
        pts.append((x, y))
    b.add_lwpolyline(pts)
    # 进出水口
    b.add_line((-70*s, 40*s), (-100*s, 40*s))   # 冷水进
    b.add_line((70*s, -40*s), (100*s, -40*s))    # 热水出


def _water_tank(doc, s):
    """水箱：矩形 + 水位线"""
    b = doc.blocks.new('水箱')
    b.add_lwpolyline([(-80*s, -60*s), (80*s, -60*s), (80*s, 60*s), (-80*s, 60*s)],
                     close=True)
    # 水位线
    b.add_line((-70*s, 20*s), (70*s, 20*s), dxfattribs={'linetype': 'DASHED'})
    # 进水口
    b.add_line((-80*s, 40*s), (-110*s, 40*s))
    # 出水口
    b.add_line((0, -60*s), (0, -90*s))


def _pump(doc, s):
    """水泵：圆 + 叶轮"""
    b = doc.blocks.new('水泵')
    b.add_circle((0, 0), radius=50*s)
    # 叶轮叶片
    for angle in [0, 120, 240]:
        rad = math.radians(angle)
        b.add_line((0, 0), (35*s * math.cos(rad), 35*s * math.sin(rad)))
    # 进出口
    b.add_line((-50*s, 0), (-100*s, 0))
    b.add_line((50*s, 0), (100*s, 0))


# ============================================================
# 消防符号
# ============================================================

def _hydrant_indoor(doc, s):
    """室内消火栓：矩形 + 阀符号"""
    b = doc.blocks.new('室内消火栓')
    b.add_lwpolyline([(-50*s, -40*s), (50*s, -40*s), (50*s, 40*s), (-50*s, 40*s)],
                     close=True)
    # 阀门简化符号
    b.add_line((-20*s, -15*s), (0, 15*s))
    b.add_line((0, 15*s), (20*s, -15*s))
    # 管道连接
    b.add_line((-50*s, 0), (-80*s, 0))


def _sprinkler_head(doc, s):
    """喷头：向下圆 + 偏转盘"""
    b = doc.blocks.new('喷头')
    # 管段
    b.add_line((0, 40*s), (0, 0))
    # 偏转盘
    b.add_circle((0, 0), radius=25*s)
    # 喷水示意
    b.add_line((-15*s, -10*s), (-25*s, -30*s))
    b.add_line((15*s, -10*s), (25*s, -30*s))


# ============================================================
# 符号插入辅助函数
# ============================================================

def insert_symbol(msp, symbol_name: str, position: tuple,
                  rotation: float = 0, scale: float = 1.0,
                  layer: str = None):
    """插入符号到模型空间

    Args:
        msp: modelspace
        symbol_name: 符号 Block 名称
        position: 插入点 (x, y)
        rotation: 旋转角度（度）
        scale: 缩放比例
        layer: 图层名
    """
    attribs = {
        'xscale': scale,
        'yscale': scale,
    }
    if layer:
        attribs['layer'] = layer
    if rotation:
        attribs['rotation'] = rotation

    msp.add_blockref(symbol_name, position, dxfattribs=attribs)


# 符号名称映射（中英文对照）
SYMBOL_MAP = {
    # 阀门
    '闸阀': '闸阀', 'gate_valve': '闸阀',
    '截止阀': '截止阀', 'globe_valve': '截止阀',
    '止回阀': '止回阀', 'check_valve': '止回阀',
    '球阀': '球阀', 'ball_valve': '球阀',
    '蝶阀': '蝶阀', 'butterfly_valve': '蝶阀',
    '减压阀': '减压阀', 'pressure_reducing_valve': '减压阀',
    '浮球阀': '浮球阀', 'float_valve': '浮球阀',
    # 器具
    '洗脸盆': '洗脸盆', 'washbasin': '洗脸盆',
    '坐便器': '坐便器', 'toilet': '坐便器',
    '蹲便器': '蹲便器', 'squatting_toilet': '蹲便器',
    '小便器': '小便器', 'urinal': '小便器',
    '浴缸': '浴缸', 'bathtub': '浴缸',
    '淋浴器': '淋浴器', 'shower': '淋浴器',
    '拖布池': '拖布池', 'mop_sink': '拖布池',
    '水龙头': '水龙头', 'faucet': '水龙头',
    # 排水附件
    '地漏': '地漏', 'floor_drain': '地漏',
    '清扫口': '清扫口', 'cleanout': '清扫口',
    '通气帽': '通气帽', 'vent_cap': '通气帽',
    'P型存水弯': 'P型存水弯', 'p_trap': 'P型存水弯',
    'S型存水弯': 'S型存水弯', 's_trap': 'S型存水弯',
    # 设备
    '水表': '水表', 'water_meter': '水表',
    '热水器': '热水器', 'water_heater': '热水器',
    '水箱': '水箱', 'water_tank': '水箱',
    '水泵': '水泵', 'pump': '水泵',
    # 消防
    '室内消火栓': '室内消火栓', 'hydrant': '室内消火栓',
    '喷头': '喷头', 'sprinkler': '喷头',
}


def get_symbol_name(key: str) -> str:
    """获取标准符号名称（支持中英文）"""
    return SYMBOL_MAP.get(key, key)
