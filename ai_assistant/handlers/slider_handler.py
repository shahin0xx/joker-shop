# ai_assistant/handlers/slider_handler.py
from typing import Dict, Any
from shop.models import Slider
from ..conversation_state import ConversationStep
from .base import BaseHandler


class SliderHandler(BaseHandler):
    """مدیریت کامل اسلایدر"""
    
    def handle_intent(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower()
        
        if any(w in msg_lower for w in ['لیست', 'همه', 'نمایش']):
            return self.list_sliders()
        
        if any(w in msg_lower for w in ['اضافه', 'جدید', 'ایجاد', 'add', 'new']):
            return self.start_add_slider()
        
        if any(w in msg_lower for w in ['حذف', 'پاک', 'delete', 'remove']):
            return self.delete_slider(message)
        
        if any(w in msg_lower for w in ['فعال', 'غیرفعال', 'active']):
            return self.toggle_slider(message)
        
        return self.show_main_menu()
    
    def show_main_menu(self) -> Dict:
        active = Slider.objects.filter(is_active=True).count()
        inactive = Slider.objects.filter(is_active=False).count()
        
        text = "🎠 **مدیریت اسلایدر**\n\n"
        text += f"📊 اسلایدهای فعال: {active} | غیرفعال: {inactive}\n\n"
        text += "**عملیات:**\n"
        text += "• 🖼️ 'اسلاید جدید' - افزودن\n"
        text += "• 📋 'لیست اسلایدها' - مشاهده\n"
        text += "• ✅ 'فعال کردن اسلاید [شماره]'\n"
        text += "• 🗑️ 'حذف اسلاید [شماره]'"
        
        return {'text': text}
    
    def list_sliders(self) -> Dict:
        sliders = Slider.objects.all().order_by('-created_at')
        
        if not sliders.exists():
            return {'text': "🎠 هیچ اسلایدی وجود نداره.\n\nمی‌خوای 'اسلاید جدید' اضافه کنی؟"}
        
        text = f"🎠 **لیست اسلایدها ({sliders.count()} عدد)**\n\n"
        for i, s in enumerate(sliders, 1):
            status = "✅" if s.is_active else "❌"
            text += f"**{i}.** {status} اسلاید {s.id}"
            if s.image:
                text += " 📸"
            text += f"\n  📅 {s.created_at.strftime('%Y/%m/%d')}\n\n"
        
        return {'text': text}
    
    def start_add_slider(self) -> Dict:
        self.conversation.update_step(ConversationStep.ADDING_SLIDER_IMAGE, {})
        
        text = "🎠 **افزودن اسلاید جدید**\n\n"
        text += "لطفاً **عکس اسلاید** رو بفرست.\n"
        text += "📸 روی دکمه 📎 کلیک کن و عکس رو انتخاب کن.\n\n"
        text += "💡 سایز پیشنهادی: ۱۹۲۰×۶۰۰"
        
        return {'text': text}
    
    def delete_slider(self, message: str) -> Dict:
        number = self._extract_number(message)
        
        if number:
            sliders = Slider.objects.all().order_by('-created_at')
            if 1 <= number <= sliders.count():
                slider = sliders[number - 1]
                self.conversation.update_step(ConversationStep.DELETING_SLIDER_CONFIRM, {
                    'slider_id': slider.id,
                    'slider_number': number
                })
                return {'text': self._confirm_action(f"حذف اسلاید شماره {number}")}
            else:
                return {'text': f"❌ شماره {number} معتبر نیست. (۱ تا {sliders.count()})"}
        else:
            return {'text': "🗑️ لطفاً شماره اسلاید رو بگو:\nمثال: 'حذف اسلاید ۳'"}
    
    def toggle_slider(self, message: str) -> Dict:
        number = self._extract_number(message)
        
        if number:
            sliders = Slider.objects.all().order_by('-created_at')
            if 1 <= number <= sliders.count():
                slider = sliders[number - 1]
                slider.is_active = not slider.is_active
                slider.save()
                return {'text': f"✅ اسلاید شماره {number} {'فعال ✅' if slider.is_active else 'غیرفعال ❌'} شد."}
            else:
                return {'text': f"❌ شماره {number} معتبر نیست."}
        else:
            return {'text': "لطفاً شماره اسلاید رو بگو:\nمثال: 'فعال کردن اسلاید ۲'"}