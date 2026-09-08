from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import ContactMessage, Schedule, Station, Train, TrainClass


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class SearchForm(forms.Form):
    origin = forms.ModelChoiceField(queryset=Station.objects.all(), required=False, empty_label="-- เลือก --")
    destination = forms.ModelChoiceField(queryset=Station.objects.all(), required=False, empty_label="-- เลือก --")
    travel_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "subject", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}


class StationForm(forms.ModelForm):
    class Meta:
        model = Station
        fields = ("name", "province")


class TrainForm(forms.ModelForm):
    class Meta:
        model = Train
        fields = ("train_number", "train_type")


class TrainClassForm(forms.ModelForm):
    class Meta:
        model = TrainClass
        fields = ("name", "price")


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ("train", "origin", "destination", "travel_date", "departure_time", "arrival_time")
        widgets = {
            "travel_date": forms.DateInput(attrs={"type": "date"}),
            "departure_time": forms.TimeInput(attrs={"type": "time"}),
            "arrival_time": forms.TimeInput(attrs={"type": "time"}),
        }
