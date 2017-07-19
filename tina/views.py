import os
import json

import couchdb

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.core import urlresolvers
from django.contrib import messages
from django.conf import settings
from django.views.generic import View

from models import Project, SequencingFacility
from forms import ProjectForm
from util import resize_project_thumbnail, TinaCouchDB
import seqfacility

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from tina.serializers import UserSerializer, GroupSerializer

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


class ProjectViews:
    class Manage(View):
        def get(self, request, subproj_id=None):
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

    class Add(View):
        def post(self, request):
            project_form = ProjectForm(request.POST, request.FILES, instance=Project())
            if project_form.is_valid():
                # Create the new Project model, send success message
                project = project_form.save()
                messages.success(request, 'Project {} was successfully created.'.format(project.name))

                # Resize project cover image into thumbnail
                if project.project_cover_image:
                    resize_project_thumbnail(project.project_cover_image.path)

                # Create new couchDB document id, put in new metadata
                doc_metadata = TinaCouchDB.format_handson_data(request.POST.get('project_other_metadata', '{}'))
                try:
                    project.details_doc_id, _ = TinaCouchDB.save_tina_doc(doc_metadata)
                    project.save()
                except:
                    # TODO Jquery Toast is acting funky if more than one message is sent
                    messages.error(request, 'Metadata document could not be established')

                library_defaults = [m for m in json.loads(request.POST.get('project_other_metadata', '{}')) if m[0]]

            return HttpResponseRedirect(urlresolvers.reverse('manage_project'))

        def get(self, request):
            project_form = ProjectForm(instance=Project())
            context = {
                'page_title': 'Add Project',
                'project_form': project_form,
                'action': 'add',
                'existing_doc_metadata': '{}'
            }
            return render(request, 'tina/project/add_edit_project.html', context)

    class Edit(View):
        def post(self, request, proj_id):
            # TODO What is proj_id isn't given?
            updated_project = Project.objects.get(pk=proj_id)

            # Get the cover image instance before the updated data is applied to the project instance
            preupdate_cover_img = updated_project.project_cover_image

            # Apply updated data to the project instance
            updated_project_form = ProjectForm(request.POST, request.FILES, instance=updated_project)
            if updated_project_form.is_valid():
                updated_project_form.save()

                # Check for a cover image change
                if preupdate_cover_img != updated_project.project_cover_image:
                    # If an old cover image exists, delete it
                    if preupdate_cover_img.name:
                        os.remove(preupdate_cover_img.path)

                    # If a new cover image is uploaded, resize it to a thumbnail
                    if updated_project.project_cover_image.name:
                        resize_project_thumbnail(updated_project.project_cover_image.path)

                # Send success message to the user
                messages.success(request, 'Project {} was successfully updated.'.format(updated_project.name))

                # Update the document metadata
                update_doc_body = TinaCouchDB.format_handson_data(request.POST.get('project_other_metadata', '{}'))
                TinaCouchDB.update_tina_doc(updated_project.details_doc_id, update_doc_body)

                return HttpResponseRedirect(urlresolvers.reverse('manage_project'))

        def get(self, request, proj_id):
            project = Project.objects.get(pk=proj_id)
            project_form = ProjectForm(instance=project)

            context = {
                'page_title': 'Edit Project',
                'project_form': project_form,
                'project_pk': project.pk,
                'action': 'edit',
                # The metadata in CouchDB so that it can be populated in the appropriate field
                'existing_doc_metadata': json.dumps(
                    TinaCouchDB.get_tina_doc(project.details_doc_id, include_meta=False).items()
                )
            }
            return render(request, 'tina/project/add_edit_project.html', context)

    class View(View):
        def get(self, request, proj_id):
            context = {
                'project': Project.objects.get(pk=proj_id)
            }
            return render(request, 'tina/project/view_project.html', context)

    class Delete(View):
        def get(self, request, proj_id):
            project = Project.objects.get(pk=proj_id)
            project_name = project.name

            # Attempt to delete the Project
            try:
                # Project delete has a signal receiver attached to it in models.py
                project.delete()

                # Send successful delete message to the user
                messages.success(request, 'Project {} and all its contents were deleted.'.format(project_name))
            except:
                # Send error message to the user
                messages.error(request, 'There was an error deleting project {}'.format(project_name))

            return HttpResponseRedirect(urlresolvers.reverse('manage_project'))


class SubmitViews:
    class SubmitLibrary(View):
        def post(self, request):
            facility = request.POST.get('facility_select')
            # success = seqfacility.handle_submission(facility, dict(zip(request.POST.keys(), request.POST.values())))
            success = seqfacility.handle_submission(facility, request.POST)
            print request.POST
            print 'Success: {}'.format(str(success))
            # TODO On success or failure, notify user through a message (a toast message)
            return HttpResponseRedirect(urlresolvers.reverse('home'))

        def get(self, request):
            context = {
                'projects': Project.objects.all(),
                'facilities': SequencingFacility.objects.all()
            }
            return render(request, 'tina/submit/submit.html', context)

class LibraryViews:
    class Manage(View):
        def get(self, request):
            bid1 = {'bid':'1','project': 'PEC', 'status': 'submitted'}
            bid2 = {'bid':'2','project': 'mod', 'status': 'processed'}
            bid3 = {'bid':'3','project': 'PanCan', 'status': 'processing'}
            testContext = [bid1, bid2, bid3]
            context = {
                'bids': testContext
            }
            return render(request, 'tina/project/view_libraries.html', context)

# Using generic class-based views

# http http://127.0.0.1:8000/projects/list/

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


class UserViewSet(viewsets.ModelViewSet):
    """
    API end point that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'projects': reverse('project-list', request=request, format=format)
    })