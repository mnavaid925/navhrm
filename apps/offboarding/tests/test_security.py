from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.core.models import set_current_tenant
from apps.employees.tests.factories import (
    make_employee, make_employee_user, make_tenant, make_user,
)
from apps.offboarding.models import Resignation


def _make_resignation(tenant, employee):
    return Resignation.objects.create(
        tenant=tenant, employee=employee,
        resignation_date=date(2026, 4, 25),
        last_working_day=date(2026, 5, 25),
        reason='Personal reasons',
        status='submitted',
    )


class ResignationApprovalRBACTests(TestCase):
    """D-07 regression: only HR-privileged roles can approve resignations."""

    def setUp(self):
        self.tenant = make_tenant()
        set_current_tenant(self.tenant)
        self.employee = make_employee(self.tenant)
        self.resignation = _make_resignation(self.tenant, self.employee)

    def tearDown(self):
        set_current_tenant(None)

    def test_plain_employee_cannot_approve(self):
        plain = make_employee_user(self.tenant)
        self.client.force_login(plain)
        r = self.client.post(
            reverse('offboarding:resignation_approve', args=[self.resignation.pk]),
            data={'action': 'approve'},
        )
        self.resignation.refresh_from_db()
        self.assertNotEqual(self.resignation.status, 'approved',
                            'Plain employee must NOT be able to approve resignations.')
        # Either a 302 redirect (to dashboard) or 403 is acceptable; not 200/approved.
        self.assertIn(r.status_code, (302, 403))

    def test_tenant_admin_can_approve_and_employee_status_propagates(self):
        """D-16 regression: approval flips Employee.status to 'resigned'."""
        admin = make_user(self.tenant, role='tenant_admin', is_tenant_admin=True)
        self.client.force_login(admin)
        r = self.client.post(
            reverse('offboarding:resignation_approve', args=[self.resignation.pk]),
            data={'action': 'approve'},
        )
        self.assertEqual(r.status_code, 302)
        self.resignation.refresh_from_db()
        self.employee.refresh_from_db()
        self.assertEqual(self.resignation.status, 'approved')
        self.assertEqual(self.employee.status, 'resigned')
        self.assertEqual(self.employee.date_of_leaving, self.resignation.last_working_day)

    def test_other_tenant_resignation_returns_404(self):
        """Cross-tenant IDOR: tenant filter should reject."""
        admin = make_user(self.tenant, role='tenant_admin', is_tenant_admin=True)
        other = make_tenant()
        other_emp = make_employee(other)
        other_res = _make_resignation(other, other_emp)
        self.client.force_login(admin)
        r = self.client.post(
            reverse('offboarding:resignation_approve', args=[other_res.pk]),
            data={'action': 'approve'},
        )
        self.assertEqual(r.status_code, 404)
