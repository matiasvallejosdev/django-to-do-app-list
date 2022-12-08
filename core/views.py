from django.shortcuts import render
from tasks.models import List


def home_view(request, *args, **kwargs):
    lists = List.objects.all()
    context = {
        'user': request.user,
        'list': lists
    }
    return render(request, 'home.html', context)
