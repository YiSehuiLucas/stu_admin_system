from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import User_log
from django.db import connection


# 注册视图
@require_http_methods(['GET', 'POST'])
def register(request):
    if request.method == "GET":
        return render(request, 'register.html')
    # 学生注册
    elif request.POST.get('radio') == 'student':
        username = request.POST.get('user')
        password = request.POST.get('pwd')
        identity = request.POST.get('radio')
        user = User_log.objects.filter(user_name=username).first()
        print(user)
        if not User_log.objects.filter(user_name=username).first():
            User_log.objects.create_user(user_name=username, user_pwd=password,
                                         identity=identity)
            User_log.objects.filter(user_name=username).update(user_pwd=password)
            User_log.objects.filter(user_name=username).update(identity=identity)
            return JsonResponse({"注册成功": "注册成功"})
        else:
            return JsonResponse({"用户已存在": "用户已存在"})
        # 教师注册
    elif request.POST.get('radio') == 'teacher':
        username = request.POST.get('user')
        password = request.POST.get('pwd')
        identity = request.POST.get('radio')
        user = User_log.objects.filter(user_name=username).first()
        print(user)
        if not User_log.objects.filter(user_name=username).first():
            User_log.objects.create_user(user_name=username, user_pwd=password,
                                         identity=identity)
            User_log.objects.filter(user_name=username).update(user_pwd=password)
            User_log.objects.filter(user_name=username).update(identity=identity)
            return JsonResponse({"注册成功": "注册成功"})
        else:
            return JsonResponse({"用户已存在": "用户已存在"})
    elif request.POST.get('radio') == 'admin':
        username = request.POST.get('user')
        password = request.POST.get('pwd')
        identity = request.POST.get('radio')
        user = User_log.objects.filter(user_name=username).first()
        print(user)
        if not User_log.objects.filter(user_name=username).first():
            User_log.objects.create_user(user_name=username, user_pwd=password,
                                         identity=identity)
            User_log.objects.filter(user_name=username).update(user_pwd=password)
            User_log.objects.filter(user_name=username).update(identity=identity)
            return JsonResponse({"注册成功": "注册成功"})
        else:
            return JsonResponse({"用户已存在": "用户已存在"})
    pass


# 登陆视图
@require_http_methods(['GET', 'POST'])
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        if request.method == "POST":
            identity = request.POST.get('radio')
            username = request.POST.get('user')
            password = request.POST.get('pwd')
            print(f"{identity} {username} {password}")
            user = User_log.objects.filter(user_name=username).first()
            use = user.check_password(password)
            # 学生用户登陆
            if identity == 'student':
                stu_id = str(user)
                if use:
                    cursor = connection.cursor()
                    sql = '''SELECT stu_name as 学生姓名
                                FROM student
                                WHERE stu_id = %s;'''
                    cursor.execute(sql, stu_id)
                    name = cursor.fetchall()
                    print(type(stu_id))
                    print(name)
                    name = name[0][0]
                    cursor.close()
                    return render(request, 'stu_main.html', {"stu_id": stu_id, "name": name})
                else:
                    return JsonResponse({'error': '用户名或密码错误'})
            # 教师用户登陆
            elif identity == 'teacher':
                tch_id = str(user)
                if use:
                    cursor = connection.cursor()
                    sql = '''SELECT tch_name as 教师姓名
                                       FROM teacher
                                       WHERE tch_id = %s;'''
                    cursor.execute(sql, tch_id)
                    tch_name = cursor.fetchall()
                    tch_name = tch_name[0][0]
                    cursor.close()
                    cursor.close()
                    return render(request, 'teach_index.html', {"tch_id": tch_id, "name": tch_name})
                else:
                    return JsonResponse({'error': '用户名或密码错误'})

            # 管理员用户登陆
            elif identity == 'admin':
                admin_id = str(user)
                if use:
                    cursor = connection.cursor()
                    sql = '''SELECT admin_name as 管理员姓名
                                       FROM admin
                                       WHERE admin_id = %s;'''
                    cursor.execute(sql, admin_id)
                    admin_name = cursor.fetchall()
                    admin_name = admin_name[0][0]
                    cursor.close()
                    cursor.close()
                    return render(request, 'admins/admin_dashboard.html', {"admin_id": admin_id, "admin_name": admin_name})
                else:
                    return JsonResponse({'error': '用户名或密码错误'})
                pass
            else:
                return JsonResponse({'error': '用户名或密码错误'})
        else:
            return JsonResponse({'error': 'error'})
