# Generated by Django 5.0.2 on 2024-02-21 06:21

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0005_alter_follow_unique_together'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='like',
            unique_together={('user', 'tweet')},
        ),
        migrations.AlterUniqueTogether(
            name='retweet',
            unique_together={('user', 'tweet')},
        ),
    ]
