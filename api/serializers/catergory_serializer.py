from rest_framework import serializers
from app.models import LearningModule, Exercise
from helpers.model_base import Helper_ModelSerializer


class LearningModuleSerializer(Helper_ModelSerializer):
    level_name = serializers.SerializerMethodField()
    topic_category_name = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = LearningModule
        fields = '__all__'

    def get_level_name(self, obj):
        return obj.level.name if obj.level else None

    def get_topic_category_name(self, obj):
        return obj.topic_category.name if obj.topic_category else None

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            return request.build_absolute_uri(obj.thumbnail.url) if request else obj.thumbnail.url
        return None


class ExerciseSerializer(Helper_ModelSerializer):

    class Meta:
        model = Exercise
        fields = '__all__'
