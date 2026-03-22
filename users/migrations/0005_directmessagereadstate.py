from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_directmessage"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DirectMessageReadState",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_read_message_id", models.PositiveIntegerField(default=0, verbose_name="最后已读消息ID")),
                ("last_read_at", models.DateTimeField(auto_now=True, verbose_name="最后已读时间")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                (
                    "thread",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="read_states",
                        to="users.directmessagethread",
                        verbose_name="会话",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="direct_message_read_states",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="用户",
                    ),
                ),
            ],
            options={
                "verbose_name": "私信已读状态",
                "verbose_name_plural": "私信已读状态",
                "db_table": "direct_message_read_state",
                "unique_together": {("thread", "user")},
            },
        ),
        migrations.AddIndex(
            model_name="directmessagereadstate",
            index=models.Index(fields=["user", "thread"], name="direct_mess_user_id_24302b_idx"),
        ),
        migrations.AddIndex(
            model_name="directmessagereadstate",
            index=models.Index(fields=["thread", "last_read_message_id"], name="direct_mess_thread__3a6726_idx"),
        ),
    ]
