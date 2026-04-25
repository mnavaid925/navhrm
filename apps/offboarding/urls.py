from django.urls import path
from . import views

app_name = 'offboarding'

urlpatterns = [
    # Resignations
    path('resignations/', views.ResignationListView.as_view(), name='resignation_list'),
    path('resignations/submit/', views.ResignationCreateView.as_view(), name='resignation_submit'),
    path('resignations/<int:pk>/', views.ResignationDetailView.as_view(), name='resignation_detail'),
    path('resignations/<int:pk>/approve/', views.ResignationApproveView.as_view(), name='resignation_approve'),
    path('resignations/<int:pk>/delete/', views.ResignationDeleteView.as_view(), name='resignation_delete'),
    # Exit Interviews
    path('exit-interviews/', views.ExitInterviewListView.as_view(), name='exitinterview_list'),
    path('exit-interviews/schedule/', views.ExitInterviewCreateView.as_view(), name='exitinterview_schedule'),
    path('exit-interviews/<int:pk>/', views.ExitInterviewDetailView.as_view(), name='exitinterview_detail'),
    path('exit-interviews/<int:pk>/feedback/', views.ExitInterviewFeedbackView.as_view(), name='exitinterview_feedback'),
    path('exit-interviews/<int:pk>/delete/', views.ExitInterviewDeleteView.as_view(), name='exitinterview_delete'),
    # Clearance
    path('clearance/', views.ClearanceListView.as_view(), name='clearance_list'),
    path('clearance/initiate/<int:employee_id>/', views.ClearanceInitiateView.as_view(), name='clearance_initiate'),
    path('clearance/<int:pk>/', views.ClearanceDetailView.as_view(), name='clearance_detail'),
    path('clearance/<int:pk>/delete/', views.ClearanceDeleteView.as_view(), name='clearance_delete'),
    # F&F
    path('settlements/', views.FnFListView.as_view(), name='fnf_list'),
    path('settlements/create/<int:employee_id>/', views.FnFCreateView.as_view(), name='fnf_create'),
    path('settlements/<int:pk>/', views.FnFDetailView.as_view(), name='fnf_detail'),
    path('settlements/<int:pk>/delete/', views.FnFDeleteView.as_view(), name='fnf_delete'),
    # Experience Letters
    path('letters/', views.ExperienceLetterListView.as_view(), name='letter_list'),
    path('letters/generate/<int:employee_id>/', views.ExperienceLetterGenerateView.as_view(), name='letter_generate'),
    path('letters/<int:pk>/', views.ExperienceLetterDetailView.as_view(), name='letter_detail'),
    path('letters/<int:pk>/delete/', views.ExperienceLetterDeleteView.as_view(), name='letter_delete'),
]
