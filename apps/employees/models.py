from django.db import models
from apps.core.models import TenantAwareModel, TimeStampedModel
from apps.core.validators import (
    document_extension_validator,
    image_extension_validator,
    validate_avatar_size,
    validate_document_size,
)


class Employee(TenantAwareModel, TimeStampedModel):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    MARITAL_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
        ('freelance', 'Freelance'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('suspended', 'Suspended'),
        ('terminated', 'Terminated'),
        ('resigned', 'Resigned'),
        ('retired', 'Retired'),
    ]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    user = models.OneToOneField(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='employee'
    )
    employee_id = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    personal_email = models.EmailField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_CHOICES, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(
        upload_to='employees/avatars/', blank=True, null=True,
        validators=[image_extension_validator, validate_avatar_size],
    )

    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)

    # Employment
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='employees'
    )
    designation = models.ForeignKey(
        'organization.Designation', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='employees'
    )
    reporting_manager = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='direct_reports'
    )
    employment_type = models.CharField(
        max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time'
    )
    date_of_joining = models.DateField()
    date_of_leaving = models.DateField(null=True, blank=True)
    probation_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Salary
    salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bank_name = models.CharField(max_length=255, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['first_name', 'last_name']
        unique_together = [('tenant', 'employee_id')]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    def delete(self, *args, **kwargs):
        # D-09: clear FileField storage on delete to avoid orphaning media files.
        if self.avatar:
            self.avatar.delete(save=False)
        return super().delete(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_initials(self):
        return f"{self.first_name[0]}{self.last_name[0]}".upper()


class EmergencyContact(TenantAwareModel, TimeStampedModel):
    RELATIONSHIP_CHOICES = [
        ('spouse', 'Spouse'),
        ('parent', 'Parent'),
        ('sibling', 'Sibling'),
        ('child', 'Child'),
        ('friend', 'Friend'),
        ('other', 'Other'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_primary', 'name']

    def __str__(self):
        return f"{self.name} ({self.relationship}) - {self.employee}"


class EmployeeDocument(TenantAwareModel, TimeStampedModel):
    DOCUMENT_TYPES = [
        ('id_proof', 'ID Proof'),
        ('address_proof', 'Address Proof'),
        ('education', 'Education Certificate'),
        ('experience', 'Experience Letter'),
        ('contract', 'Employment Contract'),
        ('nda', 'NDA'),
        ('offer_letter', 'Offer Letter'),
        ('other', 'Other'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(
        upload_to='employees/documents/',
        validators=[document_extension_validator, validate_document_size],
    )
    document_number = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.employee}"

    def delete(self, *args, **kwargs):
        # D-09: remove the underlying file when the row is deleted (incl. CASCADE).
        if self.file:
            self.file.delete(save=False)
        return super().delete(*args, **kwargs)


class EmployeeLifecycleEvent(TenantAwareModel, TimeStampedModel):
    EVENT_TYPES = [
        ('hired', 'Hired'),
        ('promoted', 'Promoted'),
        ('transferred', 'Transferred'),
        ('demoted', 'Demoted'),
        ('salary_revision', 'Salary Revision'),
        ('suspended', 'Suspended'),
        ('resumed', 'Resumed'),
        ('resigned', 'Resigned'),
        ('terminated', 'Terminated'),
        ('retired', 'Retired'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='lifecycle_events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    event_date = models.DateField()
    description = models.TextField(blank=True)

    # For transfers/promotions
    from_department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transfer_from_events'
    )
    to_department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transfer_to_events'
    )
    from_designation = models.ForeignKey(
        'organization.Designation', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='promotion_from_events'
    )
    to_designation = models.ForeignKey(
        'organization.Designation', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='promotion_to_events'
    )
    old_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    new_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    processed_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ['-event_date']

    def __str__(self):
        return f"{self.employee} - {self.get_event_type_display()} ({self.event_date})"
