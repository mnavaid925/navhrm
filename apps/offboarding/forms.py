from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from .models import (
    Resignation, ExitInterview, ClearanceProcess,
    FnFSettlement, ExperienceLetter
)
from apps.employees.models import Employee
from apps.accounts.models import User


class ResignationForm(forms.ModelForm):
    class Meta:
        model = Resignation
        fields = ['employee', 'resignation_date', 'last_working_day', 'reason']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'resignation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'last_working_day': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant)

    def clean(self):
        cleaned = super().clean()
        res_date = cleaned.get('resignation_date')
        lwd = cleaned.get('last_working_day')
        if res_date and lwd and lwd < res_date:
            self.add_error('last_working_day', 'Last working day must be on or after the resignation date.')
        return cleaned


class ExitInterviewForm(forms.ModelForm):
    class Meta:
        model = ExitInterview
        fields = ['employee', 'interviewer', 'scheduled_date']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'interviewer': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant)
            self.fields['interviewer'].queryset = User.objects.filter(tenant=tenant)


class ExitInterviewFeedbackForm(forms.ModelForm):
    class Meta:
        model = ExitInterview
        fields = [
            'overall_experience', 'reason_for_leaving', 'what_liked',
            'what_disliked', 'would_recommend', 'additional_feedback'
        ]
        widgets = {
            'overall_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
            }),
            'reason_for_leaving': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'what_liked': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'what_disliked': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'would_recommend': forms.Select(
                choices=[('', '---------'), (True, 'Yes'), (False, 'No')],
                attrs={'class': 'form-select'},
            ),
            'additional_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # D-04: enforce 1–5 range server-side; HTML min/max are advisory only.
        self.fields['overall_experience'].validators = [MinValueValidator(1), MaxValueValidator(5)]
        self.fields['overall_experience'].help_text = 'Rating between 1 (poor) and 5 (excellent).'


class ClearanceProcessForm(forms.ModelForm):
    class Meta:
        model = ClearanceProcess
        fields = ['employee', 'initiated_date', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'initiated_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant)


class FnFSettlementForm(forms.ModelForm):
    class Meta:
        model = FnFSettlement
        fields = [
            # Earnings
            'basic_salary', 'pending_salary', 'leave_encashment',
            'bonus', 'gratuity', 'other_earnings',
            # Deductions
            'notice_period_recovery', 'loan_recovery',
            'tax_deduction', 'other_deductions',
            # Meta
            'settlement_date', 'notes',
        ]
        widgets = {
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pending_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'leave_encashment': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bonus': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'gratuity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'other_earnings': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notice_period_recovery': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'loan_recovery': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_deduction': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'other_deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'settlement_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ExperienceLetterForm(forms.ModelForm):
    class Meta:
        model = ExperienceLetter
        fields = ['employee', 'letter_date', 'letter_type', 'content']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'letter_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'letter_type': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant)
