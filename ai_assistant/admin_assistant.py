# ai_assistant/admin_assistant.py
"""
دستیار هوشمند جذاب - نسخه نهایی و کامل
پشتیبانی از تمام عملیات پنل ادمین
"""

import re
import base64
import uuid
from typing import Dict, Any, Optional, List
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db.models import Sum

from shop.models import SiteSettings, Order, Product, Slider, ChatMessage
from .conversation_state import ConversationManager, ConversationStep
from .handlers import (
    ProductHandler, UserHandler, OrderHandler, DiscountHandler,
    CategoryHandler, GameHandler, NewsHandler, VideoHandler,
    SliderHandler, ThemeHandler, SettingsHandler, ChatHandler
)


class AdminAssistant:
    """کلاس اصلی دستیار هوشمند"""
    
    def __init__(self, user: User):
        self.user = user
        self.conversation = ConversationManager(user.id)
        self.site_settings = SiteSettings.objects.first()
        if not self.site_settings:
            self.site_settings = SiteSettings.objects.create()
        
        # هندلرها
        self.product_handler = ProductHandler(user, self.conversation)
        self.user_handler = UserHandler(user, self.conversation)
        self.order_handler = OrderHandler(user, self.conversation)
        self.discount_handler = DiscountHandler(user, self.conversation)
        self.category_handler = CategoryHandler(user, self.conversation)
        self.game_handler = GameHandler(user, self.conversation)
        self.news_handler = NewsHandler(user, self.conversation)
        self.video_handler = VideoHandler(user, self.conversation)
        self.slider_handler = SliderHandler(user, self.conversation)
        self.theme_handler = ThemeHandler(user, self.conversation)
        self.settings_handler = SettingsHandler(user, self.conversation)
        self.chat_handler = ChatHandler(user, self.conversation)
    
    def process_message(self, message: str, image_data: str = None) -> Dict[str, Any]:
        """پردازش پیام کاربر"""
        message = message.strip() if message else ""
        message_lower = message.lower()
        
        if message:
            self.conversation.add_to_history('user', message)
        
        ctx = self.conversation.get_context()
        pending_step = ctx.step
        
        # آپلود عکس
        if image_data:
            return self._handle_image_upload(image_data, ctx.data, pending_step)
        
        # لغو
        cancel_words = ['لغو', 'انصراف', 'بیخیال', 'cancel', 'برگشت', 'بازگشت', 'منو اصلی']
        if any(w in message_lower for w in cancel_words):
            self.conversation.reset()
            return {'text': "✅ برگشتیم به منوی اصلی. چیکار کنم برات؟", 'actions': self._get_main_actions()}
        
        # ادامه مراحل
        if pending_step != ConversationStep.IDLE:
            return self._handle_pending_step(pending_step, message)
        
        # سلام
        hello_words = ['سلام', 'درود', 'خوبی', 'چطوری', 'وقت بخیر', 'خوش آمدی']
        if any(w in message_lower for w in hello_words):
            return self._greeting()
        
        # تشکر
        thanks_words = ['ممنون', 'متشکرم', 'مرسی', 'تشکر', 'دستت درد نکنه']
        if any(w in message_lower for w in thanks_words):
            return {'text': "خواهش می‌کنم! 😊 چیز دیگه‌ای می‌خوای؟", 'actions': self._get_main_actions()}
        
        # راهنما
        help_words = ['راهنما', 'کمک', 'help', 'چه کارا', 'چیکار می‌تونی']
        if any(w in message_lower for w in help_words):
            return self._help()
        
        # آمار
        stats_words = ['آمار', 'گزارش', 'فروش', 'درآمد', 'stats']
        if any(w in message_lower for w in stats_words):
            return self._stats()
        
        # ========== هندلرها ==========
        
        # کاربران
        if any(w in message_lower for w in ['کاربر', 'user', 'مشتری', 'ادمین']):
            return self.user_handler.handle_intent(message)
        
        # محصولات
        if any(w in message_lower for w in ['محصول', 'کالا', 'product']):
            return self.product_handler.handle_intent(message)
        
        # سفارشات
        if any(w in message_lower for w in ['سفارش', 'order', 'خرید']):
            return self.order_handler.handle_intent(message)
        
        # تخفیف
        if any(w in message_lower for w in ['تخفیف', 'discount', 'کد', 'کوپن']):
            return self.discount_handler.handle_intent(message)
        
        # دسته‌بندی
        if any(w in message_lower for w in ['دسته', 'category', 'گروه']):
            return self.category_handler.handle_intent(message)
        
        # بازی
        if any(w in message_lower for w in ['بازی', 'game', 'گیم']):
            return self.game_handler.handle_intent(message)
        
        # اخبار
        if any(w in message_lower for w in ['خبر', 'news', 'اطلاعیه']):
            return self.news_handler.handle_intent(message)
        
        # ویدیو
        if any(w in message_lower for w in ['ویدیو', 'video', 'فیلم', 'کلیپ']):
            return self.video_handler.handle_intent(message)
        
        # اسلایدر
        if any(w in message_lower for w in ['اسلایدر', 'slider', 'اسلاید', 'بنر']):
            return self.slider_handler.handle_intent(message)
        
        # تم و پس‌زمینه
        if any(w in message_lower for w in ['تم', 'theme', 'قالب', 'پس‌زمینه', 'بک‌گراند', 'background']):
            return self.theme_handler.handle_intent(message)
        
        # تنظیمات
        if any(w in message_lower for w in ['تنظیمات', 'settings', 'پیکربندی']):
            return self.settings_handler.handle_intent(message)
        
        # چت و پیام
        if any(w in message_lower for w in ['پیام', 'چت', 'message', 'chat']):
            return self.chat_handler.handle_intent(message)
        
        # ناشناخته
        return {
            'text': "🤔 متوجه نشدم.\n\n"
                   "**کارهایی که می‌تونم انجام بدم:**\n"
                   "• 👤 **کاربران:** 'کاربر جدید' | 'ویرایش کاربر ali' | 'لیست کاربران'\n"
                   "• 📦 **محصولات:** 'محصول جدید' | 'ویرایش محصول ps5' | 'لیست محصولات'\n"
                   "• 🛒 **سفارشات:** 'سفارشات در انتظار' | 'تغییر وضعیت سفارش'\n"
                   "• 🏷️ **تخفیف:** 'کد تخفیف جدید' | 'لیست کدهای تخفیف'\n"
                   "• 🎠 **اسلایدر:** 'اسلاید جدید' | 'لیست اسلایدها'\n"
                   "• 🎨 **ظاهر:** 'تغییر تم' | 'تغییر پس‌زمینه'\n"
                   "• 💬 **پیام:** 'ارسال پیام به ali'\n"
                   "• 📊 **آمار:** 'آمار فروش'\n\n"
                   "بگو چیکار می‌خوای انجام بدی!",
            'actions': self._get_main_actions()
        }
    
    def _handle_pending_step(self, step: ConversationStep, message: str) -> Dict:
        """مدیریت مراحل در انتظار"""
        ctx = self.conversation.get_context()
        data = ctx.data
        msg_lower = message.lower()
        
        # ========== کاربران ==========
        if step in [ConversationStep.ADDING_USER_USERNAME, ConversationStep.ADDING_USER_EMAIL,
                   ConversationStep.ADDING_USER_PASSWORD, ConversationStep.ADDING_USER_FULLNAME,
                   ConversationStep.ADDING_USER_PHONE, ConversationStep.ADDING_USER_IS_ADMIN]:
            return self.user_handler.process_add_user_step(step, message, data)
        
        if step in [ConversationStep.EDITING_USER_USERNAME, ConversationStep.EDITING_USER_EMAIL,
                   ConversationStep.EDITING_USER_FULLNAME, ConversationStep.EDITING_USER_PHONE,
                   ConversationStep.EDITING_USER_ADDRESS, ConversationStep.EDITING_USER_POSTAL,
                   ConversationStep.EDITING_USER_CREDIT, ConversationStep.EDITING_USER_PASSWORD]:
            return self.user_handler.process_edit_user_value(step, message, data)
        
        if step == ConversationStep.EDITING_USER_SELECT:
            return self.user_handler.start_edit_user(message)
        
        if step == ConversationStep.EDITING_USER_CHOOSE_FIELD:
            return self.user_handler.process_edit_user_field(message, data)
        
        if step == ConversationStep.DELETING_USER_CONFIRM:
            if msg_lower in ['بله', 'آره', 'yes']:
                user = User.objects.get(id=data['user_id'])
                username = user.username
                user.delete()
                self.conversation.reset()
                return {'text': f"✅ کاربر **{username}** با موفقیت حذف شد.\n\nکار دیگه‌ای می‌خوای؟", 'actions': self._get_main_actions()}
            else:
                self.conversation.reset()
                return {'text': "❌ حذف کاربر لغو شد."}
        
        # ========== محصولات ==========
        if step in [ConversationStep.ADDING_PRODUCT_NAME, ConversationStep.ADDING_PRODUCT_CATEGORY,
                   ConversationStep.ADDING_PRODUCT_GAME, ConversationStep.ADDING_PRODUCT_PRICE,
                   ConversationStep.ADDING_PRODUCT_IS_NEW, ConversationStep.ADDING_PRODUCT_DESCRIPTION]:
            return self.product_handler.process_add_product_step(step, message, data)
        
        if step == ConversationStep.ADDING_PRODUCT_IMAGE:
            if msg_lower in ['بله', 'آره', 'yes']:
                return {'text': "📸 لطفاً عکس محصول رو بفرست."}
            else:
                self.conversation.reset()
                return {'text': "✅ محصول ثبت شد! کار دیگه‌ای می‌خوای؟", 'actions': self._get_main_actions()}
        
        if step == ConversationStep.DELETING_PRODUCT_CONFIRM:
            if msg_lower in ['بله', 'آره', 'yes']:
                from shop.models import Product
                product = Product.objects.get(id=data['product_id'])
                product_name = product.name
                product.delete()
                self.conversation.reset()
                return {'text': f"✅ محصول **{product_name}** حذف شد.", 'actions': self._get_main_actions()}
            else:
                self.conversation.reset()
                return {'text': "❌ حذف محصول لغو شد."}
        
        # ========== اسلایدر ==========
        if step == ConversationStep.ADDING_SLIDER_IMAGE:
            return {'text': "📸 لطفاً عکس اسلاید رو بفرست."}
        
        if step == ConversationStep.DELETING_SLIDER_CONFIRM:
            if msg_lower in ['بله', 'آره', 'yes']:
                Slider.objects.get(id=data['slider_id']).delete()
                self.conversation.reset()
                return {'text': f"✅ اسلاید حذف شد.", 'actions': self._get_main_actions()}
            else:
                self.conversation.reset()
                return {'text': "❌ حذف اسلاید لغو شد."}
        
        # ========== پس‌زمینه ==========
        if step == ConversationStep.CHANGING_BACKGROUND:
            if msg_lower in ['بله', 'آره', 'yes']:
                return {'text': "📸 لطفاً عکس پس‌زمینه رو بفرست."}
            else:
                self.conversation.reset()
                return {'text': "✅ باشه. کار دیگه‌ای می‌خوای؟", 'actions': self._get_main_actions()}
        
        # ========== پیام ==========
        if step == ConversationStep.SENDING_MESSAGE_TEXT:
            return self.chat_handler.process_send_message_text(message, data)
        
        # ========== تخفیف ==========
        if step == ConversationStep.DELETING_DISCOUNT_CONFIRM:
            if msg_lower in ['بله', 'آره', 'yes']:
                from shop.models import DiscountCode
                discount = DiscountCode.objects.get(id=data['discount_id'])
                code = discount.code
                discount.delete()
                self.conversation.reset()
                return {'text': f"✅ کد تخفیف **{code}** حذف شد.", 'actions': self._get_main_actions()}
            else:
                self.conversation.reset()
                return {'text': "❌ حذف کد تخفیف لغو شد."}
        
        self.conversation.reset()
        return self._greeting()
    
    def _handle_image_upload(self, image_data: str, data: Dict, step: ConversationStep) -> Dict:
        """پردازش عکس آپلود شده"""
        try:
            if ';base64,' in image_data:
                format_part, imgstr = image_data.split(';base64,')
                ext = format_part.split('/')[-1] if '/' in format_part else 'jpg'
            else:
                imgstr = image_data
                ext = 'jpg'
            
            filename = f"{uuid.uuid4()}.{ext}"
            image_file = ContentFile(base64.b64decode(imgstr), name=filename)
            
            # عکس محصول
            if step == ConversationStep.ADDING_PRODUCT_IMAGE:
                from shop.models import Product
                product_id = data.get('product_id')
                if product_id:
                    product = Product.objects.get(id=product_id)
                    product.image = image_file
                    product.save()
                    self.conversation.reset()
                    return {'text': f"✅ عکس محصول **{product.name}** ذخیره شد!\n\nکار دیگه‌ای می‌خوای؟", 'actions': self._get_main_actions()}
            
            # عکس اسلایدر
            elif step == ConversationStep.ADDING_SLIDER_IMAGE:
                Slider.objects.create(image=image_file, is_active=True)
                self.conversation.reset()
                return {'text': "✅ اسلاید جدید با موفقیت اضافه شد! 🎠\n\nکار دیگه‌ای می‌خوای؟", 'actions': self._get_main_actions()}
            
            # عکس پس‌زمینه
            elif step == ConversationStep.CHANGING_BACKGROUND:
                self.site_settings.background_image = image_file
                self.site_settings.save()
                self.conversation.reset()
                return {'text': "✅ عکس پس‌زمینه با موفقیت تغییر کرد! 🖼️\nصفحه رو Refresh کن.\n\nکار دیگه‌ای می‌خوای؟", 'actions': self._get_main_actions()}
            
            # عکس خبر
            elif step == ConversationStep.ADDING_NEWS_IMAGE:
                from shop.models import News
                news_id = data.get('news_id')
                if news_id:
                    news = News.objects.get(id=news_id)
                    news.image = image_file
                    news.save()
                    self.conversation.reset()
                    return {'text': f"✅ عکس خبر **{news.title}** ذخیره شد!", 'actions': self._get_main_actions()}
            
            # عکس ویدیو
            elif step == ConversationStep.ADDING_VIDEO_THUMBNAIL:
                from shop.models import Video
                video_id = data.get('video_id')
                if video_id:
                    video = Video.objects.get(id=video_id)
                    video.thumbnail = image_file
                    video.save()
                    self.conversation.reset()
                    return {'text': f"✅ تصویر ویدیو **{video.title}** ذخیره شد!", 'actions': self._get_main_actions()}
            
            return {'text': "❌ نتونستم عکس رو ذخیره کنم."}
            
        except Exception as e:
            self.conversation.reset()
            return {'text': f"❌ خطا در آپلود: {str(e)}"}
    
    def _greeting(self) -> Dict:
        hour = timezone.now().hour
        greeting = "صبح بخیر" if hour < 12 else ("ظهر بخیر" if hour < 18 else "شب بخیر")
        user_name = self.user.get_full_name() or self.user.username
        
        pending = Order.objects.filter(status='pending').count()
        products = Product.objects.filter(is_available=True).count()
        users = User.objects.filter(is_staff=False).count()
        unread_messages = ChatMessage.objects.filter(is_admin=False, is_read=False).count()
        
        text = f"{greeting} {user_name}! 👋\n\n"
        text += f"📊 **وضعیت فروشگاه:**\n"
        text += f"• 👥 کاربران: {users} نفر\n"
        text += f"• 📦 محصولات: {products} عدد\n"
        text += f"• 🛒 سفارشات در انتظار: {pending}\n"
        if unread_messages > 0:
            text += f"• 💬 پیام‌های جدید: {unread_messages}\n"
        text += "\n**چیکار کنم برات؟**\n"
        text += "• 'کاربر جدید بساز'\n"
        text += "• 'محصول جدید اضافه کن'\n"
        text += "• 'سفارشات در انتظار'\n"
        text += "• 'کد تخفیف جدید'\n"
        text += "• 'اسلاید جدید'\n"
        text += "• 'تغییر تم'\n"
        text += "• 'راهنما'"
        
        return {'text': text, 'actions': self._get_main_actions()}
    
    def _help(self) -> Dict:
        text = "📚 **راهنمای کامل دستیار هوشمند**\n\n"
        
        text += "**👤 کاربران:**\n"
        text += "• 'کاربر جدید' - افزودن کاربر\n"
        text += "• 'ویرایش کاربر [نام]' - ویرایش کامل\n"
        text += "• 'تغییر رمز کاربر [نام]'\n"
        text += "• 'فعال/غیرفعال کردن کاربر [نام]'\n"
        text += "• 'ادمین کردن کاربر [نام]'\n"
        text += "• 'افزایش اعتبار کاربر [نام] [مبلغ]'\n"
        text += "• 'حذف کاربر [نام]'\n"
        text += "• 'لیست کاربران'\n\n"
        
        text += "**📦 محصولات:**\n"
        text += "• 'محصول جدید' - افزودن مرحله به مرحله\n"
        text += "• 'ویرایش محصول [نام]' - ویرایش کامل\n"
        text += "• 'تغییر موجودی محصول [نام]'\n"
        text += "• 'حذف محصول [نام]'\n"
        text += "• 'لیست محصولات'\n"
        text += "• 'جستجوی محصول [نام]'\n\n"
        
        text += "**🛒 سفارشات:**\n"
        text += "• 'سفارشات در انتظار'\n"
        text += "• 'تغییر وضعیت سفارش [شماره] به [وضعیت]'\n"
        text += "• 'جزئیات سفارش [شماره]'\n\n"
        
        text += "**🏷️ تخفیف:**\n"
        text += "• 'کد تخفیف جدید'\n"
        text += "• 'لیست کدهای تخفیف'\n"
        text += "• 'حذف کد تخفیف [کد]'\n\n"
        
        text += "**🎠 اسلایدر:**\n"
        text += "• 'اسلاید جدید' - آپلود عکس\n"
        text += "• 'لیست اسلایدها'\n"
        text += "• 'فعال/غیرفعال کردن اسلاید [شماره]'\n"
        text += "• 'حذف اسلاید [شماره]'\n\n"
        
        text += "**🎨 ظاهر:**\n"
        text += "• 'تغییر تم [نام]'\n"
        text += "• 'تغییر پس‌زمینه' - آپلود عکس\n\n"
        
        text += "**💬 پیام:**\n"
        text += "• 'ارسال پیام به [نام کاربری]'\n"
        text += "• 'مشاهده پیام‌های [نام کاربری]'\n\n"
        
        text += "**📊 سایر:**\n"
        text += "• 'آمار فروش'\n"
        text += "• 'تنظیمات سایت'\n\n"
        
        text += "💡 هر جا خواستی بگو **'لغو'**"
        
        return {'text': text, 'actions': self._get_main_actions()}
    
    def _stats(self) -> Dict:
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        today_sales = Order.objects.filter(
            created_at__date=today, status__in=['paid', 'completed']
        ).aggregate(total=Sum('final_amount'))['total'] or 0
        
        month_sales = Order.objects.filter(
            created_at__date__gte=month_start, status__in=['paid', 'completed']
        ).aggregate(total=Sum('final_amount'))['total'] or 0
        
        pending = Order.objects.filter(status='pending').count()
        paid = Order.objects.filter(status='paid').count()
        completed = Order.objects.filter(status='completed').count()
        
        # محصولات پرفروش
        from django.db.models import Count
        top_products = Product.objects.filter(
            cartitem__cart__order__status='completed'
        ).annotate(sold=Count('cartitem')).order_by('-sold')[:5]
        
        text = "📊 **آمار و گزارشات**\n\n"
        text += f"**💰 فروش:**\n"
        text += f"• امروز: {today_sales:,} تومان\n"
        text += f"• این ماه: {month_sales:,} تومان\n\n"
        
        text += f"**📦 سفارشات:**\n"
        text += f"• در انتظار: {pending}\n"
        text += f"• پرداخت شده: {paid}\n"
        text += f"• تکمیل شده: {completed}\n\n"
        
        if top_products:
            text += "**🔥 محصولات پرفروش:**\n"
            for i, p in enumerate(top_products, 1):
                text += f"{i}. {p.name} - {p.sold} عدد\n"
        
        return {'text': text, 'actions': self._get_main_actions()}
    
    def _get_main_actions(self) -> List:
        return [
            {'text': '👤 کاربر جدید', 'intent': 'user', 'action': 'add'},
            {'text': '📦 محصول جدید', 'intent': 'product', 'action': 'add'},
            {'text': '🛒 سفارشات', 'intent': 'order', 'action': 'view'},
            {'text': '🏷️ کد تخفیف', 'intent': 'discount', 'action': 'add'},
            {'text': '🎠 اسلاید جدید', 'intent': 'slider', 'action': 'add'},
            {'text': '🎨 تغییر تم', 'intent': 'theme', 'action': 'change'},
            {'text': '💬 ارسال پیام', 'intent': 'chat', 'action': 'send'},
            {'text': '❓ راهنما', 'intent': 'help', 'action': 'view'},
        ]


# Import for type hints
