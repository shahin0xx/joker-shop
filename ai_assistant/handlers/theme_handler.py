# ai_assistant/handlers/theme_handler.py
from typing import Dict, Any
from shop.models import SiteSettings
from ..conversation_state import ConversationStep
from .base import BaseHandler


class ThemeHandler(BaseHandler):
    """مدیریت تم و پس‌زمینه"""
    
    THEME_MAP = {
        'اقیانوسی': 'ocean', 'ocean': 'ocean',
        'جنگلی': 'forest', 'forest': 'forest',
        'غروب': 'sunset', 'sunset': 'sunset',
        'نیمه‌شب': 'midnight', 'نیمه شب': 'midnight', 'midnight': 'midnight',
        'سایبرپانک': 'cyberpunk', 'cyberpunk': 'cyberpunk',
        'سلطنتی': 'royal', 'royal': 'royal',
        'نئون': 'neon', 'neon': 'neon',
        'آبنباتی': 'candy', 'candy': 'candy',
        'کلاسیک': 'classic', 'classic': 'classic',
        'پیش‌فرض': 'default', 'پیش فرض': 'default', 'default': 'default',
    }
    
    THEME_NAMES = {
        'ocean': 'اقیانوسی 🌊',
        'forest': 'جنگلی 🌲',
        'sunset': 'غروب 🌅',
        'midnight': 'نیمه‌شب 🌙',
        'cyberpunk': 'سایبرپانک 🤖',
        'royal': 'سلطنتی 👑',
        'neon': 'نئون ⚡',
        'candy': 'آبنباتی 🍬',
        'classic': 'کلاسیک 🔴',
        'default': 'پیش‌فرض 🎨',
    }
    
    def handle_intent(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower()
        
        if any(w in msg_lower for w in ['پس‌زمینه', 'بک‌گراند', 'background']):
            return self.change_background()
        
        return self.change_theme(message)
    
    def change_theme(self, message: str) -> Dict:
        msg_lower = message.lower()
        
        theme_code = None
        for key, value in self.THEME_MAP.items():
            if key in msg_lower:
                theme_code = value
                break
        
        if theme_code:
            settings = SiteSettings.objects.first()
            if not settings:
                settings = SiteSettings.objects.create()
            
            old_theme = settings.theme
            settings.theme = theme_code
            settings.enable_custom_colors = False
            settings.save()
            
            text = f"✅ تم از **{self.THEME_NAMES.get(old_theme, old_theme)}** به **{self.THEME_NAMES.get(theme_code, theme_code)}** تغییر کرد! 🎨\n\n"
            text += "🖼️ **می‌خوای تصویر پس‌زمینه رو هم عوض کنی؟**\n(بله/خیر)"
            
            self.conversation.update_step(ConversationStep.CHANGING_BACKGROUND, {'theme_changed': True})
            
            return {'text': text, 'actions': [
                {'text': '✅ بله', 'action': 'yes'},
                {'text': '⏭️ خیر', 'action': 'no'}
            ]}
        
        text = "🎨 **تم‌های موجود:**\n\n"
        text += "• 🌊 اقیانوسی\n• 🌲 جنگلی\n• 🌅 غروب\n• 🌙 نیمه‌شب\n• 🤖 سایبرپانک\n"
        text += "• 👑 سلطنتی\n• ⚡ نئون\n• 🍬 آبنباتی\n• 🔴 کلاسیک\n• 🎨 پیش‌فرض\n\n"
        text += "بگو مثلاً: **'تم سلطنتی'**"
        
        return {'text': text}
    
    def change_background(self) -> Dict:
        self.conversation.update_step(ConversationStep.CHANGING_BACKGROUND, {})
        
        text = "🖼️ **تغییر تصویر پس‌زمینه**\n\n"
        text += "لطفاً **عکس جدید** رو بفرست.\n"
        text += "📸 روی دکمه 📎 کلیک کن و عکس رو انتخاب کن.\n\n"
        text += "💡 سایز پیشنهادی: ۱۹۲۰×۱۰۸۰"
        
        return {'text': text, 'actions': [{'text': '📸 انتخاب عکس', 'action': 'select_image'}]}