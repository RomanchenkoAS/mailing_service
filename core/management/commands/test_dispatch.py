from django.core.management.base import BaseCommand

from core.models import Dispatch


class Command(BaseCommand):
    help = 'Send scheduled dispatches that are due'

    def handle(self, *args, **options):
        d = Dispatch.objects.get(id=3)
        print(d, d.last_sent_at, d.next_due_at)
        print(d.is_due())

        # d.send()