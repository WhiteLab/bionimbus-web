from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.urlpatterns import format_suffix_patterns

import views
from django.conf.urls import include

import seqfacility
from views import ProjectViews, SubmitViews

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
# router.register(r'groups', views.GroupViewSet)


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='tina/home.html'), name='home'),

    url(r'^projects/$', ProjectViews.Manage.as_view(), name='manage_project'),
    url(r'^projects/(?P<subproj_id>\d+)/$', ProjectViews.Manage.as_view(), name='manage_subproject'),
    url(r'^projects/add/$', ProjectViews.Add.as_view(), name='add_project'),
    url(r'^projects/edit/(?P<proj_id>\d+)/$', ProjectViews.Edit.as_view(), name='edit_project'),
    url(r'^projects/view/(?P<proj_id>\d+)/$', ProjectViews.View.as_view(), name='view_project'),
    url(r'^projects/delete/(?P<proj_id>\d+)/$', ProjectViews.Delete.as_view(), name='delete_project'),
    # Url to include routers and api-authentication
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # what the names of the urls are. Can be changed later to something more suitable
    url(r'^projects/list/$', views.ProjectList.as_view(), name='project-list'),
    url(r'^projects/get/(?P<pk>[0-9]+)$', views.ProjectDetail.as_view(), name='project-detail'),
    url(r'^users/$', views.UserList.as_view(), name='user_list'),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name='get_user'),
    # Submit Tab
    url(r'^submit/$', SubmitViews.SubmitLibrary.as_view(), name='submit_library'),

    # Sequencing Facility AJAX
    url(r'^seqfacility/(?P<facility>\w+)/$', seqfacility.get_submit_form,
        name='seqfacility_get_submit_form')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
