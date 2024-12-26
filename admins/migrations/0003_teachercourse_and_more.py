# Generated by Django 5.1.4 on 2024-12-23 06:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0002_alter_teacherdepart_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeacherCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': '教师课程关联表',
                'verbose_name_plural': '教师课程关联表',
                'db_table': 'teachercourse',
            },
        ),
        migrations.RemoveConstraint(
            model_name='teacherdepart',
            name='unique_teacher_depart',
        ),
        migrations.AlterUniqueTogether(
            name='teacherdepart',
            unique_together={('tch_id', 'depart_id')},
        ),
        migrations.AddField(
            model_name='teachercourse',
            name='cour_id',
            field=models.ForeignKey(db_column='cour_id', on_delete=django.db.models.deletion.CASCADE, to='admins.course', verbose_name='课程ID'),
        ),
        migrations.AddField(
            model_name='teachercourse',
            name='tch_id',
            field=models.ForeignKey(db_column='tch_id', max_length=100, on_delete=django.db.models.deletion.CASCADE, to='admins.teacher', verbose_name='教师ID'),
        ),
    ]
