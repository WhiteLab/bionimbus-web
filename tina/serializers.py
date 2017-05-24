from django.contrib.auth.models import User, Group
from tina.models import Project
from rest_framework import serializers


# Serializers help convert the database information into JSON format
# Created using the HyperLinkedSerializer class, which make the api viewable on the web

class UserSerializer(serializers.HyperlinkedModelSerializer):
  projects = serializers.HyperlinkedRelatedField(many=True, view_name='project-detail', read_only=True)
  class Meta:
    model = User
    fields = ('url', 'id', 'username', 'projects')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Group
    fields = ('url', 'name')

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
  # owner = serializers.ReadOnlyField(source='owner.username')
  class Meta:
    model = Project
    fields = ('id', 'name', 'description', 'pi', 'public', 'cloud', 'organism', 'platform', 'parent_project',
              'details_doc_id', 'project_cover_image')


