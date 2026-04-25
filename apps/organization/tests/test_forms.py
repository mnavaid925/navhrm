from django.test import TestCase

from apps.core.models import set_current_tenant
from apps.organization.forms import DepartmentForm
from apps.employees.tests.factories import make_department, make_tenant


class DepartmentFormTests(TestCase):
    def setUp(self):
        self.tenant = make_tenant()
        set_current_tenant(self.tenant)

    def tearDown(self):
        set_current_tenant(None)

    def test_self_excluded_from_parent_choices(self):
        """D-19 regression: a department cannot pick itself as parent."""
        d = make_department(self.tenant)
        form = DepartmentForm(instance=d, tenant=self.tenant)
        self.assertNotIn(d.pk, form.fields['parent'].queryset.values_list('pk', flat=True))

    def test_cycle_rejected_in_clean(self):
        """D-19 regression: A → B → A loop is rejected."""
        a = make_department(self.tenant, name='A')
        b = make_department(self.tenant, name='B', parent=a)
        # Now try to set A.parent = B — would close the loop.
        form = DepartmentForm(
            data={'name': 'A', 'is_active': True, 'parent': b.pk},
            instance=a, tenant=self.tenant,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('parent', form.errors)
