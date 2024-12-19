from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def teach_index(request):
    return render(request,'teach_index.html')

def teach_courselist(request):
    return render(request,'teach_courselist.html')

def teach_pushgrades(request):
    return render(request,'teach_pushgrades.html')

def teach_courseadapt(request):
    return render(request, 'teach_courseadapt.html')

def teach_waiverreview(request):
    return render(request, 'teach_waiverreview.html')



