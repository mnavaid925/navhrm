"""Query-budget tests for the offboarding resignation list view (D-10)."""
from datetime import date

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from apps.core.models import set_current_tenant
from apps.employees.tests.factories import make_employee, make_tenant, make_user
from apps.offboarding.models import Resignation


class ResignationListQueryBudgetTests(TestCase):
    def setUp(self):
        self.tenant = make_tenant()
        set_current_tenant(self.tenant)
        self.admin = make_user(self.tenant)
        for _ in range(20):
            Resignation.objects.create(
                tenant=self.tenant,
                employee=make_employee(self.tenant),
                resignation_date=date(2026, 4, 25),
                last_working_day=date(2026, 5, 25),
                reason='r', status='submitted',
            )

    def tearDown(self):
        set_current_tenant(None)

    def test_list_avoids_n_plus_one(self):
        """20 resignations must render in a fixed (not row-proportional) count."""
        self.client.force_login(self.admin)
        with CaptureQueriesContext(connection) as ctx:
            r = self.client.get(reverse('offboarding:resignation_list'))
        self.assertEqual(r.status_code, 200)
        # Currently ~5 with select_related. Cap at 10.
        self.assertLessEqual(
            len(ctx.captured_queries), 10,
            f'Suspected N+1: {len(ctx.captured_queries)} queries (budget 10). '
            'Did select_related drop?',
        )
