from django.db import models
from apps.core.models import TenantAwareModel, TimeStampedModel
from apps.core.validators import image_extension_validator, validate_logo_size


class Company(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    logo = models.ImageField(
        upload_to='companies/logos/', blank=True, null=True,
        validators=[image_extension_validator, validate_logo_size],
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    founded_date = models.DateField(null=True, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Companies'
        ordering = ['name']

    def __str__(self):
        return self.name


class Location(TenantAwareModel, TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=255)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_headquarters = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.city}"


class Department(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='children'
    )
    head = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='headed_departments'
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='departments',
        null=True, blank=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def employee_count(self):
        return self.employees.filter(status='active').count()


class JobGrade(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    level = models.PositiveIntegerField(default=1)
    min_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['level']

    def __str__(self):
        return f"{self.name} (Level {self.level})"


class Designation(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='designations'
    )
    job_grade = models.ForeignKey(
        JobGrade, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='designations'
    )
    description = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CostCenter(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='cost_centers'
    )
    budget = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    spent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def remaining_budget(self):
        return self.budget - self.spent

    @property
    def utilization_percentage(self):
        if self.budget > 0:
            return round((self.spent / self.budget) * 100, 2)
        return 0
