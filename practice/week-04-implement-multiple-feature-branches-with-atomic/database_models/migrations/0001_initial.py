# Generated initial migration for database_models app

from django.db import migrations, models
import django.db.models.deletion
import database_models.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Workspace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=150, unique=True)),
                ('slug', models.SlugField(max_length=160, unique=True, validators=[database_models.validators.validate_slug_format])),
                ('description', models.TextField(blank=True, default='')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
            ],
            options={
                'verbose_name': 'Workspace',
                'verbose_name_plural': 'Workspaces',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ProjectTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(max_length=60, validators=[database_models.validators.validate_slug_format])),
                ('color_hex', models.CharField(default='#3B82F6', max_length=7, validators=[database_models.validators.validate_hex_color])),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='database_models.workspace')),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('slug', 'workspace')},
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(db_index=True, max_length=200)),
                ('slug', models.SlugField(max_length=220, validators=[database_models.validators.validate_slug_format])),
                ('description', models.TextField(blank=True, default='')),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('ACTIVE', 'Active'), ('ON_HOLD', 'On Hold'), ('COMPLETED', 'Completed'), ('ARCHIVED', 'Archived')], db_index=True, default='DRAFT', max_length=20)),
                ('priority', models.CharField(choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('CRITICAL', 'Critical')], db_index=True, default='MEDIUM', max_length=20)),
                ('budget', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('target_date', models.DateField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False)),
                ('tags', models.ManyToManyField(blank=True, related_name='projects', to='database_models.projecttag')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='database_models.workspace')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProjectAuditRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('CREATE', 'Created'), ('UPDATE', 'Updated'), ('DELETE', 'Deleted')], max_length=20)),
                ('actor_username', models.CharField(default='system', max_length=150)),
                ('summary', models.CharField(max_length=255)),
                ('recorded_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='audit_records', to='database_models.project')),
            ],
            options={
                'ordering': ['-recorded_at'],
            },
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['workspace', 'status'], name='database_mo_workspa_35e8be_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['status', 'priority'], name='database_mo_status_0ee05f_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='project',
            unique_together={('slug', 'workspace')},
        ),
    ]
