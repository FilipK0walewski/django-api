from django.core.management.base import BaseCommand
from images.models import Tier


class Command(BaseCommand):
    help = 'Creates builtin account tiers'

    def handle(self, *args, **options):
        obj, created = Tier.objects.get_or_create(name='Basic', sizes=[200])
        self.stdout.write(self.style.SUCCESS('Tier "%s" %s.' % (obj, 'created' if created is True else 'already exists')))
        obj, created = Tier.objects.get_or_create(name='Premium', sizes=[200, 400], original_image_access=True)
        self.stdout.write(self.style.SUCCESS('Tier "%s" %s.' % (obj, 'created' if created is True else 'already exists')))
        obj, created = Tier.objects.get_or_create(name='Enterprise', sizes=[200, 400], original_image_access=True, expiring_link_access=True)
        self.stdout.write(self.style.SUCCESS('Tier "%s" %s.' % (obj, 'created' if created is True else 'already exists')))
