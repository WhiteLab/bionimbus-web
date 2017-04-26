from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.urlpatterns import format_suffix_patterns

import views
from django.conf.urls import include


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
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    url(r'^$', views.home, name='home'),

    # Projects Tab
    url(r'^projects/$', views.manage_project, name='manage_project'),
    url(r'^projects/(?P<subproj_id>\d+)/$', views.manage_project, name='manage_subproject'),
    url(r'^projects/add/$', views.add_project, name='add_project'),
    url(r'^projects/edit/(?P<proj_id>\d+)/$', views.edit_project, name='edit_project'),
    url(r'^projects/view/(?P<proj_id>\d+)/$', views.view_project, name='view_project'),
    url(r'^projects/delete/(?P<proj_id>\d+)/$', views.delete_project, name='delete_project'),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'^projects/list/$', views.project_list),
    # url(r'^projects/get/(?P<pk>[0-9]+)$', views.project_detail),
    url(r'^projects/list/$', views.ProjectList.as_view(), name='project-list'),
    url(r'^projects/get/(?P<pk>[0-9]+)$', views.ProjectDetail.as_view(), name='project-detail'),
    url(r'^users/$', views.UserList.as_view(), name='user_list'),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name='get_user'),

    # Submit Tab
    url(r'^submit/$', views.submit_library, name='submit_library')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]