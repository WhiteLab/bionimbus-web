from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

import seqfacility
from views import ProjectViews, SubmitViews

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='tina/home.html'), name='home'),

    url(r'^projects/$', ProjectViews.Manage.as_view(), name='manage_project'),
    url(r'^projects/(?P<subproj_id>\d+)/$', ProjectViews.Manage.as_view(), name='manage_subproject'),
    url(r'^projects/add/$', ProjectViews.Add.as_view(), name='add_project'),
    url(r'^projects/edit/(?P<proj_id>\d+)/$', ProjectViews.Edit.as_view(), name='edit_project'),
    url(r'^projects/view/(?P<proj_id>\d+)/$', ProjectViews.View.as_view(), name='view_project'),
    url(r'^projects/delete/(?P<proj_id>\d+)/$', ProjectViews.Delete.as_view(), name='delete_project'),

    # Submit Tab
    url(r'^submit/$', SubmitViews.SubmitLibrary.as_view(), name='submit_library'),

    # Sequencing Facility AJAX
    url(r'^seqfacility/(?P<facility>\w+)/$', seqfacility.get_submit_form,
        name='seqfacility_get_submit_form')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
