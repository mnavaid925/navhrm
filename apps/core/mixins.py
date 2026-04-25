from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


HR_APPROVAL_ROLES = {'tenant_admin', 'hr_manager', 'hr_staff', 'manager', 'super_admin'}


class HRRoleRequiredMixin(UserPassesTestMixin):
    """Restrict approval/destructive HR actions to privileged roles.

    Allows: tenant admins, HR managers/staff, line managers, super admins.
    Denies: plain employees and any other role.
    """

    raise_exception = False

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser or getattr(user, 'is_tenant_admin', False):
            return True
        return getattr(user, 'role', None) in HR_APPROVAL_ROLES

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'You do not have permission to perform this action.')
            return redirect('dashboard')
        return super().handle_no_permission()
