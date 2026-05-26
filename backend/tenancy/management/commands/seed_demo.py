from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from tenancy.models import Organization


class Command(BaseCommand):
    help = 'Seed demo organization and users.'

    def handle(self, *args, **options):
        org, _ = Organization.objects.get_or_create(
            slug='breathe-demo',
            defaults={
                'name': 'Breathe Manufacturing Group',
                'industry': 'Industrial Manufacturing',
                'country': 'DE',
                'timezone': 'Europe/Berlin',
            },
        )

        User = get_user_model()
        users = [
            ('admin', 'admin@breathe.demo', 'admin'),
            ('analyst', 'analyst@breathe.demo', 'analyst'),
            ('viewer', 'viewer@breathe.demo', 'viewer'),
        ]
        for username, email, role in users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'organization': org, 'role': role},
            )
            if created:
                user.set_password('breathe123')
                user.save()

        self.stdout.write(self.style.SUCCESS('Demo organization and users created.'))
