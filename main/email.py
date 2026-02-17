"""
自定义 Djoser 邮件类
强制使用配置的前端域名而不是请求的 HOST
"""
from djoser import email as djoser_email
from django.conf import settings


class CustomActivationEmail(djoser_email.ActivationEmail):
    """自定义激活邮件，强制使用配置的前端域名"""
    
    def get_context_data(self):
        context = super().get_context_data()
        # 强制使用配置的域名和协议
        context['protocol'] = 'http'
        context['domain'] = 'localhost:5178'
        return context
