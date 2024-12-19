from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def teach_index(request):
    return render(request,'tech_index.html')


