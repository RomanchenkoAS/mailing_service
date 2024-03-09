from django.test import TestCase

from .factories import EmailFactory, SendListFactory, DispatchFactory


class DispatchModelTests(TestCase):

    def test_get_recipient_count(self):
        emails = EmailFactory.create_batch(5)
        send_list = SendListFactory(emails=emails)
        dispatch = DispatchFactory(send_list=send_list)

        self.assertEqual(dispatch.get_recipient_count(), 5)

    def test_get_recipient_count_no_send_list(self):
        dispatch = DispatchFactory(send_list=None)
        self.assertIsNone(dispatch.get_recipient_count())
