import hashlib
import math
from decimal import Decimal, InvalidOperation

from dateutil import parser


UNIT_ALIASES = {
    'l': 'l',
    'liter': 'l',
    'liters': 'l',
    'litre': 'l',
    'litres': 'l',
    'gal': 'gal',
    'gallon': 'gal',
    'gallons': 'gal',
    'kg': 'kg',
    'kilogram': 'kg',
    'kilograms': 'kg',
    't': 't',
    'tonne': 't',
    'tonnes': 't',
    'metric ton': 't',
    'metric tons': 't',
    'kwh': 'kwh',
}

UNIT_CONVERSIONS = {
    ('gal', 'l'): Decimal('3.78541'),
    ('t', 'kg'): Decimal('1000'),
}


def parse_decimal(value):
    if value is None:
        return None
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    cleaned = str(value).strip()
    if cleaned == '':
        return None
    cleaned = cleaned.replace(',', '.')
    cleaned = ''.join(ch for ch in cleaned if ch.isdigit() or ch in {'.', '-', '+'})
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def parse_date(value):
    if not value:
        return None
    try:
        return parser.parse(str(value), dayfirst=True).date()
    except (parser.ParserError, TypeError, ValueError):
        return None


def normalize_unit(value, unit):
    if value is None:
        return None, None, {}
    alias = UNIT_ALIASES.get(str(unit).strip().lower())
    if not alias:
        return value, str(unit).strip().lower(), {'warning': 'unknown_unit'}
    standard_unit = alias
    metadata = {'original_unit': unit, 'standard_unit': standard_unit}
    converted = Decimal(str(value))
    if standard_unit == 'gal':
        metadata['conversion'] = 'gal_to_l'
        standard_unit = 'l'
        converted = converted * UNIT_CONVERSIONS[('gal', 'l')]
    if standard_unit == 't':
        metadata['conversion'] = 't_to_kg'
        standard_unit = 'kg'
        converted = converted * UNIT_CONVERSIONS[('t', 'kg')]
    return converted, standard_unit, metadata


def hash_row(payload):
    serialized = str(sorted(payload.items())).encode('utf-8')
    return hashlib.sha256(serialized).hexdigest()


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(min(1, math.sqrt(a)))
    return radius * c
