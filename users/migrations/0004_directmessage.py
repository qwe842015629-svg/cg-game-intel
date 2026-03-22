from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_userprofile_global_ai_visibility_directmessagethread_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="DirectMessage",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.TextField(verbose_name="内容")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                (
                    "sender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sent_direct_messages",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="发送者",
                    ),
                ),
                (
                    "thread",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="users.directmessagethread",
                        verbose_name="会话",
                    ),
                ),
            ],
            options={
                "verbose_name": "私信消息",
                "verbose_name_plural": "私信消息",
                "db_table": "direct_message",
                "ordering": ["id"],
            },
        ),
        migrations.AddIndex(
            model_name="directmessage",
            index=models.Index(fields=["thread", "created_at"], name="direct_mess_thread__213f2d_idx"),
        ),
    ]
