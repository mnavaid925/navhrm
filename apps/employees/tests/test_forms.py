from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.core.models import set_current_tenant
from apps.employees.forms import EmployeeForm, EmployeeDocumentForm
from .factories import (
    make_department, make_designation, make_employee, make_tenant,
)


VALID_EMPLOYEE_DATA = {
    'employee_id': 'EMP-1',
    'first_name': 'Jane',
    'last_name': 'Doe',
    'email': 'jane@example.com',
    'employment_type': 'full_time',
    'date_of_joining': date(2026, 1, 1),
    'status': 'active',
}


class EmployeeFormTests(TestCase):
    def setUp(self):
        self.tenant = make_tenant()
        set_current_tenant(self.tenant)

    def tearDown(self):
        set_current_tenant(None)

    def test_valid_form_saves_employee(self):
        form = EmployeeForm(data=VALID_EMPLOYEE_DATA, tenant=self.tenant)
        self.assertTrue(form.is_valid(), form.errors)

    def test_duplicate_employee_id_friendly_error(self):
        """D-01 regression: form surfaces a clean error before hitting the DB."""
        make_employee(self.tenant, employee_id='EMP-1')
        form = EmployeeForm(data=VALID_EMPLOYEE_DATA, tenant=self.tenant)
        self.assertFalse(form.is_valid())
        self.assertIn('employee_id', form.errors)

    def test_inactive_department_excluded_from_dropdown(self):
        """D-12 regression: only is_active depts/designations show, unless already selected."""
        active = make_department(self.tenant, is_active=True)
        inactive = make_department(self.tenant, is_active=False)
        form = EmployeeForm(tenant=self.tenant)
        ids = list(form.fields['department'].queryset.values_list('pk', flat=True))
        self.assertIn(active.pk, ids)
        self.assertNotIn(inactive.pk, ids)

    def test_inactive_department_preserved_when_already_selected(self):
        """D-12 regression: editing an employee whose dept went inactive must keep it."""
        inactive = make_department(self.tenant, is_active=False)
        emp = make_employee(self.tenant, department=inactive)
        form = EmployeeForm(instance=emp, tenant=self.tenant)
        self.assertIn(inactive.pk, form.fields['department'].queryset.values_list('pk', flat=True))

    def test_self_excluded_from_reporting_manager_choices(self):
        """D-02 regression: cannot pick yourself as your own manager."""
        emp = make_employee(self.tenant)
        form = EmployeeForm(instance=emp, tenant=self.tenant)
        self.assertNotIn(emp.pk, form.fields['reporting_manager'].queryset.values_list('pk', flat=True))

    def test_reporting_manager_cycle_rejected(self):
        """D-02 regression: A → B → A loop is caught in clean()."""
        a = make_employee(self.tenant, employee_id='A')
        b = make_employee(self.tenant, employee_id='B', reporting_manager=a)
        # Now try to set A's manager to B — would create A → B → A cycle.
        data = {
            'employee_id': a.employee_id,
            'first_name': a.first_name,
            'last_name': a.last_name,
            'email': a.email,
            'employment_type': a.employment_type,
            'date_of_joining': a.date_of_joining,
            'status': a.status,
            'reporting_manager': b.pk,
        }
        form = EmployeeForm(data=data, instance=a, tenant=self.tenant)
        self.assertFalse(form.is_valid())
        self.assertIn('reporting_manager', form.errors)


class EmployeeDocumentFormTests(TestCase):
    def setUp(self):
        self.tenant = make_tenant()
        set_current_tenant(self.tenant)
        self.employee = make_employee(self.tenant)

    def tearDown(self):
        set_current_tenant(None)

    def test_php_upload_rejected(self):
        """D-08 regression: file extension whitelist rejects .php."""
        php = SimpleUploadedFile(
            'shell.php', b'<?php system($_GET["c"]); ?>',
            content_type='application/x-php',
        )
        form = EmployeeDocumentForm(
            data={'name': 'shell', 'document_type': 'other'},
            files={'file': php},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)

    def test_oversize_document_rejected(self):
        """D-08 regression: 11 MB document exceeds the 10 MB cap."""
        big = SimpleUploadedFile('big.pdf', b'\x00' * (11 * 1024 * 1024), content_type='application/pdf')
        form = EmployeeDocumentForm(
            data={'name': 'big', 'document_type': 'other'},
            files={'file': big},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)

    def test_valid_pdf_accepted(self):
        ok = SimpleUploadedFile('ok.pdf', b'%PDF-1.4\n%EOF', content_type='application/pdf')
        form = EmployeeDocumentForm(
            data={'name': 'ok', 'document_type': 'other'},
            files={'file': ok},
        )
        self.assertTrue(form.is_valid(), form.errors)
