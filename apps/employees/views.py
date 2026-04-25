from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView
from django.db.models import Q

from .models import Employee, EmergencyContact, EmployeeDocument, EmployeeLifecycleEvent
from .forms import EmployeeForm, EmergencyContactForm, EmployeeDocumentForm, LifecycleEventForm
from apps.core.mixins import HRRoleRequiredMixin
from apps.organization.models import Department


# ---------------------------------------------------------------------------
# Employee Directory (list)
# ---------------------------------------------------------------------------

class EmployeeDirectoryView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/directory.html'
    context_object_name = 'employees'
    paginate_by = 20

    def get_queryset(self):
        qs = Employee.objects.filter(tenant=self.request.tenant)

        # Search
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(department__name__icontains=search)
            )

        # Filters
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)

        department = self.request.GET.get('department', '')
        if department:
            qs = qs.filter(department_id=department)

        employment_type = self.request.GET.get('employment_type', '')
        if employment_type:
            qs = qs.filter(employment_type=employment_type)

        return qs.select_related('department', 'designation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_department'] = self.request.GET.get('department', '')
        context['current_employment_type'] = self.request.GET.get('employment_type', '')
        context['departments'] = Department.objects.filter(tenant=self.request.tenant, is_active=True)
        context['status_choices'] = Employee.STATUS_CHOICES
        context['employment_type_choices'] = Employee.EMPLOYMENT_TYPE_CHOICES
        return context


# ---------------------------------------------------------------------------
# Employee Create
# ---------------------------------------------------------------------------

class EmployeeCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = EmployeeForm(tenant=request.tenant)
        return render(request, 'employees/form.html', {
            'form': form,
            'title': 'Add Employee',
        })

    def post(self, request):
        form = EmployeeForm(request.POST, request.FILES, tenant=request.tenant)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.tenant = request.tenant
            employee.save()
            messages.success(request, f'Employee {employee.full_name} created successfully.')
            return redirect('employees:detail', pk=employee.pk)
        return render(request, 'employees/form.html', {
            'form': form,
            'title': 'Add Employee',
        })


# ---------------------------------------------------------------------------
# Employee Detail (tabbed: personal, employment, documents, lifecycle)
# ---------------------------------------------------------------------------

class EmployeeDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        employee = get_object_or_404(
            Employee.objects.select_related('department', 'designation', 'reporting_manager'),
            pk=pk,
            tenant=request.tenant,
        )
        emergency_contacts = employee.emergency_contacts.all()
        documents = employee.documents.all()
        lifecycle_events = employee.lifecycle_events.select_related(
            'from_department', 'to_department', 'from_designation', 'to_designation',
        ).all()

        # Emergency contact form for inline add
        contact_form = EmergencyContactForm()

        # Active tab
        tab = request.GET.get('tab', 'personal')

        return render(request, 'employees/detail.html', {
            'employee': employee,
            'emergency_contacts': emergency_contacts,
            'documents': documents,
            'lifecycle_events': lifecycle_events,
            'contact_form': contact_form,
            'active_tab': tab,
        })

    def post(self, request, pk):
        """Handle inline emergency-contact creation from the detail page."""
        employee = get_object_or_404(Employee, pk=pk, tenant=request.tenant)
        contact_form = EmergencyContactForm(request.POST)
        if contact_form.is_valid():
            contact = contact_form.save(commit=False)
            contact.employee = employee
            contact.tenant = request.tenant
            contact.save()
            messages.success(request, f'Emergency contact {contact.name} added.')
            return redirect(f"{request.path}?tab=personal")

        # Re-render with errors
        emergency_contacts = employee.emergency_contacts.all()
        documents = employee.documents.all()
        lifecycle_events = employee.lifecycle_events.select_related(
            'from_department', 'to_department', 'from_designation', 'to_designation',
        ).all()
        return render(request, 'employees/detail.html', {
            'employee': employee,
            'emergency_contacts': emergency_contacts,
            'documents': documents,
            'lifecycle_events': lifecycle_events,
            'contact_form': contact_form,
            'active_tab': 'personal',
        })


# ---------------------------------------------------------------------------
# Employee Update
# ---------------------------------------------------------------------------

class EmployeeUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk, tenant=request.tenant)
        form = EmployeeForm(instance=employee, tenant=request.tenant)
        return render(request, 'employees/form.html', {
            'form': form,
            'employee': employee,
            'title': 'Edit Employee',
        })

    def post(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk, tenant=request.tenant)
        form = EmployeeForm(request.POST, request.FILES, instance=employee, tenant=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Employee {employee.full_name} updated successfully.')
            return redirect('employees:detail', pk=employee.pk)
        return render(request, 'employees/form.html', {
            'form': form,
            'employee': employee,
            'title': 'Edit Employee',
        })


# ---------------------------------------------------------------------------
# Employee Delete (POST only)
# ---------------------------------------------------------------------------

class EmployeeDeleteView(HRRoleRequiredMixin, LoginRequiredMixin, View):
    def post(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk, tenant=request.tenant)
        name = employee.full_name
        employee.delete()
        messages.success(request, f'Employee {name} deleted successfully.')
        return redirect('employees:directory')


# ---------------------------------------------------------------------------
# Employee Documents (list)
# ---------------------------------------------------------------------------

class EmployeeDocumentsView(LoginRequiredMixin, View):
    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk, tenant=request.tenant)
        documents = employee.documents.all()
        upload_form = EmployeeDocumentForm()
        return render(request, 'employees/documents.html', {
            'employee': employee,
            'documents': documents,
            'form': upload_form,
        })


# ---------------------------------------------------------------------------
# Document Upload
# ---------------------------------------------------------------------------

class DocumentUploadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk, tenant=request.tenant)
        form = EmployeeDocumentForm()
        return render(request, 'employees/documents.html', {
            'employee': employee,
            'documents': employee.documents.all(),
            'form': form,
        })

    def post(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk, tenant=request.tenant)
        form = EmployeeDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.employee = employee
            document.tenant = request.tenant
            document.save()
            messages.success(request, f'Document "{document.name}" uploaded successfully.')
            return redirect('employees:documents', pk=employee.pk)
        # Re-render with errors
        return render(request, 'employees/documents.html', {
            'employee': employee,
            'documents': employee.documents.all(),
            'form': form,
        })


# ---------------------------------------------------------------------------
# Document Delete (POST only)
# ---------------------------------------------------------------------------

class DocumentDeleteView(HRRoleRequiredMixin, LoginRequiredMixin, View):
    def post(self, request, pk):
        document = get_object_or_404(EmployeeDocument, pk=pk, tenant=request.tenant)
        employee_pk = document.employee_id
        name = document.name
        document.delete()
        messages.success(request, f'Document "{name}" deleted successfully.')
        return redirect('employees:documents', pk=employee_pk)


# ---------------------------------------------------------------------------
# Employee Lifecycle Events (list)
# ---------------------------------------------------------------------------

class EmployeeLifecycleView(LoginRequiredMixin, View):
    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk, tenant=request.tenant)
        events = employee.lifecycle_events.select_related(
            'from_department', 'to_department', 'from_designation', 'to_designation', 'processed_by',
        ).all()
        return render(request, 'employees/lifecycle.html', {
            'employee': employee,
            'events': events,
        })


# ---------------------------------------------------------------------------
# Lifecycle Event Create
# ---------------------------------------------------------------------------

class LifecycleEventCreateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk, tenant=request.tenant)
        form = LifecycleEventForm(tenant=request.tenant)
        return render(request, 'employees/lifecycle.html', {
            'employee': employee,
            'events': employee.lifecycle_events.select_related(
                'from_department', 'to_department', 'from_designation', 'to_designation', 'processed_by',
            ).all(),
            'form': form,
        })

    def post(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk, tenant=request.tenant)
        form = LifecycleEventForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            event = form.save(commit=False)
            event.employee = employee
            event.tenant = request.tenant
            event.processed_by = request.user
            event.save()
            messages.success(
                request,
                f'Lifecycle event "{event.get_event_type_display()}" recorded for {employee.full_name}.',
            )
            return redirect('employees:lifecycle', pk=employee.pk)
        # Re-render with errors
        return render(request, 'employees/lifecycle.html', {
            'employee': employee,
            'events': employee.lifecycle_events.select_related(
                'from_department', 'to_department', 'from_designation', 'to_designation', 'processed_by',
            ).all(),
            'form': form,
        })
