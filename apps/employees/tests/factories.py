"""Tiny test-data helpers for the Core HR test suite.

Plain factory functions instead of factory-boy — we don't want to add a
runtime dependency to requirements.txt for tests.
"""
from datetime import date

from django.contrib.auth import get_user_model

from apps.core.models import Tenant
from apps.employees.models import Employee
from apps.organization.models import Company, Department, Designation


User = get_user_model()


_seq = 0


def _next():
    global _seq
    _seq += 1
    return _seq


def make_tenant(**kwargs):
    n = _next()
    kwargs.setdefault('name', f'Tenant {n}')
    kwargs.setdefault('slug', f'tenant-{n}')
    return Tenant.objects.create(**kwargs)


def make_user(tenant, *, role='tenant_admin', is_tenant_admin=True, **kwargs):
    n = _next()
    kwargs.setdefault('username', f'user{n}')
    user = User.objects.create_user(
        password='pwd123',
        tenant=tenant,
        role=role,
        is_tenant_admin=is_tenant_admin,
        **kwargs,
    )
    return user


def make_employee_user(tenant, **kwargs):
    return make_user(tenant, role='employee', is_tenant_admin=False, **kwargs)


def make_company(tenant, **kwargs):
    n = _next()
    kwargs.setdefault('name', f'Company {n}')
    return Company.objects.create(tenant=tenant, **kwargs)


def make_department(tenant, **kwargs):
    n = _next()
    kwargs.setdefault('name', f'Dept {n}')
    kwargs.setdefault('is_active', True)
    return Department.objects.create(tenant=tenant, **kwargs)


def make_designation(tenant, **kwargs):
    n = _next()
    kwargs.setdefault('name', f'Role {n}')
    kwargs.setdefault('is_active', True)
    return Designation.objects.create(tenant=tenant, **kwargs)


def make_employee(tenant, **kwargs):
    n = _next()
    kwargs.setdefault('employee_id', f'EMP-{n:04d}')
    kwargs.setdefault('first_name', f'First{n}')
    kwargs.setdefault('last_name', f'Last{n}')
    kwargs.setdefault('email', f'emp{n}@example.com')
    kwargs.setdefault('date_of_joining', date(2026, 1, 1))
    kwargs.setdefault('employment_type', 'full_time')
    kwargs.setdefault('status', 'active')
    return Employee.objects.create(tenant=tenant, **kwargs)
