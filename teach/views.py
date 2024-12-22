import json
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.urls import app_name
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection, transaction

username='李飞'
def teach_index(request):
    return render(request, 'teach_index.html',context={'username':username})


def teach_courselist(request):
        teacher_id = '10001'
        schedules = get_teacher_schedules(teacher_id)

        context = {
            'schedules': schedules,
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
    teacher_id = '10001'
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
                        """, [new_grade, stu_id, cour_id, teacher_id])
                    connection.commit()

                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid action.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    classes = get_classes_by_teacher(teacher_id)
    grades = []

    if selected_class:
        grades = get_grades_for_class(selected_class, teacher_id)

    context = {
        'classes': classes,
        'grades': grades,
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
    return render(request, 'teach_courseadapt.html')

def teach_waiverreview(request):
    return render(request, 'teach_waiverreview.html')



