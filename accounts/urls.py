from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin/users/', views.user_management, name='user_management'),
    path('admin/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('tickets/search/', views.search_tickets, name='search_tickets'),
    path('tickets/<int:schedule_id>/class/<int:class_id>/', views.seat_selection, name='seat_selection'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('contact/', views.contact, name='contact'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/stations/', views.manage_stations, name='manage_stations'),
    path('admin/trains/', views.manage_trains, name='manage_trains'),
    path('admin/classes/', views.manage_classes, name='manage_classes'),
    path('admin/schedules/', views.manage_schedules, name='manage_schedules'),
    path('admin/delete/<str:model_name>/<int:item_id>/', views.delete_item, name='delete_item'),
]
