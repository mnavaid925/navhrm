from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from apps.core.models import set_current_tenant
from apps.employees.tests.factories import make_employee, make_tenant, make_user
from apps.onboarding.models import (
    OnboardingProcess, OnboardingTask, OnboardingTemplate, OnboardingTemplateTask,
)


class OnboardingTemplateCopyTests(TestCase):
    """D-05 regression: starting a process from a template must preserve the
    days_before/after_joining offsets via the cloned task's due_date."""

    def setUp(self):
        self.tenant = make_tenant()
        set_current_tenant(self.tenant)
        self.admin = make_user(self.tenant)
        self.employee = make_employee(self.tenant)

    def tearDown(self):
        set_current_tenant(None)

    def test_template_offsets_become_due_dates(self):
        tmpl = OnboardingTemplate.objects.create(
            tenant=self.tenant, name='Standard', is_active=True,
        )
        OnboardingTemplateTask.objects.create(
            tenant=self.tenant, template=tmpl, title='Send laptop',
            days_before_joining=7, days_after_joining=0, order=1,
        )
        OnboardingTemplateTask.objects.create(
            tenant=self.tenant, template=tmpl, title='Welcome lunch',
            days_before_joining=0, days_after_joining=3, order=2,
        )

        self.client.force_login(self.admin)
        start = date(2026, 5, 1)
        r = self.client.post(
            reverse('onboarding:create', args=[self.employee.pk]),
            data={'employee': self.employee.pk, 'template': tmpl.pk,
                  'start_date': start.isoformat(), 'notes': ''},
        )
        self.assertEqual(r.status_code, 302, r.content)
        process = OnboardingProcess.objects.get(employee=self.employee)
        tasks = {t.title: t for t in process.tasks.all()}
        self.assertEqual(tasks['Send laptop'].due_date, start - timedelta(days=7))
        self.assertEqual(tasks['Welcome lunch'].due_date, start + timedelta(days=3))


class OnboardingSearchTests(TestCase):
    """D-06 regression: search uses Q() lookups, no UNION duplication."""

    def setUp(self):
        self.tenant = make_tenant()
        set_current_tenant(self.tenant)
        self.admin = make_user(self.tenant)

    def tearDown(self):
        set_current_tenant(None)

    def test_search_does_not_duplicate_when_match_spans_first_and_last(self):
        """Old impl used `qs.filter(first) | qs.filter(last)` which UNION-duplicated
        rows that matched on both fields. The view's queryset should now use Q()
        and return exactly one row."""
        emp = make_employee(self.tenant, first_name='Jordan', last_name='Jordans')
        OnboardingProcess.objects.create(
            tenant=self.tenant, employee=emp, status='pending',
            start_date=date(2026, 5, 1),
        )
        self.client.force_login(self.admin)
        r = self.client.get(reverse('onboarding:list') + '?search=Jord')
        self.assertEqual(r.status_code, 200)
        # The view's paginated context should have exactly one process row.
        self.assertEqual(len(r.context['processes']), 1)
