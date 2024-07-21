import csv
from .models import GiangVien, MonHoc, PhongHoc, LopHocPhan, TietHoc,ThoiKhoaBieu

def load_giang_vien_from_csv():
    with open('C:/Users/Admin/Desktop/DoChuyenNganh_beta2.0/QuanLyThoiKhoaBieu/TKB_APP/CSV/giangvien.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            GiangVien.objects.update_or_create(
                TenGiangVien=row['TenGiangVien'],
                Email=row['Email'],
                SoDienThoai=row['SoDienThoai'],
                DiaChi=row['DiaChi']
            )

def load_mon_hoc_from_csv():
    with open('C:/Users/Admin/Desktop/DoChuyenNganh_beta2.0/QuanLyThoiKhoaBieu/TKB_APP/CSV/monhoc.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            MonHoc.objects.update_or_create(
                TenMonHoc=row['TenMonHoc'],
                SoTinhChi=row['SoTinhChi'],
                LoaiMonHoc=row['LoaiMonHoc']
            )

def load_phong_hoc_from_csv():
    with open('C:/Users/Admin/Desktop/DoChuyenNganh_beta2.0/QuanLyThoiKhoaBieu/TKB_APP/CSV/phonghoc.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            PhongHoc.objects.update_or_create(
                TenPhongHoc=row['TenPhongHoc'],
                SucChua=row['SucChua']
            )

def load_lop_hoc_phan_from_csv():
    with open('C:/Users/Admin/Desktop/DoChuyenNganh_beta2.0/QuanLyThoiKhoaBieu/TKB_APP/CSV/lophocphan.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
                # Sử dụng ID từ file CSV để truy vấn các đối tượng
                mon_hoc_id = int(row['mon_hoc_id'])
                giang_vien_id = int(row['giang_vien_id'])
                phong_hoc_id = int(row['phong_hoc_id'])
                
                # Tạo mới LopHocPhan
                LopHocPhan.objects.update_or_create(
                    mon_hoc_id=mon_hoc_id,
                    giang_vien_id=giang_vien_id,
                    phong_hoc_id=phong_hoc_id,
                    SiSo=row['SiSo']
                )


def load_tiet_hoc_from_csv():
    with open('C:/Users/Admin/Desktop/DoChuyenNganh_beta2.0/QuanLyThoiKhoaBieu/TKB_APP/CSV/tiethoc.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            TietHoc.objects.update_or_create(
                TietTrongKhungGio=row['TietTrongKhungGio'],
                GioBatDau=row['GioBatDau'],
                GioKetThuc=row['GioKetThuc']
            )
def check_schedule_conflict(thoi_khoa_bieu):
    existing_entries = ThoiKhoaBieu.objects.filter(
        thoi_gian=thoi_khoa_bieu.thoi_gian,
        ngay_trong_tuan=thoi_khoa_bieu.ngay_trong_tuan
    ).exclude(id=thoi_khoa_bieu.id)
    return existing_entries.exists()
