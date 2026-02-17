"""
热门游戏板块专属配置表单
"""
from django import forms
from ..models import HomeLayout
from ..widgets import IconPickerWidget


class HotGamesSectionForm(forms.ModelForm):
    """热门游戏板块专属配置 - 控制游戏列表展示"""
    
    # 基础配置
    config_title = forms.CharField(
        max_length=200,
        required=False,
        label='📌 板块标题',
        initial='热门游戏',
        widget=forms.TextInput(attrs={
            'style': 'width: 100%;',
            'placeholder': '例如：热门游戏推荐'
        })
    )
    
    config_subtitle = forms.CharField(
        max_length=500,
        required=False,
        label='📝 板块副标题',
        initial='畅玩热门游戏，超值充值优惠',
        widget=forms.TextInput(attrs={
            'style': 'width: 100%;',
            'placeholder': '例如：更多精彩等你来'
        })
    )
    
    config_icon = forms.CharField(
        max_length=100,
        required=False,
        label='🎨 板块图标',
        initial='🔥',
        widget=IconPickerWidget(),
        help_text='从图标库选择或输入自定义图标'
    )
    
    # 热门游戏专属配置
    config_display_count = forms.IntegerField(
        required=False,
        initial=8,
        label='🎮 显示游戏数量',
        help_text='首页显示的热门游戏数量，建议4-20个',
        widget=forms.NumberInput(attrs={
            'style': 'width: 150px;',
            'min': '4',
            'max': '20',
            'step': '4'
        })
    )
    
    config_show_more_button = forms.BooleanField(
        required=False,
        initial=True,
        label='➕ 显示"查看更多"按钮',
        help_text='是否显示查看更多游戏的按钮'
    )
    
    config_layout = forms.ChoiceField(
        required=False,
        initial='grid',
        label='📐 布局样式',
        choices=[
            ('grid', '网格布局'),
            ('list', '列表布局'),
            ('carousel', '轮播布局'),
        ],
        widget=forms.RadioSelect,
        help_text='选择游戏列表的展示方式'
    )
    
    config_show_game_rating = forms.BooleanField(
        required=False,
        initial=True,
        label='⭐ 显示游戏评分',
        help_text='是否显示游戏的星级评分'
    )
    
    config_show_discount = forms.BooleanField(
        required=False,
        initial=True,
        label='💰 显示折扣信息',
        help_text='是否显示游戏充值的折扣标签'
    )
    
    class Meta:
        model = HomeLayout
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.config:
            config = self.instance.config
            self.fields['config_title'].initial = config.get('title', '热门游戏')
            self.fields['config_subtitle'].initial = config.get('subtitle', '畅玩热门游戏，超值充值优惠')
            self.fields['config_icon'].initial = config.get('icon', '🔥')
            self.fields['config_display_count'].initial = config.get('display_count', 8)
            self.fields['config_show_more_button'].initial = config.get('show_more_button', True)
            self.fields['config_layout'].initial = config.get('layout', 'grid')
            self.fields['config_show_game_rating'].initial = config.get('show_game_rating', True)
            self.fields['config_show_discount'].initial = config.get('show_discount', True)
    
    def clean(self):
        cleaned_data = super().clean()
        config = {
            'display_count': cleaned_data.get('config_display_count', 8),
            'show_more_button': cleaned_data.get('config_show_more_button', True),
            'layout': cleaned_data.get('config_layout', 'grid'),
            'show_game_rating': cleaned_data.get('config_show_game_rating', True),
            'show_discount': cleaned_data.get('config_show_discount', True),
        }
        
        if cleaned_data.get('config_title'):
            config['title'] = cleaned_data['config_title']
        if cleaned_data.get('config_subtitle'):
            config['subtitle'] = cleaned_data['config_subtitle']
        if cleaned_data.get('config_icon'):
            config['icon'] = cleaned_data['config_icon']
        
        cleaned_data['config'] = config
        return cleaned_data
