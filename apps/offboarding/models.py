from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from apps.core.models import TenantAwareModel, TimeStampedModel


class Resignation(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='resignations')
    resignation_date = models.DateField()
    last_working_day = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    approved_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_resignations'
    )
    approved_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-resignation_date']

    def __str__(self):
        return f"Resignation - {self.employee} ({self.status})"


class ExitInterview(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='exit_interviews')
    interviewer = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True
    )
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    # Feedback fields
    overall_experience = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating 1-5',
    )
    reason_for_leaving = models.TextField(blank=True)
    what_liked = models.TextField(blank=True, verbose_name='What did you like most?')
    what_disliked = models.TextField(blank=True, verbose_name='What could be improved?')
    would_recommend = models.BooleanField(null=True, blank=True)
    additional_feedback = models.TextField(blank=True)

    class Meta:
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"Exit Interview - {self.employee}"


class ClearanceItem(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL, null=True, blank=True
    )
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class ClearanceProcess(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='clearance_processes')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    initiated_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-initiated_date']

    def __str__(self):
        return f"Clearance - {self.employee}"


class ClearanceChecklistItem(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('cleared', 'Cleared'),
        ('not_applicable', 'Not Applicable'),
    ]

    process = models.ForeignKey(ClearanceProcess, on_delete=models.CASCADE, related_name='checklist_items')
    clearance_item = models.ForeignKey(ClearanceItem, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cleared_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True
    )
    cleared_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['clearance_item__order']

    def __str__(self):
        return f"{self.clearance_item} - {self.process.employee}"


class FnFSettlement(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
    ]

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='fnf_settlements')
    settlement_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Earnings
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    leave_encashment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gratuity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Deductions
    notice_period_recovery = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    loan_recovery = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ['-settlement_date']

    def __str__(self):
        return f"F&F - {self.employee}"

    @property
    def total_earnings(self):
        return (self.basic_salary + self.pending_salary + self.leave_encashment +
                self.bonus + self.gratuity + self.other_earnings)

    @property
    def total_deductions(self):
        return (self.notice_period_recovery + self.loan_recovery +
                self.tax_deduction + self.other_deductions)

    @property
    def net_payable(self):
        return self.total_earnings - self.total_deductions


class ExperienceLetter(TenantAwareModel, TimeStampedModel):
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='experience_letters')
    letter_date = models.DateField()
    letter_type = models.CharField(
        max_length=20,
        choices=[('experience', 'Experience Letter'), ('relieving', 'Relieving Letter')],
        default='experience'
    )
    content = models.TextField()
    generated_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True
    )
    is_issued = models.BooleanField(default=False)

    class Meta:
        ordering = ['-letter_date']

    def __str__(self):
        return f"{self.get_letter_type_display()} - {self.employee}"
