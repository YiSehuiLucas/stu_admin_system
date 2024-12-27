import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseBadRequest, request
from django.urls import reverse
from rest_framework.urls import app_name
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection, transaction
from django.shortcuts import render
from django.http import HttpResponse

def teach_index(request):
    tch_id = request.GET.get('tch_id')
    cursor = connection.cursor()
    sql = '''SELECT tch_name as 教师姓名
                    FROM teacher
                    WHERE tch_id = %s;'''
    cursor.execute(sql, tch_id)
    tch_name = cursor.fetchall()
    tch_name = tch_name[0][0]
    cursor.close()
    return render(request, 'teach_index.html',context={'tch_id':tch_id,'username':tch_name})


def teach_courselist(request):
    tch_id = request.GET.get('tch_id')
    schedules = get_teacher_schedules(tch_id)

    context = {
        'schedules': schedules,
        'tch_id': tch_id
    }
    return render(request, 'teach_courselist.html', context)


def get_teacher_schedules(teacher_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT cs.cour_id, c.cour_name, cs.description, cs.classroom, 
                   cs.dayofweek, cs.timeslot, cs.start, cs.end
            FROM CourseSchedule AS cs
            JOIN Course AS c ON cs.cour_id = c.cour_id
            WHERE cs.tch_id = %s
        """, [teacher_id])
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


def teach_pushgrades(request):
    tch_id = request.GET.get('tch_id')
    selected_class = request.POST.get('class')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        try:
            data = json.loads(request.body)
            action = data.get('action')

            if action == 'update_grade':
                stu_id = data.get('stu_id')
                cour_id = data.get('cour_id')
                new_grade = data.get('grade')

                with connection.cursor() as cursor:
                    cursor.execute("""
                            UPDATE Grade
                            SET grade = %s
                            WHERE stu_id = %s AND cour_id = %s AND tch_id = %s
                        """, [new_grade, stu_id, cour_id, tch_id])
                    connection.commit()

                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid action.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    classes = get_classes_by_teacher(tch_id)
    grades = []

    if selected_class:
        grades = get_grades_for_class(selected_class, tch_id)

    context = {
        'classes': classes,
        'grades': grades,
        'tch_id': tch_id
    }
    return render(request, 'teach_pushgrades.html', context)



def get_classes_by_teacher(teacher_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT C.class_id, C.class_name
            FROM Class AS C
            JOIN StudentClass AS SC ON C.class_id = SC.class_id
            JOIN StudentCourse AS SCourse ON SC.stu_id = SCourse.stu_id
            WHERE SCourse.tch_id = %s
        """, [teacher_id])
        return dictfetchall(cursor)


def get_grades_for_class(class_id, teacher_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT G.stu_id, S.stu_name, C.cour_id, C.cour_name, G.grade
            FROM Grade AS G
            JOIN Student AS S ON G.stu_id = S.stu_id
            JOIN Course AS C ON G.cour_id = C.cour_id
            JOIN StudentClass AS SC ON S.stu_id = SC.stu_id
            JOIN StudentCourse AS SCourse ON G.cour_id = SCourse.cour_id AND G.stu_id = SCourse.stu_id
            WHERE SC.class_id = %s AND SCourse.tch_id = %s
        """, [class_id, teacher_id])
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def teach_courseadapt(request):
    tch_id = request.GET.get('tch_id')
    if request.method == "GET":
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ca.*, c.cour_name 
                FROM CourseAdapt ca
                JOIN Course c ON ca.cour_id = c.cour_id
                WHERE ca.tch_id = %s;
            """, [tch_id])
            course_adapts = dictfetchall(cursor)

            cursor.execute("""
                SELECT tc.cour_id, c.cour_name
                FROM TeacherCourse tc
                JOIN Course c ON tc.cour_id = c.cour_id
                WHERE tc.tch_id = %s;
            """, [tch_id])
            courses = dictfetchall(cursor)
        return render(request, 'teach_courseadapt.html', {
            'course_adapts': course_adapts,
            'courses': courses,
            'tch_id': tch_id
        })

    elif request.method == "POST":
        action = request.POST.get('action')

        if action == 'submit':
            cour_id = request.POST['cour_id']
            week = request.POST['week']
            classroom = request.POST['classroom']
            dayofweek = request.POST['dayofweek']
            timeslot = request.POST['timeslot']
            reason = request.POST['reason']

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO CourseAdapt (tch_id, cour_id, week, classroom, dayofweek, timeslot, reason, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, '未审核');
                """, [
                    tch_id,
                    cour_id,
                    week,
                    classroom,
                    dayofweek,
                    timeslot,
                    reason
                ])
            return JsonResponse({'status': 'success'})

        elif action == 'delete':
            ca_id = request.POST.get('ca_id')
            if not ca_id:
                return HttpResponseBadRequest("Missing required parameter: ca_id")
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM CourseAdapt 
                    WHERE ca_id = %s AND tch_id = %s;
                """, [ca_id, tch_id])
                count = cursor.fetchone()[0]
                if count == 0:
                    return JsonResponse(
                        {'status': 'error', 'message': 'Record not found or does not belong to the current user.'})
                cursor.execute("""
                    DELETE FROM CourseAdapt 
                    WHERE ca_id = %s AND tch_id = %s;
                """, [ca_id, tch_id])
            return JsonResponse(
                {'status': 'success', 'message': 'The course adaptation request has been successfully deleted.'})
        else:
            return HttpResponseBadRequest("Invalid action")
    else:
        return HttpResponseBadRequest("Unsupported HTTP method")


def teach_waiverreview(request):
    tch_id = request.GET.get('tch_id')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_status':
            wa_id = request.POST.get('wa_id')
            new_status = request.POST.get('status')
            with connection.cursor() as cursor:
                cursor.execute("UPDATE WaiverApplication SET status=%s WHERE wa_id=%s", [new_status, wa_id])
            return JsonResponse({'status': 'success'})

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT w.wa_id, s.stu_id, s.stu_name, c.cour_name, w.reason, w.status
            FROM WaiverApplication w
            JOIN Student s ON w.stu_id = s.stu_id
            JOIN Course c ON w.cour_id = c.cour_id
            WHERE w.tch_id = %s
        """, [tch_id])
        waivers = [{'wa_id': row[0], 'stu_id': row[1], 'stu_name': row[2], 'cour_name': row[3], 'reason': row[4],
                    'status': row[5]} for row in cursor.fetchall()]
    return render(request, 'teach_waiverreview.html', {'waivers': waivers,'tch_id': tch_id})