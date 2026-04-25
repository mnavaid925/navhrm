"""RBAC + IDOR coverage for the linter-added Onboarding delete endpoints."""
from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.core.models import set_current_tenant
from apps.employees.tests.factories import (
    make_employee, make_employee_user, make_tenant, make_user,
)
from apps.onboarding.models import (
    AssetAllocation, OnboardingProcess, OnboardingTemplate,
    OrientationSession, WelcomeKit,
)


class OnboardingDeleteRBACTests(TestCase):
    """Each delete URL: plain employee blocked, admin allowed, cross-tenant 404."""

    def setUp(self):
        self.tenant = make_tenant()
        set_current_tenant(self.tenant)
        self.admin = make_user(self.tenant, role='tenant_admin', is_tenant_admin=True)
        self.plain = make_employee_user(self.tenant)
        self.employee = make_employee(self.tenant)

    def tearDown(self):
        set_current_tenant(None)

    def _check_rbac(self, url_name, args, model, lookup_kwargs):
        """Helper: plain employee gets blocked, admin succeeds."""
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

    def test_onboarding_process_delete(self):
        proc = OnboardingProcess.objects.create(
            tenant=self.tenant, employee=self.employee, status='pending',
            start_date=date(2026, 5, 1),
        )
        self._check_rbac('onboarding:delete', [proc.pk], OnboardingProcess, {'pk': proc.pk})

    def test_template_delete(self):
        tmpl = OnboardingTemplate.objects.create(tenant=self.tenant, name='Std', is_active=True)
        self._check_rbac('onboarding:template_delete', [tmpl.pk], OnboardingTemplate, {'pk': tmpl.pk})

    def test_asset_delete(self):
        asset = AssetAllocation.objects.create(
            tenant=self.tenant, employee=self.employee, asset_type='laptop',
            asset_name='Dell XPS', allocated_date=date(2026, 5, 1),
        )
        self._check_rbac('onboarding:asset_delete', [asset.pk], AssetAllocation, {'pk': asset.pk})

    def test_orientation_delete(self):
        from datetime import time
        sess = OrientationSession.objects.create(
            tenant=self.tenant, title='Welcome', session_type='presentation',
            date=date(2026, 5, 1), start_time=time(9, 0), end_time=time(10, 0),
        )
        self._check_rbac('onboarding:orientation_delete', [sess.pk], OrientationSession, {'pk': sess.pk})

    def test_welcomekit_delete(self):
        kit = WelcomeKit.objects.create(tenant=self.tenant, name='Std', is_active=True)
        self._check_rbac('onboarding:welcomekit_delete', [kit.pk], WelcomeKit, {'pk': kit.pk})

    def test_cross_tenant_delete_returns_404(self):
        other = make_tenant()
        other_proc = OnboardingProcess.objects.create(
            tenant=other, employee=make_employee(other), status='pending',
            start_date=date(2026, 5, 1),
        )
        self.client.force_login(self.admin)
        r = self.client.post(reverse('onboarding:delete', args=[other_proc.pk]))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(OnboardingProcess.all_objects.filter(pk=other_proc.pk).exists())
