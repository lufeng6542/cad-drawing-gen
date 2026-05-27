"""
DXF 文档管理
创建、配置、保存 DXF 图纸
"""
import ezdxf
from ezdxf.enums import TextEntityAlignment
from ezdxf import units


# GB/T 50106-2010 标准图层定义
STANDARD_LAYERS = {
    # 管道图层
    '给水-J':     {'color': 5,   'linetype': 'CONTINUOUS'},   # 蓝色实线
    '热水-R':     {'color': 1,   'linetype': 'DASHDOT'},      # 红色点画线
    '排水-W':     {'color': 3,   'linetype': 'DASHED'},       # 绿色虚线
    '雨水-Y':     {'color': 4,   'linetype': 'DASHED'},       # 青色虚线
    '消防-XH':    {'color': 1,   'linetype': 'CONTINUOUS'},   # 红色实线
    '通气-T':     {'color': 4,   'linetype': 'CONTINUOUS'},   # 青色实线
    # 辅助图层
    '阀门':       {'color': 7,   'linetype': 'CONTINUOUS'},
    '卫生器具':   {'color': 7,   'linetype': 'CONTINUOUS'},
    '设备':       {'color': 7,   'linetype': 'CONTINUOUS'},
    '标注':       {'color': 7,   'linetype': 'CONTINUOUS'},
    '楼层线':     {'color': 8,   'linetype': 'CONTINUOUS'},   # 灰色细线
    '图框':       {'color': 7,   'linetype': 'CONTINUOUS'},
}


def create_drawing(title: str = "给排水系统轴测图", unit: str = "mm"):
    """创建标准 DXF 文档

    Args:
        title: 图纸标题
        unit: 单位 (mm/m/cm)

    Returns:
        配置好的 ezdxf Document 对象
    """
    doc = ezdxf.new("R2010", setup=True)

    # 设置单位
    unit_map = {'mm': units.MM, 'm': units.M, 'cm': units.CM}
    doc.units = unit_map.get(unit, units.MM)
    doc.header["$MEASUREMENT"] = 1  # 公制

    # 创建标准图层
    for name, props in STANDARD_LAYERS.items():
        layer = doc.layers.add(name, color=props['color'],
                               linetype=props.get('linetype', 'CONTINUOUS'))

    # 设置全局线型比例
    doc.header["$LTSCALE"] = 10

    return doc


def save_drawing(doc, filepath: str):
    """保存 DXF 文件"""
    doc.saveas(filepath)
    print(f"图纸已保存: {filepath}")


def setup_title_block(msp, title: str, position=None, scale=1.0):
    """绘制图名

    Args:
        msp: modelspace
        title: 图名文字
        position: 图名位置 (x, y)，默认在图纸底部居中
        scale: 文字缩放
    """
    if position is None:
        position = (5000, -2000)

    x, y = position
    h = 500 * scale

    # 图名下方横线
    msp.add_line(
        (x - len(title) * h * 0.4, y - h * 0.6),
        (x + len(title) * h * 0.4, y - h * 0.6),
        dxfattribs={'layer': '图框'}
    )

    msp.add_text(
        title,
        height=h,
        dxfattribs={'layer': '图框', 'style': 'OpenSans'}
    ).set_placement((x, y), align=TextEntityAlignment.MIDDLE_CENTER)
