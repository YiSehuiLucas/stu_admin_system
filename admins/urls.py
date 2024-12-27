# admins/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('admin/<str:user_id>/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/<str:user_id>/profile/', views.admin_profile, name='admin_profile'),
    path('admin/<str:user_id>/edit/', views.admin_edit, name='admin_edit'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/create/', views.teacher_create, name='teacher_create'),
    path('teachers/<str:tch_id>/update/', views.teacher_edit, name='teacher_edit'),
    path('teachers/<str:tch_id>/delete/', views.teacher_delete, name='teacher_delete'),
    path('teachers/import/', views.teacher_import, name='teacher_import'),
    path('courseadapts/', views.courseadapt_list, name='courseadapt_list'),
    path('courseadapts/<int:ca_id>/review/', views.courseadapt_review, name='courseadapt_review'),
    path('waiverapplications/', views.waiverapplication_list, name='waiverapplication_list'),
    path('waiverapplications/<int:wa_id>/review', views.waiverapplication_detail, name='waiverapplication_detail'),
]