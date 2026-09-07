from django.urls import path
from .views import MovieList, MovieDetail, ShowtimeList, ShowtimeDetail, CinemaList, CinemaDetail

urlpatterns = [
    path("movies/", MovieList.as_view()),
    path("movies/<uuid:pk>/", MovieDetail.as_view()),
    path("showtimes/", ShowtimeList.as_view()),
    path("showtimes/<uuid:pk>/", ShowtimeDetail.as_view()),
    path("cinemas/", CinemaList.as_view()),
    path("cinemas/<uuid:pk>/", CinemaDetail.as_view()),
]
