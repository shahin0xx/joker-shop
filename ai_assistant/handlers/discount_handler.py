# ai_assistant/handlers/discount_handler.py
from typing import Dict, Any
from shop.models import DiscountCode
from ..conversation_state import ConversationStep
from .base import BaseHandler
from django.utils import timezone
from datetime import timedelta


class DiscountHandler(BaseHandler):
    """مدیریت کدهای تخفیف"""
    
    def handle_intent(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower()
        
        if any(w in msg_lower for w in ['لیست', 'همه', 'نمایش']):
            return self.list_discounts()
        
        if any(w in msg_lower for w in ['اضافه', 'جدید', 'ایجاد', 'add', 'new']):
            return self.start_add_discount(message)
        
        if any(w in msg_lower for w in ['حذف', 'پاک', 'delete']):
            return self.delete_discount(message)
        
        return self.show_main_menu()
    
    def show_main_menu(self) -> Dict:
        active = DiscountCode.objects.filter(is_used=False, expires_at__gte=timezone.now()).count()
        used = DiscountCode.objects.filter(is_used=True).count()
        
        text = "🏷️ **مدیریت کدهای تخفیف**\n\n"
        text += f"📊 فعال: {active} | استفاده شده: {used}\n\n"
        text += "**عملیات:**\n"
        text += "• 'کد تخفیف جدید'\n"
        text += "• 'لیست کدهای تخفیف'\n"
        text += "• 'حذف کد تخفیف [کد]'"
        
        return {'text': text}
    
    def list_discounts(self) -> Dict:
        discounts = DiscountCode.objects.all().order_by('-created_at')[:15]
        
        if not discounts.exists():
            return {'text': "🏷️ هیچ کد تخفیفی وجود نداره.\n\nمی‌خوای 'کد تخفیف جدید' بسازی؟"}
        
        text = f"🏷️ **لیست کدهای تخفیف:**\n\n"
        for d in discounts:
            status = "✅ فعال" if not d.is_used and d.expires_at >= timezone.now() else "❌ منقضی/استفاده شده"
            text += f"• **{d.code}** - {d.amount}{'%' if d.discount_type == 'percentage' else ' تومان'}\n"
            text += f"  👤 {d.user.username} | {status}\n"
            text += f"  📅 اعتبار: {d.expires_at.strftime('%Y/%m/%d')}\n\n"
        
        return {'text': text}
    
    def start_add_discount(self, message: str) -> Dict:
        import random
        import string
        
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        discount = DiscountCode.objects.create(
            code=code,
            user=self.user,
            discount_type='percentage',
            amount=10,
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        text = f"🎉 **کد تخفیف ۱۰٪ ایجاد شد!**\n\n"
        text += f"🎫 کد: **{code}**\n"
        text += f"📅 اعتبار: ۳۰ روز\n\n"
        text += "کار دیگه‌ای می‌خوای؟"
        
        return {'text': text, 'actions': self._get_main_actions()}
    
    def delete_discount(self, message: str) -> Dict:
        return {'text': "🗑️ لطفاً کد تخفیف رو بگو:\nمثال: 'حذف کد تخفیف ABC123'"}