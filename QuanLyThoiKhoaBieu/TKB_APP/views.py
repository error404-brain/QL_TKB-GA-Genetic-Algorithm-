from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render
from .utils import load_giang_vien_from_csv, load_mon_hoc_from_csv, load_phong_hoc_from_csv, load_lop_hoc_phan_from_csv, load_tiet_hoc_from_csv, check_schedule_conflict
from .models import GiangVien, MonHoc, PhongHoc, LopHocPhan, TietHoc, ThoiKhoaBieu
from deap import base, creator, tools, algorithms
from .forms import LopHocPhanForm,ThoiKhoaBieuForm
from django.http import HttpResponse, HttpResponseRedirect
import random



