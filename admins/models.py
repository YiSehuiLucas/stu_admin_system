from django.db import models
from django.contrib.auth.models import AbstractUser


class User(models.Model):
    IDENTITY_CHOICES = [
        ('管理员', '管理员'),
        ('教师', '教师'),
        ('学生', '学生'),
    ]
    user_id = models.CharField(max_length=100, primary_key=True, verbose_name='用户ID')
    password = models.CharField(max_length=100, verbose_name='密码')
    identity = models.CharField(max_length=100, choices=IDENTITY_CHOICES, verbose_name='身份')

    def __str__(self):
        return self.user_id

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户信息'


class Admin(models.Model):
    admin_id = models.OneToOneField(User, on_delete=models.CASCADE, max_length=100, db_column='admin_id',
                                    primary_key=True, verbose_name='管理员ID')
    admin_name = models.CharField(max_length=100, verbose_name='管理员姓名')
    admin_phnum = models.CharField(max_length=20, verbose_name='联系电话')

    def __str__(self):
        return self.admin_name

    class Meta:
        db_table = 'admin'
        verbose_name = '管理员'
        verbose_name_plural = '管理员信息'


class Semesters(models.Model):
    semester = models.CharField(max_length=20, unique=True, primary_key=True, verbose_name='学期')

    def __str__(self):
        return self.semester

    class Meta:
        db_table = 'semester'
        verbose_name = '学期表'
        verbose_name_plural = '学期'


class Teacher(models.Model):
    tch_id = models.OneToOneField(User, on_delete=models.CASCADE, max_length=100, db_column='tch_id', primary_key=True,
                                  verbose_name='教师ID')
    tch_name = models.CharField(max_length=100, verbose_name='教师姓名')
    tch_phnum = models.CharField(max_length=100, verbose_name='联系电话')

    def __str__(self):
        return self.tch_name

    class Meta:
        db_table = 'teacher'
        verbose_name = '教师'
        verbose_name_plural = '教师信息'
    # def get_departments(self):
    #     return ", ".join([depart.depart_id for depart in self.teacherdepart_set.all()])


class Depart(models.Model):
    depart_id = models.CharField(max_length=100, primary_key=True, verbose_name='院系ID')
    depart_name = models.CharField(max_length=100, verbose_name='院系名')

    def __str__(self):
        return self.depart_name

    class Meta:
        db_table = 'depart'
        verbose_name = '院系表'
        verbose_name_plural = '院系表'


class TeacherDepart(models.Model):
    tch_id = models.ForeignKey(Teacher, on_delete=models.CASCADE, max_length=100, db_column='tch_id',
                               verbose_name='教师ID')
    depart_id = models.ForeignKey(Depart, on_delete=models.CASCADE, max_length=100, db_column='depart_id',
                                  verbose_name='院系ID')

    def __str__(self):
        return f"{self.tch_id.tch_name} - {self.depart_id.depart_name}"

    class Meta:
        unique_together = ('tch_id', 'depart_id')
        db_table = 'teacherdepart'
        verbose_name = '教师院系关联'
        verbose_name_plural = '教师院系关联表'


class Student(models.Model):
    stu_id = models.OneToOneField(User, on_delete=models.CASCADE, max_length=100, db_column='stu_id', primary_key=True,
                                  verbose_name='学生ID')
    stu_name = models.CharField(max_length=100, verbose_name='学生姓名')
    stu_phnum = models.CharField(max_length=100, verbose_name='联系电话')
    stu_semester = models.ForeignKey(Semesters, on_delete=models.CASCADE, max_length=100, db_column='stu_semester',
                                     verbose_name='年级')

    def __str__(self):
        return self.stu_name

    class Meta:
        db_table = 'student'
        verbose_name = '学生表'
        verbose_name_plural = '学生信息'


class Class(models.Model):
    class_id = models.CharField(max_length=100, primary_key=True, verbose_name='班级ID')
    class_name = models.CharField(max_length=100, verbose_name='班级名')

    def __str__(self):
        return self.class_name

    class Meta:
        db_table = 'class'
        verbose_name = '班级表'
        verbose_name_plural = '班级表'


class StudentClass(models.Model):
    stu_id = models.ForeignKey(Student, on_delete=models.CASCADE, max_length=100, db_column='stu_id',
                               verbose_name='学生ID')
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, max_length=100, db_column='class_id',
                                 verbose_name='班级ID')

    def __str__(self):
        return self.class_id

    class Meta:
        db_table = 'studentclass'
        verbose_name = '学生班级关联表'
        verbose_name_plural = '学生班级关联表'


class Major(models.Model):
    major_id = models.CharField(max_length=100, primary_key=True, verbose_name='专业ID')
    major_name = models.CharField(max_length=100, verbose_name='专业名')

    def __str__(self):
        return self.major_name

    class Meta:
        db_table = 'major'
        verbose_name = '专业表'
        verbose_name_plural = '专业表'


class StudentMajor(models.Model):
    stu_id = models.ForeignKey(Student, on_delete=models.CASCADE, max_length=100, db_column='stu_id',
                               verbose_name='学生ID')
    major_id = models.ForeignKey(Major, on_delete=models.CASCADE, max_length=100, db_column='major_id',
                                 verbose_name='专业ID')

    def __str__(self):
        return self.major_id

    class Meta:
        db_table = 'studentmajor'
        verbose_name = '学生专业关联表'
        verbose_name_plural = '学生专业关联表'


class Course(models.Model):
    cour_id = models.CharField(max_length=100, primary_key=True, verbose_name='课程ID')
    cour_name = models.CharField(max_length=100, verbose_name='课程名')
    cour_credits = models.FloatField(verbose_name='学分')
    cour_semester = models.CharField(max_length=100, verbose_name='开设学期')

    def __str__(self):
        return self.cour_name

    class Meta:
        db_table = 'course'
        verbose_name = '课程表'
        verbose_name_plural = '课程信息'


class CourseAdapt(models.Model):
    STATUS_CHOICES = [
        ('未审核', '未审核'),
        ('同意', '同意'),
        ('否决', '否决'),
    ]
    DAY_OF_WEEK_CHOICES = [
        ('周一', '周一'),
        ('周二', '周二'),
        ('周三', '周三'),
        ('周四', '周四'),
        ('周五', '周五'),
        ('周六', '周六'),
        ('周日', '周日'),
    ]
    ca_id = models.AutoField(primary_key=True, verbose_name="调课申请ID")
    tch_id = models.ForeignKey(Teacher, on_delete=models.CASCADE, db_column='tch_id', verbose_name='教师ID')
    cour_id = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='cour_id', verbose_name='课程ID')
    week = models.CharField(max_length=100, verbose_name='第几周')
    classroom = models.CharField(max_length=100, verbose_name='上课地点')
    dayofweek = models.CharField(max_length=100, verbose_name='周几')
    timeslot = models.CharField(max_length=100, verbose_name='时间段')
    reason = models.CharField(max_length=500, verbose_name='申请理由')
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='未审核', verbose_name='状态')

    def __str__(self):
        return self.ca_id

    class Meta:
        db_table = 'courseadapt'
        verbose_name = '调课申请表'
        verbose_name_plural = '调课申请表'


class WaiverApplication(models.Model):
    STATUS_CHOICES = [
        ('未审核', '未审核'),
        ('审核中', '审核中'),
        ('同意', '同意'),
        ('否决', '否决'),
    ]
    wa_id = models.AutoField(primary_key=True, verbose_name="免听申请ID")
    stu_id = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='stu_id', verbose_name='学生ID')
    cour_id = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='cour_id', verbose_name='课程ID')
    tch_id = models.ForeignKey(Teacher, on_delete=models.CASCADE, db_column='tch_id', verbose_name='教师ID')
    reason = models.CharField(max_length=500, verbose_name='申请理由')
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='未审核', verbose_name='状态')

    def __str__(self):
        return self.wa_id

    class Meta:
        db_table = 'waiverapplication'
        verbose_name = '免听申请表'
        verbose_name_plural = '免听申请表'


class CoursePlan(models.Model):
    plan_id = models.CharField(primary_key=True, max_length=100, verbose_name='计划ID')
    plan_content = models.CharField(max_length=1000, verbose_name='内容')
    plan_submittime = models.DateTimeField(verbose_name='提交时间')

    def __str__(self):
        return self.plan_id

    class Meta:
        db_table = 'courseplan'
        verbose_name = '课程计划表'
        verbose_name_plural = '课程计划表'


class TeacherCourse_1(models.Model):
    tch_id = models.ForeignKey(Teacher, on_delete=models.CASCADE, max_length=100, db_column='tch_id',
                               verbose_name='教师ID')
    cour_id = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='cour_id', verbose_name='课程ID')

    def __str__(self):
        return self.cour_id

    class Meta:
        db_table = 'teachercourse'
        verbose_name = '教师课程关联表'
        verbose_name_plural = '教师课程关联表'
