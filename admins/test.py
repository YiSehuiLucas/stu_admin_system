from django.db import connection
major = '计算机科学与技术'
cursor = connection.cursor()
sql = '''select major_id
         from major
         where major_name = %s'''
cursor.execute(sql, major)
major_id = cursor.fetchall()
print(major_id)