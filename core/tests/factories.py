import factory
from factory.django import DjangoModelFactory

from core.models import *


class EmailFactory(DjangoModelFactory):
    class Meta:
        model = Email

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    name = factory.Faker('name')


class SendListFactory(DjangoModelFactory):
    class Meta:
        model = SendList

    title = factory.Sequence(lambda n: f"Send List {n}")

    @factory.post_generation
    def emails(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of emails were passed in, use them
            for email in extracted:
                self.emails.add(email)


class FooterFactory(DjangoModelFactory):
    class Meta:
        model = Footer

    text = factory.Faker('sentence')


class DispatchFactory(DjangoModelFactory):
    class Meta:
        model = Dispatch

    title = factory.Sequence(lambda n: f"Dispatch {n}")
    send_list = factory.SubFactory(SendListFactory)
    subject = factory.Faker('sentence')
    text = factory.Faker('paragraph')
    footer = factory.SubFactory(FooterFactory)


class SchedulerFactory(DjangoModelFactory):
    class Meta:
        model = Scheduler

    frequency = factory.Iterator(['daily', 'weekly', 'monthly'])
    time_of_day = factory.LazyFunction(
        lambda: timezone.now().time().replace(hour=12, minute=0, second=0, microsecond=0))
