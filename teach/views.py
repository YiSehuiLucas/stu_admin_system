from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.urls import app_name


def teach_index(request):
    username='L1jiu'
    return render(request, 'teach_index.html',context={'username':username})

def teach_courselist(request):
    return render(request, 'teach_courselist.html')

def teach_pushgrades(request):
    return render(request, 'teach_pushgrades.html')

def teach_courseadapt(request):
    return render(request, 'teach_courseadapt.html')

def teach_waiverreview(request):
    return render(request, 'teach_waiverreview.html')



