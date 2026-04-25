from datetime import date

from django.test import TestCase

from apps.core.models import set_current_tenant
from apps.employees.tests.factories import make_employee, make_tenant
from apps.offboarding.forms import ExitInterviewFeedbackForm, ResignationForm


class ResignationFormTests(TestCase):
    def setUp(self):
        self.tenant = make_tenant()
        set_current_tenant(self.tenant)
        self.employee = make_employee(self.tenant)

    def tearDown(self):
        set_current_tenant(None)

    def test_last_working_day_must_be_after_resignation_date(self):
        """D-03 regression."""
        form = ResignationForm(
            data={
                'employee': self.employee.pk,
                'resignation_date': date(2026, 4, 25),
                'last_working_day': date(2026, 4, 20),
                'reason': 'test',
            },
            tenant=self.tenant,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('last_working_day', form.errors)

    def test_valid_dates_accepted(self):
        form = ResignationForm(
            data={
                'employee': self.employee.pk,
                'resignation_date': date(2026, 4, 25),
                'last_working_day': date(2026, 5, 25),
                'reason': 'test',
            },
            tenant=self.tenant,
        )
        self.assertTrue(form.is_valid(), form.errors)


class ExitInterviewFeedbackFormTests(TestCase):
    """D-04 regression: rating must be 1–5 server-side."""

    def _form(self, rating):
        return ExitInterviewFeedbackForm(data={
            'overall_experience': rating,
            'reason_for_leaving': 'x',
            'what_liked': 'x',
            'what_disliked': 'x',
            'additional_feedback': 'x',
        })

    def test_rating_in_range_accepted(self):
        for r in (1, 3, 5):
            with self.subTest(rating=r):
                self.assertTrue(self._form(r).is_valid())

    def test_rating_out_of_range_rejected(self):
        for r in (0, 6, -1, 999):
            with self.subTest(rating=r):
                form = self._form(r)
                self.assertFalse(form.is_valid())
                self.assertIn('overall_experience', form.errors)

    def test_rating_non_numeric_rejected(self):
        form = self._form('abc')
        self.assertFalse(form.is_valid())
        self.assertIn('overall_experience', form.errors)
