from collections import defaultdict
from decimal import Decimal

from .utils import parse_date


def detect_utility_anomalies(records):
    anomalies = []
    by_meter = defaultdict(list)
    for record in records:
        data = record.data or {}
        meter_id = data.get('meter_id')
        if meter_id:
            by_meter[meter_id].append(record)

    for meter_id, meter_records in by_meter.items():
        seen_periods = set()
        usages = []
        for record in meter_records:
            data = record.data or {}
            start = parse_date(data.get('billing_start'))
            end = parse_date(data.get('billing_end'))
            usage = record.normalized_quantity or Decimal('0')
            usages.append(usage)
            if start and end:
                period_key = (start, end)
                if period_key in seen_periods:
                    anomalies.append((record, 'duplicate_bill', 'Duplicate billing period.', 'high'))
                seen_periods.add(period_key)

        average_usage = sum(usages) / max(len(usages), 1)
        for record in meter_records:
            data = record.data or {}
            start = parse_date(data.get('billing_start'))
            end = parse_date(data.get('billing_end'))
            if start and end:
                for other in meter_records:
                    if other == record:
                        continue
                    other_start = parse_date(other.data.get('billing_start'))
                    other_end = parse_date(other.data.get('billing_end'))
                    if not other_start or not other_end:
                        continue
                    overlap = start <= other_end and other_start <= end
                    if overlap and (start, end) != (other_start, other_end):
                        anomalies.append(
                            (record, 'overlapping_period', 'Overlapping billing periods.', 'medium')
                        )
                        break
            if average_usage and record.normalized_quantity and record.normalized_quantity > average_usage * 2:
                anomalies.append((record, 'usage_spike', 'Usage spike vs average.', 'medium'))

    return anomalies
