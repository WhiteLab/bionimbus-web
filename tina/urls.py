from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

import seqfacility

from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from views import ProjectViews, LibraryViews, SubmitViews, CartViews
from serializers import UserSerializer


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

    # Libraries tab
    url(r'^libraries/$', LibraryViews.ViewLibraries.as_view(), name='view_libraries'),
    url(r'^libraries/data/$', LibraryViews.TableDisplayAJAX.as_view(), name='table_display_ajax'),

    url(r'^cart/$', CartViews.ViewCart.as_view(), name='view_cart'),
    url(r'^cart/add/(?P<library_id>\d+)/$', CartViews.AddToCart.as_view(), name='add_to_cart'),
    url(r'^cart/clear/$', CartViews.ClearCart.as_view(), name='clear_cart'),
    url(r'^cart/download/$', CartViews.HandleDownloadRequest.as_view(), name='download_cart'),

    # Projects tab
    url(r'^projects/$', ProjectViews.Manage.as_view(), name='manage_project'),
    url(r'^projects/(?P<subproj_id>\d+)/$', ProjectViews.Manage.as_view(), name='manage_subproject'),
    url(r'^projects/add/$', ProjectViews.Add.as_view(), name='add_project'),
    url(r'^projects/edit/(?P<proj_id>\d+)/$', ProjectViews.Edit.as_view(), name='edit_project'),
    url(r'^projects/view/(?P<proj_id>\d+)/$', ProjectViews.View.as_view(), name='view_project'),
    url(r'^projects/delete/(?P<proj_id>\d+)/$', ProjectViews.Delete.as_view(), name='delete_project'),

    # Submit Tab
    url(r'^submit/$', SubmitViews.SubmitLibrary.as_view(), name='submit_library'),
    url(r'^libraries2/$', LibraryViews.Manage.as_view(), name='libraries'),
    # Sequencing Facility AJAX
    url(r'^seqfacility/(?P<facility>\w+)/$', seqfacility.get_submit_form,
        name='seqfacility_get_submit_form')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
