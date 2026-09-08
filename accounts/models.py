from django.conf import settings
from django.db import models


class Station(models.Model):
    name = models.CharField(max_length=100)
    province = models.CharField(max_length=100)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Train(models.Model):
    train_number = models.CharField(max_length=50)
    train_type = models.CharField(max_length=100)

    class Meta:
        ordering = ("train_number",)

    def __str__(self):
        return self.train_number


class TrainClass(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


class Schedule(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="schedules")
    origin = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="departures")
    destination = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="arrivals")
    travel_date = models.DateField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()

    class Meta:
        ordering = ("-travel_date", "-departure_time")

    def __str__(self):
        return f"{self.train} - {self.origin} to {self.destination}"


class Seat(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="seats")
    number = models.CharField(max_length=5)
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="booked_seats",
    )

    class Meta:
        ordering = ("number",)
        constraints = [
            models.UniqueConstraint(fields=("schedule", "number"), name="unique_schedule_seat"),
        ]

    @property
    def is_booked(self):
        return self.booked_by_id is not None

    def __str__(self):
        return self.number


class Booking(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Cancelled", "Cancelled"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    schedule = models.ForeignKey(Schedule, on_delete=models.PROTECT, related_name="bookings")
    seat = models.OneToOneField(Seat, on_delete=models.PROTECT, related_name="booking")
    train_class = models.ForeignKey(TrainClass, on_delete=models.PROTECT, related_name="bookings")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")

    class Meta:
        ordering = ("-booking_date",)


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
