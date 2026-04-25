from django.urls import path
from . import views

app_name = 'onboarding'

urlpatterns = [
    path('', views.OnboardingListView.as_view(), name='list'),
    path('create/<int:employee_id>/', views.OnboardingCreateView.as_view(), name='create'),
    path('<int:pk>/', views.OnboardingDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', views.OnboardingDeleteView.as_view(), name='delete'),
    path('<int:pk>/task/<int:task_id>/update/', views.TaskUpdateView.as_view(), name='task_update'),
    # Templates
    path('templates/', views.TemplateListView.as_view(), name='template_list'),
    path('templates/create/', views.TemplateCreateView.as_view(), name='template_create'),
    path('templates/<int:pk>/edit/', views.TemplateUpdateView.as_view(), name='template_edit'),
    path('templates/<int:pk>/delete/', views.TemplateDeleteView.as_view(), name='template_delete'),
    # Assets
    path('assets/', views.AssetListView.as_view(), name='asset_list'),
    path('assets/allocate/', views.AssetAllocateView.as_view(), name='asset_allocate'),
    path('assets/<int:pk>/return/', views.AssetReturnView.as_view(), name='asset_return'),
    path('assets/<int:pk>/delete/', views.AssetDeleteView.as_view(), name='asset_delete'),
    # Orientation
    path('orientation/', views.OrientationListView.as_view(), name='orientation_list'),
    path('orientation/create/', views.OrientationCreateView.as_view(), name='orientation_create'),
    path('orientation/<int:pk>/edit/', views.OrientationUpdateView.as_view(), name='orientation_edit'),
    path('orientation/<int:pk>/delete/', views.OrientationDeleteView.as_view(), name='orientation_delete'),
    # Welcome Kit
    path('welcome-kits/', views.WelcomeKitListView.as_view(), name='welcomekit_list'),
    path('welcome-kits/create/', views.WelcomeKitCreateView.as_view(), name='welcomekit_create'),
    path('welcome-kits/<int:pk>/edit/', views.WelcomeKitUpdateView.as_view(), name='welcomekit_edit'),
    path('welcome-kits/<int:pk>/delete/', views.WelcomeKitDeleteView.as_view(), name='welcomekit_delete'),
]
