from django.core.management.base import BaseCommand

from ingestion.models import AirportLookup, EmissionCategory, SourceSystem, UnitConversion


class Command(BaseCommand):
    help = 'Seed reference data for emission categories, sources, and unit conversions.'

    def handle(self, *args, **options):
        categories = [
            ('fuel_combustion', 'Fuel Combustion', 'scope_1'),
            ('procurement', 'Procurement', 'scope_3'),
            ('electricity', 'Electricity', 'scope_2'),
            ('business_travel', 'Business Travel', 'scope_3'),
        ]
        for key, name, scope in categories:
            EmissionCategory.objects.get_or_create(key=key, defaults={'name': name, 'scope': scope})

        sources = [
            ('SAP Fuel & Procurement', 'sap', 'SAP exports for fuel and procurement data.'),
            ('Utility Electricity', 'utility', 'Utility portal electricity export.'),
            ('Corporate Travel', 'travel', 'Concur/Navan style travel export.'),
        ]
        for name, source_type, description in sources:
            SourceSystem.objects.get_or_create(
                name=name, source_type=source_type, defaults={'description': description}
            )

        UnitConversion.objects.get_or_create(from_unit='gal', to_unit='l', defaults={'multiplier': '3.78541'})
        UnitConversion.objects.get_or_create(from_unit='t', to_unit='kg', defaults={'multiplier': '1000'})

        airports = [
            ('FRA', 'Frankfurt', 'DE', 50.0379, 8.5622),
            ('LHR', 'London', 'UK', 51.4700, -0.4543),
            ('JFK', 'New York', 'US', 40.6413, -73.7781),
            ('SFO', 'San Francisco', 'US', 37.6213, -122.3790),
            ('SIN', 'Singapore', 'SG', 1.3644, 103.9915),
            ('DXB', 'Dubai', 'AE', 25.2532, 55.3657),
            ('BOM', 'Mumbai', 'IN', 19.0896, 72.8656),
            ('DEL', 'Delhi', 'IN', 28.5562, 77.1000),
        ]
        for code, city, country, lat, lon in airports:
            AirportLookup.objects.get_or_create(
                code=code,
                defaults={'city': city, 'country': country, 'latitude': lat, 'longitude': lon},
            )

        self.stdout.write(self.style.SUCCESS('Reference data seeded.'))
