"""
游戏分类板块专属配置表单
"""
from django import forms
from ..models import HomeLayout
from ..widgets import IconPickerWidget


class CategoriesSectionForm(forms.ModelForm):
    """游戏分类板块专属配置 - 展示游戏分类导航"""
    
    # 基础配置
    config_title = forms.CharField(
        max_length=200,
        required=False,
        label='📌 板块标题',
        initial='游戏分类',
        widget=forms.TextInput(attrs={
            'style': 'width: 100%;',
            'placeholder': '例如：热门游戏分类'
        })
    )
    
    config_subtitle = forms.CharField(
        max_length=500,
        required=False,
        label='📝 板块副标题',
        initial='快速找到您喜欢的游戏类型',
        widget=forms.TextInput(attrs={
            'style': 'width: 100%;',
            'placeholder': '例如：多种分类任您选择'
        })
    )
    
    config_icon = forms.CharField(
        max_length=100,
        required=False,
        label='🎨 板块图标',
        initial='🎮',
        widget=IconPickerWidget(),
        help_text='从图标库选择或输入自定义图标'
    )
    
    # 游戏分类专属配置
    config_show_all_category = forms.BooleanField(
        required=False,
        initial=True,
        label='📂 显示"全部分类"选项',
        help_text='是否在分类列表最前面显示"全部"选项'
    )
    
    config_layout_style = forms.ChoiceField(
        required=False,
        initial='card',
        label='📐 布局样式',
        choices=[
            ('card', '卡片样式'),
            ('icon', '图标样式'),
            ('list', '列表样式'),
            ('grid', '网格样式'),
        ],
        widget=forms.RadioSelect,
        help_text='选择分类的展示方式'
    )
    
    config_columns = forms.IntegerField(
        required=False,
        initial=4,
        label='📊 每行显示数量',
        help_text='每行显示的分类数量，建议3-6个',
        widget=forms.NumberInput(attrs={
            'style': 'width: 150px;',
            'min': '3',
            'max': '6',
            'step': '1'
        })
    )
    
    config_show_game_count = forms.BooleanField(
        required=False,
        initial=True,
        label='🔢 显示游戏数量',
        help_text='是否显示每个分类下的游戏数量'
    )
    
    config_show_category_icon = forms.BooleanField(
        required=False,
        initial=True,
        label='🎨 显示分类图标',
        help_text='是否显示分类的图标'
    )
    
    config_enable_hover_effect = forms.BooleanField(
        required=False,
        initial=True,
        label='✨ 启用悬停效果',
        help_text='鼠标悬停时是否显示特效（如放大、阴影）'
    )
    
    config_show_hot_badge = forms.BooleanField(
        required=False,
        initial=True,
        label='🔥 显示热门标签',
        help_text='是否在热门分类上显示"HOT"标签'
    )
    
    config_display_count = forms.IntegerField(
        required=False,
        initial=8,
        label='📋 显示分类数量',
        help_text='首页显示的分类数量，建议6-12个',
        widget=forms.NumberInput(attrs={
            'style': 'width: 150px;',
            'min': '6',
            'max': '12',
            'step': '2'
        })
    )
    
    config_show_more_button = forms.BooleanField(
        required=False,
        initial=False,
        label='➕ 显示"查看全部"按钮',
        help_text='是否显示查看全部分类的按钮'
    )
    
    class Meta:
        model = HomeLayout
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.config:
            config = self.instance.config
            self.fields['config_title'].initial = config.get('title', '游戏分类')
            self.fields['config_subtitle'].initial = config.get('subtitle', '快速找到您喜欢的游戏类型')
            self.fields['config_icon'].initial = config.get('icon', '🎮')
            self.fields['config_show_all_category'].initial = config.get('show_all_category', True)
            self.fields['config_layout_style'].initial = config.get('layout_style', 'card')
            self.fields['config_columns'].initial = config.get('columns', 4)
            self.fields['config_show_game_count'].initial = config.get('show_game_count', True)
            self.fields['config_show_category_icon'].initial = config.get('show_category_icon', True)
            self.fields['config_enable_hover_effect'].initial = config.get('enable_hover_effect', True)
            self.fields['config_show_hot_badge'].initial = config.get('show_hot_badge', True)
            self.fields['config_display_count'].initial = config.get('display_count', 8)
            self.fields['config_show_more_button'].initial = config.get('show_more_button', False)
    
    def clean(self):
        cleaned_data = super().clean()
        config = {
            'show_all_category': cleaned_data.get('config_show_all_category', True),
            'layout_style': cleaned_data.get('config_layout_style', 'card'),
            'columns': cleaned_data.get('config_columns', 4),
            'show_game_count': cleaned_data.get('config_show_game_count', True),
            'show_category_icon': cleaned_data.get('config_show_category_icon', True),
            'enable_hover_effect': cleaned_data.get('config_enable_hover_effect', True),
            'show_hot_badge': cleaned_data.get('config_show_hot_badge', True),
            'display_count': cleaned_data.get('config_display_count', 8),
            'show_more_button': cleaned_data.get('config_show_more_button', False),
        }
        
        if cleaned_data.get('config_title'):
            config['title'] = cleaned_data['config_title']
        if cleaned_data.get('config_subtitle'):
            config['subtitle'] = cleaned_data['config_subtitle']
        if cleaned_data.get('config_icon'):
            config['icon'] = cleaned_data['config_icon']
        
        cleaned_data['config'] = config
        return cleaned_data
