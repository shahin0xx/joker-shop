# ai_assistant/responses.py
"""
تولید پاسخ‌های طبیعی و دوستانه
"""

import random
from typing import Dict, Any, Tuple


class ResponseGenerator:
    """کلاس تولید پاسخ‌های طبیعی"""
    
    def __init__(self):
        self.conversation_context = {}
    
    def generate_response(self, intent: str, success: bool, message: str, data: Dict[str, Any], user_name: str = "") -> Dict[str, Any]:
        """
        تولید پاسخ نهایی با فرمت مناسب
        
        Returns:
            Dict with 'text', 'type', 'data'
        """
        response = {
            'text': message,
            'type': 'text',
            'data': data,
            'actions': []
        }
        
        # اضافه کردن دکمه‌های پیشنهادی بر اساس intent
        if success:
            response['actions'] = self._get_suggested_actions(intent, data)
        
        # اضافه کردن شکلک‌های مناسب
        response['text'] = self._add_emojis(response['text'], intent, success)
        
        return response
    
    def _get_suggested_actions(self, intent: str, data: Dict[str, Any]) -> list:
        """پیشنهاد عملیات بعدی"""
        suggestions = {
            'greeting': [
                {'text': '📦 افزودن محصول', 'intent': 'add_product'},
                {'text': '🛒 مشاهده سفارشات', 'intent': 'view_orders'},
                {'text': '📊 آمار فروش', 'intent': 'sales_stats'},
                {'text': '❓ راهنما', 'intent': 'help'},
            ],
            'add_product': [
                {'text': '➕ محصول جدید', 'intent': 'add_product'},
                {'text': '🔍 جستجوی محصول', 'intent': 'search_product'},
                {'text': '📋 لیست محصولات', 'intent': 'list_products'},
            ],
            'view_orders': [
                {'text': '📦 سفارشات امروز', 'intent': 'view_orders', 'params': {'time_period': 'امروز'}},
                {'text': '⏳ در انتظار پرداخت', 'intent': 'change_order_status'},
                {'text': '📊 آمار فروش', 'intent': 'sales_stats'},
            ],
            'change_theme': [
                {'text': '🎨 تم اقیانوسی', 'intent': 'change_theme', 'params': {'theme': 'ocean'}},
                {'text': '🌲 تم جنگلی', 'intent': 'change_theme', 'params': {'theme': 'forest'}},
                {'text': '🌅 تم غروب', 'intent': 'change_theme', 'params': {'theme': 'sunset'}},
            ],
            'sales_stats': [
                {'text': '📊 فروش امروز', 'intent': 'sales_stats', 'params': {'time_period': 'امروز'}},
                {'text': '📈 فروش این هفته', 'intent': 'sales_stats', 'params': {'time_period': 'این هفته'}},
                {'text': '📉 فروش این ماه', 'intent': 'sales_stats', 'params': {'time_period': 'این ماه'}},
            ],
            'help': [
                {'text': '📦 مدیریت محصولات', 'intent': 'list_products'},
                {'text': '🛒 مدیریت سفارشات', 'intent': 'view_orders'},
                {'text': '🎨 تنظیمات ظاهری', 'intent': 'change_theme'},
                {'text': '👥 مدیریت کاربران', 'intent': 'view_users'},
            ],
        }
        
        return suggestions.get(intent, [
            {'text': '📦 محصولات', 'intent': 'list_products'},
            {'text': '🛒 سفارشات', 'intent': 'view_orders'},
            {'text': '📊 آمار', 'intent': 'sales_stats'},
            {'text': '❓ راهنما', 'intent': 'help'},
        ])
    
    def _add_emojis(self, text: str, intent: str, success: bool) -> str:
        """اضافه کردن شکلک‌های مناسب"""
        if not success:
            return text
        
        emoji_map = {
            'greeting': '👋',
            'goodbye': '👋',
            'thanks': '😊',
            'add_product': '✅',
            'edit_product': '✏️',
            'delete_product': '🗑️',
            'search_product': '🔍',
            'list_products': '📦',
            'change_theme': '🎨',
            'view_orders': '🛒',
            'change_order_status': '✅',
            'view_users': '👥',
            'sales_stats': '📊',
            'help': '❓',
        }
        
        # اگر شکلک در ابتدای متن نیست، اضافه کن
        emoji = emoji_map.get(intent, '')
        if emoji and not any(e in text[:10] for e in ['✅', '❌', '🔍', '📦', '🛒', '👋', '🎨', '👥', '📊']):
            text = f"{emoji} {text}"
        
        return text
    
    def get_welcome_message(self, user_name: str) -> str:
        """پیام خوش‌آمدگویی"""
        hour = timezone.now().hour if hasattr(timezone, 'now') else __import__('django').utils.timezone.now().hour
        
        if hour < 12:
            greeting = "صبح بخیر"
        elif hour < 18:
            greeting = "ظهر بخیر"
        else:
            greeting = "شب بخیر"
        
        messages = [
            f"{greeting} {user_name} جان! 👋 من دستیار هوشمند پنل مدیریت هستم.",
            f"سلام {user_name} عزیز! 🌟 چه کمکی می‌تونم بهت بکنم؟",
            f"{greeting}! 😊 امروز چطور می‌تونم کمکت کنم {user_name}؟",
        ]
        
        return random.choice(messages)
    
    def get_error_message(self, error_type: str) -> str:
        """پیام‌های خطای استاندارد"""
        errors = {
            'not_authenticated': '⛔ برای استفاده از دستیار هوشمند باید وارد پنل ادمین بشی.',
            'not_staff': '⛔ فقط ادمین‌ها می‌تونن از دستیار هوشمند استفاده کنن.',
            'unknown_intent': '🤔 متأسفم، منظورت رو متوجه نشدم. می‌تونی یه جور دیگه بگی یا بگو "راهنما".',
            'action_failed': '❌ متأسفانه نتونستم این کار رو انجام بدم. لطفاً دوباره تلاش کن.',
            'incomplete': '📝 لطفاً کامل‌تر بگو چی می‌خوای.',
        }
        
        return errors.get(error_type, '⚠️ یه مشکلی پیش اومد. لطفاً دوباره تلاش کن.')
    
    def get_typing_indicators(self) -> list:
        """نشانگرهای تایپ برای نمایش در حال پردازش"""
        return [
            "🤔 بذار ببینم...",
            "🔍 دارم بررسی می‌کنم...",
            "⏳ یه لحظه صبر کن...",
            "💭 در حال انجام...",
        ]
    
    def format_product_list(self, products: list) -> str:
        """فرمت‌بندی لیست محصولات"""
        if not products:
            return "هیچ محصولی پیدا نشد."
        
        text = "📦 **لیست محصولات:**\n\n"
        for p in products[:10]:
            text += f"• **{p.get('name', 'بدون نام')}**\n"
            text += f"  💰 {p.get('price', 0):,} تومان\n"
            text += f"  🆔 کد: {p.get('id', '')}\n\n"
        
        if len(products) > 10:
            text += f"\n... و {len(products) - 10} محصول دیگر."
        
        return text
    
    def format_order_list(self, orders: list) -> str:
        """فرمت‌بندی لیست سفارشات"""
        if not orders:
            return "هیچ سفارشی پیدا نشد."
        
        text = "🛒 **لیست سفارشات:**\n\n"
        for o in orders[:5]:
            text += f"• **{o.get('order_number', '')}**\n"
            text += f"  👤 {o.get('full_name', '')}\n"
            text += f"  💰 {o.get('final_amount', 0):,} تومان\n"
            text += f"  📊 {o.get('status', '')}\n\n"
        
        if len(orders) > 5:
            text += f"\n... و {len(orders) - 5} سفارش دیگر."
        
        return text

# برای استفاده در views
from django.utils import timezone