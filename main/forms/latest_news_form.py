"""
最新资讯板块专属配置表单
"""
from django import forms
from ..models import HomeLayout
from ..widgets import IconPickerWidget


class LatestNewsSectionForm(forms.ModelForm):
    """最新资讯板块专属配置 - 控制新闻列表展示"""
    
    # 基础配置
    config_title = forms.CharField(
        max_length=200,
        required=False,
        label='📌 板块标题',
        initial='最新资讯',
        widget=forms.TextInput(attrs={
            'style': 'width: 100%;',
            'placeholder': '例如：游戏资讯中心'
        })
    )
    
    config_subtitle = forms.CharField(
        max_length=500,
        required=False,
        label='📝 板块副标题',
        initial='第一时间掌握游戏动态',
        widget=forms.TextInput(attrs={
            'style': 'width: 100%;',
            'placeholder': '例如：每日更新精彩内容'
        })
    )
    
    config_icon = forms.CharField(
        max_length=100,
        required=False,
        label='🎨 板块图标',
        initial='📰',
        widget=IconPickerWidget(),
        help_text='从图标库选择或输入自定义图标'
    )
    
    # 最新资讯专属配置
    config_display_count = forms.IntegerField(
        required=False,
        initial=6,
        label='📄 显示资讯数量',
        help_text='首页显示的资讯条数，建议3-12条',
        widget=forms.NumberInput(attrs={
            'style': 'width: 150px;',
            'min': '3',
            'max': '12',
            'step': '3'
        })
    )
    
    config_show_category = forms.BooleanField(
        required=False,
        initial=True,
        label='🏷️ 显示资讯分类',
        help_text='是否显示资讯的分类标签（如：活动、公告、攻略）'
    )
    
    config_show_author = forms.BooleanField(
        required=False,
        initial=False,
        label='👤 显示作者信息',
        help_text='是否显示资讯的作者名称'
    )
    
    config_show_date = forms.BooleanField(
        required=False,
        initial=True,
        label='📅 显示发布日期',
        help_text='是否显示资讯的发布时间'
    )
    
    config_show_thumbnail = forms.BooleanField(
        required=False,
        initial=True,
        label='🖼️ 显示缩略图',
        help_text='是否显示资讯的封面图片'
    )
    
    config_show_more_button = forms.BooleanField(
        required=False,
        initial=True,
        label='➕ 显示"查看更多"按钮',
        help_text='是否显示查看更多资讯的按钮'
    )
    
    config_layout = forms.ChoiceField(
        required=False,
        initial='card',
        label='📐 布局样式',
        choices=[
            ('card', '卡片布局'),
            ('list', '列表布局'),
            ('timeline', '时间线布局'),
        ],
        widget=forms.RadioSelect,
        help_text='选择资讯列表的展示方式'
    )
    
    class Meta:
        model = HomeLayout
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.config:
            config = self.instance.config
            self.fields['config_title'].initial = config.get('title', '最新资讯')
            self.fields['config_subtitle'].initial = config.get('subtitle', '第一时间掌握游戏动态')
            self.fields['config_icon'].initial = config.get('icon', '📰')
            self.fields['config_display_count'].initial = config.get('display_count', 6)
            self.fields['config_show_category'].initial = config.get('show_category', True)
            self.fields['config_show_author'].initial = config.get('show_author', False)
            self.fields['config_show_date'].initial = config.get('show_date', True)
            self.fields['config_show_thumbnail'].initial = config.get('show_thumbnail', True)
            self.fields['config_show_more_button'].initial = config.get('show_more_button', True)
            self.fields['config_layout'].initial = config.get('layout', 'card')
    
    def clean(self):
        cleaned_data = super().clean()
        config = {
            'display_count': cleaned_data.get('config_display_count', 6),
            'show_category': cleaned_data.get('config_show_category', True),
            'show_author': cleaned_data.get('config_show_author', False),
            'show_date': cleaned_data.get('config_show_date', True),
            'show_thumbnail': cleaned_data.get('config_show_thumbnail', True),
            'show_more_button': cleaned_data.get('config_show_more_button', True),
            'layout': cleaned_data.get('config_layout', 'card'),
        }
        
        if cleaned_data.get('config_title'):
            config['title'] = cleaned_data['config_title']
        if cleaned_data.get('config_subtitle'):
            config['subtitle'] = cleaned_data['config_subtitle']
        if cleaned_data.get('config_icon'):
            config['icon'] = cleaned_data['config_icon']
        
        cleaned_data['config'] = config
        return cleaned_data
