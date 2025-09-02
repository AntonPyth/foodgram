from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)

EMPTY_MSG = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_display_links = ('name',)
    search_fields = ('name',)
    empty_value_display = EMPTY_MSG


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug',)
    list_display_links = ('name', 'slug',)
    search_fields = ('name', 'slug',)
    empty_value_display = EMPTY_MSG


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'text', 'cooking_time',
                    'get_tags', 'created_at', 'get_favorites_count',
                    'get_ingredients', 'get_image')
    list_display_links = ('name', 'author',)
    search_fields = ('name',)
    list_filter = (
        'tags',
        'author__username',
        'author__first_name',
        'author__last_name'
    )
    empty_value_display = EMPTY_MSG
    inlines = (RecipeIngredientInline,)

    def get_queryset(self, request):
        """Оптимизация запросов:
        загрузка связанных данных для автора, тегов и ингредиентов."""
        queryset = super().get_queryset(request)
        return queryset.select_related('author').prefetch_related(
            'tags', 'recipe_ingredients__ingredient',
        )

    @admin.display(description='в избранном')
    def get_favorites_count(self, obj):
        return obj.favorite.count()

    @admin.display(description='Тэги')
    def get_tags(self, obj):
        tags = [tag.name for tag in obj.tags.all()]
        return ', '.join(tags)

    @admin.display(description="ингредиенты")
    @mark_safe
    def get_ingredients(self, obj):
        if not obj.recipe_ingredients.exists():
            return "Нет ингредиентов"
        return "<br>".join(
            [
                f"{item.ingredient.name} - "
                f"{item.amount} "
                f"{item.ingredient.measurement_unit}"
                for item in obj.recipe_ingredients.all()
            ]
        )

    @admin.display(description="изображение")
    @mark_safe
    def get_image(self, obj):
        if not obj.image:
            return "Нет изображения"
        return f'<img src="{obj.image.url}" width="100">'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_display_links = ('user', 'recipe',)
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = EMPTY_MSG


@admin.register(ShoppingCart)
class SoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_display_links = ('user', 'recipe',)
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = EMPTY_MSG
