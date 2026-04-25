from django.test import TestCase
from django.urls import reverse

from .factories import make_employee, make_tenant, make_user


class EmployeeDirectoryTests(TestCase):
    def setUp(self):
        self.tenant = make_tenant()
        self.other_tenant = make_tenant()
        self.admin = make_user(self.tenant, username='admin1')

    def test_anonymous_redirected_to_login(self):
        r = self.client.get(reverse('employees:directory'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/login', r.url)

    def test_only_own_tenant_employees_listed(self):
        make_employee(self.tenant, first_name='Mine', last_name='Own')
        make_employee(self.other_tenant, first_name='Theirs', last_name='Other')
        self.client.force_login(self.admin)
        r = self.client.get(reverse('employees:directory'))
        body = r.content.decode()
        self.assertIn('Mine', body)
        self.assertNotIn('Theirs', body)

    def test_search_by_partial_name(self):
        make_employee(self.tenant, first_name='Alice', last_name='Wonder')
        make_employee(self.tenant, first_name='Bob', last_name='Smith')
        self.client.force_login(self.admin)
        r = self.client.get(reverse('employees:directory') + '?search=Won')
        body = r.content.decode()
        self.assertIn('Alice', body)
        self.assertNotIn('Bob', body)


class EmployeeIDORTests(TestCase):
    """OWASP A01: cross-tenant access must 404."""

    def setUp(self):
        self.tenant = make_tenant()
        self.other_tenant = make_tenant()
        self.admin = make_user(self.tenant)
        self.other_emp = make_employee(self.other_tenant)
        self.client.force_login(self.admin)

    def test_other_tenant_detail_404(self):
        r = self.client.get(reverse('employees:detail', args=[self.other_emp.pk]))
        self.assertEqual(r.status_code, 404)

    def test_other_tenant_edit_404(self):
        r = self.client.get(reverse('employees:edit', args=[self.other_emp.pk]))
        self.assertEqual(r.status_code, 404)

    def test_other_tenant_delete_404(self):
        r = self.client.post(reverse('employees:delete', args=[self.other_emp.pk]))
        self.assertEqual(r.status_code, 404)


class EmployeeXSSTests(TestCase):
    """OWASP A03: user-supplied text rendered in templates is escaped."""

    def test_first_name_xss_escaped_in_directory(self):
        tenant = make_tenant()
        admin = make_user(tenant)
        make_employee(tenant, first_name='<script>alert(1)</script>', last_name='Y')
        self.client.force_login(admin)
        r = self.client.get(reverse('employees:directory'))
        body = r.content.decode()
        self.assertNotIn('<script>alert(1)</script>', body)
        self.assertIn('&lt;script&gt;', body)
