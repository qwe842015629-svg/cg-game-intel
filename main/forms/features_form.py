"""
核心特性板块专属配置表单
"""
from django import forms
from ..models import HomeLayout
from ..widgets import IconPickerWidget


class FeaturesSectionForm(forms.ModelForm):
    """核心特性板块专属配置 - 展示平台核心优势"""
    
    # 基础配置
    config_title = forms.CharField(
        max_length=200,
        required=False,
        label='📌 板块标题',
        initial='我们的优势',
        widget=forms.TextInput(attrs={
            'style': 'width: 100%;',
            'placeholder': '例如：为什么选择我们'
        })
    )
    
    config_subtitle = forms.CharField(
        max_length=500,
        required=False,
        label='📝 板块副标题',
        initial='专业、安全、便捷的游戏充值服务',
        widget=forms.TextInput(attrs={
            'style': 'width: 100%;',
            'placeholder': '例如：值得信赖的充值平台'
        })
    )
    
    config_icon = forms.CharField(
        max_length=100,
        required=False,
        label='🎨 板块图标',
        initial='✨',
        widget=IconPickerWidget(),
        help_text='从图标库选择或输入自定义图标'
    )
    
    # 特性1配置
    config_feature_1_icon = forms.CharField(
        max_length=100,
        required=False,
        label='🎨 特性1图标',
        initial='⚡',
        widget=IconPickerWidget(),
        help_text='从图标库选择或输入自定义图标'
    )
    
    config_feature_1_title = forms.CharField(
        max_length=200,
        required=False,
        label='📌 特性1标题',
        initial='极速到账',
        widget=forms.TextInput(attrs={
            'style': 'width: 100%;',
            'placeholder': '例如：极速到账'
        })
    )
    
    config_feature_1_desc = forms.CharField(
        max_length=500,
        required=False,
        label='📝 特性1描述',
        initial='自动充值，秒速到账，无需等待',
        widget=forms.Textarea(attrs={
            'style': 'width: 100%;',
            'rows': 2,
            'placeholder': '详细描述这个特性的优势'
        })
    )
    
    # 特性2配置
    config_feature_2_icon = forms.CharField(
        max_length=100,
        required=False,
        label='🎨 特性2图标',
        initial='🔒',
        widget=IconPickerWidget(),
        help_text='从图标库选择或输入自定义图标'
    )
    
    config_feature_2_title = forms.CharField(
        max_length=200,
        required=False,
        label='📌 特性2标题',
        initial='安全可靠',
        widget=forms.TextInput(attrs={
            'style': 'width: 100%;',
            'placeholder': '例如：安全可靠'
        })
    )
    
    config_feature_2_desc = forms.CharField(
        max_length=500,
        required=False,
        label='📝 特性2描述',
        initial='官方授权，正规渠道，保障您的账号安全',
        widget=forms.Textarea(attrs={
            'style': 'width: 100%;',
            'rows': 2,
            'placeholder': '详细描述这个特性的优势'
        })
    )
    
    # 特性3配置
    config_feature_3_icon = forms.CharField(
        max_length=100,
        required=False,
        label='🎨 特性3图标',
        initial='💰',
        widget=IconPickerWidget(),
        help_text='从图标库选择或输入自定义图标'
    )
    
    config_feature_3_title = forms.CharField(
        max_length=200,
        required=False,
        label='📌 特性3标题',
        initial='超值优惠',
        widget=forms.TextInput(attrs={
            'style': 'width: 100%;',
            'placeholder': '例如：超值优惠'
        })
    )
    
    config_feature_3_desc = forms.CharField(
        max_length=500,
        required=False,
        label='📝 特性3描述',
        initial='多种优惠活动，充值越多优惠越多',
        widget=forms.Textarea(attrs={
            'style': 'width: 100%;',
            'rows': 2,
            'placeholder': '详细描述这个特性的优势'
        })
    )
    
    # 展示配置
    config_layout = forms.ChoiceField(
        required=False,
        initial='horizontal',
        label='📐 布局方式',
        choices=[
            ('horizontal', '横向排列'),
            ('vertical', '纵向排列'),
            ('grid', '网格布局'),
        ],
        widget=forms.RadioSelect,
        help_text='选择特性的展示方式'
    )
    
    config_show_animation = forms.BooleanField(
        required=False,
        initial=True,
        label='✨ 开启动画效果',
        help_text='是否在滚动时显示进入动画'
    )
    
    class Meta:
        model = HomeLayout
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.config:
            config = self.instance.config
            self.fields['config_title'].initial = config.get('title', '我们的优势')
            self.fields['config_subtitle'].initial = config.get('subtitle', '专业、安全、便捷的游戏充值服务')
            self.fields['config_icon'].initial = config.get('icon', '✨')
            
            # 特性1
            self.fields['config_feature_1_icon'].initial = config.get('feature_1_icon', '⚡')
            self.fields['config_feature_1_title'].initial = config.get('feature_1_title', '极速到账')
            self.fields['config_feature_1_desc'].initial = config.get('feature_1_desc', '自动充值，秒速到账，无需等待')
            
            # 特性2
            self.fields['config_feature_2_icon'].initial = config.get('feature_2_icon', '🔒')
            self.fields['config_feature_2_title'].initial = config.get('feature_2_title', '安全可靠')
            self.fields['config_feature_2_desc'].initial = config.get('feature_2_desc', '官方授权，正规渠道，保障您的账号安全')
            
            # 特性3
            self.fields['config_feature_3_icon'].initial = config.get('feature_3_icon', '💰')
            self.fields['config_feature_3_title'].initial = config.get('feature_3_title', '超值优惠')
            self.fields['config_feature_3_desc'].initial = config.get('feature_3_desc', '多种优惠活动，充值越多优惠越多')
            
            self.fields['config_layout'].initial = config.get('layout', 'horizontal')
            self.fields['config_show_animation'].initial = config.get('show_animation', True)
    
    def clean(self):
        cleaned_data = super().clean()
        config = {
            'layout': cleaned_data.get('config_layout', 'horizontal'),
            'show_animation': cleaned_data.get('config_show_animation', True),
        }
        
        # 基础信息
        if cleaned_data.get('config_title'):
            config['title'] = cleaned_data['config_title']
        if cleaned_data.get('config_subtitle'):
            config['subtitle'] = cleaned_data['config_subtitle']
        if cleaned_data.get('config_icon'):
            config['icon'] = cleaned_data['config_icon']
        
        # 特性1
        if cleaned_data.get('config_feature_1_icon'):
            config['feature_1_icon'] = cleaned_data['config_feature_1_icon']
        if cleaned_data.get('config_feature_1_title'):
            config['feature_1_title'] = cleaned_data['config_feature_1_title']
        if cleaned_data.get('config_feature_1_desc'):
            config['feature_1_desc'] = cleaned_data['config_feature_1_desc']
        
        # 特性2
        if cleaned_data.get('config_feature_2_icon'):
            config['feature_2_icon'] = cleaned_data['config_feature_2_icon']
        if cleaned_data.get('config_feature_2_title'):
            config['feature_2_title'] = cleaned_data['config_feature_2_title']
        if cleaned_data.get('config_feature_2_desc'):
            config['feature_2_desc'] = cleaned_data['config_feature_2_desc']
        
        # 特性3
        if cleaned_data.get('config_feature_3_icon'):
            config['feature_3_icon'] = cleaned_data['config_feature_3_icon']
        if cleaned_data.get('config_feature_3_title'):
            config['feature_3_title'] = cleaned_data['config_feature_3_title']
        if cleaned_data.get('config_feature_3_desc'):
            config['feature_3_desc'] = cleaned_data['config_feature_3_desc']
        
        cleaned_data['config'] = config
        return cleaned_data
