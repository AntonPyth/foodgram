from io import BytesIO

from accounts.models import Subscription
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipe.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, redirect

from .filters import IngredientFilter, RecipeFilter
from .pagination import Pagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    CreateRecipeSerializer,
    CreateUserSerializer,
    CustomUserSerializer,
    FavoriteSerializer,
    FollowSerializer,
    GetFollowSerializer,
    IngredientSerializer,
    ReadRecipeSerializer,
    ShoppingCartSerializer,
    ShortRecipeSerializer,
    TagSerializer,
    UserAvatarSerializer,
)

User = get_user_model()


class TagView(viewsets.ModelViewSet):
    """Представления тегов."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    http_method_names = ('get', 'head', 'options')
    pagination_class = None


class IngredientView(viewsets.ModelViewSet):
    """Представления ингредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    permission_classes = (AllowAny,)
    http_method_names = ('get', 'head', 'options')
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = Pagination
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags',
        'ingredients'
    )
    serializer_class = ReadRecipeSerializer

    def get_permissions(self):
        """Получение класса ограничения."""
        if self.action in ('list', 'retrieve', 'generate_short_link'):
            return (AllowAny(),)
        elif self.action in ('update', 'partial_update', 'destroy',):
            return (IsOwnerOrReadOnly(),)
        return super().get_permissions()

    def get_serializer_class(self):
        """Выбор класса сериализатора."""
        if self.action == 'favorite':
            return ShortRecipeSerializer
        if self.action in ('update', 'partial_update', 'create', 'destroy'):
            return CreateRecipeSerializer
        return super().get_serializer_class()

    def handle_post_delete(self, request, model, serializer_class, pk):
        """Обработка добавления/удаления рецепта в избранное или корзину."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if request.method == 'POST':
            data = {'recipe': recipe.id, 'user': user.id}
            serializer = serializer_class(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted_count, _ = model.objects.filter(
            recipe=recipe, user=user
        ).delete()
        if deleted_count == 0:
            return Response({'error': 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'], url_path='favorite',
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранное."""
        return self.handle_post_delete(request, Favorite,
                                       FavoriteSerializer, pk)

    @action(detail=True, methods=['POST', 'DELETE'], url_path='shopping_cart',
            permission_classes=(IsAuthenticated,),)
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта из корзины."""
        return self.handle_post_delete(request, ShoppingCart,
                                       ShoppingCartSerializer, pk)

    def generate_shopping_list_buffer(self, ingredients):
        """Генерирует буфер BytesIO со списком покупок."""
        output = '\n'.join(
            f'{counter}. {item["ingredient__name"]} - '
            f'{item["total_amount"]} '
            f'{item["ingredient__measurement_unit"]}.'
            for counter, item in enumerate(ingredients, start=1)
        )
        buffer = BytesIO(output.encode('utf-8'))
        return buffer

    @action(detail=False, methods=['GET'], url_path='download_shopping_cart',
            permission_classes=(IsAuthenticated,),)
    def download_shopping_cart(self, request):
        """Скачать список ингредиентов из корзины."""
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__in_shopping_cart__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        buffer = self.generate_shopping_list_buffer(ingredients)
        response = HttpResponse(buffer.getvalue(), content_type='text/plain')
        buffer.close()
        return response

    @action(detail=True, methods=['GET'], url_path='get-link')
    def generate_short_link(self, request, pk=None):
        """Создание линка на рецепт."""
        short_link_id = get_object_or_404(Recipe, id=pk).id
        short_link = f'{settings.SITE_DOMAIN}/s/{short_link_id}'
        return Response({'short-link': short_link})


@api_view(['GET'])
@permission_classes((AllowAny, ))
def redirect_to_recipe(request, recipe_id):
    """Редирект по короткой ссылке на детальный URL рецепта."""
    if not Recipe.objects.filter(id=recipe_id).exists():
        raise ValidationError(f'Рецепт с id={recipe_id} не существует')
    return redirect(f'/recipes/{recipe_id}/')


@api_view(['GET'])
def get_csrf_token(request):
    return Response({'csrfToken': get_token(request)})


class CustomUserViewSet(UserViewSet):
    """Вьюсет для работы с пользователями."""

    queryset = User.objects.all()
    pagination_class = Pagination

    def get_permissions(self):
        """Получение класса ограничения."""
        if self.action in ('list', 'retrieve', 'create'):
            return (AllowAny(),)
        return super().get_permissions()

    def get_serializer_class(self):
        """Получение класса сериализатора."""
        if self.action in ('list', 'retrieve'):
            return CustomUserSerializer
        if self.action == 'create':
            return CreateUserSerializer
        return super().get_serializer_class()

    @action(methods=('PUT', 'DELETE',), detail=False, url_path='me/avatar',
            permission_classes=(IsAuthenticated,), )
    def user_avatar(self, request):
        """Добавления и удаление аватара."""
        user = get_object_or_404(User, username=request.user.username)
        if request.method == 'PUT':
            avatar_data = request.data.get('avatar')
            if not avatar_data:
                return Response(
                    {'avatar': 'Поле avatar пустое!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = UserAvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('GET',), detail=False, url_path='subscriptions',
            permission_classes=(IsAuthenticated,), )
    def get_subscriptions(self, request):
        """Получение списка подписок."""
        following_users = User.objects.filter(
            subscribers__subscriber=request.user
        ).annotate(recipes_count=Count('recipes')).distinct()
        paginator = Pagination()
        result_page = paginator.paginate_queryset(following_users, request)
        serializer = GetFollowSerializer(result_page, many=True,
                                         context={'request': request},)
        return paginator.get_paginated_response(serializer.data)

    @action(
        methods=('POST', 'DELETE',),
        detail=True,
        url_path='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        """Подписка/отписка на пользователя."""
        following = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowSerializer(
                data={'subscriber': request.user.id, 'target': following.id},
                context={
                    'request': request,
                    'recipes_limit': request.query_params.get('recipes_limit')}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            annotated_target = User.objects.annotate(
                recipes_count=Count('recipes')
            ).get(id=following.id)
            follow_serializer = GetFollowSerializer(
                annotated_target, context={'request': request}
            )
            return Response(
                follow_serializer.data, status=status.HTTP_201_CREATED
            )

        elif request.method == 'DELETE':
            deleted_count, _ = Subscription.objects.filter(
                subscriber=request.user.id,
                target=following.id
            ).delete()
            if deleted_count == 0:
                return Response(
                    {'error': 'Подписка не найдена'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_204_NO_CONTENT)
