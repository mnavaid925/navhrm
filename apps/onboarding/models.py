from django.db import models
from apps.core.models import TenantAwareModel, TimeStampedModel


class OnboardingTemplate(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class OnboardingTemplateTask(TenantAwareModel, TimeStampedModel):
    template = models.ForeignKey(OnboardingTemplate, on_delete=models.CASCADE, related_name='template_tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_role = models.CharField(max_length=20, blank=True)
    days_before_joining = models.IntegerField(default=0)
    days_after_joining = models.IntegerField(default=0)
    is_mandatory = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class OnboardingProcess(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='onboarding_processes')
    template = models.ForeignKey(OnboardingTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField()
    target_completion_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Onboarding - {self.employee}"

    @property
    def progress_percentage(self):
        # D-10: prefer annotated counts when the queryset provides them, so list
        # views don't issue 2 extra COUNT queries per row.
        total = getattr(self, 'total_tasks_count', None)
        if total is None:
            total = self.tasks.count()
        if total == 0:
            return 0
        completed = getattr(self, 'completed_tasks_count', None)
        if completed is None:
            completed = self.tasks.filter(status='completed').count()
        return round((completed / total) * 100)


class OnboardingTask(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]

    process = models.ForeignKey(OnboardingProcess, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    is_mandatory = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class AssetAllocation(TenantAwareModel, TimeStampedModel):
    ASSET_TYPES = [
        ('laptop', 'Laptop'),
        ('desktop', 'Desktop'),
        ('phone', 'Phone'),
        ('id_card', 'ID Card'),
        ('access_card', 'Access Card'),
        ('key', 'Key'),
        ('vehicle', 'Vehicle'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('allocated', 'Allocated'),
        ('returned', 'Returned'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ]

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='assets')
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    asset_name = models.CharField(max_length=255)
    asset_id = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    allocated_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='allocated')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-allocated_date']

    def __str__(self):
        return f"{self.asset_name} - {self.employee}"


class OrientationSession(TenantAwareModel, TimeStampedModel):
    SESSION_TYPES = [
        ('training', 'Training'),
        ('meet_greet', 'Meet & Greet'),
        ('tour', 'Office Tour'),
        ('presentation', 'Presentation'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    description = models.TextField(blank=True)
    facilitator = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255, blank=True)
    employees = models.ManyToManyField('employees.Employee', related_name='orientation_sessions', blank=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return self.title


class WelcomeKit(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    message = models.TextField(blank=True)
    policies = models.TextField(blank=True, help_text='Company policies to share')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
