from django.contrib import admin

from django.utils.safestring import mark_safe

# Register your models here.
from .models import Category,Movie,Genre, MovieImage


class MovieInline(admin.TabularInline):
    model = Movie
    extra = 0



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [MovieInline]
    list_display = ['id','name','slug','count_movies']
    search_fields = ['name',]
    ordering = ['id']
    prepopulated_fields = {"slug": ("name",)}


class MovieImageInline(admin.TabularInline):
    model = MovieImage
    extra = 0

    
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    search_fields = ['name',]
    list_display = ['id',  'name','created_date','country','raiting']
    list_display_links = ['name',]
    list_filter = ['category', 'genres']
    # readonly_fields = ['get_image']
    inlines = (MovieImageInline,)
    # exclude = ("category",)
    filter_horizontal = ("genres",)

    # @admin.display(description="Изображение")
    # def get_image(self, movie):
    #     if movie.image:
    #         text = mark_safe(f'<img scr="{movie.image.url}" width="150px" />')
    #         return text
    #     return "-"
    
    

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass

