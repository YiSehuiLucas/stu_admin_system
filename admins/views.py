# admins/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Teacher, CourseAdapt, User, Depart, TeacherDepart, WaiverApplication, Admin, Student
from .forms import TeacherForm, TeacherImportForm, CourseAdaptReviewForm, AdminProfileForm
import csv
from io import TextIOWrapper
from django.db import connection, DatabaseError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db import transaction
import logging
from django.views.decorators.http import require_http_methods
logger = logging.getLogger(__name__)


def is_admin(user):
    return user.is_authenticated and user.identity == '管理员'


# @login_required
# @user_passes_test(is_admin)
def admin_dashboard(request, user_id):
    try:
        admin = Admin.objects.select_related('admin_id__admin').get(admin_id__user_id=user_id)
    except Admin.DoesNotExist:
        messages.error(request, '管理员信息不存在。')
        return redirect('login')  # 重定向到登录页面或其他适当的页面

    return render(request, 'admins/admin_dashboard.html', {'admin_id': user_id})


def admin_profile(request, user_id):
    try:
        admin = Admin.objects.select_related('admin_id__admin').get(admin_id__user_id=user_id)
    except Admin.DoesNotExist:
        messages.error(request, '管理员信息不存在。')
        return redirect('admin_dashboard', user_id=user_id)

    if request.method == 'POST':
        form = AdminProfileForm(request.POST, instance=admin)
        if form.is_valid():
            form.save()
            messages.success(request, '个人信息更新成功。')
            return redirect('admin_profile', user_id=user_id)
        else:
            messages.error(request, '请修正表单中的错误。')
    else:
        form = AdminProfileForm(instance=admin)

    return render(request, 'admins/admin_profile.html', {
        'admin': admin,
        'form': form,
        'user_id': user_id
    })


def admin_edit(request, user_id):
    admin = Admin.objects.select_related('admin_id__admin').get(admin_id__user_id=user_id)
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, instance=admin)
        if form.is_valid():
            form.save()
            messages.success(request, '个人信息更新成功。')
            return redirect('admin_profile', user_id=user_id)
        else:
            messages.error(request, '请修正表单中的错误。')
    else:
        form = AdminProfileForm(instance=admin)
    return render(request, 'admins/admin_edit.html', {
        'admin': admin,
        'form': form,
    })

    # -----------------------------------以下是教师列表部分--------------------------------------


# @login_required
# @user_passes_test(is_admin)
def teacher_list(request, user_id):
    # 获取搜索参数，默认为空字符串
    search_query = request.GET.get('q', '').strip()
    params = []
    conditions = []

    # 构建查询语句
    query = """
        SELECT 
            teacher.tch_id, 
            teacher.tch_name, 
            teacher.tch_phnum, 
            depart.depart_id, 
            depart.depart_name
        FROM 
            teacher
        LEFT JOIN 
            teacherdepart ON teacher.tch_id = teacherdepart.tch_id
        LEFT JOIN 
            depart ON teacherdepart.depart_id = depart.depart_id
    """

    # 添加搜索条件
    if search_query:
        # 假设教师ID和教师姓名都是字符串类型
        conditions.append("(teacher.tch_id LIKE %s OR teacher.tch_name LIKE %s)")
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # 分页参数
    paginate_by = 10  # 每页显示10条记录，可以根据需要调整
    page = request.GET.get('page', 1)
    offset = (int(page) - 1) * paginate_by
    query += " ORDER BY teacher.tch_id LIMIT %s OFFSET %s"
    params.append(paginate_by)
    params.append(offset)

    # 执行查询
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        teachers = cursor.fetchall()

    # 获取总记录数
    count_query = """
        SELECT COUNT(DISTINCT teacher.tch_id)
        FROM 
            teacher
        LEFT JOIN 
            teacherdepart ON teacher.tch_id = teacherdepart.tch_id
        LEFT JOIN 
            depart ON teacherdepart.depart_id = depart.depart_id
    """
    if conditions:
        count_query += " WHERE " + " AND ".join(conditions)

    with connection.cursor() as cursor:
        cursor.execute(count_query, params[:-2])  # 排除 LIMIT 和 OFFSET 参数
        total = cursor.fetchone()[0]

    # 创建分页器
    paginator = Paginator(range(total), paginate_by)
    page_obj = paginator.page(page)

    # 准备教师数据
    teacher_data = []
    for teacher in teachers:
        teacher_data.append({
            'tch_id': teacher[0],
            'tch_name': teacher[1],
            'tch_phnum': teacher[2],
            'depart_ids': [teacher[3]],
            'depart_names': [teacher[4]],
        })

    # 准备上下文
    context = {
        'teacher_data': teacher_data,
        'search_query': search_query,
        'paginator': paginator,
        'page_obj': page_obj,
        'user_id': user_id
    }

    # 渲染模板
    return render(request, 'admins/teacher_list.html', context)


# @login_required
# @user_passes_test(is_admin)
def teacher_create(request,user_id):
    if request.method == 'POST':
        # 获取用户输入的数据
        user_idadd = request.POST.get('user_id_add').strip()
        tch_name = request.POST.get('tch_name').strip()
        tch_phnum = request.POST.get('tch_phnum').strip()
        depart_id = request.POST.get('depart_id').strip()
        default_password = '000000'  # 默认密码，可以根据需要修改

        # 验证输入数据
        if not user_idadd or not tch_name or not tch_phnum or not depart_id:
            messages.error(request, '所有字段都是必填的。')
            return render(request, 'admins/teacher_form.html')

        try:
            with connection.cursor() as cursor:
                # 开始事务
                with transaction.atomic():
                    # 验证部门ID是否存在
                    cursor.execute("""
                        SELECT depart_id FROM depart WHERE depart_id = %s
                    """, [depart_id])
                    if not cursor.fetchone():
                        messages.error(request, '指定的部门ID不存在。')
                        return render(request, 'admins/teacher_form.html')

                    # 检查用户ID是否已经存在（可选，根据需求决定是否允许重复）
                    cursor.execute("""
                        SELECT user_id FROM user WHERE user_id = %s
                    """, [user_idadd])
                    if cursor.fetchone():
                        messages.error(request, '用户ID已经存在，请选择其他ID。')
                        return render(request, 'admins/teacher_form.html')

                    # 更新 User 表：设置用户身份为“教师”并设置默认密码
                    cursor.execute("""
                        UPDATE user
                        SET identity = %s, password = %s
                        WHERE user_id = %s
                    """, ['教师', default_password, user_idadd])

                    # 如果用户ID不存在，则插入新用户
                    if cursor.rowcount == 0:
                        cursor.execute("""
                            INSERT INTO user (user_id, password, identity)
                            VALUES (%s, %s, %s)
                        """, [user_idadd, default_password, '教师'])

                    # 插入教师信息到 Teacher 表
                    cursor.execute("""
                        INSERT INTO teacher (tch_id, tch_name, tch_phnum)
                        VALUES (%s, %s, %s)
                    """, [user_idadd, tch_name, tch_phnum])

                    # 插入教师与部门的关联信息到 TeacherDepart 表
                    cursor.execute("""
                        INSERT INTO teacherdepart (tch_id, depart_id)
                        VALUES (%s, %s)
                    """, [user_idadd, depart_id])

            messages.success(request, '教师信息创建成功。')
            return redirect('teacher_list', user_id=user_id)
        except Exception as e:
            # 记录错误日志（可选）
            # logger.error(str(e))
            messages.error(request, '创建教师信息时发生错误，请稍后再试。')
            return render(request, 'admins/teacher_form.html',{'user_id': user_id})
    if request.method == 'GET':
        return render(request, 'admins/teacher_form.html',{'user_id': user_id})


# @login_required
# @user_passes_test(is_admin)
def teacher_edit(request, tch_id):
    try:
        # 获取 Teacher 对象
        teacher = Teacher.objects.select_related('tch_id__teacher').get(tch_id=tch_id)
    except Teacher.DoesNotExist:
        messages.error(request, '教师信息不存在。')
        return redirect('teacher_list')

    if request.method == 'POST':
        # 获取用户输入的数据
        tch_phnum = request.POST.get('tch_phnum').strip()
        depart_id = request.POST.get('depart_id').strip()

        # 验证输入数据
        if not tch_phnum or not depart_id:
            messages.error(request, '所有字段都是必填的。')
            return render(request, 'admins/teacher_edit.html', {'teacher': teacher})

        try:
            with connection.cursor() as cursor:
                # 开始事务
                with transaction.atomic():
                    # 验证部门ID是否存在
                    cursor.execute("""
                        SELECT depart_id FROM depart WHERE depart_id = %s
                    """, [depart_id])
                    if not cursor.fetchone():
                        messages.error(request, '指定的部门ID不存在。')
                        return render(request, 'admins/teacher_edit.html', {'teacher': teacher})

                    # 更新 Teacher 表中的联系电话
                    cursor.execute("""
                        UPDATE teacher
                        SET tch_phnum = %s
                        WHERE tch_id = %s
                    """, [tch_phnum, tch_id])

                    # 更新 TeacherDepart 表中的部门ID
                    # 首先检查是否存在关联记录
                    cursor.execute("""
                        SELECT tch_id FROM teacherdepart WHERE tch_id = %s
                    """, [tch_id])
                    if cursor.fetchone():
                        # 如果存在，则更新
                        cursor.execute("""
                            UPDATE teacherdepart
                            SET depart_id = %s
                            WHERE tch_id = %s
                        """, [depart_id, tch_id])
                    else:
                        # 如果不存在，则插入
                        cursor.execute("""
                            INSERT INTO teacherdepart (tch_id, depart_id)
                            VALUES (%s, %s)
                        """, [tch_id, depart_id])

            messages.success(request, '教师信息更新成功。')
            return redirect('teacher_list')
        except Exception as e:
            # 记录错误日志（可选）
            # logger.error(str(e))
            messages.error(request, '更新教师信息时发生错误，请稍后再试。')
            return render(request, 'admins/teacher_edit.html', {'teacher': teacher})

    else:
        return render(request, 'admins/teacher_edit.html', {'teacher': teacher})


# @login_required
# @user_passes_test(is_admin)
def teacher_delete(request, tch_id, user_id):
    teacher = get_object_or_404(Teacher, tch_id__user_id=tch_id)
    if request.method == 'POST':
        teacher.delete()
        messages.success(request, '教师信息删除成功')
        return redirect('teacher_list',user_id=user_id)
    return render(request, 'admins/teacher_confirm_delete.html', {'teacher': teacher,'user_id':user_id})


# @login_required
# @user_passes_test(is_admin)
def teacher_import(request,user_id):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, '请上传一个 CSV 文件。')
            return render(request, 'admins/teacher_import.html')

        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            # 验证 CSV 文件是否包含必要的表头
            required_headers = {'tch_id', 'tch_name', 'tch_phnum', 'depart_id'}
            if not required_headers.issubset(reader.fieldnames):
                messages.error(request, 'CSV 文件缺少必要的表头。')
                return render(request, 'admins/teacher_import.html')

            with connection.cursor() as cursor:
                # 开始事务
                with transaction.atomic():
                    for row in reader:
                        tch_id = row['tch_id'].strip()
                        tch_name = row['tch_name'].strip()
                        tch_phnum = row['tch_phnum'].strip()
                        depart_id = row['depart_id'].strip()
                        default_password = '000000'  # 默认密码

                        # 验证部门ID是否存在
                        cursor.execute("""
                            SELECT depart_id FROM depart WHERE depart_id = %s
                        """, [depart_id])
                        if not cursor.fetchone():
                            messages.error(request, f'部门ID "{depart_id}" 不存在。跳过该行。')
                            continue

                        # 更新或插入 User 表
                        cursor.execute("""
                            INSERT INTO user (user_id, password, identity)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (user_id) DO UPDATE
                            SET password = EXCLUDED.password, identity = EXCLUDED.identity
                        """, [tch_id, default_password, '教师'])

                        # 更新 Teacher 表
                        cursor.execute("""
                            INSERT INTO teacher (tch_id, tch_name, tch_phnum)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (tch_id) DO UPDATE
                            SET tch_name = EXCLUDED.tch_name, tch_phnum = EXCLUDED.tch_phnum
                        """, [tch_id, tch_name, tch_phnum])

                        # 更新 TeacherDepart 表
                        cursor.execute("""
                            INSERT INTO teacherdepart (tch_id, depart_id)
                            VALUES (%s, %s)
                            ON CONFLICT (tch_id, depart_id) DO UPDATE
                            SET tch_id = EXCLUDED.tch_id, depart_id = EXCLUDED.depart_id
                        """, [tch_id, depart_id])

            messages.success(request, '教师信息导入成功。')
            return redirect('teacher_list',user_id=user_id)
        except Exception as e:
            # 记录错误日志（可选）
            # logger.error(str(e))
            messages.error(request, '导入教师信息时发生错误，请检查 CSV 文件格式。')
            return render(request, 'admins/teacher_import.html',{'user_id': user_id})
    if request.method == 'GET':
        return render(request, 'admins/teacher_import.html',{'user_id':user_id})


# ------------------------------以下是调课审核功能-----------------------------------------------------
# @login_required
# @user_passes_test(is_admin)
def courseadapt_list(request):
    week = request.GET.get('week', '')
    status_filter = request.GET.get('status_filter', '')
    # 初始化查询集
    courseadapts = CourseAdapt.objects.all()

    if week:
        courseadapts = courseadapts.filter(Q(week=week))
    if status_filter:
        courseadapts = courseadapts.filter(status=status_filter)

    weeks = [
        ('第一周', '第一周'),
        ('第二周', '第二周'),
        ('第三周', '第三周'),
        ('第四周', '第四周'),
        ('第五周', '第五周'),
        ('第六周', '第六周'),
        ('第七周', '第七周'),
        ('第八周', '第八周'),
        ('第九周', '第九周'),
        ('第十周', '第十周'),
        ('第十一周', '第十一周'),
        ('第十二周', '第十二周'),
        ('第十三周', '第十三周'),
        ('第十四周', '第十四周'),
        ('第十五周', '第十五周'),
        ('第十六周', '第十六周'),
        ('第十七周', '第十七周'),
        ('第十八周', '第十八周'),
    ]
    statuses = CourseAdapt.STATUS_CHOICES

    paginator = Paginator(courseadapts, 10)  # 每页显示10条记录
    page = request.GET.get('page')  # 获取当前页码

    try:
        courseadapts_page = paginator.page(page)
    except PageNotAnInteger:
        # 如果页码不是整数，则显示第一页
        courseadapts_page = paginator.page(1)
    except EmptyPage:
        # 如果页码超出范围，则显示最后一页
        courseadapts_page = paginator.page(paginator.num_pages)

    return render(request, 'admins/courseadapt_list.html', {
        'courseadapts': courseadapts_page,
        'weeks': weeks,
        'statuses': statuses,
        'week': week,
        'status_filter': status_filter,
        'paginator': paginator,
        'page': page
    })


# @login_required
# @user_passes_test(is_admin)
def courseadapt_review(request, ca_id):
    courseadapt = get_object_or_404(CourseAdapt, ca_id=ca_id)
    if request.method == 'POST':
        if 'approve' in request.POST:
            # 处理同意申请
            courseadapt.status = '同意'
            courseadapt.save()
            messages.success(request, '调课申请已同意')
            return redirect('courseadapt_review')
        elif 'reject' in request.POST:
            # 处理拒绝申请
            courseadapt.status = '拒绝'
            courseadapt.save()
            messages.success(request, '调课申请已拒绝')
            return redirect('courseadapt_review')
    else:
        form = CourseAdaptReviewForm()
    return render(request, 'admins/courseadapt_review.html', {'courseadapt': courseadapt})


# ------------------------------以下是免听审核功能------------------------------------------------------------
def waiverapplication_list(request):
    # 获取查询参数
    search_query = request.GET.get('q', '').strip()
    filter_status = request.GET.get('status', '').strip()

    # 定义状态映射，将“未审核”替换为“待教师审核”
    status_mapping = {
        '未审核': '待教师审核',
        '审核中': '待管理员审核',
        '同意': '同意',
        '否决': '否决',
    }

    # 构建查询语句
    query = """
        SELECT 
            wa.wa_id,
            stu.stu_id,
            tch.tch_id,
            cou.cour_id,
            cou.cour_name,
            wa.status
        FROM 
            waiverapplication wa
        LEFT JOIN 
            student stu ON wa.stu_id = stu.stu_id
        LEFT JOIN 
            course cou ON wa.cour_id = cou.cour_id
        LEFT JOIN 
            teacher tch ON wa.tch_id = tch.tch_id
    """

    params = []
    conditions = []

    # 添加搜索条件（课程ID或教师ID）
    if search_query:
        conditions.append("(cou.cour_id LIKE %s OR tch.tch_id LIKE %s)")
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    # 添加状态筛选条件
    if filter_status:
        if filter_status == '未审核':
            conditions.append("wa.status = %s")
            params.append('未审核')
        else:
            conditions.append("wa.status = %s")
            params.append(filter_status)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # 分页参数
    paginate_by = 10
    page = request.GET.get('page', 1)
    offset = (int(page) - 1) * paginate_by
    query += " ORDER BY wa.wa_id LIMIT %s OFFSET %s"
    params.append(paginate_by)
    params.append(offset)

    # 执行查询
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        applications = cursor.fetchall()

    # 获取总记录数
    count_query = query.split('ORDER BY')[0]
    count_query = "SELECT COUNT(*) FROM (" + count_query + ") as count_table"
    with connection.cursor() as cursor:
        cursor.execute(count_query, params[:-2])  # 排除 LIMIT 和 OFFSET 参数
        total = cursor.fetchone()[0]

    # 创建分页器
    paginator = Paginator(range(total), paginate_by)
    page_obj = paginator.page(page)

    # 准备展示数据
    application_data = []
    for app in applications:
        application_data.append({
            'wa_id': app[0],
            'stu_id': app[1],
            'tch_id': app[2],
            'cour_id': app[3],
            'cour_name': app[4],
            'status': status_mapping.get(app[5], app[5]),
        })

    # 定义筛选状态选项
    statuses = [
        ('未审核', '待教师审核'),
        ('审核中', '待管理员审核'),
        ('同意', '同意'),
        ('否决', '否决'),
    ]

    # 渲染模板并传递数据
    return render(request, 'admins/waiverapplication_list.html', {
        'applications': application_data,
        'search_query': search_query,
        'filter_status': filter_status,
        'statuses': statuses,
        'paginator': paginator,
        'page_obj': page_obj,
    })


def waiverapplication_detail(request, wa_id):
    application = get_object_or_404(WaiverApplication, wa_id=wa_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'agree':
            application.status = '同意'
            messages.success(request, '申请已同意。')
        elif action == 'reject':
            application.status = '否决'
            messages.success(request, '申请已拒绝。')
        else:
            messages.error(request, '无效的操作。')
            return render(request, 'admins/waiverapplication_detail.html', {'application': application})

        application.save()
        return redirect('admins/waiverapplication_list')

    return render(request, 'admins/waiverapplication_detail.html', {'application': application})


def student_list(request):
    # 获取搜索参数，默认为空字符串
    search_query = request.GET.get('q', '').strip()
    params = []
    conditions = []

    # 构建查询语句
    query = """
        SELECT student.stu_id,
               student.stu_name,
               student.stu_phnum,
               student.stu_semester,
               major.major_name
        FROM student,
             major
        WHERE major.major_name IN (
            SELECT major.major_name
            FROM major
            WHERE major.major_id IN (
                SELECT studentmajor.major_id
                FROM studentmajor
                WHERE studentmajor.stu_id = student.stu_id
            )
        )
    """
    # 添加搜索条件
    if search_query:
        conditions.append("(student.stu_id LIKE %s OR student.stu_name LIKE %s)")
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    # 判断是否需要拼接搜索条件
    if conditions:
        # 如果主查询已有 WHERE，则添加 AND
        if "WHERE" in query:
            query += " AND " + " AND ".join(conditions)
        else:
            query += " WHERE " + " AND ".join(conditions)

    # 添加分页参数
    paginate_by = 10
    page = request.GET.get('page', 1)
    offset = (int(page) - 1) * paginate_by
    query += " ORDER BY student.stu_id LIMIT %s OFFSET %s"
    params.append(paginate_by)
    params.append(offset)

    # 执行查询
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        students = cursor.fetchall()

    # 获取总记录数
    count_query = """
        SELECT COUNT(DISTINCT student.stu_id)
        FROM 
            student
    """
    if conditions:
        count_query += " WHERE " + " AND ".join(conditions)

    with connection.cursor() as cursor:
        cursor.execute(count_query, params[:-2])  # 排除 LIMIT 和 OFFSET 参数
        total = cursor.fetchone()[0]

    # 创建分页器
    paginator = Paginator(range(total), paginate_by)
    page_obj = paginator.page(page)

    # 准备学生数据
    student_data = []
    for student in students:
        student_data.append({
            'stu_id': student[0],
            'stu_name': student[1],
            'stu_phnum': student[2],
            'stu_semester': student[3],
            'stu_major': student[4]
        })
        print(f"{student[0]} {student[1]} {student[2]} {student[3]} {student[4]}")

    # 准备上下文
    context = {
        'student_data': student_data,
        'search_query': search_query,
        'paginator': paginator,
        'page_obj': page_obj,
    }

    # 渲染模板
    return render(request, 'admins/student_list.html', context)

@require_http_methods(['GET', 'POST'])
def student_edit(request, stu_id):
    if request.method == 'GET':
        cursor = connection.cursor()
        sql = '''
        select stu_name
        from student
        where stu_id=%s
        '''
        cursor.execute(sql, stu_id)
        stu_name = cursor.fetchall()
        stu_name = stu_name[0][0]
        print(stu_name)
        return render(request, 'admins/student_edit.html', {"stu_name": stu_name,
                                                            "stu_id": stu_id})
    elif request.method == 'POST':
        stu_name = request.POST.get('stu_name')
        stu_phone = request.POST.get('stu_phone')
        stu_semester = request.POST.get('stu_semester')
        print(f"{stu_name} {stu_phone} {stu_semester}")
        return render(request, 'admins/student_list.html')

@require_http_methods(['GET', 'POST'])
def student_create(request):
    if request.method == 'GET':
        return render(request, 'admins/student_create.html')
    pass


@require_http_methods(['GET', 'POST'])
def student_import(request):
    pass

