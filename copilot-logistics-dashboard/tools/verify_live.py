"""按培训数据基准验证真实 MCP；不修改数据、不输出凭据。"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.dashboard import get_dashboard
from services.settings import load_settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vscode-config', nargs='?', type=Path,
                        const=Path(os.environ.get('APPDATA', Path.home()/'AppData/Roaming'))/'Code/User/mcp.json')
    args = parser.parse_args()
    settings = load_settings(args.vscode_config)
    all_data = get_dashboard(settings)
    first = get_dashboard(settings, 'CAR002')
    last = get_dashboard(settings, 'CAR002', 7)
    empty = get_dashboard(settings, 'CAR999')
    for data, expected in ((all_data, (500, 380, 304, 76)), (first, (134, 104, 77, 27))):
        actual = tuple(data['summary'][key] for key in ('shipment_count', 'eligible_count', 'on_time_count', 'delayed_count'))
        if actual != expected:
            raise RuntimeError(f'基准不符：{actual} != {expected}')
    if len(last['shipments']) != 14 or last['page_count'] != 7:
        raise RuntimeError('最后一页条数不符。')
    if {r['shipment_id'] for r in first['shipments']} & {r['shipment_id'] for r in last['shipments']}:
        raise RuntimeError('不同页的明细重复。')
    if empty['summary']['on_time_rate'] is not None or empty['shipments']:
        raise RuntimeError('空范围处理不符。')
    if len(all_data['daily']) != 65 or all_data['snapshot_epoch'] != 1793851200:
        raise RuntimeError('自然日或快照时间不符。')
    print(json.dumps({'verified_at': datetime.now(timezone.utc).isoformat(), 'overall': all_data['summary'],
                      'CAR002': first['summary'], 'last_page_rows': len(last['shipments']),
                      'empty_rate': empty['summary']['on_time_rate'], 'natural_days': len(all_data['daily']),
                      'snapshot_epoch': all_data['snapshot_epoch'],
                      'statement_ids': [d['source']['statement_id'] for d in (all_data, first, last, empty)]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
