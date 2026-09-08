from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import (
    ContactForm,
    ScheduleForm,
    SearchForm,
    SignUpForm,
    StationForm,
    TrainClassForm,
    TrainForm,
)
from .models import Booking, Schedule, Seat, Station, Train, TrainClass


def home(request):
    return render(request, "accounts/home.html")


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your account has been created successfully.')
            return redirect('dashboard')
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    users = User.objects.all().order_by('username')
    return render(request, 'accounts/dashboard.html', {'users': users})


@login_required
def search_tickets(request):
    form = SearchForm(request.GET or None)
    schedules = Schedule.objects.select_related("train", "origin", "destination").all()
    if form.is_valid():
        if form.cleaned_data["origin"]:
            schedules = schedules.filter(origin=form.cleaned_data["origin"])
        if form.cleaned_data["destination"]:
            schedules = schedules.filter(destination=form.cleaned_data["destination"])
        if form.cleaned_data["travel_date"]:
            schedules = schedules.filter(travel_date=form.cleaned_data["travel_date"])
    else:
        schedules = Schedule.objects.none()
    classes = TrainClass.objects.all()
    return render(
        request,
        "accounts/search.html",
        {"form": form, "schedules": schedules, "classes": classes},
    )


@login_required
def seat_selection(request, schedule_id, class_id):
    schedule = get_object_or_404(
        Schedule.objects.select_related("train", "origin", "destination"),
        pk=schedule_id,
    )
    train_class = get_object_or_404(TrainClass, pk=class_id)
    if request.method == "POST":
        seat_id = request.POST.get("seat_id")
        with transaction.atomic():
            seat = get_object_or_404(
                Seat.objects.select_for_update(),
                pk=seat_id,
                schedule=schedule,
            )
            if seat.is_booked:
                messages.error(request, "ที่นั่งถูกจองแล้ว กรุณาเลือกใหม่")
            else:
                seat.booked_by = request.user
                seat.save(update_fields=("booked_by",))
                Booking.objects.create(
                    user=request.user,
                    schedule=schedule,
                    seat=seat,
                    train_class=train_class,
                    price=train_class.price,
                    status="Confirmed",
                )
                messages.success(request, "จองสำเร็จแล้ว")
                return redirect("my_bookings")
    seats = schedule.seats.select_related("booked_by").all()
    return render(
        request,
        "accounts/seat_selection.html",
        {"schedule": schedule, "train_class": train_class, "seats": seats},
    )


@login_required
def my_bookings(request):
    if request.method == "POST":
        booking = get_object_or_404(Booking, pk=request.POST.get("booking_id"), user=request.user)
        booking.seat.booked_by = None
        booking.seat.save(update_fields=("booked_by",))
        booking.status = "Cancelled"
        booking.save(update_fields=("status",))
        messages.success(request, "ยกเลิกการจองเรียบร้อยแล้ว")
        return redirect("my_bookings")
    bookings = Booking.objects.filter(user=request.user).select_related(
        "schedule__train",
        "schedule__origin",
        "schedule__destination",
        "seat",
        "train_class",
    )
    return render(request, "accounts/my_bookings.html", {"bookings": bookings})


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "ส่งข้อความเรียบร้อยแล้ว! ขอบคุณที่ติดต่อเรา")
            return redirect("contact")
    else:
        form = ContactForm(initial={"name": request.user.username, "email": request.user.email} if request.user.is_authenticated else None)
    return render(request, "accounts/contact.html", {"form": form})


def staff_required(request):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "คุณไม่มีสิทธิ์เข้าถึงส่วนแอดมิน")
        return redirect("dashboard")
    return None


@login_required
def admin_dashboard(request):
    denied = staff_required(request)
    if denied:
        return denied
    counts = {
        "stations": Station.objects.count(),
        "trains": Train.objects.count(),
        "schedules": Schedule.objects.count(),
        "users": User.objects.count(),
        "bookings": Booking.objects.count(),
    }
    return render(request, "accounts/admin_dashboard.html", {"counts": counts})


def _admin_crud(request, model, form_class, template_name, title):
    denied = staff_required(request)
    if denied:
        return denied
    if request.method == "POST":
        item_id = request.POST.get("id")
        instance = get_object_or_404(model, pk=item_id) if item_id else None
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "บันทึกข้อมูลเรียบร้อยแล้ว")
            return redirect(request.resolver_match.url_name)
    else:
        form = form_class()
    items = model.objects.all()
    return render(request, template_name, {"form": form, "items": items, "title": title})


@login_required
def manage_stations(request):
    return _admin_crud(request, Station, StationForm, "accounts/manage_items.html", "จัดการสถานี")


@login_required
def manage_trains(request):
    return _admin_crud(request, Train, TrainForm, "accounts/manage_items.html", "จัดการขบวนรถไฟ")


@login_required
def manage_classes(request):
    return _admin_crud(request, TrainClass, TrainClassForm, "accounts/manage_items.html", "จัดการชั้นโดยสาร")


@login_required
def manage_schedules(request):
    return _admin_crud(request, Schedule, ScheduleForm, "accounts/manage_items.html", "จัดการตารางเวลา")


@login_required
@require_http_methods(["POST"])
def delete_item(request, model_name, item_id):
    denied = staff_required(request)
    if denied:
        return denied
    models = {"station": Station, "train": Train, "class": TrainClass, "schedule": Schedule}
    model = models.get(model_name)
    if model is None:
        return redirect("admin_dashboard")
    get_object_or_404(model, pk=item_id).delete()
    messages.success(request, "ลบข้อมูลเรียบร้อยแล้ว")
    return redirect({
        "station": "manage_stations",
        "train": "manage_trains",
        "class": "manage_classes",
        "schedule": "manage_schedules",
    }[model_name])


@login_required
def user_management(request):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to manage users.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User account created successfully.')
            return redirect('user_management')
    else:
        form = SignUpForm()

    users = User.objects.all().order_by('username')
    return render(request, 'accounts/user_management.html', {'form': form, 'users': users})


@login_required
@require_http_methods(['POST'])
def delete_user(request, user_id):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete users.')
        return redirect('dashboard')

    target = get_object_or_404(User, pk=user_id)
    if target == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('user_management')

    target.delete()
    messages.success(request, f'User {target.username} was deleted.')
    return redirect('user_management')
