from django.urls import path, include

from .views import movies_list, movie_detail, categories_list, category_detail, genres_list, genre_detail


urlpatterns = [
    path('', include('api.yasg')),
    path("movies/", movies_list),
    path("movies/<int:pk>/", movie_detail),
    path("categories/", categories_list),
    path("categories/<int:pk>/", category_detail),
    path("genres/", genres_list),
    path("genres/<int:pk>/", genre_detail),
]