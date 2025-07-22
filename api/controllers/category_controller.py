from rest_framework import viewsets, status
from rest_framework.response import Response

from api.serializers.catergory_serializer import LearningModuleSerializer, ExerciseSerializer
from app.models import TopicCategory, Exercise, LearningModule
from helpers.pagination import StandardResultsSetPagination
from utils.respose import UtilResponse
from rest_framework.permissions import AllowAny


class CategoryViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        eData = {}
        uResponse = UtilResponse()
        try:
            categories = TopicCategory.objects.filter(
                is_active=True
            ).order_by('order')

            categories_data = [{
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'icon': category.icon,
                'order': category.order
            } for category in categories]
            return uResponse.response_success(data=categories_data)
        except Exception as ex:
            return uResponse.response_error(message=str(ex),status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class TopicCategoryViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def list(self, request):
        eData = {}
        uResponse = UtilResponse()
        try:
            eData['title'] = 'Topics'
            eData['subtitle'] = 'Topics'
            learning = Exercise.objects.filter(module__topic_category__id=request.GET['id'],is_active=True).order_by('-id')

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(learning, request)

            eData['total'] = learning.count()
            if page is not None:
                eData['exercises'] = ExerciseSerializer(page, many=True).data
                eData['pagination'] = paginator.get_paginated_response({}).data['metadata']
                return uResponse.response_success(data=eData)

            eData['exercises'] = ExerciseSerializer(page,many=True).data
            return uResponse.response_success(data=eData)
        except Exception as ex:
            return uResponse.response_error(message=str(ex),status=status.HTTP_500_INTERNAL_SERVER_ERROR)