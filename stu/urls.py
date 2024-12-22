from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path("main", views.stu_main,name="stu_main"),
    path("select", views.stu_select,name="stu_select"),
    path("grade", views.stu_grade,name="stu_grade"),
    path("course", views.stu_course,name="stu_course"),
    path("free", views.stu_free,name="stu_free"),
]