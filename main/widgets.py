"""
自定义 Admin 小部件
"""
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.conf import settings


class IconPickerWidget(forms.Widget):
    """
    图标选择器小部件
    支持：
    1. 内置 Emoji 图标库选择
    2. 自定义文本输入（可以是 emoji、图标类名或图片 URL）
    3. 图片上传（可选）
    """
    
    template_name = 'admin/widgets/icon_picker.html'
    
    # 内置图标库 - 分类组织
    ICON_LIBRARY = {
        '游戏': [
            {'value': '🎮', 'label': '游戏手柄'},
            {'value': '🕹️', 'label': '游戏摇杆'},
            {'value': '👾', 'label': '太空侵略者'},
            {'value': '🎯', 'label': '靶心'},
            {'value': '🎲', 'label': '骰子'},
            {'value': '🃏', 'label': '扑克'},
            {'value': '🎰', 'label': '老虎机'},
            {'value': '🏆', 'label': '奖杯'},
            {'value': '🥇', 'label': '金牌'},
            {'value': '🎖️', 'label': '军功章'},
        ],
        '火热': [
            {'value': '🔥', 'label': '火焰'},
            {'value': '⚡', 'label': '闪电'},
            {'value': '💥', 'label': '爆炸'},
            {'value': '✨', 'label': '星光'},
            {'value': '⭐', 'label': '星星'},
            {'value': '🌟', 'label': '闪亮星'},
            {'value': '💫', 'label': '眩晕'},
            {'value': '🔆', 'label': '高亮'},
        ],
        '资讯': [
            {'value': '📰', 'label': '报纸'},
            {'value': '📰', 'label': '新闻'},
            {'value': '📢', 'label': '喇叭'},
            {'value': '📣', 'label': '扩音器'},
            {'value': '📡', 'label': '卫星天线'},
            {'value': '📺', 'label': '电视'},
            {'value': '📻', 'label': '收音机'},
            {'value': '🔔', 'label': '铃铛'},
            {'value': '📬', 'label': '邮箱'},
            {'value': '✉️', 'label': '信封'},
        ],
        '功能': [
            {'value': '🔒', 'label': '锁'},
            {'value': '🔓', 'label': '开锁'},
            {'value': '🔐', 'label': '带钥匙的锁'},
            {'value': '🔑', 'label': '钥匙'},
            {'value': '⚙️', 'label': '齿轮'},
            {'value': '🛠️', 'label': '工具'},
            {'value': '🔧', 'label': '扳手'},
            {'value': '🔨', 'label': '锤子'},
            {'value': '⚡', 'label': '电'},
            {'value': '💡', 'label': '灯泡'},
        ],
        '商业': [
            {'value': '💰', 'label': '钱袋'},
            {'value': '💵', 'label': '美元'},
            {'value': '💴', 'label': '日元'},
            {'value': '💶', 'label': '欧元'},
            {'value': '💷', 'label': '英镑'},
            {'value': '💳', 'label': '信用卡'},
            {'value': '💎', 'label': '钻石'},
            {'value': '🏅', 'label': '奖牌'},
            {'value': '🎁', 'label': '礼物'},
            {'value': '🛍️', 'label': '购物袋'},
        ],
        '分类': [
            {'value': '📁', 'label': '文件夹'},
            {'value': '📂', 'label': '打开的文件夹'},
            {'value': '🗂️', 'label': '卡片索引'},
            {'value': '📋', 'label': '剪贴板'},
            {'value': '📊', 'label': '柱状图'},
            {'value': '📈', 'label': '上升趋势'},
            {'value': '📉', 'label': '下降趋势'},
            {'value': '🗃️', 'label': '文件柜'},
        ],
        '用户': [
            {'value': '👤', 'label': '用户'},
            {'value': '👥', 'label': '用户组'},
            {'value': '👨', 'label': '男人'},
            {'value': '👩', 'label': '女人'},
            {'value': '🧑', 'label': '人'},
            {'value': '👨‍💼', 'label': '男商人'},
            {'value': '👩‍💼', 'label': '女商人'},
            {'value': '🤵', 'label': '穿燕尾服的人'},
        ],
        '其他': [
            {'value': '🎨', 'label': '调色板'},
            {'value': '🖼️', 'label': '画框'},
            {'value': '🎭', 'label': '面具'},
            {'value': '🎪', 'label': '马戏团帐篷'},
            {'value': '🎡', 'label': '摩天轮'},
            {'value': '🎢', 'label': '过山车'},
            {'value': '🎠', 'label': '旋转木马'},
            {'value': '🌈', 'label': '彩虹'},
            {'value': '🌸', 'label': '樱花'},
            {'value': '🌺', 'label': '芙蓉花'},
        ],
    }
    
    class Media:
        css = {
            'all': ('admin/css/icon_picker.css',)
        }
        js = ('admin/js/icon_picker.js',)
    
    def __init__(self, attrs=None):
        super().__init__(attrs)
        if attrs is None:
            attrs = {}
        attrs.setdefault('class', 'icon-picker-input')
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['icon_library'] = self.ICON_LIBRARY
        context['widget']['current_value'] = value or ''
        return context
    
    def render(self, name, value, attrs=None, renderer=None):
        """渲染图标选择器"""
        if attrs is None:
            attrs = {}
        
        # 添加自定义 CSS 类
        attrs['class'] = attrs.get('class', '') + ' icon-picker-input'
        
        # 构建 HTML
        html = []
        
        # 隐藏的实际输入框
        html.append(format_html(
            '<input type="text" name="{}" value="{}" id="id_{}" class="{}" style="display:none;">',
            name,
            value or '',
            name,
            attrs.get('class', '')
        ))
        
        # 显示区域
        html.append('<div class="icon-picker-wrapper" style="margin-top: 10px;">')
        
        # 当前选中的图标显示
        html.append('<div class="icon-picker-current" style="margin-bottom: 15px;">')
        html.append('<label style="display: block; margin-bottom: 5px; font-weight: bold;">当前图标：</label>')
        html.append(format_html(
            '<div class="current-icon-display" style="display: inline-flex; align-items: center; gap: 10px; padding: 10px 15px; background: #f5f5f5; border: 2px solid #ddd; border-radius: 8px;">'
            '<span class="icon-preview" style="font-size: 32px;">{}</span>'
            '<input type="text" class="icon-text-input" value="{}" placeholder="输入 emoji 或图标类名" '
            'style="padding: 5px 10px; border: 1px solid #ccc; border-radius: 4px; width: 200px;">'
            '<button type="button" class="icon-clear-btn" style="padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">清除</button>'
            '</div>',
            value or '❓',
            value or ''
        ))
        html.append('</div>')
        
        # 图标库选择器
        html.append('<div class="icon-picker-library">')
        html.append('<label style="display: block; margin-bottom: 10px; font-weight: bold;">从图标库选择：</label>')
        html.append('<div class="icon-categories" style="display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap;">')
        
        # 分类标签
        for idx, category in enumerate(self.ICON_LIBRARY.keys()):
            active_class = 'active' if idx == 0 else ''
            html.append(format_html(
                '<button type="button" class="category-tab {}" data-category="{}" '
                'style="padding: 8px 16px; background: {}; color: {}; border: 1px solid #007bff; border-radius: 4px; cursor: pointer;">{}</button>',
                active_class,
                category,
                '#007bff' if idx == 0 else '#fff',
                '#fff' if idx == 0 else '#007bff',
                category
            ))
        
        html.append('</div>')
        
        # 图标网格
        html.append('<div class="icon-grid-container" style="max-height: 300px; overflow-y: auto; border: 1px solid #ddd; border-radius: 4px; padding: 15px; background: #fafafa;">')
        
        for category, icons in self.ICON_LIBRARY.items():
            display = 'block' if category == list(self.ICON_LIBRARY.keys())[0] else 'none'
            html.append(format_html(
                '<div class="icon-category-grid" data-category="{}" style="display: {}; display: grid; grid-template-columns: repeat(auto-fill, minmax(60px, 1fr)); gap: 10px;">',
                category,
                display
            ))
            
            for icon in icons:
                html.append(format_html(
                    '<button type="button" class="icon-option" data-icon="{}" title="{}" '
                    'style="padding: 15px; font-size: 28px; background: white; border: 2px solid #e0e0e0; border-radius: 8px; cursor: pointer; transition: all 0.2s; text-align: center;"'
                    'onmouseover="this.style.transform=\'scale(1.1)\'; this.style.borderColor=\'#007bff\'; this.style.boxShadow=\'0 4px 8px rgba(0,123,255,0.3)\';" '
                    'onmouseout="this.style.transform=\'scale(1)\'; this.style.borderColor=\'#e0e0e0\'; this.style.boxShadow=\'none\';">{}</button>',
                    icon['value'],
                    icon['label'],
                    icon['value']
                ))
            
            html.append('</div>')
        
        html.append('</div>')
        html.append('</div>')
        
        # 使用说明
        html.append('<div class="icon-picker-help" style="margin-top: 15px; padding: 10px; background: #e7f3ff; border-left: 4px solid #007bff; border-radius: 4px;">')
        html.append('<p style="margin: 0; font-size: 13px; color: #555;">')
        html.append('<strong>💡 使用提示：</strong><br>')
        html.append('• 从上方图标库中点击选择预设图标<br>')
        html.append('• 或在输入框中直接输入 emoji 表情（如：🎮）<br>')
        html.append('• 支持输入图标类名（如：fas fa-gamepad）<br>')
        html.append('• 支持输入图片 URL（如：https://example.com/icon.png）')
        html.append('</p>')
        html.append('</div>')
        
        html.append('</div>')
        
        # JavaScript 交互代码
        js_code = '''
        <script>
        document.addEventListener("DOMContentLoaded", function() {
          const wrapper = document.querySelector(".icon-picker-wrapper");
          const input = document.getElementById("id_''' + name + '''");
          const textInput = wrapper.querySelector(".icon-text-input");
          const preview = wrapper.querySelector(".icon-preview");
          const clearBtn = wrapper.querySelector(".icon-clear-btn");
          const categoryTabs = wrapper.querySelectorAll(".category-tab");
          const iconGrids = wrapper.querySelectorAll(".icon-category-grid");
          const iconOptions = wrapper.querySelectorAll(".icon-option");
          
          // 分类切换
          categoryTabs.forEach(tab => {
            tab.addEventListener("click", function() {
              const category = this.dataset.category;
              categoryTabs.forEach(t => {
                t.classList.remove("active");
                t.style.background = "#fff";
                t.style.color = "#007bff";
              });
              this.classList.add("active");
              this.style.background = "#007bff";
              this.style.color = "#fff";
              iconGrids.forEach(grid => {
                grid.style.display = grid.dataset.category === category ? "grid" : "none";
              });
            });
          });
          
          // 图标选择
          iconOptions.forEach(option => {
            option.addEventListener("click", function() {
              const icon = this.dataset.icon;
              input.value = icon;
              textInput.value = icon;
              preview.textContent = icon;
            });
          });
          
          // 文本输入
          textInput.addEventListener("input", function() {
            const value = this.value;
            input.value = value;
            preview.textContent = value || "❓";
          });
          
          // 清除按钮
          clearBtn.addEventListener("click", function() {
            input.value = "";
            textInput.value = "";
            preview.textContent = "❓";
          });
        });
        </script>
        '''
        html.append(js_code)
        
        return mark_safe(''.join(html))
