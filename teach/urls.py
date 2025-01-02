from . import views
from django.contrib import admin
from django.urls import path, include


urlpatterns = [

    path("index", views.teach_index, name="teach_index" ),

    path("courselist", views.teach_courselist, name="teach_courselist" ),

    path("courseadapt",views.teach_courseadapt,name="teach_courseadapt" ),

    path("pushgrades",views.teach_pushgrades,name="teach_pushgrades" ),

    path("waiverreview",views.teach_waiverreview,name="teach_waiverreview" ),

]
