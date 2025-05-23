# Generated by Django 5.2 on 2025-04-13 11:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_course_category_course_image'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='instructor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='instructor_courses', to=settings.AUTH_USER_MODEL),
        ),
    ]
