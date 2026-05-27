"""
标注模块
管径、标高、楼层线、坡度、立管编号标注
"""
import ezdxf
from ezdxf.enums import TextEntityAlignment
from core.iso_engine import iso, iso_offset


def label_diameter(msp, position_xyz, text, offset_dir='top', scale=1.0,
                   layer='标注'):
    """管径标注

    Args:
        msp: modelspace
        position_xyz: 标注点轴测坐标 (x, y, z)
        text: 标注文字 (e.g. "DN25 PPR")
        offset_dir: 'top'=管上方, 'left'=管左侧, 'bottom'=管下方
        scale: 缩放
        layer: 图层
    """
    p = iso(*position_xyz)
    h = 180 * scale

    offsets = {
        'top': (0, 300 * scale, TextEntityAlignment.BOTTOM_CENTER),
        'bottom': (0, -200 * scale, TextEntityAlignment.TOP_CENTER),
        'left': (-300 * scale, 0, TextEntityAlignment.MIDDLE_RIGHT),
        'right': (300 * scale, 0, TextEntityAlignment.MIDDLE_LEFT),
    }
    dx, dy, align = offsets.get(offset_dir, offsets['top'])

    msp.add_text(
        text, height=h,
        dxfattribs={'layer': layer, 'style': 'OpenSans'}
    ).set_placement((p[0] + dx, p[1] + dy), align=align)


def label_elevation(msp, position_xyz, elev_text, side='left', scale=1.0,
                    layer='标注'):
    """标高标注

    Args:
        msp: modelspace
        position_xyz: 标注点轴测坐标
        elev_text: 标高值 (e.g. "+3.000", "-1.500", "±0.000")
        side: 'left' 或 'right'
        scale: 缩放
        layer: 图层
    """
    p = iso(*position_xyz)
    s = scale
    h = 150 * s

    # 标高符号：倒三角形
    tri_size = 80 * s
    if side == 'left':
        tri = [(p[0] - tri_size, p[1] + tri_size / 2),
               (p[0] - tri_size, p[1] - tri_size / 2),
               (p[0], p[1])]
        text_x = p[0] - tri_size - 50 * s
        align = TextEntityAlignment.MIDDLE_RIGHT
    else:
        tri = [(p[0] + tri_size, p[1] + tri_size / 2),
               (p[0] + tri_size, p[1] - tri_size / 2),
               (p[0], p[1])]
        text_x = p[0] + tri_size + 50 * s
        align = TextEntityAlignment.MIDDLE_LEFT

    attribs = {'layer': layer, 'color': 7}
    msp.add_lwpolyline(tri + [tri[0]], dxfattribs=attribs)

    # 引出线
    if side == 'left':
        msp.add_line(tri[0], (tri[0][0] - 200 * s, tri[0][1]), dxfattribs=attribs)
        msp.add_text(elev_text, height=h,
                     dxfattribs={'layer': layer}).set_placement(
            (text_x - 100 * s, p[1]), align=align)
    else:
        msp.add_line(tri[1], (tri[1][0] + 200 * s, tri[1][1]), dxfattribs=attribs)
        msp.add_text(elev_text, height=h,
                     dxfattribs={'layer': layer}).set_placement(
            (text_x + 100 * s, p[1]), align=align)


def draw_floor_line(msp, y_position, x_start, x_end, z_start=0, z_end=0,
                    floor_name='', elevation='', scale=1.0, layer='楼层线'):
    """绘制楼层地面线

    Args:
        msp: modelspace
        y_position: 楼层高度 (y 轴值, mm)
        x_start, x_end: X 方向范围
        z_start, z_end: Z 方向范围
        floor_name: 楼层名称 (e.g. "一层 1F")
        elevation: 标高值 (e.g. "+3.000")
        scale: 缩放
        layer: 图层
    """
    p1 = iso(x_start, y_position, z_start)
    p2 = iso(x_end, y_position, z_end)
    s = scale

    attribs = {'layer': layer, 'color': 8, 'linetype': 'CONTINUOUS'}
    msp.add_line(p1, p2, dxfattribs=attribs)

    # 楼层标注（左侧）
    if floor_name:
        text = f"{floor_name}"
        if elevation:
            text += f"  {elevation}"
        label_x = p1[0] - 200 * s
        msp.add_text(
            text, height=150 * s,
            dxfattribs={'layer': layer, 'color': 8}
        ).set_placement(
            (label_x, p1[1] + 100 * s),
            align=TextEntityAlignment.MIDDLE_RIGHT
        )


def label_slope(msp, position_xyz, slope_text, scale=1.0, layer='标注'):
    """坡度标注（排水管）

    Args:
        msp: modelspace
        position_xyz: 标注点轴测坐标
        slope_text: 坡度值 (e.g. "i=0.020")
        scale: 缩放
        layer: 图层
    """
    p = iso(*position_xyz)
    h = 150 * scale
    msp.add_text(
        slope_text, height=h,
        dxfattribs={'layer': layer}
    ).set_placement(
        (p[0] + 200 * scale, p[1] - 200 * scale),
        align=TextEntityAlignment.TOP_LEFT
    )


def label_riser_id(msp, position_xyz, riser_id, scale=1.0, layer='标注'):
    """立管编号标注

    Args:
        msp: modelspace
        position_xyz: 立管顶部轴测坐标
        riser_id: 立管编号 (e.g. "JL-1", "WL-1")
        scale: 缩放
        layer: 图层
    """
    p = iso(*position_xyz)
    s = scale
    r = 200 * s
    h = 140 * s

    # 圆圈
    msp.add_circle((p[0], p[1] + r + 50 * s), radius=r,
                   dxfattribs={'layer': layer, 'color': 7})

    # 编号文字
    msp.add_text(
        riser_id, height=h,
        dxfattribs={'layer': layer}
    ).set_placement(
        (p[0], p[1] + r + 50 * s),
        align=TextEntityAlignment.MIDDLE_CENTER
    )


def label_pipe_code(msp, position_xyz, code, scale=1.0, layer='标注'):
    """管道代号标注（管道线旁边的字母代码，如 J、W、XH）

    Args:
        msp: modelspace
        position_xyz: 标注点轴测坐标
        code: 管道代号 (e.g. "J", "W", "XH", "R")
        scale: 缩放
        layer: 图层
    """
    p = iso(*position_xyz)
    h = 250 * scale
    msp.add_text(
        code, height=h,
        dxfattribs={'layer': layer}
    ).set_placement(
        (p[0] - 300 * scale, p[1]),
        align=TextEntityAlignment.MIDDLE_RIGHT
    )
