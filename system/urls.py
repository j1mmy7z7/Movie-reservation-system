from django.urls import path

from .views import (
    MovieList, MovieDetail, ShowtimeList,
    ShowtimeDetail, CinemaList, CinemaDetail,
    CinemaShowtimeList, ShowtimeTicketList, HoldTickets,
    InitiatePayment, CancelTickets, MpesaCallback,
    PaymentStatus,
    Register, ClientDetail, health_check
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("movies/", MovieList.as_view()),
    path("movies/<uuid:pk>/", MovieDetail.as_view()),
    path("showtimes/", ShowtimeList.as_view()),
    path("showtimes/<uuid:pk>/", ShowtimeDetail.as_view()),
    path("cinemas/", CinemaList.as_view()),
    path("cinemas/<uuid:pk>/", CinemaDetail.as_view()),
    path("cinemas/<uuid:cinema_id>/showtimes/", CinemaShowtimeList.as_view()),
    path("showtimes/<uuid:showtime_id>/tickets/", ShowtimeTicketList.as_view()),
    path("showtimes/<uuid:showtime_id>/hold/", HoldTickets.as_view()),
    path("payments/initiate/", InitiatePayment.as_view()),
    path("tickets/cancel/", CancelTickets.as_view()),
    path("health/", health_check),
    path("payments/<uuid:id>/", PaymentStatus.as_view()),
    path("mpesa/callback/", MpesaCallback.as_view()),
    path("auth/register/", Register.as_view()),
    path("auth/login/", TokenObtainPairView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),
    path("clients/me/", ClientDetail.as_view()),

]
