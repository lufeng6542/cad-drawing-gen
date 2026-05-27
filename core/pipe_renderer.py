"""
管道绘制模块
绘制管道线段、管件（三通、弯头、异径管）
"""
from core.iso_engine import iso, iso_offset


def draw_pipe(msp, start_xyz, end_xyz, layer='给水-J', color=None):
    """绘制一段管道

    Args:
        msp: modelspace
        start_xyz: 轴测坐标起点 (x, y, z)
        end_xyz: 轴测坐标终点 (x, y, z)
        layer: 图层名（决定线型和颜色）
        color: 强制颜色（覆盖图层颜色）
    """
    p1 = iso(*start_xyz)
    p2 = iso(*end_xyz)
    attribs = {'layer': layer}
    if color is not None:
        attribs['color'] = color
    msp.add_line(p1, p2, dxfattribs=attribs)


def draw_pipe_path(msp, points, layer='给水-J', color=None):
    """沿轴测坐标路径绘制连续管道

    Args:
        msp: modelspace
        points: 轴测坐标点列表 [(x1,y1,z1), (x2,y2,z2), ...]
        layer: 图层名
        color: 强制颜色
    """
    attribs = {'layer': layer}
    if color is not None:
        attribs['color'] = color
    for i in range(len(points) - 1):
        p1 = iso(*points[i])
        p2 = iso(*points[i + 1])
        msp.add_line(p1, p2, dxfattribs=attribs)


def draw_riser(msp, base_xyz, height, layer='给水-J', color=None):
    """绘制立管（垂直管道）

    Args:
        msp: modelspace
        base_xyz: 立管底部轴测坐标 (x, y, z)
        height: 立管高度 (mm)
        layer: 图层名
    """
    x, y, z = base_xyz
    draw_pipe(msp, (x, y, z), (x, y + height, z), layer, color)


def draw_horizontal_branch(msp, start_xyz, length, direction='x',
                           layer='给水-J', color=None):
    """绘制水平支管

    Args:
        msp: modelspace
        start_xyz: 起点 (x, y, z)
        length: 长度 (mm)
        direction: 'x' = 左右水平, 'z' = 45度进深
        layer: 图层名
    """
    x, y, z = start_xyz
    if direction == 'x':
        end = (x + length, y, z)
    else:
        end = (x, y, z + length)
    draw_pipe(msp, start_xyz, end, layer, color)


def draw_reducer(msp, position_xyz, scale=1.0):
    """绘制异径管标记

    在管径变化处绘制一个渐变符号
    """
    p = iso(*position_xyz)
    s = 30 * scale

    attribs = {'layer': '标注', 'color': 7}
    # 左侧短线（大径）
    msp.add_line((p[0] - s, p[1] - s), (p[0] - s, p[1] + s), dxfattribs=attribs)
    # 右侧短线（小径）
    msp.add_line((p[0] + s, p[1] - s * 0.6), (p[0] + s, p[1] + s * 0.6),
                 dxfattribs=attribs)
    # 渐变连接线
    msp.add_line((p[0] - s, p[1] + s), (p[0] + s, p[1] + s * 0.6),
                 dxfattribs=attribs)
    msp.add_line((p[0] - s, p[1] - s), (p[0] + s, p[1] - s * 0.6),
                 dxfattribs=attribs)


def draw_tee_marker(msp, position_xyz, scale=1.0):
    """绘制三通标记（小圆点标记分支点）"""
    p = iso(*position_xyz)
    msp.add_circle(p, radius=15 * scale, dxfattribs={'layer': '标注', 'color': 7})


def draw_elbow_marker(msp, position_xyz, scale=1.0):
    """绘制弯头标记（小弧线）"""
    p = iso(*position_xyz)
    s = 20 * scale
    msp.add_arc(p, radius=s, start_angle=0, end_angle=90,
                dxfattribs={'layer': '标注', 'color': 7})


def draw_cross_break(msp, position_xyz, direction='y', gap=200, scale=1.0):
    """绘制管道交叉处的断开线（后方管道断开）

    Args:
        msp: modelspace
        position_xyz: 交叉点轴测坐标
        direction: 被断开管道的方向 ('x', 'y', 'z')
        gap: 断开间距
    """
    p = iso(*position_xyz)
    s = gap * scale / 2
    attribs = {'layer': '标注', 'color': 7}

    if direction == 'y':
        msp.add_line((p[0], p[1] - s), (p[0] - 5, p[1] - s + 10),
                     dxfattribs=attribs)
        msp.add_line((p[0], p[1] + s), (p[0] + 5, p[1] + s - 10),
                     dxfattribs=attribs)
    elif direction == 'x':
        msp.add_line((p[0] - s, p[1]), (p[0] - s + 10, p[1] + 5),
                     dxfattribs=attribs)
        msp.add_line((p[0] + s, p[1]), (p[0] + s - 10, p[1] - 5),
                     dxfattribs=attribs)
