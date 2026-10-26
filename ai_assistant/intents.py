# ai_assistant/intents.py
"""
سیستم تشخیص نیت کاربر بر اساس قواعد
نسخه بهبود یافته
"""

import re
from typing import Tuple, Dict, Any, Optional, List
from .patterns import INTENT_PATTERNS, KEYWORDS, THEME_MAPPING, ORDER_STATUS_MAPPING


class IntentRecognizer:
    """کلاس تشخیص نیت کاربر از متن فارسی"""
    
    def __init__(self):
        self.patterns = INTENT_PATTERNS
        self.keywords = KEYWORDS
    
    def _normalize_text(self, text: str) -> str:
        """نرمال‌سازی متن فارسی"""
        if not text:
            return ""
        
        # یکسان‌سازی کاراکترهای فارسی
        replacements = {
            'ي': 'ی',
            'ك': 'ک',
            'ة': 'ه',
            'ؤ': 'و',
            'إ': 'ا',
            'أ': 'ا',
            'آ': 'ا',
            'ئ': 'ی',
            '0': '۰',
            '1': '۱',
            '2': '۲',
            '3': '۳',
            '4': '۴',
            '5': '۵',
            '6': '۶',
            '7': '۷',
            '8': '۸',
            '9': '۹',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # حذف نیم‌فاصله و فاصله‌های اضافی
        text = text.replace('\u200c', ' ')
        text = ' '.join(text.split())
        
        return text.strip()
    
    def recognize(self, text: str) -> Tuple[str, float, Dict[str, Any]]:
        """
        تشخیص نیت از متن
        
        Returns:
            Tuple[intent, confidence, extracted_data]
        """
        text = self._normalize_text(text)
        original_text = text
        text_lower = text.lower()
        
        if not text:
            return 'unknown', 0.0, {}
        
        best_intent = 'unknown'
        best_confidence = 0.0
        extracted_data = {}
        
        # بررسی هر نیت
        for intent, patterns in self.patterns.items():
            confidence = 0.0
            
            for pattern in patterns:
                pattern_lower = pattern.lower()
                
                # بررسی وجود الگو در متن
                if pattern_lower in text_lower:
                    confidence = 0.7
                    
                    # اگر دقیقاً match شد، confidence بالاتر
                    if pattern_lower == text_lower:
                        confidence = 0.95
                    # اگر در ابتدای متن بود
                    elif text_lower.startswith(pattern_lower):
                        confidence = 0.85
                    
                    # اگر چند الگو match شد
                    match_count = sum(1 for p in patterns if p.lower() in text_lower)
                    if match_count > 1:
                        confidence = min(0.95, confidence + 0.1)
                    
                    if confidence > best_confidence:
                        best_intent = intent
                        best_confidence = confidence
                        extracted_data = self._extract_data(intent, original_text)
                    break
        
        # اگر نیتی پیدا نشد، بررسی‌های خاص
        if best_intent == 'unknown':
            # بررسی کلمات کلیدی اضافه کردن محصول
            if any(word in text_lower for word in ['اضافه', 'جدید', 'ثبت', 'قیمت', 'تومان', 'میلیون']):
                # اگر کلمه "تم" هم بود، احتمالاً تغییر تم هست
                if 'تم' in text_lower:
                    best_intent = 'change_theme'
                    best_confidence = 0.7
                    extracted_data = self._extract_data('change_theme', original_text)
                else:
                    best_intent = 'add_product'
                    best_confidence = 0.6
                    extracted_data = self._extract_data('add_product', original_text)
            
            # بررسی تم
            elif any(theme in text_lower for theme in THEME_MAPPING.keys()):
                best_intent = 'change_theme'
                best_confidence = 0.8
                extracted_data = self._extract_data('change_theme', original_text)
            
            # بررسی سفارشات
            elif any(word in text_lower for word in ['سفارش', 'خرید', 'فروش']):
                best_intent = 'view_orders'
                best_confidence = 0.6
                extracted_data = self._extract_data('view_orders', original_text)
            
            # سوال کلی
            elif any(word in text_lower for word in ['چی', 'چه', 'کی', 'کجا', 'چطور', 'چگونه']):
                best_intent = 'question'
                best_confidence = 0.4
        
        return best_intent, best_confidence, extracted_data
    
    def _extract_data(self, intent: str, text: str) -> Dict[str, Any]:
        """استخراج اطلاعات اضافی از متن"""
        data = {}
        text_lower = text.lower()
        
        # استخراج نام محصول
        if intent in ['add_product', 'edit_product', 'delete_product', 'search_product']:
            product_name = self._extract_product_name(text)
            if product_name:
                data['product_name'] = product_name
        
        # استخراج قیمت
        price = self._extract_price(text)
        if price:
            data['price'] = price
        
        # استخراج تم
        if intent in ['change_theme']:
            theme = self._extract_theme(text)
            if theme:
                data['theme'] = theme
                data['theme_code'] = THEME_MAPPING.get(theme, 'default')
        
        # استخراج رنگ
        if intent in ['change_colors']:
            color = self._extract_color(text)
            if color:
                data['color'] = color
        
        # استخراج شماره سفارش
        if intent in ['view_orders', 'change_order_status']:
            order_number = self._extract_order_number(text)
            if order_number:
                data['order_number'] = order_number
            
            status = self._extract_order_status(text)
            if status:
                data['status'] = status
                data['status_code'] = ORDER_STATUS_MAPPING.get(status, 'pending')
        
        # استخراج نام کاربر
        if intent in ['send_message']:
            username = self._extract_username(text)
            if username:
                data['username'] = username
        
        # استخراج بازه زمانی
        if intent in ['sales_stats', 'view_orders']:
            time_period = self._extract_time_period(text)
            if time_period:
                data['time_period'] = time_period
        
        return data
    
    def _extract_product_name(self, text: str) -> Optional[str]:
        """استخراج نام محصول از متن"""
        text_lower = text.lower()
        
        # کلمات کلیدی که قبل از نام محصول میان
        prefixes = ['محصول', 'کالا', 'اضافه', 'جدید', 'ثبت']
        
        # حذف کلمات اضافی
        words_to_remove = [
            'اضافه کن', 'اضافه', 'جدید', 'محصول', 'کالا', 'با', 'قیمت', 'تومان', 
            'میلیون', 'هزار', 'ثبت', 'کن', 'می‌خوام', 'میخوام', 'بذارم', 'بزارم'
        ]
        
        # استخراج اعداد قیمت
        price_pattern = r'(\d+(?:\.\d+)?)\s*(?:میلیون|هزار|تومان)?'
        price_match = re.search(price_pattern, text_lower)
        
        name = text_lower
        for word in words_to_remove:
            name = name.replace(word, '')
        
        # حذف اعداد
        name = re.sub(r'\d+', '', name)
        
        # اگر قیمت پیدا شد، متن قبل از قیمت رو به عنوان نام در نظر بگیر
        if price_match:
            price_pos = text_lower.find(price_match.group(0))
            if price_pos > 0:
                name = text_lower[:price_pos]
                for word in words_to_remove:
                    name = name.replace(word, '')
        
        # پاکسازی نهایی
        name = name.strip()
        
        # حذف کاراکترهای اضافی
        name = re.sub(r'[^\w\sآ-ی]', '', name)
        name = ' '.join(name.split())
        
        if len(name) > 2 and len(name) < 100:
            return name
        
        return None
    
    def _extract_price(self, text: str) -> Optional[int]:
        """استخراج قیمت از متن"""
        text_lower = text.lower()
        
        # جستجوی اعداد
        numbers = re.findall(r'(\d+(?:\.\d+)?)', text)
        
        for num_str in numbers:
            try:
                price = float(num_str)
                
                # تبدیل میلیون و هزار
                if 'میلیون' in text_lower:
                    price *= 1000000
                elif 'هزار' in text_lower:
                    price *= 1000
                
                price = int(price)
                if 1000 <= price <= 100000000:
                    return price
            except ValueError:
                continue
        
        return None
    
    def _extract_theme(self, text: str) -> Optional[str]:
        """استخراج نام تم از متن"""
        text_lower = text.lower()
        
        for theme_fa, theme_code in THEME_MAPPING.items():
            if theme_fa.lower() in text_lower:
                return theme_fa
        
        return None
    
    def _extract_color(self, text: str) -> Optional[str]:
        """استخراج رنگ از متن"""
        for color in self.keywords['colors']:
            if color in text:
                return color
        return None
    
    def _extract_order_number(self, text: str) -> Optional[str]:
        """استخراج شماره سفارش"""
        pattern = r'ORD-\d{8}-[A-Z0-9]{8}'
        match = re.search(pattern, text.upper())
        if match:
            return match.group(0)
        
        numbers = re.findall(r'\d+', text)
        if numbers:
            return numbers[0]
        
        return None
    
    def _extract_order_status(self, text: str) -> Optional[str]:
        """استخراج وضعیت سفارش"""
        for status_fa in ORDER_STATUS_MAPPING.keys():
            if status_fa in text:
                return status_fa
        return None
    
    def _extract_username(self, text: str) -> Optional[str]:
        """استخراج نام کاربری"""
        patterns = [
            r'به\s+(\w+)',
            r'کاربر\s+(\w+)',
            r'برای\s+(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_time_period(self, text: str) -> str:
        """استخراج بازه زمانی"""
        for period in self.keywords['time_periods']:
            if period in text:
                return period
        return 'امروز'
    
    def get_suggestions(self, partial_text: str) -> List[str]:
        """پیشنهاد تکمیل متن"""
        partial_text = self._normalize_text(partial_text)
        suggestions = []
        
        if len(partial_text) < 2:
            common = ['add_product', 'view_orders', 'change_theme', 'help']
            for intent in common:
                if self.patterns[intent]:
                    suggestions.append(self.patterns[intent][0])
            return suggestions[:5]
        
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if partial_text.lower() in pattern.lower():
                    suggestions.append(pattern)
                    if len(suggestions) >= 5:
                        return suggestions
        
        return suggestions[:5]