from django import forms
from .models import Company, Location, Department, Designation, JobGrade, CostCenter


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'legal_name', 'registration_number', 'tax_id', 'logo',
                  'email', 'phone', 'website', 'address_line1', 'address_line2',
                  'city', 'state', 'country', 'zip_code', 'founded_date',
                  'industry', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'legal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'founded_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'description', 'parent', 'company', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            parent_qs = Department.all_objects.filter(tenant=tenant)
            if self.instance.pk:
                parent_qs = parent_qs.exclude(pk=self.instance.pk)
            self.fields['parent'].queryset = parent_qs
            self.fields['company'].queryset = Company.all_objects.filter(tenant=tenant)

    def clean_parent(self):
        parent = self.cleaned_data.get('parent')
        if parent and self.instance.pk:
            if parent.pk == self.instance.pk:
                raise forms.ValidationError("A department cannot be its own parent.")
            ancestor = parent
            while ancestor is not None:
                if ancestor.pk == self.instance.pk:
                    raise forms.ValidationError("Circular hierarchy: this parent is already a descendant of the current department.")
                ancestor = ancestor.parent
        return parent


class DesignationForm(forms.ModelForm):
    class Meta:
        model = Designation
        fields = ['name', 'code', 'department', 'job_grade', 'description', 'responsibilities', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'job_grade': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant)
            self.fields['job_grade'].queryset = JobGrade.all_objects.filter(tenant=tenant)


class CostCenterForm(forms.ModelForm):
    class Meta:
        model = CostCenter
        fields = ['name', 'code', 'description', 'department', 'budget', 'spent', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'spent': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant)
