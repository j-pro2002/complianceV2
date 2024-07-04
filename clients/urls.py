# Dans complaints/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_complaint, name='home_complaint'),
    path('complaint', views.complaint_list, name='complaint_list'),
    path('submit/', views.submit_complaint, name='submit_complaint'),
    path('success/', views.success_view, name='success'),
    path('<slug:slug>/', views.complaint_detail, name='complaint_detail'),
    path('<slug:slug>/update/', views.update_complaint, name='update_complaint'),
    path('<slug:slug>/delete/', views.delete_complaint, name='delete_complaint'),
]
