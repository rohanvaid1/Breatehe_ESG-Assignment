from decimal import Decimal

from .utils import haversine_km, normalize_unit, parse_date, parse_decimal

SAP_FIELD_MAP = {
    'plant_code': 'plant_code',
    'werk': 'plant_code',
    'material_description': 'material_description',
    'materialkurztext': 'material_description',
    'quantity': 'quantity',
    'menge': 'quantity',
    'unit': 'unit',
    'me': 'unit',
    'cost_center': 'cost_center',
    'kostenstelle': 'cost_center',
    'vendor': 'vendor',
    'lieferant': 'vendor',
    'posting_date': 'posting_date',
    'buchungsdatum': 'posting_date',
    'fuel_type': 'fuel_type',
    'kraftstoffart': 'fuel_type',
    'currency': 'currency',
    'waehrung': 'currency',
    'währung': 'currency',
}

UTILITY_FIELD_MAP = {
    'meter_id': 'meter_id',
    'meter id': 'meter_id',
    'billing_start': 'billing_start',
    'billing start': 'billing_start',
    'billing_end': 'billing_end',
    'billing end': 'billing_end',
    'kwh_usage': 'kwh_usage',
    'kwh usage': 'kwh_usage',
    'peak_usage': 'peak_usage',
    'peak usage': 'peak_usage',
    'off_peak_usage': 'off_peak_usage',
    'off peak usage': 'off_peak_usage',
    'tariff_plan': 'tariff_plan',
    'tariff plan': 'tariff_plan',
    'utility_provider': 'utility_provider',
    'utility provider': 'utility_provider',
}

TRAVEL_FIELD_MAP = {
    'employee_id': 'employee_id',
    'employee id': 'employee_id',
    'travel_type': 'travel_type',
    'travel type': 'travel_type',
    'origin': 'origin',
    'destination': 'destination',
    'departure_date': 'departure_date',
    'departure date': 'departure_date',
    'return_date': 'return_date',
    'return date': 'return_date',
    'airline': 'airline',
    'hotel_name': 'hotel_name',
    'hotel name': 'hotel_name',
    'transport_mode': 'transport_mode',
    'transport mode': 'transport_mode',
    'distance_km': 'distance_km',
    'distance km': 'distance_km',
}

FUEL_FACTORS = {
    'diesel': Decimal('2.68'),
    'petrol': Decimal('2.31'),
    'gasoline': Decimal('2.31'),
    'kerosene': Decimal('2.54'),
    'natural gas': Decimal('2.75'),
}

TRAVEL_FACTORS = {
    'flight': Decimal('0.115'),
    'rail': Decimal('0.041'),
    'taxi': Decimal('0.210'),
}


def _to_json(value):
    """Recursively convert Decimal → float so dicts are JSON-serializable."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {k: _to_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_json(v) for v in value]
    return value


def _map_fields(row, mapping):
    mapped = {}
    for key, value in row.items():
        if key is None:
            continue
        normalized_key = mapping.get(str(key).strip().lower())
        if normalized_key:
            mapped[normalized_key] = value
    return mapped


def normalize_sap_row(row):
    data = _map_fields(row, SAP_FIELD_MAP)
    anomalies = []

    quantity = parse_decimal(data.get('quantity'))
    unit = data.get('unit')
    fuel_type = (data.get('fuel_type') or '').strip().lower()

    if quantity is None:
        anomalies.append(('missing_quantity', 'Missing quantity value.', 'high'))
    elif quantity < 0:
        anomalies.append(('negative_quantity', 'Negative quantity value.', 'high'))

    normalized_quantity, normalized_unit, unit_meta = normalize_unit(quantity, unit)
    if unit_meta.get('warning') == 'unknown_unit':
        anomalies.append(('unknown_unit', f"Unknown unit {unit}.", 'medium'))

    emission_factor = FUEL_FACTORS.get(fuel_type)
    if emission_factor is None:
        emission_factor = Decimal('1.0')
        anomalies.append(('unknown_fuel', f"Unknown fuel type '{fuel_type}'.", 'medium'))

    estimated_emissions = None
    if normalized_quantity is not None:
        estimated_emissions = normalized_quantity * emission_factor

    emission_scope = 'scope_1' if fuel_type in FUEL_FACTORS else 'scope_3'
    emission_category_key = 'fuel_combustion' if emission_scope == 'scope_1' else 'procurement'

    normalized_payload = _to_json({
        'plant_code': data.get('plant_code'),
        'material_description': data.get('material_description'),
        'cost_center': data.get('cost_center'),
        'vendor': data.get('vendor'),
        'posting_date': str(parse_date(data.get('posting_date')) or ''),
        'fuel_type': data.get('fuel_type'),
    })

    return {
        'emission_scope': emission_scope,
        'emission_category_key': emission_category_key,
        'activity_quantity': quantity,
        'activity_unit': unit,
        'normalized_quantity': normalized_quantity,
        'normalized_unit': normalized_unit,
        'emission_factor': emission_factor,
        'estimated_emissions': estimated_emissions,
        'currency': (data.get('currency') or '').strip(),
        'data': normalized_payload,
        'conversion_metadata': _to_json(unit_meta),
        'anomalies': anomalies,
    }


def normalize_utility_row(row):
    data = _map_fields(row, UTILITY_FIELD_MAP)
    anomalies = []

    kwh_usage = parse_decimal(data.get('kwh_usage'))
    if kwh_usage is None:
        anomalies.append(('missing_kwh', 'Missing kWh usage.', 'high'))
    if kwh_usage is not None and kwh_usage < 0:
        anomalies.append(('negative_kwh', 'Negative kWh usage.', 'high'))

    emission_factor = Decimal('0.475')
    estimated_emissions = kwh_usage * emission_factor if kwh_usage is not None else None

    normalized_payload = _to_json({
        'meter_id': data.get('meter_id'),
        'billing_start': str(parse_date(data.get('billing_start')) or ''),
        'billing_end': str(parse_date(data.get('billing_end')) or ''),
        'peak_usage': parse_decimal(data.get('peak_usage')),
        'off_peak_usage': parse_decimal(data.get('off_peak_usage')),
        'tariff_plan': data.get('tariff_plan'),
        'utility_provider': data.get('utility_provider'),
    })

    return {
        'emission_scope': 'scope_2',
        'emission_category_key': 'electricity',
        'activity_quantity': kwh_usage,
        'activity_unit': 'kwh',
        'normalized_quantity': kwh_usage,
        'normalized_unit': 'kwh',
        'emission_factor': emission_factor,
        'estimated_emissions': estimated_emissions,
        'currency': '',
        'data': normalized_payload,
        'conversion_metadata': {},
        'anomalies': anomalies,
    }


def normalize_travel_row(row, airports):
    data = _map_fields(row, TRAVEL_FIELD_MAP)
    anomalies = []

    travel_type = (data.get('travel_type') or '').strip().lower()
    origin = (data.get('origin') or '').strip().upper()
    destination = (data.get('destination') or '').strip().upper()
    departure_date = parse_date(data.get('departure_date'))
    return_date = parse_date(data.get('return_date'))

    distance_km = parse_decimal(data.get('distance_km'))
    if distance_km is not None and distance_km < 0:
        anomalies.append(('negative_distance', 'Negative distance value.', 'high'))

    # Auto-calculate distance from airport coords for flight/rail/taxi when distance is missing
    if travel_type in ('flight', 'rail', 'taxi') and distance_km is None and origin and destination:
        origin_airport = airports.get(origin)
        destination_airport = airports.get(destination)
        if origin_airport and destination_airport:
            distance_km = Decimal(
                str(
                    haversine_km(
                        float(origin_airport['latitude']),
                        float(origin_airport['longitude']),
                        float(destination_airport['latitude']),
                        float(destination_airport['longitude']),
                    )
                )
            )
        else:
            anomalies.append(('unknown_airport', 'Airport code not found for distance estimate.', 'medium'))

    if origin == destination and origin:
        anomalies.append(('same_origin_destination', 'Origin and destination are identical.', 'high'))

    emission_factor = TRAVEL_FACTORS.get(travel_type, Decimal('0.1'))
    estimated_emissions = distance_km * emission_factor if distance_km is not None else None

    nights = None
    if travel_type == 'hotel' and departure_date and return_date:
        nights = max((return_date - departure_date).days, 0)
        emission_factor = Decimal('15')
        estimated_emissions = Decimal(nights) * emission_factor

    normalized_payload = _to_json({
        'employee_id': data.get('employee_id'),
        'travel_type': travel_type,
        'origin': origin,
        'destination': destination,
        'departure_date': str(departure_date or ''),
        'return_date': str(return_date or ''),
        'airline': data.get('airline'),
        'hotel_name': data.get('hotel_name'),
        'transport_mode': data.get('transport_mode'),
        'distance_km': distance_km,
        'nights': nights,
    })

    return {
        'emission_scope': 'scope_3',
        'emission_category_key': 'business_travel',
        'activity_quantity': distance_km if travel_type != 'hotel' else (Decimal(nights) if nights is not None else None),
        'activity_unit': 'km' if travel_type != 'hotel' else 'nights',
        'normalized_quantity': distance_km if travel_type != 'hotel' else (Decimal(nights) if nights is not None else None),
        'normalized_unit': 'km' if travel_type != 'hotel' else 'nights',
        'emission_factor': emission_factor,
        'estimated_emissions': estimated_emissions,
        'currency': '',
        'data': normalized_payload,
        'conversion_metadata': {},
        'anomalies': anomalies,
    }
