"""
系统图组装器
从配置参数生成完整的给排水系统轴测图
"""
import yaml
from core.drawing import create_drawing, save_drawing, setup_title_block
from core.iso_engine import iso
from core.symbols import create_all_symbols, insert_symbol, get_symbol_name
from core.pipe_renderer import (
    draw_riser, draw_horizontal_branch, draw_pipe,
    draw_tee_marker, draw_reducer
)
from core.annotation import (
    label_diameter, label_elevation, draw_floor_line,
    label_slope, label_riser_id, label_pipe_code
)


class SystemBuilder:
    """给排水系统图构建器"""

    def __init__(self, config: dict, scale: float = 1.0):
        self.config = config
        self.scale = scale
        self.doc = None
        self.msp = None

    def build(self, output_path: str):
        """构建完整的系统图 DXF 文件"""
        building = self.config.get('building', {})
        systems = self.config.get('systems', [])

        # 创建文档
        title = systems[0].get('title', '给排水系统轴测图') if systems else '给排水系统轴测图'
        self.doc = create_drawing(title)
        self.msp = self.doc.modelspace()

        # 创建符号
        create_all_symbols(self.doc, self.scale)

        # 绘制楼层线
        self._draw_floor_lines(building)

        # 绘制每个系统
        for system_cfg in systems:
            sys_type = system_cfg.get('type', '给水')
            if sys_type == '给水':
                self._build_water_supply(system_cfg, building)
            elif sys_type == '排水':
                self._build_drainage(system_cfg, building)
            elif sys_type == '消防':
                self._build_fire_protection(system_cfg, building)

        # 图名
        total_floors = building.get('floors', 6)
        floor_h = building.get('floor_height', 3000)
        total_height = total_floors * floor_h
        setup_title_block(self.msp, title,
                          position=(5000, -1500), scale=self.scale)

        # 设置视图
        self.doc.set_modelspace_vport(
            height=total_height * 2.5,
            center=(5000, total_height * 0.5)
        )

        # 保存
        save_drawing(self.doc, output_path)

    def _draw_floor_lines(self, building: dict):
        """绘制楼层地面线"""
        floors = building.get('floors', 6)
        floor_h = building.get('floor_height', 3000)
        basement = building.get('basement', 0)

        x_start = -1000
        x_end = 15000
        z_start = 0
        z_end = 8000

        for i in range(-basement, floors + 1):
            y = i * floor_h
            if i < 0:
                name = f"B{abs(i)}F"
                elev = f"-{abs(i) * floor_h / 1000:.3f}"
            elif i == 0:
                name = "1F"
                elev = "±0.000"
            elif i <= floors:
                name = f"{i + 1}F"
                elev = f"+{i * floor_h / 1000:.3f}"
            else:
                # 屋面层：只画线，不标注楼层名
                name = ""
                elev = f"+{i * floor_h / 1000:.3f}"

            draw_floor_line(
                self.msp, y, x_start, x_end, z_start, z_end,
                floor_name=name, elevation=elev, scale=self.scale
            )

    def _build_water_supply(self, cfg: dict, building: dict):
        """构建给水系统"""
        code = cfg.get('code', 'J')
        layer = '给水-J'
        risers = cfg.get('risers', [])
        floor_h = building.get('floor_height', 3000)
        floors = building.get('floors', 6)
        basement = building.get('basement', 0)

        for riser in risers:
            rid = riser.get('id', f'JL-1')
            rx, rz = riser.get('position', [0, 0])
            main_dia = riser.get('diameter', 'DN50')
            branches = riser.get('branches', [])
            valves = riser.get('valves', [])

            total_h = (floors + basement) * floor_h

            # 绘制立管
            draw_riser(self.msp, (rx, -basement * floor_h, rz),
                       total_h, layer=layer)

            # 立管编号
            label_riser_id(self.msp, (rx, total_h, rz), rid,
                           scale=self.scale)

            # 立管管径标注
            label_diameter(self.msp, (rx, total_h * 0.3, rz),
                           main_dia, offset_dir='left', scale=self.scale)

            # 管道代号
            label_pipe_code(self.msp, (rx, 0, rz), code, scale=self.scale)

            # 绘制每层支管
            for branch in branches:
                floor = branch.get('floor', 1)
                branch_dia = branch.get('diameter', 'DN25')
                branch_len = branch.get('length', 3000)
                direction = branch.get('direction', 'x')
                fixtures = branch.get('fixtures', [])
                branch_valves = branch.get('valves', [])

                # 支管起点高度
                by = (floor - 1) * floor_h + floor_h * 0.7  # 支管在楼板上方0.7层高

                # 绘制支管
                draw_horizontal_branch(
                    self.msp, (rx, by, rz), branch_len,
                    direction=direction, layer=layer
                )

                # 三通标记
                draw_tee_marker(self.msp, (rx, by, rz), scale=self.scale)

                # 支管管径标注
                mid_x = rx + branch_len * 0.5 if direction == 'x' else rx
                mid_z = rz + branch_len * 0.5 if direction == 'z' else rz
                label_diameter(
                    self.msp, (mid_x, by, mid_z),
                    branch_dia, offset_dir='top', scale=self.scale
                )

                # 如果管径与主管不同，标注异径管
                if branch_dia != main_dia:
                    draw_reducer(self.msp, (rx, by, rz),
                                 scale=self.scale)

                # 绘制器具
                for fix in fixtures:
                    fix_type = fix.get('type', '水龙头')
                    fix_x = fix.get('position', [branch_len, 0])[0]
                    fix_z = fix.get('position', [0, branch_len])[1] if len(fix.get('position', [0])) > 1 else 0

                    symbol_name = get_symbol_name(fix_type)
                    pos = iso(rx + fix_x, by, rz + fix_z)

                    # 器具在支管末端时，可能需要竖向短管
                    drop = fix.get('drop', 0)
                    if drop:
                        draw_pipe(self.msp,
                                  (rx + fix_x, by, rz + fix_z),
                                  (rx + fix_x, by - drop, rz + fix_z),
                                  layer=layer)
                        pos = iso(rx + fix_x, by - drop, rz + fix_z)

                    insert_symbol(self.msp, symbol_name, pos,
                                  scale=self.scale * 0.8, layer='卫生器具')

            # 绘制主管道阀门
            for valve in valves:
                v_type = valve.get('type', '闸阀')
                v_pos_str = valve.get('position', '')
                v_floor = valve.get('floor', 1)

                # 阀门位置
                vy = (v_floor - 1) * floor_h + floor_h * 0.5
                if '入口' in v_pos_str:
                    vy = -basement * floor_h + 500
                elif '顶层' in v_pos_str:
                    vy = floors * floor_h - 500

                symbol_name = get_symbol_name(v_type)
                v_pos = iso(rx, vy, rz)

                insert_symbol(self.msp, symbol_name, v_pos,
                              rotation=0, scale=self.scale * 0.8,
                              layer='阀门')

    def _build_drainage(self, cfg: dict, building: dict):
        """构建排水系统"""
        code = cfg.get('code', 'W')
        layer = '排水-W'
        risers = cfg.get('risers', [])
        floor_h = building.get('floor_height', 3000)
        floors = building.get('floors', 6)
        basement = building.get('basement', 0)

        for riser in risers:
            rid = riser.get('id', f'WL-1')
            rx, rz = riser.get('position', [5000, 0])
            main_dia = riser.get('diameter', 'DN100')
            branches = riser.get('branches', [])

            total_h = (floors + basement) * floor_h

            # 立管（从最高层到排出管）
            draw_riser(self.msp, (rx, -basement * floor_h, rz),
                       total_h, layer=layer)

            # 立管编号
            label_riser_id(self.msp, (rx, total_h, rz), rid,
                           scale=self.scale)

            # 立管管径
            label_diameter(self.msp, (rx, total_h * 0.3, rz),
                           main_dia, offset_dir='left', scale=self.scale)

            # 管道代号
            label_pipe_code(self.msp, (rx, 0, rz), code, scale=self.scale)

            # 排出管
            out_len = riser.get('outlet_length', 3000)
            out_y = -basement * floor_h
            draw_horizontal_branch(
                self.msp, (rx, out_y, rz), out_len,
                direction='z', layer=layer
            )
            label_diameter(self.msp, (rx, out_y, rz + out_len * 0.5),
                           main_dia, offset_dir='bottom', scale=self.scale)
            label_slope(self.msp, (rx, out_y, rz + out_len * 0.3),
                        'i=0.020', scale=self.scale)

            # 通气帽（立管顶部）
            insert_symbol(self.msp, get_symbol_name('通气帽'),
                          iso(rx, total_h, rz),
                          scale=self.scale * 0.8, layer='卫生器具')

            # 每层支管
            for branch in branches:
                floor = branch.get('floor', 1)
                branch_dia = branch.get('diameter', 'DN75')
                branch_len = branch.get('length', 3000)
                direction = branch.get('direction', 'x')
                slope = branch.get('slope', 'i=0.020')
                fixtures = branch.get('fixtures', [])

                by = (floor - 1) * floor_h + floor_h * 0.3

                draw_horizontal_branch(
                    self.msp, (rx, by, rz), branch_len,
                    direction=direction, layer=layer
                )

                draw_tee_marker(self.msp, (rx, by, rz), scale=self.scale)
                label_slope(self.msp, (rx + 500, by, rz),
                            slope, scale=self.scale)
                label_diameter(
                    self.msp, (rx + branch_len * 0.5, by, rz),
                    branch_dia, offset_dir='top', scale=self.scale
                )

                for fix in fixtures:
                    fix_type = fix.get('type', '地漏')
                    fix_x = fix.get('position', [branch_len, 0])[0]
                    fix_z = fix.get('position', [0, 0])[1] if len(fix.get('position', [0])) > 1 else 0
                    drop = fix.get('drop', 500)

                    # 排水器具需要竖管连接
                    draw_pipe(self.msp,
                              (rx + fix_x, by, rz + fix_z),
                              (rx + fix_x, by - drop, rz + fix_z),
                              layer=layer)

                    # 存水弯
                    insert_symbol(self.msp, get_symbol_name('P型存水弯'),
                                  iso(rx + fix_x, by - drop, rz + fix_z),
                                  scale=self.scale * 0.7, layer='卫生器具')

                    # 器具
                    symbol_name = get_symbol_name(fix_type)
                    insert_symbol(self.msp, symbol_name,
                                  iso(rx + fix_x, by - drop - 300, rz + fix_z),
                                  scale=self.scale * 0.8, layer='卫生器具')

    def _build_fire_protection(self, cfg: dict, building: dict):
        """构建消防系统"""
        code = cfg.get('code', 'XH')
        layer = '消防-XH'
        risers = cfg.get('risers', [])
        floor_h = building.get('floor_height', 3000)
        floors = building.get('floors', 6)
        basement = building.get('basement', 0)

        for riser in risers:
            rid = riser.get('id', f'XL-1')
            rx, rz = riser.get('position', [10000, 0])
            main_dia = riser.get('diameter', 'DN100')
            branches = riser.get('branches', [])

            total_h = (floors + basement) * floor_h

            draw_riser(self.msp, (rx, -basement * floor_h, rz),
                       total_h, layer=layer)

            label_riser_id(self.msp, (rx, total_h, rz), rid,
                           scale=self.scale)
            label_diameter(self.msp, (rx, total_h * 0.3, rz),
                           main_dia, offset_dir='left', scale=self.scale)
            label_pipe_code(self.msp, (rx, 0, rz), code, scale=self.scale)

            for branch in branches:
                floor = branch.get('floor', 1)
                branch_dia = branch.get('diameter', 'DN65')
                branch_len = branch.get('length', 4000)
                direction = branch.get('direction', 'x')

                by = (floor - 1) * floor_h + floor_h * 0.5

                draw_horizontal_branch(
                    self.msp, (rx, by, rz), branch_len,
                    direction=direction, layer=layer
                )

                draw_tee_marker(self.msp, (rx, by, rz), scale=self.scale)
                label_diameter(
                    self.msp, (rx + branch_len * 0.5, by, rz),
                    branch_dia, offset_dir='top', scale=self.scale
                )

                # 消火栓
                hydrants = branch.get('hydrants', [])
                for hyd in hydrants:
                    hx = hyd.get('position', [branch_len * 0.5, 0])[0]
                    insert_symbol(self.msp, get_symbol_name('室内消火栓'),
                                  iso(rx + hx, by - 500, rz),
                                  scale=self.scale * 0.8, layer='设备')


def build_from_yaml(config_path: str, output_path: str, scale: float = 1.0):
    """从 YAML 配置文件生成系统图"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    builder = SystemBuilder(config, scale=scale)
    builder.build(output_path)
