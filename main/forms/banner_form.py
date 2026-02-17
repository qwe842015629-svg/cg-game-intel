"""
轮播图板块专属配置表单
"""
from django import forms
from ..models import HomeLayout


class BannerSectionForm(forms.ModelForm):
    """轮播图板块专属配置 - 控制轮播行为"""
    
    # 基础配置
    config_title = forms.CharField(
        max_length=200,
        required=False,
        label='板块标题',
        initial='精彩轮播',
        widget=forms.TextInput(attrs={
            'style': 'width: 100%;',
            'placeholder': '例如：热门活动'
        })
    )
    
    config_subtitle = forms.CharField(
        max_length=500,
        required=False,
        label='板块副标题',
        initial='最新优惠与精彩活动',
        widget=forms.TextInput(attrs={
            'style': 'width: 100%;',
            'placeholder': '例如：更多惊喜等你来'
        })
    )
    
    # 轮播专属配置
    config_auto_play = forms.BooleanField(
        required=False,
        initial=True,
        label='✅ 自动轮播',
        help_text='勾选后自动切换轮播图'
    )
    
    config_interval = forms.IntegerField(
        required=False,
        initial=5000,
        label='⏱️ 轮播间隔（毫秒）',
        help_text='自动切换的时间间隔，1000毫秒=1秒，建议3000-8000',
        widget=forms.NumberInput(attrs={
            'style': 'width: 200px;',
            'min': '2000',
            'max': '10000',
            'step': '1000'
        })
    )
    
    config_show_indicators = forms.BooleanField(
        required=False,
        initial=True,
        label='⚫ 显示指示器',
        help_text='是否显示底部圆点指示器'
    )
    
    config_show_arrows = forms.BooleanField(
        required=False,
        initial=True,
        label='◀️ 显示箭头',
        help_text='是否显示左右切换箭头'
    )
    
    config_pause_on_hover = forms.BooleanField(
        required=False,
        initial=True,
        label='⏸️ 鼠标悬停暂停',
        help_text='鼠标悬停时是否暂停自动轮播'
    )
    
    class Meta:
        model = HomeLayout
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.config:
            config = self.instance.config
            self.fields['config_title'].initial = config.get('title', '精彩轮播')
            self.fields['config_subtitle'].initial = config.get('subtitle', '最新优惠与精彩活动')
            self.fields['config_auto_play'].initial = config.get('auto_play', True)
            self.fields['config_interval'].initial = config.get('interval', 5000)
            self.fields['config_show_indicators'].initial = config.get('show_indicators', True)
            self.fields['config_show_arrows'].initial = config.get('show_arrows', True)
            self.fields['config_pause_on_hover'].initial = config.get('pause_on_hover', True)
    
    def clean(self):
        cleaned_data = super().clean()
        config = {
            'auto_play': cleaned_data.get('config_auto_play', True),
            'interval': cleaned_data.get('config_interval', 5000),
            'show_indicators': cleaned_data.get('config_show_indicators', True),
            'show_arrows': cleaned_data.get('config_show_arrows', True),
            'pause_on_hover': cleaned_data.get('config_pause_on_hover', True),
        }
        
        if cleaned_data.get('config_title'):
            config['title'] = cleaned_data['config_title']
        if cleaned_data.get('config_subtitle'):
            config['subtitle'] = cleaned_data['config_subtitle']
        
        cleaned_data['config'] = config
        return cleaned_data
