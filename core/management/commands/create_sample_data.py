from django.core.management.base import BaseCommand
from faker import Faker

from core.models import Email


class Command(BaseCommand):
    help = 'Generate 50 fake emails'

    def handle(self, *args, **kwargs):
        faker = Faker()

        emails_created = 0
        while emails_created < 50:
            email = faker.email()
            name = faker.name()
            # Check if the email already exists to avoid duplicates
            if not Email.objects.filter(email=email).exists():
                Email.objects.create(email=email, name=name)
                emails_created += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {email} ({name})'))
            else:
                # If a duplicate email is generated, just continue to the next iteration
                continue

        self.stdout.write(self.style.SUCCESS(f'Successfully created {emails_created} emails.'))
