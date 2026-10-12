# Generated for citizen withdrawal while retaining complaint history.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('complaints', '0003_category_department_related_name')]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='status',
            field=models.CharField(
                choices=[
                    ('SUBMITTED', 'Submitted'), ('RECEIVED', 'Received'), ('ASSIGNED', 'Assigned'),
                    ('UNDER_REVIEW', 'Under review'), ('NEEDS_INFO', 'More information needed'),
                    ('IN_PROGRESS', 'In progress'), ('RESOLVED', 'Resolved'), ('CLOSED', 'Closed'),
                    ('WITHDRAWN', 'Withdrawn by citizen'),
                ], default='SUBMITTED', max_length=14),
        ),
        migrations.AlterField(
            model_name='statushistory',
            name='status',
            field=models.CharField(choices=[
                ('SUBMITTED', 'Submitted'), ('RECEIVED', 'Received'), ('ASSIGNED', 'Assigned'),
                ('UNDER_REVIEW', 'Under review'), ('NEEDS_INFO', 'More information needed'),
                ('IN_PROGRESS', 'In progress'), ('RESOLVED', 'Resolved'), ('CLOSED', 'Closed'),
                ('WITHDRAWN', 'Withdrawn by citizen'),
            ], max_length=14),
        ),
    ]
