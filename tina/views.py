import os
import json

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.core import urlresolvers
from django.contrib import messages
from django.conf import settings

from models import Project, SequencingFacility
from forms import ProjectForm
from util import resize_project_thumbnail
import seqfacility


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
    if request.method == 'POST':
        facility = request.POST.get('facility_select')
        # success = seqfacility.handle_submission(facility, dict(zip(request.POST.keys(), request.POST.values())))
        success = seqfacility.handle_submission(facility, request.POST)
        print request.POST
        print 'Success: {}'.format(str(success))
        # TODO On success or failure, notify user through a message (a toast message)
        return HttpResponseRedirect(urlresolvers.reverse('home'))
    else:
        context = {
            'projects': Project.objects.all(),
            'facilities': SequencingFacility.objects.all()
        }
        return render(request, 'tina/submit/submit.html', context)
