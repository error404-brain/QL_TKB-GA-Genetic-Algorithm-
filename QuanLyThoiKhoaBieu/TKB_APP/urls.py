from django.urls import path
from . import views

urlpatterns = [
    path('', views.schedule, name='schedule'),  # This might be different based on your setup
    path('schedule/', views.view_schedule, name='view_schedule'),
    path('search/', views.search_schedule, name='search_schedule'),
    path('suaLopHocPhan/<int:lop_hoc_phan_id>/', views.suaLopHocPhan, name='suaLopHocPhan'),
    path('suaThoiKhoaBieu/<int:thoi_khoa_bieu_id>/', views.suaThoiKhoaBieu, name='suaThoiKhoaBieu'),

    # Other URL patterns
]
