from datetime import date

from django.db import IntegrityError
from django.test import TestCase

from apps.core.models import set_current_tenant
from apps.employees.models import Employee
from .factories import make_employee, make_tenant


class EmployeeModelTests(TestCase):
    def setUp(self):
        self.tenant = make_tenant()
        set_current_tenant(self.tenant)

    def tearDown(self):
        set_current_tenant(None)

    def test_full_name(self):
        e = make_employee(self.tenant, first_name='Jane', last_name='Doe')
        self.assertEqual(e.full_name, 'Jane Doe')

    def test_get_initials(self):
        e = make_employee(self.tenant, first_name='Jane', last_name='Doe')
        self.assertEqual(e.get_initials(), 'JD')

    def test_str_format(self):
        e = make_employee(self.tenant, first_name='Jane', last_name='Doe', employee_id='E1')
        self.assertEqual(str(e), 'Jane Doe (E1)')

    def test_duplicate_employee_id_within_tenant_rejected(self):
        """D-01 regression: tenant + employee_id must be unique together."""
        make_employee(self.tenant, employee_id='SAME-1')
        with self.assertRaises(IntegrityError):
            Employee.objects.create(
                tenant=self.tenant,
                employee_id='SAME-1',
                first_name='X', last_name='Y', email='xy@e.com',
                date_of_joining=date(2026, 1, 1),
            )

    def test_same_employee_id_across_tenants_allowed(self):
        """Tenant boundary is honoured — duplicates across tenants are fine."""
        other = make_tenant()
        make_employee(self.tenant, employee_id='SHARED')
        # Different tenant, same id — must succeed.
        e2 = Employee.objects.create(
            tenant=other,
            employee_id='SHARED',
            first_name='X', last_name='Y', email='xy@e.com',
            date_of_joining=date(2026, 1, 1),
        )
        self.assertEqual(e2.employee_id, 'SHARED')

    def test_delete_clears_avatar_file(self):
        """D-09 regression: deleting an Employee must not leave its avatar on disk."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        # 1x1 PNG bytes
        png = bytes.fromhex(
            '89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C4'
            '890000000A49444154789C6300010000000500010D0A2DB40000000049454E44AE426082'
        )
        e = make_employee(self.tenant)
        e.avatar.save('a.png', SimpleUploadedFile('a.png', png, 'image/png'), save=True)
        path = e.avatar.path
        from pathlib import Path
        self.assertTrue(Path(path).exists())
        e.delete()
        self.assertFalse(Path(path).exists())
