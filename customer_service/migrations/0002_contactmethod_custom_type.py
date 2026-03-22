from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("customer_service", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contactmethod",
            name="contact_type",
            field=models.CharField(
                choices=[
                    ("online_chat", "在线客服"),
                    ("email", "邮件支持"),
                    ("phone", "电话客服"),
                    ("wechat", "微信客服"),
                    ("custom", "自定义"),
                ],
                default="custom",
                max_length=50,
                verbose_name="联系方式类型",
            ),
        ),
    ]
