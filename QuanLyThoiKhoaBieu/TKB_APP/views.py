from django.shortcuts import redirect, render
from .models import GiangVien, MonHoc, PhongHoc, LopHocPhan, TietHoc, ThoiKhoaBieu
from datetime import date, timedelta
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
        return redirect('show_tkb')
    
    else:
        # Hiển thị trang nạp dữ liệu (có thể là một form để người dùng nhấn nút POST)
        return render(request, 'pages/schedule.html')

def show_tkb(request):
    # Lấy tất cả dữ liệu thời khóa biểu
    timetable = ThoiKhoaBieu.objects.all()
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return render(request, 'pages/show_schedule.html', {'timetable': timetable, 'days_of_week': days_of_week})