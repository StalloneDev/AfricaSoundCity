from django.core.management.base import BaseCommand
from django.utils import timezone
from app.models import ProchainConcert

class Command(BaseCommand):
    help = 'Update active concert'

    def handle(self, *args, **options):
        now = timezone.now()
        ProchainConcert.objects.filter(date__lt=now, is_active=True).update(is_active=False)
        next_concert = ProchainConcert.objects.filter(date__gt=now, is_active=False).first()
        if next_concert:
            next_concert.is_active = True
            next_concert.save()
