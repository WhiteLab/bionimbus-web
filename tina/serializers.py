from django.contrib.auth.models import User, Group
from tina.models import Project
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
  projects = serializers.PrimaryKeyRelatedField(many=True, queryset=Project.objects.all())
  class Meta:
    model = User
    fields = ('id', 'username', 'projects')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Group
    fields = ('url', 'name')

class ProjectSerializer(serializers.ModelSerializer):
  class Meta:
    model = Project
    owner = serializers.ReadOnlyField(source='owner.username')
    fields = ('id', 'name', 'description', 'pi', 'public', 'cloud', 'organism', 'platform', 'parent_project',
              'details_doc_id', 'project_cover_image', 'owner')


  # def create(self, validated_data):
  #   """
  #   create and return a new 'Project' instance, given the validated data.
  #   """
  #   return Project.objects.create(**validated_data)
  #
  # def update(self, instance, validated_data):
  #   """
  #   Update and return an existing 'Project' instance, given the validated data
  #   """
  #   instance.name = validated_data.get('name', instance.name)
  #   instance.description = validated_data('description', instance.description)
  #   instance.pi = validated_data('pi', instance.pi)
  #   instance.public = validated_data('public', instance.public)
  #   instance.cloud = validated_data('cloud', instance.cloud)
  #   instance.organism = validated_data('organism', instance.organism)
  #   instance.platform = validated_data('platform', instance.platform)
  #   instance.parent_project = validated_data('parent_project', instance.parent_project)
