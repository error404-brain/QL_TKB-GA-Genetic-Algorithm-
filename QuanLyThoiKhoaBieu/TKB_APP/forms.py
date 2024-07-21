from django import forms
from .models import GiangVien,MonHoc,PhongHoc,TietHoc,LopHocPhan,ThoiKhoaBieu


class LopHocPhanForm(forms.ModelForm):
    class Meta:
        model = LopHocPhan
        fields = ['mon_hoc','giang_vien','phong_hoc','SiSo']
    def save(self,commit = True):
        lop_hoc_phan = super().save(commit= False)
        if commit:
            lop_hoc_phan.save()
        return lop_hoc_phan
        
class ThoiKhoaBieuForm(forms.ModelForm):
    class Meta:
        model = ThoiKhoaBieu
        fields = ['lop_hoc_phan','thoi_gian','ngay_trong_tuan']
    def save(self,commit = True):
        thoi_khoa_bieu = super().save(commit= False)
        if commit:
            thoi_khoa_bieu.save()
        return thoi_khoa_bieu