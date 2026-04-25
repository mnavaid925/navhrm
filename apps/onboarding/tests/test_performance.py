"""Query-budget tests for the onboarding list view (D-10)."""
from datetime import date

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from apps.core.models import set_current_tenant
from apps.employees.tests.factories import make_employee, make_tenant, make_user
from apps.onboarding.models import OnboardingProcess, OnboardingTask, OnboardingTemplate


class OnboardingListQueryBudgetTests(TestCase):
    def setUp(self):
        self.tenant = make_tenant()
        set_current_tenant(self.tenant)
        self.admin = make_user(self.tenant)
        tmpl = OnboardingTemplate.objects.create(
            tenant=self.tenant, name='Std', is_active=True,
        )
        # 20 processes, each with 3 tasks, mix of statuses, so progress_percentage
        # has real work to do. Without the annotation fix, this is ~100 queries.
        for _ in range(20):
            proc = OnboardingProcess.objects.create(
                tenant=self.tenant,
                employee=make_employee(self.tenant),
                template=tmpl,
                status='pending',
                start_date=date(2026, 5, 1),
            )
            for status in ('pending', 'in_progress', 'completed'):
                OnboardingTask.objects.create(
                    tenant=self.tenant, process=proc,
                    title=f'Task-{status}', status=status,
                )

    def tearDown(self):
        set_current_tenant(None)

    def test_list_avoids_n_plus_one(self):
        """progress_percentage must use annotated counts, not run COUNT() per row."""
        self.client.force_login(self.admin)
        with CaptureQueriesContext(connection) as ctx:
            r = self.client.get(reverse('onboarding:list'))
        self.assertEqual(r.status_code, 200)
        # Without the annotation, was ~105 queries. With it: ~5.
        self.assertLessEqual(
            len(ctx.captured_queries), 10,
            f'Suspected N+1: {len(ctx.captured_queries)} queries. Did the queryset '
            'lose total_tasks_count / completed_tasks_count annotations?',
        )
