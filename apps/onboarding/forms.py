from django import forms
from .models import (
    OnboardingProcess, OnboardingTask, OnboardingTemplate,
    AssetAllocation, OrientationSession, WelcomeKit
)
from apps.employees.models import Employee
from apps.organization.models import Department
from apps.accounts.models import User


class OnboardingProcessForm(forms.ModelForm):
    class Meta:
        model = OnboardingProcess
        fields = ['employee', 'template', 'start_date', 'target_completion_date', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'template': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'target_completion_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant)
            self.fields['template'].queryset = OnboardingTemplate.all_objects.filter(
                tenant=tenant, is_active=True
            )


class OnboardingTaskForm(forms.ModelForm):
    class Meta:
        model = OnboardingTask
        fields = ['title', 'description', 'assigned_to', 'due_date', 'is_mandatory']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_mandatory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['assigned_to'].queryset = User.objects.filter(tenant=tenant)


class OnboardingTemplateForm(forms.ModelForm):
    class Meta:
        model = OnboardingTemplate
        fields = ['name', 'description', 'department', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant)


class AssetAllocationForm(forms.ModelForm):
    class Meta:
        model = AssetAllocation
        fields = [
            'employee', 'asset_type', 'asset_name', 'asset_id',
            'serial_number', 'allocated_date', 'notes'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'asset_type': forms.Select(attrs={'class': 'form-select'}),
            'asset_name': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_id': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'allocated_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant)


class OrientationSessionForm(forms.ModelForm):
    class Meta:
        model = OrientationSession
        fields = [
            'title', 'session_type', 'description', 'facilitator',
            'date', 'start_time', 'end_time', 'location', 'employees'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'session_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'facilitator': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'employees': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['facilitator'].queryset = User.objects.filter(tenant=tenant)
            self.fields['employees'].queryset = Employee.all_objects.filter(tenant=tenant)

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_time')
        end = cleaned.get('end_time')
        if start and end and end <= start:
            raise forms.ValidationError("End time must be after start time.")
        return cleaned


class WelcomeKitForm(forms.ModelForm):
    class Meta:
        model = WelcomeKit
        fields = ['name', 'description', 'message', 'policies', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'policies': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
