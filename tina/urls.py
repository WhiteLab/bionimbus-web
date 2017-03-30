from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

import views
import seqfacility

urlpatterns = [
    url(r'^$', views.home, name='home'),

    # Projects Tab
    url(r'^projects/$', views.manage_project, name='manage_project'),
    url(r'^projects/(?P<subproj_id>\d+)/$', views.manage_project, name='manage_subproject'),
    url(r'^projects/add/$', views.add_project, name='add_project'),
    url(r'^projects/edit/(?P<proj_id>\d+)/$', views.edit_project, name='edit_project'),
    url(r'^projects/view/(?P<proj_id>\d+)/$', views.view_project, name='view_project'),
    url(r'^projects/delete/(?P<proj_id>\d+)/$', views.delete_project, name='delete_project'),

    # Submit Tab
    url(r'^submit/$', views.submit_library, name='submit_library'),

    # Sequencing Facility AJAX
    url(r'^seqfacility/(?P<facility>\w+)/$', seqfacility.get_submit_form,
        name='seqfacility_get_submit_form')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
