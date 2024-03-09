from django.core.management.base import BaseCommand

from core.models import Dispatch


class Command(BaseCommand):
    help = 'Send scheduled dispatches that are due'

    def handle(self, *args, **options):
        dispatches_due = [dispatch for dispatch in Dispatch.objects.all() if dispatch.is_due()]
        if not dispatches_due:
            self.stdout.write(self.style.SUCCESS('No dispatches are due at this time.'))
            return

        for dispatch in dispatches_due:
            try:
                dispatch.send()
                self.stdout.write(self.style.SUCCESS(f'Successfully sent dispatch: {dispatch.title}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to send dispatch: {dispatch.title}. Error: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'Total dispatched: {len(dispatches_due)}'))
