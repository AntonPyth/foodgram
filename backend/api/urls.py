from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientView,
    RecipesViewSet,
    TagView,
    CustomUserViewSet
)

router = routers.DefaultRouter()
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('tags', TagView, basename='tags')
router.register('ingredients', IngredientView, basename='ingredients')
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
