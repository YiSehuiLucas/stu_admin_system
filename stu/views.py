from django.http import HttpResponse,JsonResponse
from django.shortcuts import render,redirect
from django.db import connection
from django.utils.translation.trans_null import activate
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def stu_main(request):
    stu_id = request.GET.get('stu_id')
    cursor = connection.cursor()
    sql = '''SELECT stu_name as 学生姓名
                FROM student
                WHERE stu_id = %s;'''
    cursor.execute(sql,stu_id)
    stu = cursor.fetchall()
    stu=stu[0][0]
    cursor.close()
    if request.method == 'GET':
        return render(request,"stu_main.html",{"stu":stu,"stu_id":stu_id})

def stu_select(request):
    stu_id=request.GET.get('stu_id')
    str = " 选择…… "
    cursor = connection.cursor()
    sql = '''SELECT * FROM semesters;'''
    cursor.execute(sql)
    semesters = cursor.fetchall()
    cursor.close()
    first_semesters = [t[0] for t in semesters]
    # 已经选过了
    cursor = connection.cursor()
    sql = '''SELECT course.cour_id as 课程代码,
                    course.cour_name as 课程名,
                    teacher.tch_name as 教师姓名,
                    courseschedule.classroom as 教室,
                    courseschedule.dayofweek as 周几,
                    courseschedule.timeslot as 上课时间,
                    courseschedule.start as 开始周数,
                    courseschedule.end as 结束周数,
                    course.cour_credits as 学分
                    FROM courseschedule,course,teacher,studentcourse
                    WHERE courseschedule.cour_id=course.cour_id
                    and courseschedule.tch_id=teacher.tch_id
                    and studentcourse.stu_id=%s
                    and studentcourse.cour_id=course.cour_id
                    and studentcourse.tch_id=teacher.tch_id;'''
    cursor.execute(sql, stu_id)
    courseshaveselects = cursor.fetchall()
    for i in courseshaveselects:
        print(i)
    cursor.close()
    cursor = connection.cursor()
    sql = '''SELECT course.cour_id as 课程代码,
                    course.cour_name as 课程名,
                    teacher.tch_name as 教师姓名,
                    courseschedule.classroom as 教室,
                    courseschedule.dayofweek as 周几,
                    courseschedule.timeslot as 上课时间,
                    courseschedule.start as 开始周数,
                    courseschedule.end as 结束周数,
                    course.cour_credits as 学分
                FROM courseschedule,course,teacher
                WHERE courseschedule.cour_id=course.cour_id
                and courseschedule.tch_id=teacher.tch_id;'''
    cursor.execute(sql)
    courses = cursor.fetchall()
    for i in courses:
        print(i)
    cursor.close()
    if request.method == 'GET':
        return render(request,"stu_select.html",{"str":str,"semesters":first_semesters,"courses":courses,"stu_id":stu_id,"courseshaveselects":courseshaveselects})

    if request.method == 'POST':
        str = request.POST.get('option')
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course_name')
        course_credits = request.POST.get('course_credits')
        btn_action = request.POST.get('action')
        print(course_id)
        print(course_name)
        print(course_credits)
        print(str)
        #查找选课的课程的老师id
        if(course_id != None):
            cursor = connection.cursor()
            sql = '''SELECT courseschedule.tch_id as 教师号
                            FROM courseschedule
                            WHERE courseschedule.cour_id = %s;'''
            cursor.execute(sql,(course_id))
            teacher_id = cursor.fetchall()
            cursor.close()
            teacher_id=teacher_id[0][0]
            print(teacher_id)

        #选课功能
        if btn_action == "select":
            cursor = connection.cursor()
            sql = '''INSERT INTO StudentCourse(stu_id,cour_id,tch_id)
                     VALUE (%s, %s, %s);'''
            cursor.execute(sql,(stu_id,course_id,teacher_id))
            connection.commit()
            cursor.close()
            cursor = connection.cursor()
            sql = '''INSERT INTO Grade(stu_id,cour_id,tch_id)
                                 VALUE (%s, %s, %s);'''
            cursor.execute(sql, (stu_id, course_id, teacher_id))
            connection.commit()
            cursor.close()
            if (str != "选择……"):
                cursor = connection.cursor()
                sql = '''SELECT course.cour_id as 课程代码,
                                course.cour_name as 课程名,
                                teacher.tch_name as 教师姓名,
                                courseschedule.classroom as 教室,
                                courseschedule.dayofweek as 周几,
                                courseschedule.timeslot as 上课时间,
                                courseschedule.start as 开始周数,
                                courseschedule.end as 结束周数,
                                course.cour_credits as 学分
                                   FROM courseschedule,course,teacher
                                   WHERE courseschedule.cour_id=course.cour_id
                                   and courseschedule.tch_id=teacher.tch_id
                                   and course.cour_semester = %s;'''
                cursor.execute(sql, str)
                courses = cursor.fetchall()
                cursor.close()
            else:  # 如果没有输入了对学期的筛选条件
                cursor = connection.cursor()
                sql = '''SELECT course.cour_id as 课程代码,
                                course.cour_name as 课程名,
                                teacher.tch_name as 教师姓名,
                                courseschedule.classroom as 教室,
                                courseschedule.dayofweek as 周几,
                                courseschedule.timeslot as 上课时间,
                                courseschedule.start as 开始周数,
                                courseschedule.end as 结束周数,
                                course.cour_credits as 学分
                                   FROM courseschedule,course,teacher
                                   WHERE courseschedule.cour_id=course.cour_id
                                   and courseschedule.tch_id=teacher.tch_id;'''
                cursor.execute(sql)
                courses = cursor.fetchall()
                cursor.close()
            cursor = connection.cursor()
            sql = '''SELECT course.cour_id as 课程代码,
                                course.cour_name as 课程名,
                                teacher.tch_name as 教师姓名,
                                courseschedule.classroom as 教室,
                                courseschedule.dayofweek as 周几,
                                courseschedule.timeslot as 上课时间,
                                courseschedule.start as 开始周数,
                                courseschedule.end as 结束周数,
                                course.cour_credits as 学分
                               FROM courseschedule,course,teacher,studentcourse
                               WHERE courseschedule.cour_id=course.cour_id
                               and courseschedule.tch_id=teacher.tch_id
                               and studentcourse.stu_id = %s
                               and studentcourse.cour_id=course.cour_id
                               and studentcourse.tch_id=teacher.tch_id;'''
            cursor.execute(sql, stu_id)
            courseshaveselects = cursor.fetchall()
            for i in courseshaveselects:
                print(i)
            cursor.close()
            return render(request, "stu_select.html",
                          {"stu_id": stu_id, "str": str, "semesters": first_semesters, "courses": courses,
                           "courseshaveselects": courseshaveselects})
        elif btn_action =="unselect":
            cursor = connection.cursor()
            sql = '''DELETE from StudentCourse
                     where stu_id = %s 
                     and cour_id = %s
                     and tch_id = %s;'''
            cursor.execute(sql, (stu_id, course_id, teacher_id))
            connection.commit()
            cursor.close()
            cursor = connection.cursor()
            sql = '''DELETE from Grade
                     where stu_id = %s 
                     and cour_id = %s
                     and tch_id = %s;'''
            cursor.execute(sql, (stu_id, course_id, teacher_id))
            connection.commit()
            cursor.close()
            if (str != "选择……"):
                cursor = connection.cursor()
                sql = '''SELECT course.cour_id as 课程代码,
                                course.cour_name as 课程名,
                                teacher.tch_name as 教师姓名,
                                courseschedule.classroom as 教室,
                                courseschedule.dayofweek as 周几,
                                courseschedule.timeslot as 上课时间,
                                courseschedule.start as 开始周数,
                                courseschedule.end as 结束周数,
                                course.cour_credits as 学分
                                   FROM courseschedule,course,teacher
                                   WHERE courseschedule.cour_id=course.cour_id
                                   and courseschedule.tch_id=teacher.tch_id
                                   and course.cour_semester = %s;'''
                cursor.execute(sql, str)
                courses = cursor.fetchall()
                cursor.close()
            else:  # 如果没有输入了对学期的筛选条件
                cursor = connection.cursor()
                sql = '''SELECT course.cour_id as 课程代码,
                                    course.cour_name as 课程名,
                                    teacher.tch_name as 教师姓名,
                                    courseschedule.classroom as 教室,
                                    courseschedule.dayofweek as 周几,
                                    courseschedule.timeslot as 上课时间,
                                    courseschedule.start as 开始周数,
                                    courseschedule.end as 结束周数,
                                    course.cour_credits as 学分
                                   FROM courseschedule,course,teacher
                                   WHERE courseschedule.cour_id=course.cour_id
                                   and courseschedule.tch_id=teacher.tch_id;'''
                cursor.execute(sql)
                courses = cursor.fetchall()
                cursor.close()
            cursor = connection.cursor()
            sql = '''SELECT course.cour_id as 课程代码,
                                course.cour_name as 课程名,
                                teacher.tch_name as 教师姓名,
                                courseschedule.classroom as 教室,
                                courseschedule.dayofweek as 周几,
                                courseschedule.timeslot as 上课时间,
                                courseschedule.start as 开始周数,
                                courseschedule.end as 结束周数,
                                course.cour_credits as 学分
                               FROM courseschedule,course,teacher,studentcourse
                               WHERE courseschedule.cour_id=course.cour_id
                               and courseschedule.tch_id=teacher.tch_id
                               and studentcourse.stu_id = %s
                               and studentcourse.cour_id=course.cour_id
                               and studentcourse.tch_id=teacher.tch_id;'''
            cursor.execute(sql, stu_id)
            courseshaveselects = cursor.fetchall()
            for i in courseshaveselects:
                print(i)
            cursor.close()
            return render(request, "stu_select.html",
                          {"stu_id": stu_id, "str": str, "semesters": first_semesters, "courses": courses,
                           "courseshaveselects": courseshaveselects})
        # 如果输入了对学期的筛选条件
        if (str != "选择……"):
            cursor = connection.cursor()
            sql = '''SELECT course.cour_id as 课程代码,
                                course.cour_name as 课程名,
                                teacher.tch_name as 教师姓名,
                                courseschedule.classroom as 教室,
                                courseschedule.dayofweek as 周几,
                                courseschedule.timeslot as 上课时间,
                                courseschedule.start as 开始周数,
                                courseschedule.end as 结束周数,
                                course.cour_credits as 学分
                               FROM courseschedule,course,teacher
                               WHERE courseschedule.cour_id=course.cour_id
                               and courseschedule.tch_id=teacher.tch_id
                               and course.cour_semester = %s;'''
            cursor.execute(sql, str)
            courses = cursor.fetchall()
            cursor.close()
        else:  # 如果没有输入了对学期的筛选条件
            cursor = connection.cursor()
            sql = '''SELECT course.cour_id as 课程代码,
                                course.cour_name as 课程名,
                                teacher.tch_name as 教师姓名,
                                courseschedule.classroom as 教室,
                                courseschedule.dayofweek as 周几,
                                courseschedule.timeslot as 上课时间,
                                courseschedule.start as 开始周数,
                                courseschedule.end as 结束周数,
                                course.cour_credits as 学分
                               FROM courseschedule,course,teacher
                               WHERE courseschedule.cour_id=course.cour_id
                               and courseschedule.tch_id=teacher.tch_id;'''
            cursor.execute(sql)
            courses = cursor.fetchall()
            cursor.close()

        return render(request, "stu_select.html", {"stu_id":stu_id,"str":str,"semesters":first_semesters,"courses":courses,"courseshaveselects":courseshaveselects})
    else:
        return HttpResponse("TO DO")

def stu_grade(request):
    stu_id = request.GET.get('stu_id')
    str=" 选择…… "
    # views.py 中的数据
    cursor = connection.cursor()
    sql = '''SELECT course.cour_name as 课程名,
            grade.grade as 成绩,
            course.cour_credits as 学分
            FROM grade, student,course
            WHERE grade.stu_id = %s
            and grade.cour_id = course.cour_id
            and grade.stu_id = student.stu_id;'''
    cursor.execute(sql,stu_id)
    gradelist = cursor.fetchall()
    cursor.close()

    cursor = connection.cursor()
    sql = '''SELECT sum(course.cour_credits) as 总学分
                FROM grade, student,course
                WHERE grade.stu_id = %s
                and grade.cour_id = course.cour_id
                and grade.stu_id = student.stu_id
                and grade.grade >= 60;'''
    cursor.execute(sql, stu_id)
    total = cursor.fetchall()
    total = total[0][0]
    cursor.close()

    cursor = connection.cursor()
    sql = '''SELECT * FROM semesters;'''
    cursor.execute(sql)
    semesters = cursor.fetchall()
    cursor.close()
    first_semesters = [t[0] for t in semesters]
    if total == None:
        total = "0"
    if request.method == 'POST':
        str = request.POST.get('option')
        str_test = request.POST.get('optionnull')
        print(str_test)
        print(str)
        cursor = connection.cursor()
        sql = '''SELECT course.cour_name as 课程名,
                grade.grade as 成绩,
                course.cour_credits as 学分
                FROM grade, student,course
                WHERE grade.stu_id = %s
                and grade.cour_id = course.cour_id
                and grade.stu_id = student.stu_id
                and course.cour_semester = %s;'''
        cursor.execute(sql, (stu_id,str))
        gradelist = cursor.fetchall()
        cursor.close()
        cursor = connection.cursor()
        sql = '''SELECT sum(course.cour_credits) as 总学分
                        FROM grade, student,course
                        WHERE grade.stu_id = %s
                        and grade.cour_id = course.cour_id
                        and grade.stu_id = student.stu_id
                        and course.cour_semester = %s
                        and grade.grade >= 60;'''
        cursor.execute(sql, (stu_id,str))
        total = cursor.fetchall()
        total = total[0][0]
        cursor.close()
        if total == None:
            total = "0"
        return render(request, "stu_grade.html", {"total":total,"grades": gradelist,"stu_id":stu_id, "semesters": first_semesters,"str":str})
    if request.method == 'GET':
        return render(request,"stu_grade.html",{"total":total,"grades":gradelist,"stu_id":stu_id,"semesters": first_semesters,"str":str})

def stu_course(request):
    stu_id = request.GET.get('stu_id')
    str = " 选择…… "
    cursor = connection.cursor()
    sql = '''SELECT * FROM semesters;'''
    cursor.execute(sql)
    semesters = cursor.fetchall()
    cursor.close()
    first_semesters = [t[0] for t in semesters]
    if request.method == 'GET':
        cursor = connection.cursor()
        sql = '''SELECT course.cour_id as 课程代码,
                        course.cour_name as 课程名,
                        teacher.tch_name as 教师姓名,
                        courseschedule.classroom as 教室,
                        courseschedule.dayofweek as 周几,
                        courseschedule.timeslot as 上课时间,
                        courseschedule.start as 开始周数,
                        courseschedule.end as 结束周数,
                        course.cour_credits as 学分
                           FROM courseschedule,course,teacher,studentcourse
                           WHERE courseschedule.cour_id=course.cour_id
                           and courseschedule.tch_id=teacher.tch_id
                           and courseschedule.cour_id=studentcourse.cour_id
                           and studentcourse.tch_id=courseschedule.tch_id
                           and studentcourse.stu_id = %s;'''
        cursor.execute(sql,stu_id)
        courses_stu = cursor.fetchall()
        cursor.close()
        return render(request,"stu_course.html",{"stu_id":stu_id,"courses":courses_stu,"semesters": first_semesters,"str":str})
    if request.method == 'POST':
        str = request.POST.get('option')
        str_test = request.POST.get('optionnull')
        print(str_test)
        print(str)
        cursor = connection.cursor()
        sql = '''SELECT course.cour_id as 课程代码,
                        course.cour_name as 课程名,
                        teacher.tch_name as 教师姓名,
                        courseschedule.classroom as 教室,
                        courseschedule.dayofweek as 周几,
                        courseschedule.timeslot as 上课时间,
                        courseschedule.start as 开始周数,
                        courseschedule.end as 结束周数,
                        course.cour_credits as 学分
                           FROM courseschedule,course,teacher,studentcourse
                           WHERE courseschedule.cour_id=course.cour_id
                           and courseschedule.tch_id=teacher.tch_id
                           and courseschedule.cour_id=studentcourse.cour_id
                           and studentcourse.tch_id=courseschedule.tch_id
                           and studentcourse.stu_id = %s
                           and course.cour_semester = %s;'''
        cursor.execute(sql, (stu_id,str))
        courses_stu = cursor.fetchall()
        cursor.close()
        return render(request, "stu_course.html", {"stu_id": stu_id, "courses": courses_stu,"semesters": first_semesters,"str":str})
    else:
        return HttpResponse("TO DO")

def stu_free(request):
    stu_id = request.GET.get('stu_id')
    str = " 选择…… "
    status = ('未审核', '审核中' ,'同意', '否决')
    cursor = connection.cursor()
    sql = '''SELECT course.cour_id as 课程代码,
                    course.cour_name as 课程名,
                    teacher.tch_id as 教师编号,
                    teacher.tch_name as 教师姓名,
                    courseschedule.dayofweek as 周几
                       FROM courseschedule,course,teacher,studentcourse
                       WHERE courseschedule.cour_id=course.cour_id
                       and courseschedule.tch_id=teacher.tch_id
                       and courseschedule.cour_id=studentcourse.cour_id
                       and studentcourse.tch_id=courseschedule.tch_id
                       and studentcourse.stu_id = %s;'''
    cursor.execute(sql, stu_id)
    courseslist = cursor.fetchall()
    cursor.close()
    if request.method == 'GET':
        cursor = connection.cursor()
        sql = '''SELECT WaiverApplication.wa_id as 申请序列,
                        course.cour_id as 课程代码,
                        course.cour_name as 课程名,
                        teacher.tch_name as 教师姓名,
                        WaiverApplication.reason as 申请理由,
                        WaiverApplication.status as 状态
                           FROM WaiverApplication,course,teacher
                           WHERE WaiverApplication.cour_id=course.cour_id
                           and WaiverApplication.tch_id=teacher.tch_id
                           and WaiverApplication.stu_id = %s;'''
        cursor.execute(sql, (stu_id))
        APlist = cursor.fetchall()
        cursor.close()
        return render(request,"stu_free.html",{"stu_id":stu_id,"status": status,"str":str,"APlist":APlist,"courseslist":courseslist})
    if request.method == 'POST':
        str = request.POST.get('option')
        str_test = request.POST.get('optionnull')
        action = request.POST.get('action')
        wa_id = request.POST.get("wa_id")
        print(wa_id)
        if(str != None):
            cursor = connection.cursor()
            sql = '''SELECT WaiverApplication.wa_id as 申请序列,
                            course.cour_id as 课程代码,
                            course.cour_name as 课程名,
                            teacher.tch_name as 教师姓名,
                            WaiverApplication.reason as 申请理由,
                            WaiverApplication.status as 状态
                               FROM WaiverApplication,course,teacher
                               WHERE WaiverApplication.cour_id=course.cour_id
                               and WaiverApplication.tch_id=teacher.tch_id
                               and WaiverApplication.stu_id = %s
                               and WaiverApplication.status = %s;'''
            cursor.execute(sql, (stu_id,str))
            APlist = cursor.fetchall()
            cursor.close()
        else:
            cursor = connection.cursor()
            sql = '''SELECT WaiverApplication.wa_id as 申请序列,
                            course.cour_id as 课程代码,
                            course.cour_name as 课程名,
                            teacher.tch_name as 教师姓名,
                            WaiverApplication.reason as 申请理由,
                            WaiverApplication.status as 状态
                               FROM WaiverApplication,course,teacher
                               WHERE WaiverApplication.cour_id=course.cour_id
                               and WaiverApplication.tch_id=teacher.tch_id
                               and WaiverApplication.stu_id = %s;'''
            cursor.execute(sql, (stu_id))
            APlist = cursor.fetchall()
            cursor.close()
            str = " 选择…… "
        course_tch = request.POST.get('course_tch')
        if(course_tch):
            course_id,teacher_id = course_tch.split('|',1)
            print(course_id, teacher_id)
        message = request.POST.get('message')
        print(message)
        if(course_tch and message):
            cursor = connection.cursor()
            sql = '''INSERT INTO WaiverApplication(stu_id, cour_id, tch_id, reason, status)
                                            VALUE (%s, %s, %s, %s, %s);'''
            cursor.execute(sql, (stu_id, course_id, teacher_id, message, "未审核"))
            connection.commit()
            cursor.close()
            cursor = connection.cursor()
            sql = '''SELECT WaiverApplication.wa_id as 申请序列,
                            course.cour_id as 课程代码,
                            course.cour_name as 课程名,
                            teacher.tch_name as 教师姓名,
                            WaiverApplication.reason as 申请理由,
                            WaiverApplication.status as 状态
                               FROM WaiverApplication,course,teacher
                               WHERE WaiverApplication.cour_id=course.cour_id
                               and WaiverApplication.tch_id=teacher.tch_id
                               and WaiverApplication.stu_id = %s;'''
            cursor.execute(sql, (stu_id))
            APlist = cursor.fetchall()
            cursor.close()
            str = " 选择…… "
        if action == "uncommit":
            cursor = connection.cursor()
            sql = '''DELETE from WaiverApplication
                                 where wa_id=%s;'''
            cursor.execute(sql, (wa_id))
            connection.commit()
            cursor.close()
            cursor = connection.cursor()
            sql = '''SELECT WaiverApplication.wa_id as 申请序列,
                            course.cour_id as 课程代码,
                           course.cour_name as 课程名,
                           teacher.tch_name as 教师姓名,
                           WaiverApplication.reason as 申请理由,
                           WaiverApplication.status as 状态
                              FROM WaiverApplication,course,teacher
                              WHERE WaiverApplication.cour_id=course.cour_id
                              and WaiverApplication.tch_id=teacher.tch_id
                              and WaiverApplication.stu_id = %s;'''
            cursor.execute(sql, (stu_id))
            APlist = cursor.fetchall()
            cursor.close()
            str = " 选择…… "
        return render(request, "stu_free.html", {"stu_id": stu_id, "status": status,"str":str,"APlist":APlist,"courseslist":courseslist})
    else:
        return HttpResponse("TO DO")