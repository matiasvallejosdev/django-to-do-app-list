from django.contrib import admin
from django.urls import path, include

# Import views
from core.views import home_view

app_name = 'todoapp'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('', include('tasks.urls')),
    path('', include('users.urls')),
]
