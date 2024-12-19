from . import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    path("index", views.teach_index ),

    path("courselist", views.teach_courselist ),

    path("courseadapt",views.teach_courseadapt ),

    path("pushgrades",views.teach_pushgrades ),

    path("waiverreview",views.teach_waiverreview ),

]
