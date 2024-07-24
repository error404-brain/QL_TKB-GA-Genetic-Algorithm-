from django.urls import path
from . import views

urlpatterns = [
    path('load-schedule/', views.load_schedule_view, name='load_schedule'),
    path('schedule/', views.show_tkb, name='show_tkb'),
    path('', views.find_tkb_by_id, name='find_tkb_by_id'),
   
    
]
