from rest_framework import routers

from django.urls import include, path

from .views import (
    CustomUserViewSet,
    IngredientView,
    RecipesViewSet,
    TagView,
    get_csrf_token
)

router = routers.DefaultRouter()
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('tags', TagView, basename='tags')
router.register('ingredients', IngredientView, basename='ingredients')
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
]
