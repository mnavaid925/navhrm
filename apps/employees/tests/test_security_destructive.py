"""RBAC + IDOR coverage for the destructive Employee/Document endpoints.

Same defect class as D-07: any logged-in tenant user could previously delete
employees and documents. Now gated by HRRoleRequiredMixin.
"""
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.core.models import set_current_tenant
from apps.employees.models import Employee, EmployeeDocument
from .factories import (
    make_employee, make_employee_user, make_tenant, make_user,
)


# 1x1 PNG so the file passes the avatar/document validators.
PNG_BYTES = bytes.fromhex(
    '89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C4'
    '890000000A49444154789C6300010000000500010D0A2DB40000000049454E44AE426082'
)


class EmployeeDeleteRBACTests(TestCase):
    def setUp(self):
        self.tenant = make_tenant()
        set_current_tenant(self.tenant)
        self.target = make_employee(self.tenant)

    def tearDown(self):
        set_current_tenant(None)

    def test_plain_employee_cannot_delete(self):
        plain = make_employee_user(self.tenant)
        self.client.force_login(plain)
        r = self.client.post(reverse('employees:delete', args=[self.target.pk]))
        self.assertTrue(Employee.all_objects.filter(pk=self.target.pk).exists(),
                        'Plain employee must NOT be able to delete employees.')
        self.assertIn(r.status_code, (302, 403))

    def test_tenant_admin_can_delete(self):
        admin = make_user(self.tenant, role='tenant_admin', is_tenant_admin=True)
        self.client.force_login(admin)
        r = self.client.post(reverse('employees:delete', args=[self.target.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Employee.all_objects.filter(pk=self.target.pk).exists())

    def test_other_tenant_delete_404(self):
        admin = make_user(self.tenant, role='tenant_admin', is_tenant_admin=True)
        other = make_tenant()
        other_emp = make_employee(other)
        self.client.force_login(admin)
        r = self.client.post(reverse('employees:delete', args=[other_emp.pk]))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(Employee.all_objects.filter(pk=other_emp.pk).exists())


class DocumentDeleteRBACTests(TestCase):
    def setUp(self):
        self.tenant = make_tenant()
        set_current_tenant(self.tenant)
        self.employee = make_employee(self.tenant)
        self.doc = EmployeeDocument.objects.create(
            tenant=self.tenant, employee=self.employee,
            name='ID', document_type='id_proof',
            file=SimpleUploadedFile('id.png', PNG_BYTES, content_type='image/png'),
        )

    def tearDown(self):
        set_current_tenant(None)

    def test_plain_employee_cannot_delete_document(self):
        plain = make_employee_user(self.tenant)
        self.client.force_login(plain)
        r = self.client.post(reverse('employees:document_delete', args=[self.doc.pk]))
        self.assertTrue(EmployeeDocument.all_objects.filter(pk=self.doc.pk).exists())
        self.assertIn(r.status_code, (302, 403))

    def test_tenant_admin_can_delete_document(self):
        admin = make_user(self.tenant, role='tenant_admin', is_tenant_admin=True)
        self.client.force_login(admin)
        r = self.client.post(reverse('employees:document_delete', args=[self.doc.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(EmployeeDocument.all_objects.filter(pk=self.doc.pk).exists())
