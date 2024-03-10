from unittest.mock import patch

from django.test import TestCase

from .factories import *


class DispatchModelTests(TestCase):

    def test_get_recipient_count(self):
        emails = EmailFactory.create_batch(5)
        send_list = SendListFactory(emails=emails)
        dispatch = DispatchFactory(send_list=send_list)

        self.assertEqual(dispatch.get_recipient_count(), 5)

    def test_get_recipient_count_no_send_list(self):
        dispatch = DispatchFactory(send_list=None)
        self.assertIsNone(dispatch.get_recipient_count())

    def create_dispatch_with_scheduler(self, frequency, time_of_day):
        """Helper method to create a Dispatch instance with a specific scheduler."""
        scheduler = SchedulerFactory(frequency=frequency, time_of_day=time_of_day)
        return DispatchFactory(scheduler=scheduler)


# Mock email sending method to avoid sending real emails during tests
class EmailModelTests(TestCase):
    @patch('core.models.send_mail')
    def test_send_email(self, mock_send_mail):
        email = EmailFactory()
        subject = "Test Subject"
        message = "Test message"
        footer_text = "Test footer"
        email.send_email(subject, message, footer_text)

        mock_send_mail.assert_called_once_with(
            subject=subject,
            message=f"{message}\n\n{footer_text}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email.email],
            fail_silently=False,
        )
