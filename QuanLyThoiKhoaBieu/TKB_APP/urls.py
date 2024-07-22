from django.urls import path
from . import views

urlpatterns = [
    path('load-schedule/', views.load_schedule_view, name='load_schedule'),
]
