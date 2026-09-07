from django.urls import path
from .views import MovieList, MovieDetail, ShowtimeList, ShowtimeDetail

urlpatterns = [
    path("movies/", MovieList.as_view()),
    path("movies/<int:pk>/", MovieDetail.as_view()),
    path("showtimes/", ShowtimeList.as_view()),
    path("showtimes/<int:pk>/", ShowtimeDetail.as_view()),
]
