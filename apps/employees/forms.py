from django import forms
from django.db.models import Q
from .models import Employee, EmergencyContact, EmployeeDocument, EmployeeLifecycleEvent
from apps.organization.models import Department, Designation


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'last_name', 'email', 'phone',
            'personal_email', 'date_of_birth', 'gender', 'marital_status',
            'blood_group', 'nationality', 'avatar',
            'address_line1', 'address_line2', 'city', 'state', 'country', 'zip_code',
            'department', 'designation', 'reporting_manager', 'employment_type',
            'date_of_joining', 'probation_end_date', 'status',
            'salary', 'bank_name', 'bank_account', 'ifsc_code'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'personal_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'reporting_manager': forms.Select(attrs={'class': 'form-select'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'date_of_joining': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'probation_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
            'ifsc_code': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._tenant = tenant
        if tenant:
            current_dept_id = getattr(self.instance, 'department_id', None)
            current_desig_id = getattr(self.instance, 'designation_id', None)
            # D-12: hide inactive options but preserve current selection when editing.
            self.fields['department'].queryset = Department.all_objects.filter(
                tenant=tenant
            ).filter(Q(is_active=True) | Q(pk=current_dept_id))
            self.fields['designation'].queryset = Designation.all_objects.filter(
                tenant=tenant
            ).filter(Q(is_active=True) | Q(pk=current_desig_id))
            # D-02: cannot manage yourself; only active managers eligible.
            mgr_qs = Employee.all_objects.filter(tenant=tenant, status='active')
            if self.instance.pk:
                mgr_qs = mgr_qs.exclude(pk=self.instance.pk)
            self.fields['reporting_manager'].queryset = mgr_qs
            self.fields['reporting_manager'].required = False

    def clean_employee_id(self):
        # D-01: tenant is not a form field, so Django's default validate_unique
        # excludes it — duplicates would otherwise hit the DB as a 500.
        eid = self.cleaned_data.get('employee_id')
        if eid and self._tenant:
            qs = Employee.all_objects.filter(tenant=self._tenant, employee_id=eid)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('An employee with this ID already exists in this tenant.')
        return eid

    def clean(self):
        # D-02: prevent reporting-manager cycles (A → B → A).
        cleaned = super().clean()
        manager = cleaned.get('reporting_manager')
        if manager and self.instance.pk:
            seen = {self.instance.pk}
            current = manager
            while current is not None:
                if current.pk in seen:
                    self.add_error('reporting_manager', 'Reporting manager assignment creates a cycle.')
                    break
                seen.add(current.pk)
                current = current.reporting_manager
        return cleaned


class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'relationship', 'phone', 'email', 'address', 'is_primary']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'relationship': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class EmployeeDocumentForm(forms.ModelForm):
    class Meta:
        model = EmployeeDocument
        fields = ['name', 'document_type', 'file', 'document_number', 'issue_date', 'expiry_date', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class LifecycleEventForm(forms.ModelForm):
    class Meta:
        model = EmployeeLifecycleEvent
        fields = ['event_type', 'event_date', 'description', 'from_department',
                  'to_department', 'from_designation', 'to_designation',
                  'old_salary', 'new_salary']
        widgets = {
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'event_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'from_department': forms.Select(attrs={'class': 'form-select'}),
            'to_department': forms.Select(attrs={'class': 'form-select'}),
            'from_designation': forms.Select(attrs={'class': 'form-select'}),
            'to_designation': forms.Select(attrs={'class': 'form-select'}),
            'old_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'new_salary': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['from_department'].queryset = Department.all_objects.filter(tenant=tenant)
            self.fields['to_department'].queryset = Department.all_objects.filter(tenant=tenant)
            self.fields['from_designation'].queryset = Designation.all_objects.filter(tenant=tenant)
            self.fields['to_designation'].queryset = Designation.all_objects.filter(tenant=tenant)
