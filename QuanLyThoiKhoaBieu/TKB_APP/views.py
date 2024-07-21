from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render
from .utils import load_giang_vien_from_csv, load_mon_hoc_from_csv, load_phong_hoc_from_csv, load_lop_hoc_phan_from_csv, load_tiet_hoc_from_csv, check_schedule_conflict
from .models import GiangVien, MonHoc, PhongHoc, LopHocPhan, TietHoc, ThoiKhoaBieu
from deap import base, creator, tools, algorithms
from .forms import LopHocPhanForm,ThoiKhoaBieuForm
from django.http import HttpResponse, HttpResponseRedirect

import random

def create_individual():
    lop_hoc_phans = list(LopHocPhan.objects.all())
    return [(random.choice(lop_hoc_phans), random.choice(TietHoc.objects.all())) for _ in range(len(lop_hoc_phans))]

def evaluate(individual):
    penalty = 0
    lop_hoc_phan_set = set()
    for ind in individual:
        lop_hoc_phan = ind[0]
        if lop_hoc_phan in lop_hoc_phan_set:
            penalty += 1
        lop_hoc_phan_set.add(lop_hoc_phan)
    
    return penalty,

# Khởi tạo creator và toolbox cho thuật toán di truyền
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

def schedule(request):
    if request.method == "POST":
        ThoiKhoaBieu.objects.all().delete()
        LopHocPhan.objects.all().delete()
        # Đọc dữ liệu từ file CSV và lưu vào cơ sở dữ liệu
        load_giang_vien_from_csv()
        load_mon_hoc_from_csv()
        load_phong_hoc_from_csv()
        load_lop_hoc_phan_from_csv()
        load_tiet_hoc_from_csv()

        # Khởi tạo dân số ban đầu
        population = toolbox.population(n=100)

        # Thiết lập các tham số cho GA
        NGEN = 50
        CXPB = 0.7
        MUTPB = 0.2

        # Chạy GA
        for gen in range(NGEN):
            offspring = algorithms.varAnd(population, toolbox, cxpb=CXPB, mutpb=MUTPB)
            fits = map(toolbox.evaluate, offspring)
            for fit, ind in zip(fits, offspring):
                ind.fitness.values = fit
            population = toolbox.select(offspring, k=len(population))

        # Lấy cá thể tốt nhất và lưu vào thời khóa biểu
        best_ind = tools.selBest(population, 1)[0]
        ThoiKhoaBieu.objects.all().delete()  # Xóa các bản ghi cũ trong thời khóa biểu
        for ind in best_ind:
            thoi_khoa_bieu = ThoiKhoaBieu(
                lop_hoc_phan=ind[0],
                thoi_gian=ind[1],
                ngay_trong_tuan=random.choice(['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy'])
            )
            thoi_khoa_bieu.save()

        # Trả về kết quả cho template
        return render(request, 'pages/schedule.html', {'best_ind': best_ind})

    # Nếu không phải POST request, trả về trang giao diện lập thời khóa biểu
    return render(request, 'pages/schedule.html')



def view_schedule(request):
    timetable = ThoiKhoaBieu.objects.all()
    return render(request, 'pages/schedule_view.html', {'timetable': timetable})

def search_schedule(request):
    giang_viens = GiangVien.objects.all()
    timetable = []
    selected_giang_vien = None

    if request.method == 'GET':
        giang_vien_id = request.GET.get('giang_vien_id')
        if giang_vien_id:
            selected_giang_vien = GiangVien.objects.get(id=giang_vien_id)
            timetable = ThoiKhoaBieu.objects.filter(lop_hoc_phan__giang_vien=selected_giang_vien)

    return render(request, 'pages/search_schedule.html', {'timetable': timetable, 'giang_viens': giang_viens, 'selected_giang_vien': selected_giang_vien})

def suaLopHocPhan(request, lop_hoc_phan_id):
    lop_hoc_phan= get_object_or_404(LopHocPhan, id=lop_hoc_phan_id)
    if request.method == 'POST':
        form = LopHocPhanForm(request.POST, request.FILES, instance=lop_hoc_phan)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/TKB_APP/schedule')
    else:
        form = LopHocPhanForm(instance=lop_hoc_phan)
    return render(request, 'pages/SuaLopHocPhan.html', {'form': form})

def suaThoiKhoaBieu(request, thoi_khoa_bieu_id):
    thoi_khoa_bieu = get_object_or_404(ThoiKhoaBieu, id=thoi_khoa_bieu_id)
    if request.method == 'POST':
        form = ThoiKhoaBieuForm(request.POST, request.FILES, instance=thoi_khoa_bieu)
        if form.is_valid():
            temp_thoi_khoa_bieu = form.save(commit=False)
            if check_schedule_conflict(temp_thoi_khoa_bieu):
                form.add_error(None,'Lỗi rùng lịch,hãy chọn lại' )
            else:
                temp_thoi_khoa_bieu.save()
                return HttpResponseRedirect('/TKB_APP/schedule')
    else:
        form = ThoiKhoaBieuForm(instance=thoi_khoa_bieu)
    return render(request, 'pages/SuaThoiKhoaBieu.html', {'form': form})


