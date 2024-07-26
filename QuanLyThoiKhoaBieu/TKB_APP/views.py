from django.shortcuts import get_object_or_404, redirect, render
from .models import GiangVien, MonHoc, PhongHoc, LopHocPhan, TietHoc, ThoiKhoaBieu
from datetime import timedelta, date, datetime
from django.utils import timezone
import random
from .utils import load_giang_vien_from_csv, load_mon_hoc_from_csv, load_phong_hoc_from_csv, load_lop_hoc_phan_from_csv, load_tiet_hoc_from_csv


# Danh sách các ngày lễ chỉ với tháng và ngày
HOLIDAYS = [
    (1, 1),   # Ngày 1 tháng 1
    (2, 14),  # Ngày 14 tháng 2
    (3, 8),   # Ngày 8 tháng 3
    (4, 30),  # Ngày 30 tháng 4
    (5, 1),   # Ngày 1 tháng 5
    # Thêm các ngày lễ khác tại đây
]

# Hàm kiểm tra ngày lễ
def is_holiday(day):
    return (day.month, day.day) in HOLIDAYS

# Tìm ngày học tiếp theo không trùng ngày lễ
def find_next_available_day(day):
    while is_holiday(day):
        day += timedelta(days=1)
    return day

# Khởi tạo cá thể
def create_individual():
    individual = []
    for lop_hoc_phan in LopHocPhan.objects.all():
        if lop_hoc_phan.NgayKetThuc >= date.today():
            tiet_hoc = random.choice(TietHoc.objects.all())
            ngay_trong_tuan = random.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
            # Chuyển đổi ngày trong tuần thành ngày thực tế
            ngay_trong_tuan = date.today() + timedelta(days=(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(ngay_trong_tuan) - date.today().weekday()))
            ngay_trong_tuan = find_next_available_day(ngay_trong_tuan)
            individual.append((lop_hoc_phan, tiet_hoc, ngay_trong_tuan))
    return individual

# Hàm đánh giá (fitness)
def fitness(individual):
    score = 0
    schedule = {}
    for lop_hoc_phan, tiet_hoc, ngay_trong_tuan in individual:
        key = (lop_hoc_phan.phong_hoc, tiet_hoc, ngay_trong_tuan)
        if key not in schedule:
            schedule[key] = lop_hoc_phan
        else:
            score -= 1  # Phòng học bị trùng
        if (lop_hoc_phan.giang_vien, tiet_hoc, ngay_trong_tuan) in schedule.values():
            score -= 1  # Giảng viên bị trùng
    return score

# Chọn lọc (selection)
def selection(population):
    population.sort(key=lambda x: fitness(x), reverse=True)
    return population[:len(population)//2]

# Lai ghép (crossover)
def crossover(parent1, parent2):
    index = random.randint(0, len(parent1)-1)
    child1 = parent1[:index] + parent2[index:]
    child2 = parent2[:index] + parent1[index:]
    return child1, child2

# Đột biến (mutation)
def mutate(individual):
    index = random.randint(0, len(individual)-1)
    lop_hoc_phan, tiet_hoc, ngay_trong_tuan = individual[index]
    tiet_hoc = random.choice(TietHoc.objects.all())
    ngay_trong_tuan = random.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    ngay_trong_tuan = date.today() + timedelta(days=(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(ngay_trong_tuan) - date.today().weekday()))
    ngay_trong_tuan = find_next_available_day(ngay_trong_tuan)
    individual[index] = (lop_hoc_phan, tiet_hoc, ngay_trong_tuan)

# Thuật toán di truyền
def genetic_algorithm(generations=100, population_size=100):
    population = [create_individual() for _ in range(population_size)]
    for generation in range(generations):
        population = selection(population)
        next_population = []
        while len(next_population) < population_size:
            parent1, parent2 = random.sample(population, 2)
            child1, child2 = crossover(parent1, parent2)
            mutate(child1)
            mutate(child2)
            next_population.extend([child1, child2])
        population = next_population
    best_individual = max(population, key=lambda x: fitness(x))
    return best_individual

def load_schedule_view(request):
    if request.method == 'POST':
        # Xóa dữ liệu cũ
        LopHocPhan.objects.all().delete()
        ThoiKhoaBieu.objects.all().delete()
        # Load data từ các tệp CSV
        load_giang_vien_from_csv()
        load_mon_hoc_from_csv()
        load_phong_hoc_from_csv()
        load_lop_hoc_phan_from_csv()
        load_tiet_hoc_from_csv()
        # Sắp xếp thời khóa biểu
        best_schedule = genetic_algorithm()
        # Lưu thời khóa biểu vào cơ sở dữ liệu
        for lop_hoc_phan, tiet_hoc, ngay_trong_tuan in best_schedule:
            ThoiKhoaBieu.objects.create(
                lop_hoc_phan=lop_hoc_phan,
                thoi_gian=tiet_hoc,
                ngay_trong_tuan=ngay_trong_tuan.strftime('%A')  # Lưu ngày trong tuần dưới dạng chuỗi
            )
        # Chuyển hướng đến trang hiển thị thời khóa biểu
        return redirect('find_tkb_by_id')
    
    else:
        # Hiển thị trang nạp dữ liệu (có thể là một form để người dùng nhấn nút POST)
        return render(request, 'pages/schedule.html')



def show_tkb(request):
    timetable = ThoiKhoaBieu.objects.all()
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return render(request, 'pages/show_schedule.html', {'timetable': timetable, 'days_of_week': days_of_week})


def find_tkb_by_id(request):
    giang_vien_s = GiangVien.objects.all()
    giang_vien_id = request.GET.get('giang_vien_id')
    start_date_str = request.GET.get('start_date')
    next_week = request.GET.get('next_week', 'false') == 'true'
    prev_week = request.GET.get('prev_week','false') == 'true'
    if request.method == 'POST':
        giang_vien_id = request.POST.get('giang_vien_id')
        start_date_str = request.POST.get('start_date')
    
    if giang_vien_id:
        giang_vien = get_object_or_404(GiangVien, id=giang_vien_id)
        lop_hoc_phan_s = LopHocPhan.objects.filter(giang_vien=giang_vien)

        if not lop_hoc_phan_s.exists():
            return render(request, 'pages/find_TKB.html', {
                'giang_viens': giang_vien_s, 
                'error': 'Không có lớp học phần nào cho giảng viên này.'
            })
        
        if not start_date_str:
            start_date = lop_hoc_phan_s.earliest('NgayBatDau').NgayBatDau
        else:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            if next_week:
                start_date += timedelta(weeks=1)
            if prev_week:
                start_date -= timedelta(weeks=1)

        start_date_of_week = start_date - timedelta(days=start_date.weekday())
        days_of_week =  ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        days_of_weeks = {days_of_week[i]: start_date_of_week + timedelta(days=i) for i in range(7)}

        timetable = ThoiKhoaBieu.objects.filter(
            lop_hoc_phan__giang_vien=giang_vien,
            lop_hoc_phan__NgayBatDau__lte=start_date_of_week + timedelta(days=6),
            lop_hoc_phan__NgayKetThuc__gte=start_date_of_week
        )
        writing_thoiKhoaBieu_csv()
        return render(request, 'pages/show_schedule.html', {
            'timetable': timetable,
            'days_of_weeks': days_of_weeks,
            'start_date_of_week': start_date_of_week,
            'giang_vien': giang_vien,
            'giang_vien_id': giang_vien_id,
            'start_date': start_date.strftime('%Y-%m-%d')
        })

    return render(request, 'pages/find_TKB.html', {'giang_viens': giang_vien_s})