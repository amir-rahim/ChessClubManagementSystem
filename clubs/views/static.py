'''Static Related Views'''
from django.shortcuts import render

from clubs.helpers import login_prohibited

@login_prohibited
def home(request):
    return render(request, 'home.html')