"""
轴测坐标变换引擎
45度正面斜轴测投影，符合 GB/T 50106-2010 系统图绘制规则

坐标系：
  X轴 = 左右（水平线，0°）
  Y轴 = 上下（垂直线，90°，立管方向）
  Z轴 = 前后（45度对角线，表示进深方向）
"""
import math

# 45度斜轴测系数
_COS45 = math.cos(math.radians(45))  # ≈ 0.7071
_SIN45 = math.sin(math.radians(45))  # ≈ 0.7071


def iso(x: float, y: float, z: float = 0) -> tuple:
    """将轴测坐标 (x, y, z) 转换为 2D 画布坐标 (wx, wy)

    Args:
        x: 左右方向距离 (mm)
        y: 垂直方向距离 (mm)，向上为正
        z: 进深方向距离 (mm)，45度对角线

    Returns:
        (wx, wy) 2D 画布坐标元组
    """
    wx = x + z * _COS45
    wy = y + z * _SIN45
    return (wx, wy)


def iso_line_points(x1, y1, z1, x2, y2, z2):
    """返回轴测坐标系中一条线段的两个端点 2D 坐标"""
    return iso(x1, y1, z1), iso(x2, y2, z2)


def iso_offset(origin, dx=0, dy=0, dz=0):
    """从轴测坐标原点偏移，返回 2D 坐标"""
    ox, oy = origin
    wx = ox + dx + dz * _COS45
    wy = oy + dy + dz * _SIN45
    return (wx, wy)


# 八方向轴测角度（用于符号旋转）
def iso_angle(axis: str) -> float:
    """获取轴测图中的绘制角度

    Args:
        axis: 'x'(水平), 'y'(垂直/立管), 'z'(45度进深),
              '-x'(反向水平), '-y'(向下), '-z'(反向进深)
    Returns:
        角度（度）
    """
    angles = {
        'x': 0, '-x': 180,
        'y': 90, '-y': 270,
        'z': 45, '-z': 225,
    }
    return angles.get(axis, 0)
