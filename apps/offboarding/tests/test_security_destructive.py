"""RBAC + IDOR coverage for the linter-added Offboarding delete endpoints."""
from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.core.models import set_current_tenant
from apps.employees.tests.factories import (
    make_employee, make_employee_user, make_tenant, make_user,
)
from apps.offboarding.models import (
    ClearanceProcess, ExitInterview, ExperienceLetter, FnFSettlement, Resignation,
)


class OffboardingDeleteRBACTests(TestCase):
    def setUp(self):
        self.tenant = make_tenant()
        set_current_tenant(self.tenant)
        self.admin = make_user(self.tenant, role='tenant_admin', is_tenant_admin=True)
        self.plain = make_employee_user(self.tenant)
        self.employee = make_employee(self.tenant)

    def tearDown(self):
        set_current_tenant(None)

    def _check_rbac(self, url_name, args, model, lookup_kwargs):
        url = reverse(url_name, args=args)

        self.client.force_login(self.plain)
        r = self.client.post(url)
        self.assertTrue(model.all_objects.filter(**lookup_kwargs).exists(),
                        f'Plain employee must NOT be able to POST to {url_name}.')
        self.assertIn(r.status_code, (302, 403))

        self.client.force_login(self.admin)
        r = self.client.post(url)
        self.assertEqual(r.status_code, 302, f'Admin should succeed at {url_name}.')
        self.assertFalse(model.all_objects.filter(**lookup_kwargs).exists())

    def test_resignation_delete(self):
        res = Resignation.objects.create(
            tenant=self.tenant, employee=self.employee,
            resignation_date=date(2026, 4, 25),
            last_working_day=date(2026, 5, 25),
            reason='Test', status='submitted',
        )
        self._check_rbac('offboarding:resignation_delete', [res.pk], Resignation, {'pk': res.pk})

    def test_exit_interview_delete(self):
        interview = ExitInterview.objects.create(
            tenant=self.tenant, employee=self.employee,
            scheduled_date=timezone.now(), status='scheduled',
        )
        self._check_rbac('offboarding:exitinterview_delete', [interview.pk],
                         ExitInterview, {'pk': interview.pk})

    def test_clearance_delete(self):
        clearance = ClearanceProcess.objects.create(
            tenant=self.tenant, employee=self.employee,
            initiated_date=date(2026, 4, 25), status='pending',
        )
        self._check_rbac('offboarding:clearance_delete', [clearance.pk],
                         ClearanceProcess, {'pk': clearance.pk})

    def test_fnf_delete(self):
        settlement = FnFSettlement.objects.create(
            tenant=self.tenant, employee=self.employee,
            settlement_date=date(2026, 5, 25), status='draft',
        )
        self._check_rbac('offboarding:fnf_delete', [settlement.pk],
                         FnFSettlement, {'pk': settlement.pk})

    def test_letter_delete(self):
        letter = ExperienceLetter.objects.create(
            tenant=self.tenant, employee=self.employee,
            letter_date=date(2026, 5, 25), letter_type='experience',
            content='Test letter', is_issued=False,
        )
        self._check_rbac('offboarding:letter_delete', [letter.pk],
                         ExperienceLetter, {'pk': letter.pk})

    def test_cross_tenant_resignation_delete_404(self):
        other = make_tenant()
        other_res = Resignation.objects.create(
            tenant=other, employee=make_employee(other),
            resignation_date=date(2026, 4, 25),
            last_working_day=date(2026, 5, 25),
            reason='x', status='submitted',
        )
        self.client.force_login(self.admin)
        r = self.client.post(reverse('offboarding:resignation_delete', args=[other_res.pk]))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(Resignation.all_objects.filter(pk=other_res.pk).exists())
