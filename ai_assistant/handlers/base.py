# ai_assistant/handlers/base.py
import re
import random
import string
from typing import Dict, Any, Optional, List
from django.contrib.auth.models import User
from shop.models import SiteSettings


class BaseHandler:
    """کلاس پایه برای همه هندلرها"""
    
    def __init__(self, user: User, conversation):
        self.user = user
        self.conversation = conversation
        self.site_settings = SiteSettings.objects.first()
        if not self.site_settings:
            self.site_settings = SiteSettings.objects.create()
    
    def _extract_price(self, text: str) -> Optional[int]:
        """استخراج قیمت از متن"""
        text_clean = text.replace(',', '')
        text_lower = text.lower()
        numbers = re.findall(r'(\d+(?:\.\d+)?)', text_clean)
        if numbers:
            try:
                price = float(numbers[0])
                if 'میلیون' in text_lower:
                    price *= 1000000
                elif 'هزار' in text_lower:
                    price *= 1000
                return int(price)
            except:
                pass
        return None
    
    def _extract_number(self, text: str) -> Optional[int]:
        """استخراج عدد از متن"""
        numbers = re.findall(r'-?\d+', text)
        if numbers:
            return int(numbers[0])
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """استخراج ایمیل"""
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return match.group(0) if match else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """استخراج شماره تلفن"""
        text_clean = text.replace(' ', '').replace('-', '')
        match = re.search(r'09\d{9}', text_clean)
        return match.group(0) if match else None
    
    def _generate_code(self, length: int = 8) -> str:
        """تولید کد تصادفی"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    def _confirm_action(self, action_name: str) -> str:
        """متن تایید عملیات"""
        return f"⚠️ آیا از **{action_name}** مطمئنی؟\n(بله/خیر)"
    
    def _get_main_actions(self) -> List[Dict]:
        """دکمه‌های اصلی"""
        return [
            {'text': '👤 کاربر جدید', 'intent': 'user', 'action': 'add'},
            {'text': '📦 محصول جدید', 'intent': 'product', 'action': 'add'},
            {'text': '🛒 سفارشات', 'intent': 'order', 'action': 'view'},
            {'text': '🏷️ کد تخفیف', 'intent': 'discount', 'action': 'add'},
            {'text': '🎨 تغییر تم', 'intent': 'theme', 'action': 'change'},
            {'text': '❓ راهنما', 'intent': 'help', 'action': 'view'},
        ]