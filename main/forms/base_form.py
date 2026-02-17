"""
基础配置表单 - 所有板块共用的通用配置
"""
from django import forms
from ..models import HomeLayout


class BaseConfigForm(forms.ModelForm):
    """基础配置表单 - 提供基本的标题和副标题配置"""
    
    config_title = forms.CharField(
        max_length=200,
        required=False,
        label='板块标题',
        help_text='显示在前端的板块标题',
        widget=forms.TextInput(attrs={
            'style': 'width: 100%;',
            'placeholder': '例如：热门推荐'
        })
    )
    
    config_subtitle = forms.CharField(
        max_length=500,
        required=False,
        label='板块副标题',
        help_text='显示在标题下方的描述文字',
        widget=forms.TextInput(attrs={
            'style': 'width: 100%;',
            'placeholder': '例如：精选内容推荐'
        })
    )
    
    class Meta:
        model = HomeLayout
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.config:
            config = self.instance.config
            self.fields['config_title'].initial = config.get('title', '')
            self.fields['config_subtitle'].initial = config.get('subtitle', '')
    
    def clean(self):
        cleaned_data = super().clean()
        config = {}
        
        if cleaned_data.get('config_title'):
            config['title'] = cleaned_data['config_title']
        if cleaned_data.get('config_subtitle'):
            config['subtitle'] = cleaned_data['config_subtitle']
        
        cleaned_data['config'] = config
        return cleaned_data
