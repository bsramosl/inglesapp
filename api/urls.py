from django.urls import path,include
from rest_framework.routers import DefaultRouter

from api.controllers.category_controller import CategoryViewSet,TopicCategoryViewSet
from api.controllers.home_controller import HomeViewSet,NavBarViewSet


router = DefaultRouter()
router.register(r'nav_bar', NavBarViewSet, basename='nav_bar')
router.register(r'home_data', HomeViewSet, basename='home_data')
router.register(r'topic_category', CategoryViewSet, basename='topic_category')
router.register(r'topic_learning', TopicCategoryViewSet, basename='topic_learning')


urlpatterns = [
    path('', include(router.urls)),
]