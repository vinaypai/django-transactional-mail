"""Transactional Email App URL configuration"""
from django.urls import path

from . import views

urlpatterns = [
    path('<slug:email_name>/', views.preview_email, name="preview")
]
