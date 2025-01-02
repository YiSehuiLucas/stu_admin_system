from django import forms
from .models import Teacher, CourseAdapt,Admin
from django.contrib.auth.hashers import check_password, make_password

class AdminProfileForm(forms.ModelForm):
    current_password = forms.CharField(max_length=100, required=False, widget=forms.PasswordInput, label='当前密码')
    new_password = forms.CharField(max_length=100, required=False, widget=forms.PasswordInput, label='新密码')
    class Meta:
        model = Admin
        fields = ['admin_name', 'admin_phnum']

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if current_password:
            if not check_password(current_password, self.instance.password):  # 直接检查实例的密码
                raise forms.ValidationError('当前密码不正确。')
        return current_password
    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        current_password = self.cleaned_data.get('current_password')
        if new_password and not current_password:
            raise forms.ValidationError('请输入当前密码以设置新密码。')
        return new_password

    def save(self, commit=True):
        admin = super().save(commit=False)
        user = admin.admin_id.user
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.password = make_password(new_password)
            if commit:
                user.save()
        if commit:
            admin.save()
        return admin

class TeacherForm(forms.ModelForm):
    depart_ids = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Teacher
        fields = ['tch_name', 'tch_phnum', 'depart_ids']
        widgets = {
            'tch_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tch_phnum': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'tch_name': '教师姓名',
            'tch_phnum': '联系电话',
            'depart_ids': '所属院系',
        }
    def __init__(self, *args, **kwargs):
        super(TeacherForm, self).__init__(*args, **kwargs)
        # 设置院系的选项
        self.fields['depart_ids'].widget.attrs['id'] = 'depart_ids'

class TeacherImportForm(forms.Form):
    file = forms.FileField(label='选择教师信息文件 (CSV 格式)')


class CourseAdaptReviewForm(forms.ModelForm):
    class Meta:
        model = CourseAdapt
        fields = []