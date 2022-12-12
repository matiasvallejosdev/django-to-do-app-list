from ast import arg
import datetime
import urllib

from http import HTTPStatus
from django.http import HttpResponse

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, RedirectView, UpdateView
from django.views.generic.edit import FormView, FormMixin

from .models import List, Task
from .forms import TaskListForm, TaskFormSimple, TaskFormComplete, TaskForm

from django.utils import timezone

class HttpResponseUnauthorized(HttpResponse):
    def __init__(self):
        self.status_code = HTTPStatus.UNAUTHORIZED

class TaskUserMixin(LoginRequiredMixin, View):
    login_url = reverse_lazy('users:login')
    redirect_field_name = 'redirect_to'

    def get_context_data(self, *args, **kwargs):
        context = super(TaskUserMixin, self).get_context_data(*args, **kwargs)

        user = User.objects.get(pk=self.request.user.id)
        context['user'] = user
        context['list'] = List.objects.filter(user=self.request.user)

        return context

class MainMixinView(TaskUserMixin, View): # TaskCreateMixin, AddListMixin,
    def get_context_data(self, *args, **kwargs):
        context = super(MainMixinView, self).get_context_data(*args, **kwargs)
        add_task = True if self.request.GET.get('add_task') != None else False
        context['add_task'] = add_task
        context['user'] = self.request.user
        return context

class TaskDeleteRedirect(RedirectView):
    query_string = True
    url = reverse_lazy('tasks:home')

    def get_redirect_url(self, *args, **kwargs):
        return super(TaskDeleteRedirect, self).get_redirect_url(args, kwargs)

    def get(self, request, *args, **kwargs):
        task_id = self.kwargs.get('pk', None)
        if task_id is not None:
            task = get_object_or_404(Task, pk=task_id)
            if task.user == self.request.user:
                task.delete()
            else:
                return HttpResponseUnauthorized()
        return super(TaskDeleteRedirect, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TaskDeleteRedirect, self).get_context_data(**kwargs)
        return context

class TaskCompleteRedirect(RedirectView):
    query_string = True
    url = reverse_lazy('tasks:home')

    def get_redirect_url(self, *args, **kwargs):
        return super(TaskCompleteRedirect, self).get_redirect_url(args, kwargs)

    def get(self, request, *args, **kwargs):
        task_id = kwargs.get('pk', None)
        if task_id is not None:
            task = get_object_or_404(Task, pk=task_id)
            if request.GET.get('check', None) is not None:
                is_complete = True if request.GET.get('check') == 'True' else False
                task.is_complete = is_complete
                task.completed_at = timezone.now()
            if task.user == self.request.user:
                task.save()
            else:
                return HttpResponseUnauthorized()
        return super(TaskCompleteRedirect, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(TaskCompleteRedirect, self).get_context_data(*args, **kwargs)
        return context

class TaskListDeleteRedirect(RedirectView):
    query_string = True
    url = reverse_lazy('tasks:home')

    def get_redirect_url(self, *args, **kwargs):
        return super(TaskListDeleteRedirect, self).get_redirect_url(args, kwargs)

    def get(self, request, *args, **kwargs):
        list_id = self.kwargs.get('name', None)
        if list_id is not None:
            list = get_object_or_404(List, name=list_id)
            list.delete()
        return super(TaskListDeleteRedirect, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TaskListDeleteRedirect, self).get_context_data(**kwargs)
        return context

class TasksView(FormMixin, MainMixinView, TemplateView):
    template_name = 'task_home_view.html'
    model = Task
    context_object_name = 'tasks'
    tasks_list = None
    form_class = TaskForm

    def get(self, request, *args, **kwargs):
        self.tasks_list = self.get_queryset(*args, **kwargs)
        return super(TasksView, self).get(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super(TasksView, self).get_form(form_class)
        list_by = self.request.GET.get('list_by') or ''
        form.fields['task_list'].queryset = List.objects.filter(user=self.request.user)
        if list_by is not '':
            form.fields['task_list'].queryset = List.objects.filter(user=self.request.user).filter(name__icontains=list_by)
        form.fields['task_list'].empty_label = None
        return form

    def filter_search(self, tasks):
        search_area = self.request.GET.get('search') or ''
        if search_area != '':
            tasks = tasks.filter(content__icontains=str(search_area))
        return tasks

    def filter_list(self, tasks):
        # filter your data here
        tasks = tasks.filter(user=self.request.user)
        list_by = self.request.GET.get('list_by') or ''
        if list_by != '':
            tasks = tasks.filter(task_list__name__icontains=str(list_by))
        return tasks

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        user = self.request.user
        if form.is_valid():
            task = form.save(commit=False)
            task.user = user
            task.save()
            return self.get_success_url()
        return render(request, self.template_name, {'form': form})

    def get_queryset(self, *args, **kwargs):
        tasks = self.model.objects.all()
        tasks = self.filter_list(tasks)
        tasks = self.filter_search(tasks)
        return tasks

    def get_success_url(self, *args, **kwargs):
        title = self.request.GET.get('list_by') or ''
        return redirect(reverse('tasks:home') + f"?list_by={title}")

    def get_context_data(self, *args, **kwargs):
        context = super(TasksView, self).get_context_data(**kwargs)
        title = self.request.GET.get('list_by') or 'Inbox'
        context['title'] = title
        context['tasks_complete'] = self.tasks_list.filter(is_complete=True).order_by('-completed_at')
        context['tasks_todo'] = self.tasks_list.filter(is_complete=False).order_by('-created_at')
        context['tasks_complete_count'] = context['tasks_complete'].count()
        context['tasks_list_by'] = self.request.GET.get('list_by') or ''
        return context

class TaskListForm(FormMixin, MainMixinView, TemplateView):
    template_name = 'task_list_add.html'
    form_class = TaskListForm
    listed_by = None

    def get_success_url(self, *args, **kwargs):
        return redirect(reverse('tasks:home') + f"?list_by={self.listed_by}")

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        user = self.request.user
        if form.is_valid():
            list = form.save(commit=False)
            list.user = user
            self.listed_by = list.name
            list.save()
            return self.get_success_url()
        return render(request, self.template_name, {'form_list': form})

    def get_context_data(self, **kwargs):
        context = super(TaskListForm, self).get_context_data(**kwargs)
        context['lists_count'] = List.objects.filter(user=self.request.user).count()
        return context

class TaskEditForm(MainMixinView, UpdateView):
    model = Task
    fields = ['content', 'task_list']
    template_name = 'task_edit.html'
    success_url = reverse_lazy('tasks:home')
    query_string = True
    listed_by = None

    def get_form(self, form_class=None):
        form = super(TaskEditForm, self).get_form(form_class)
        form.fields['task_list'].queryset = List.objects.filter(user=self.request.user)
        form.fields['task_list'].empty_label = None
        self.listed_by = self.request.GET.get('list_by', None)
        return form