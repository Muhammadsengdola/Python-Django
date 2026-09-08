from django.contrib import admin

from .models import Booking, ContactMessage, Schedule, Seat, Station, Train, TrainClass

admin.site.register((Station, Train, TrainClass, Schedule, Seat, Booking, ContactMessage))
