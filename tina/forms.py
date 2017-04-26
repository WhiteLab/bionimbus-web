from django import forms
from models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description', 'project_cover_image', 'pi',
                  'public', 'cloud', 'organism', 'platform',
                  'parent_project', 'owner')
