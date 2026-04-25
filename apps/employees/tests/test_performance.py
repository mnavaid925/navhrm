"""Query-budget regression tests (D-10).

Caps SQL query count for list views so future N+1 regressions fail fast.
Uses `CaptureQueriesContext` + `assertLessEqual` for "at most N" semantics:
this avoids flapping when a future change happens to *reduce* the count.
"""
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from apps.core.models import set_current_tenant
from .factories import (
    make_department, make_designation, make_employee, make_tenant, make_user,
)


class EmployeeDirectoryQueryBudgetTests(TestCase):
    def setUp(self):
        self.tenant = make_tenant()
        set_current_tenant(self.tenant)
        self.admin = make_user(self.tenant)
        dept = make_department(self.tenant)
        desig = make_designation(self.tenant)
        for _ in range(50):
            make_employee(self.tenant, department=dept, designation=desig)

    def tearDown(self):
        set_current_tenant(None)

    def test_directory_avoids_n_plus_one(self):
        """50 employees with FK department & designation must render in O(1) queries."""
        self.client.force_login(self.admin)
        with CaptureQueriesContext(connection) as ctx:
            r = self.client.get(reverse('employees:directory'))
        self.assertEqual(r.status_code, 200)
        # Current measured: ~6. Cap at 10 to leave room for unrelated middleware.
        self.assertLessEqual(
            len(ctx.captured_queries), 10,
            f'Suspected N+1: {len(ctx.captured_queries)} queries (budget 10).',
        )
