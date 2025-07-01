import datetime

import pytest
from django.utils import timezone
from freezegun import freeze_time

from .factories import DispatchFactory, SchedulerFactory


@pytest.mark.django_db
def test_update_next_due_at_daily_future():
    # Schedule for later today
    now = timezone.now()
    time_of_day = (now + datetime.timedelta(hours=1)).time()
    scheduler = SchedulerFactory(frequency='daily', time_of_day=time_of_day)
    dispatch = DispatchFactory(scheduler=scheduler)
    dispatch.update_next_due_at()
    # Should be today at scheduled time
    assert dispatch.next_due_at.date() == now.date()
    assert dispatch.next_due_at.time().hour == time_of_day.hour


@pytest.mark.django_db
def test_update_next_due_at_daily_past():
    # Schedule for earlier today
    now = timezone.now()
    time_of_day = (now - datetime.timedelta(hours=1)).time()
    scheduler = SchedulerFactory(frequency='daily', time_of_day=time_of_day)
    dispatch = DispatchFactory(scheduler=scheduler)
    dispatch.update_next_due_at()
    # Should be tomorrow
    tomorrow = now.date() + datetime.timedelta(days=1)
    assert dispatch.next_due_at.date() == tomorrow
    assert dispatch.next_due_at.time().hour == time_of_day.hour


@pytest.mark.django_db
def test_update_next_due_at_weekly_future():
    now = timezone.now()
    time_of_day = (now + datetime.timedelta(hours=1)).time()
    scheduler = SchedulerFactory(frequency='weekly', time_of_day=time_of_day)
    dispatch = DispatchFactory(scheduler=scheduler)
    dispatch.update_next_due_at()
    # Should be today
    assert dispatch.next_due_at.date() == now.date()


@pytest.mark.django_db
def test_update_next_due_at_weekly_past():
    now = timezone.now()
    time_of_day = (now - datetime.timedelta(hours=1)).time()
    scheduler = SchedulerFactory(frequency='weekly', time_of_day=time_of_day)
    dispatch = DispatchFactory(scheduler=scheduler)
    dispatch.update_next_due_at()
    # Should be 7 days from today
    next_week = now.date() + datetime.timedelta(days=7)
    assert dispatch.next_due_at.date() == next_week


@pytest.mark.django_db
def test_update_next_due_at_monthly_future():
    now = timezone.now()
    time_of_day = (now + datetime.timedelta(hours=1)).time()
    scheduler = SchedulerFactory(frequency='monthly', time_of_day=time_of_day)
    dispatch = DispatchFactory(scheduler=scheduler)
    dispatch.update_next_due_at()
    # Should be today
    assert dispatch.next_due_at.date() == now.date()


@pytest.mark.django_db
def test_update_next_due_at_monthly_past():
    now = timezone.now()
    time_of_day = (now - datetime.timedelta(hours=1)).time()
    scheduler = SchedulerFactory(frequency='monthly', time_of_day=time_of_day)
    dispatch = DispatchFactory(scheduler=scheduler)
    dispatch.update_next_due_at()
    # Should be next month, same day or last day if overflow
    next_month = (now.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    expected_month = next_month.month
    assert dispatch.next_due_at.month == expected_month


# Check Leap Year Overflow (Feb 29 → March)
@pytest.mark.django_db
@freeze_time("2024-02-29 12:00:00")
def test_update_next_due_at_monthly_leap_year():
    scheduler = SchedulerFactory(frequency='monthly', time_of_day=datetime.time(12, 0))
    dispatch = DispatchFactory(scheduler=scheduler)
    dispatch.update_next_due_at()
    assert dispatch.next_due_at.month == 3
    assert dispatch.next_due_at.day == 29


@pytest.mark.django_db
def test_update_next_due_at_no_scheduler():
    dispatch = DispatchFactory(scheduler=None)
    dispatch.update_next_due_at()
    assert dispatch.next_due_at is None


@pytest.mark.django_db
def test_update_next_due_at_invalid_frequency():
    scheduler = SchedulerFactory(frequency='invalid')
    with pytest.raises(ValueError):
        DispatchFactory(scheduler=scheduler)


# Check End-of-month overflow (Jan 31 → Feb)
@pytest.mark.django_db
@freeze_time("2023-01-31 12:00:00")
def test_update_next_due_at_monthly_end_of_month():
    scheduler = SchedulerFactory(frequency='monthly', time_of_day=datetime.time(12, 0))
    dispatch = DispatchFactory(scheduler=scheduler)
    dispatch.update_next_due_at()
    assert dispatch.next_due_at.month == 2
    assert dispatch.next_due_at.day == 28
