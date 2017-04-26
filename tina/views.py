import os
import json

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.core import urlresolvers
from django.contrib import messages
from django.conf import settings

from models import Project
from forms import ProjectForm
from util import resize_project_thumbnail

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from tina.serializers import UserSerializer, GroupSerializer

# from django.http import HttpResponse, JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.renderers import JSONRenderer
# from rest_framework.parsers import JSONParser

from serializers import ProjectSerializer
from permissions import IsOwnerOrReadOnly
from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

# Create your views here.
def home(request):
    return render(request, 'tina/home.html')


def manage_project(request, subproj_id=None):
    # If we're viewing subprojects of a given project
    if subproj_id is not None:
        parent_project = Project.objects.get(pk=subproj_id)
        context = {
            'projects': parent_project.subprojects(),
            'parent_project': parent_project,
            'toplevel': False
        }
        return render(request, 'tina/project/manage_project.html', context)

    # If we're viewing top-level projects
    context = {
        'projects': Project.all_toplevel_projects(),
        'toplevel': True
    }
    return render(request, 'tina/project/manage_project.html', context)

class UserViewSet (viewsets.ModelViewSet):
    """
    API end point that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class GroupViewSet (viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer

def add_project(request):
    if request.method == 'POST':
        project_form = ProjectForm(request.POST, request.FILES, instance=Project())
        if project_form.is_valid():
            # Create the new Project model
            project = project_form.save()
            messages.success(request, 'Project {} was successfully created.'.format(project.name))

            # Resize project cover image into thumbnail
            image_fullpath = os.path.join(settings.BASE_DIR, project.project_cover_image.url.strip('/'))
            resize_project_thumbnail(image_fullpath)

            # Create new couchDB document id, put in new metadata
            # TODO Send message that metadata could not be saved
            other_metadata = [m for m in json.loads(request.POST.get('project_other_metadata', '{}')) if m[0]]
            library_defaults = [m for m in json.loads(request.POST.get('project_other_metadata', '{}')) if m[0]]
            print other_metadata

        return HttpResponseRedirect(urlresolvers.reverse('manage_project'))
    else:
        project_form = ProjectForm(instance=Project())
        context = {
            'project_form': project_form,
            'action': 'add'
        }
        return render(request, 'tina/project/add_edit_project.html', context)


def edit_project(request, proj_id):
    if request.method == 'POST':
        updated_project = Project.objects.get(pk=proj_id)
        updated_project_form = ProjectForm(request.POST, request.FILES, instance=updated_project)
        if updated_project_form.is_valid():
            updated_project_form.save()
            messages.success(request, 'Project {} was successfully updated.'.format(updated_project.name))

            # TODO All the NoSQL stuff needs to be updated too, probably just create a whole new document

            return HttpResponseRedirect(urlresolvers.reverse('manage_project'))
    else:
        project = Project.objects.get(pk=proj_id)
        project_form = ProjectForm(instance=project)
        context = {
            'project_form': project_form,
            'project_pk': project.pk,
            'action': 'edit'
        }
        return render(request, 'tina/project/add_edit_project.html', context)


def view_project(request, proj_id):
    context = {
        'project': Project.objects.get(pk=proj_id)
    }
    return render(request, 'tina/project/view_project.html', context)


def delete_project(request, proj_id):
    # Delete Project, return message to user on success
    project = Project.objects.get(pk=proj_id)
    project_name = project.name
    project.delete()
    messages.success(request, 'Project {} and all its contents were deleted.'.format(project_name))

    return HttpResponseRedirect(urlresolvers.reverse('manage_project'))


def submit_library(request):
    return render(request, 'tina/submit/submit.html', {})


# restful API 

class ProjectList(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'projects': reverse('project-list', request=request, format=format)
    })

