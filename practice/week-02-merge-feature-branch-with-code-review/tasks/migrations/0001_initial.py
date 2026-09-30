# Generated for tasks app schema initialization

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Category display name', max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, help_text='URL-friendly identifier', max_length=120, unique=True)),
                ('description', models.TextField(blank=True, default='', help_text='Optional description of the category')),
                ('color_hex', models.CharField(default='#3B82F6', help_text='Hex color code for UI badges', max_length=7)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Brief summary of the task', max_length=255)),
                ('description', models.TextField(blank=True, default='', help_text='Detailed task specification')),
                ('status', models.CharField(choices=[('BACKLOG', 'Backlog'), ('TODO', 'To Do'), ('IN_PROGRESS', 'In Progress'), ('IN_REVIEW', 'In Review'), ('DONE', 'Done'), ('CANCELLED', 'Cancelled')], default='TODO', help_text='Current task lifecycle status', max_length=20)),
                ('priority', models.CharField(choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('URGENT', 'Urgent')], default='MEDIUM', help_text='Urgency and impact priority', max_length=20)),
                ('due_date', models.DateField(blank=True, help_text='Target completion date', null=True)),
                ('completed_at', models.DateTimeField(blank=True, help_text='Timestamp when task was marked as DONE (automatically populated)', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, help_text='Optional category assignment', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='tasks.category')),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
                'ordering': ['-priority', 'due_date', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['status'], name='tasks_task_status_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['priority'], name='tasks_task_priority_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['due_date'], name='tasks_task_due_date_idx'),
        ),
    ]
