# ai_assistant/handlers/settings_handler.py
from typing import Dict, Any
from shop.models import SiteSettings
from ..conversation_state import ConversationStep
from .base import BaseHandler


class SettingsHandler(BaseHandler):
    """مدیریت تنظیمات سایت"""
    
    def handle_intent(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower()
        
        if any(w in msg_lower for w in ['نمایش', 'مشاهده', 'show']):
            return self.show_settings()
        
        if any(w in msg_lower for w in ['ویرایش', 'تغییر', 'edit']):
            return self.edit_settings(message)
        
        return self.show_settings()
    
    def show_settings(self) -> Dict:
        settings = SiteSettings.objects.first()
        if not settings:
            settings = SiteSettings.objects.create()
        
        text = "⚙️ **تنظیمات سایت**\n\n"
        text += f"🏪 **نام فروشگاه:** {settings.site_name}\n"
        text += f"📝 **توضیحات:** {settings.site_description or 'ندارد'}\n"
        text += f"🎨 **تم:** {settings.get_theme_display()}\n"
        text += f"📞 **تلفن ۱:** {settings.phone1}\n"
        text += f"📞 **تلفن ۲:** {settings.phone2 or 'ندارد'}\n"
        text += f"📱 **موبایل:** {settings.mobile}\n"
        text += f"📧 **ایمیل:** {settings.email}\n"
        text += f"📍 **آدرس:** {settings.address_line1}\n"
        text += f"🏧 **شماره کارت:** {settings.card_number}\n"
        text += f"👤 **نام صاحب کارت:** {settings.card_holder_name}\n"
        text += f"🏦 **نام بانک:** {settings.bank_name}\n"
        text += f"💰 **حداقل مبلغ شبا:** {settings.min_amount_for_shaba:,} تومان\n\n"
        text += "**شبکه‌های اجتماعی:**\n"
        text += f"📷 اینستاگرام: {settings.instagram or 'ندارد'}\n"
        text += f"📱 تلگرام: {settings.telegram or 'ندارد'}\n"
        text += f"💬 واتساپ: {settings.whatsapp or 'ندارد'}\n\n"
        text += "برای ویرایش هر بخش، به پنل ادمین → **تنظیمات سایت** مراجعه کن."
        
        return {'text': text}
    
    def edit_settings(self, message: str) -> Dict:
        return {
            'text': "⚙️ برای ویرایش تنظیمات سایت، لطفاً از پنل ادمین استفاده کن:\n\n"
                   "📍 **مسیر:** پنل ادمین → تنظیمات سایت\n\n"
                   "اونجا می‌تونی همه چیز رو تغییر بدی:\n"
                   "• نام و توضیحات فروشگاه\n"
                   "• اطلاعات تماس\n"
                   "• شماره کارت و شبا\n"
                   "• شبکه‌های اجتماعی\n"
                   "• و ..."
        }