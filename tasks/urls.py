from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


app_name = 'tasks'
urlpatterns = [
    # Pages
    path('task/view/', TasksView.as_view(), name='home'),
    path('list/create/', TaskListForm.as_view(), name='list_create'),
    # Task Operations
    path('task/delete/<int:pk>/', TaskDeleteRedirect.as_view(), name='delete'),
    path('task/complete/<int:pk>/', TaskCompleteRedirect.as_view(), name='complete'),
    # List Operations
    path('list/delete/<str:name>/', TaskListDeleteRedirect.as_view(), name='list_delete'),
]
