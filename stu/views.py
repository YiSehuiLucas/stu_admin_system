from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection

# Create your views here.
def stu_main(request):
    stu = "张顺"
    if request.method == 'GET':
        return render(request,"stu_main.html",{"stu":stu})

def stu_select(request):
    stu=request.GET.get('stu')
    str = " 选择…… "
    btn=True
    btn_name="选课"
    cursor = connection.cursor()
    sql = '''SELECT * FROM semesters;'''
    cursor.execute(sql)
    semesters = cursor.fetchall()
    cursor.close()
    first_semesters = [t[0] for t in semesters]
    cursor = connection.cursor()
    sql = '''SELECT cour_id as 课程代码,
                cour_name as 课程名,
                cour_credits as 学分
                FROM course;'''
    cursor.execute(sql)
    courses = cursor.fetchall()
    cursor.close()
    # courseslist = list(courses)
#     courseslist.append("选课")
#     courses = courseslist
#     for i in courses:
#         print(i)
    if request.method == 'GET':
        return render(request,"stu_select.html",{"stu":stu,"str":str,"semesters":first_semesters,"courses":courses})
    str = request.POST.get('option')
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course_name')
        course_credits = request.POST.get('course_credits')
        print(course_id)
        print(course_name)
        print(course_credits)
        print(str)
        if(str != "选择……"):
            cursor = connection.cursor()
            sql = '''SELECT course.cour_id as 课程代码,
                            course.cour_name as 课程名,
                           course.cour_credits as 学分
                           FROM course
                           WHERE course.cour_semester = %s;'''
            cursor.execute(sql, str)
            courses = cursor.fetchall()
            cursor.close()
        else:
            cursor = connection.cursor()
            sql = '''SELECT cour_id as 课程代码,
                        cour_name as 课程名,
                        cour_credits as 学分
                        FROM course;'''
            cursor.execute(sql)
            courses = cursor.fetchall()
            cursor.close()
        courseslist = list(courses)
        # if(btn):
        #     btn = False
        #     courseslist[3] = "退选"
        #     courses = courseslist
        # else:
        #     btn = True
        #     courseslist[3] = "选课"
        #     courses = courseslist
        return render(request, "stu_select.html", {"stu": stu,"str":str,"semesters":first_semesters,"courses":courses})
    else:
        return HttpResponse("TO DO")

def stu_grade(request):
    stu = request.GET.get('stu')
    str=" 选择…… "
    # views.py 中的数据
    cursor = connection.cursor()
    sql = '''SELECT course.cour_name as 课程名,
            grade.grade as 成绩
            FROM grade, student,course
            WHERE grade.stu_id= %s
            and grade.cour_id = course.cour_id
            and grade.stu_id = student.stu_id;'''
    cursor.execute(sql,'E12214005')
    gradelist = cursor.fetchall()
    cursor.close()
    cursor = connection.cursor()
    sql = '''SELECT * FROM semesters;'''
    cursor.execute(sql)
    semesters = cursor.fetchall()
    cursor.close()
    first_semesters = [t[0] for t in semesters]
    if request.method == 'POST':
        str = request.POST.get('option')
        str_test = request.POST.get('optionnull')
        print(str_test)
        print(str)
        cursor = connection.cursor()
        sql = '''SELECT course.cour_name as 课程名,
                grade.grade as 成绩
                FROM grade, student,course
                WHERE grade.stu_id= %s
                and grade.cour_id = course.cour_id
                and grade.stu_id = student.stu_id
                and student.stu_semester = %s;'''
        cursor.execute(sql, ('E12214005',str))
        gradelist = cursor.fetchall()
        cursor.close()
        return render(request, "stu_grade.html", {"grades": gradelist, "stu": stu, "semesters": first_semesters,"str":str})
    if request.method == 'GET':
        return render(request,"stu_grade.html",{"grades":gradelist,"stu":stu,"semesters": first_semesters,"str":str})

def stu_course(request):
    stu = request.GET.get('stu')
    if request.method == 'GET':
        return render(request,"stu_course.html",{"stu":stu})

def stu_free(request):
    stu = request.GET.get('stu')
    if request.method == 'GET':
        return render(request,"stu_free.html",{"stu":stu})