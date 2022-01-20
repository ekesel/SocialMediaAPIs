from .models import *
from rest_framework import serializers


class AddPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Posts
        fields = ['id','title','desc','created_at']


class AddCommentSerializer(serializers.Serializer):
    comment = serializers.CharField()

