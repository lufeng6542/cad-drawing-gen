"""
CAD 给排水系统图生成器 CLI
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core.system_builder import build_from_yaml, SystemBuilder


def cmd_generate(args):
    """从配置文件生成系统图"""
    build_from_yaml(args.config, args.output, scale=args.scale)
    print(f"完成！可用 AutoCAD 打开: {args.output}")


def cmd_quick(args):
    """快速模式：输入基本参数直接生成"""
    config = {
        'building': {
            'floors': args.floors,
            'floor_height': 3000,
            'basement': args.basement,
        },
        'systems': []
    }

    if args.system in ('给水', 'all'):
        risers = []
        for i in range(args.risers):
            spacing = 5000
            risers.append({
                'id': f'JL-{i + 1}',
                'position': [i * spacing, 0],
                'diameter': 'DN50',
                'branches': [
                    {
                        'floor': f,
                        'diameter': 'DN25',
                        'length': 4000,
                        'direction': 'x',
                        'fixtures': [
                            {'type': '水龙头', 'position': [4000, 0], 'drop': 500},
                            {'type': '洗脸盆', 'position': [2500, 0], 'drop': 600},
                        ]
                    }
                    for f in range(1, args.floors + 1)
                ],
                'valves': [
                    {'type': '闸阀', 'position': '入口', 'floor': 0},
                    {'type': '止回阀', 'position': '入口', 'floor': 0},
                ]
            })
        config['systems'].append({
            'type': '给水',
            'title': f'给水系统轴测图 ({args.floors}层)',
            'code': 'J',
            'risers': risers,
        })

    if args.system in ('排水', 'all'):
        d_risers = []
        for i in range(args.risers):
            d_risers.append({
                'id': f'WL-{i + 1}',
                'position': [(i + 1) * 5000 + 2000, 0],
                'diameter': 'DN100',
                'outlet_length': 3000,
                'branches': [
                    {
                        'floor': f,
                        'diameter': 'DN75',
                        'length': 3000,
                        'direction': 'x',
                        'slope': 'i=0.020',
                        'fixtures': [
                            {'type': '地漏', 'position': [3000, 0]},
                        ]
                    }
                    for f in range(1, args.floors + 1)
                ],
            })
        config['systems'].append({
            'type': '排水',
            'title': f'排水系统轴测图 ({args.floors}层)',
            'code': 'W',
            'risers': d_risers,
        })

    if args.system in ('消防', 'all'):
        f_risers = []
        for i in range(args.risers):
            f_risers.append({
                'id': f'XL-{i + 1}',
                'position': [(i + 2) * 5000 + 4000, 0],
                'diameter': 'DN100',
                'branches': [
                    {
                        'floor': f,
                        'diameter': 'DN65',
                        'length': 4000,
                        'direction': 'x',
                        'hydrants': [
                            {'position': [2000, 0]},
                            {'position': [4000, 0]},
                        ]
                    }
                    for f in range(1, args.floors + 1)
                ],
            })
        config['systems'].append({
            'type': '消防',
            'title': f'消防系统轴测图 ({args.floors}层)',
            'code': 'XH',
            'risers': f_risers,
        })

    builder = SystemBuilder(config, scale=args.scale)
    builder.build(args.output)
    print(f"完成！可用 AutoCAD 打开: {args.output}")


def main():
    parser = argparse.ArgumentParser(
        description='CAD 给排水系统轴测图生成器 (GB/T 50106-2010)')
    sub = parser.add_subparsers(dest='command')

    # generate 子命令
    gen = sub.add_parser('generate', help='从 YAML 配置生成系统图')
    gen.add_argument('--config', required=True, help='配置文件路径')
    gen.add_argument('--output', default='output/system.dxf', help='输出 DXF 路径')
    gen.add_argument('--scale', type=float, default=1.0, help='缩放比例')

    # quick 子命令
    qk = sub.add_parser('quick', help='快速生成（输入基本参数）')
    qk.add_argument('--system', choices=['给水', '排水', '消防', 'all'],
                    default='给水', help='系统类型')
    qk.add_argument('--floors', type=int, default=6, help='楼层数')
    qk.add_argument('--risers', type=int, default=1, help='立管数量')
    qk.add_argument('--basement', type=int, default=0, help='地下层数')
    qk.add_argument('--output', default='output/quick_system.dxf', help='输出路径')
    qk.add_argument('--scale', type=float, default=1.0, help='缩放比例')

    args = parser.parse_args()

    if args.command == 'generate':
        cmd_generate(args)
    elif args.command == 'quick':
        cmd_quick(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
