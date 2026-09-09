from django.contrib import admin
from system.models import Cinema, Screen, Seat, Movie, Showtime

admin.site.register(Cinema)

@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ["movie", "screen", "start_time"]

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        if is_new:
            for seat in obj.screen.seats.all():
                Ticlket.objects.create(showtime=obj, seat=seat)




@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    list_display = ["name", "cinema"]
    actions = ["generate_seats"]

    @admin.action(description="Generate 8x10 seat grid for selected screens")
    def generate_seats(self, request, queryset):
        for screen in queryset:
            for row in "ABCDEFGH":
                for num in range(1, 11):
                    Seat.objects.get_or_create(screen=screen, row_label=row, seat_number=num)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ["title", "duration_minutes", "release_date"]
    search_fields = ["title"]
