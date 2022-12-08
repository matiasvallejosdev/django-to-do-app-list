from django import forms
from .models import List, Task


# That is a typically forma using models and forms
class TaskListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your list'}),
        }


class TaskFormSimple(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Your task'}),
        }

    def form_valid(self, form):
        form.instance.user = self.user
        return super().form_valid(form)


class TaskFormComplete(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['content', 'task_list', 'is_complete']