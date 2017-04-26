from django.contrib.auth.models import User, Group
from tina.models import Project
from rest_framework import serializers

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
  owner = serializers.ReadOnlyField(source='owner.username')
  class Meta:
    model = Project
    fields = ('id', 'name', 'description', 'pi', 'public', 'cloud', 'organism', 'platform', 'parent_project',
              'details_doc_id', 'project_cover_image', 'owner')


