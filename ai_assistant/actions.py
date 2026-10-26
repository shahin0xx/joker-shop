# ai_assistant/actions.py
"""
اجرای عملیات بر اساس نیت شناسایی شده
"""

from typing import Dict, Any, Optional, Tuple
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Sum, Count
from datetime import datetime, timedelta
from shop.models import (
    Product, Category, GameList, Order, SiteSettings, 
    ChatMessage as ShopChatMessage, UserProfile
)
from .patterns import THEME_MAPPING, ORDER_STATUS_MAPPING


class ActionExecutor:
    """کلاس اجرای عملیات مدیریتی"""
    
    def __init__(self, user: User):
        self.user = user
        self.site_settings = SiteSettings.objects.first()
    
    def execute(self, intent: str, data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        اجرای عملیات بر اساس نیت
        
        Returns:
            Tuple[success, message, result_data]
        """
        # نگاشت نیت به متد اجرا کننده
        action_map = {
            'greeting': self._greeting,
            'goodbye': self._goodbye,
            'thanks': self._thanks,
            'add_product': self._add_product,
            'edit_product': self._edit_product,
            'delete_product': self._delete_product,
            'search_product': self._search_product,
            'list_products': self._list_products,
            'change_theme': self._change_theme,
            'change_colors': self._change_colors,
            'change_background': self._change_background,
            'view_orders': self._view_orders,
            'change_order_status': self._change_order_status,
            'view_users': self._view_users,
            'send_message': self._send_message,
            'sales_stats': self._sales_stats,
            'site_settings': self._site_settings,
            'help': self._help,
            'new_products': self._new_products,
            'best_selling': self._best_selling,
        }
        
        if intent in action_map:
            return action_map[intent](data)
        else:
            return False, "متأسفم، این دستور رو متوجه نشدم. می‌تونی بگی 'راهنما' تا ببینی چه کارایی می‌تونم انجام بدم.", {}
    
    # ========== عملیات عمومی ==========
    
    def _greeting(self, data: Dict) -> Tuple[bool, str, Dict]:
        """سلام و احوالپرسی"""
        hour = datetime.now().hour
        if hour < 12:
            greeting = "صبح بخیر"
        elif hour < 18:
            greeting = "ظهر بخیر"
        else:
            greeting = "شب بخیر"
        
        message = f"{greeting} {self.user.get_full_name() or self.user.username} عزیز! 👋\n"
        message += "من دستیار هوشمند پنل مدیریت هستم. چطور می‌تونم کمکت کنم؟\n\n"
        message += "می‌تونی بگی 'راهنما' تا لیست کارهایی که می‌تونم انجام بدم رو ببینی."
        
        return True, message, {}
    
    def _goodbye(self, data: Dict) -> Tuple[bool, str, Dict]:
        """خداحافظی"""
        messages = [
            "خدانگهدار! هر وقت نیاز داشتی من اینجام. 👋",
            "فعلاً! موفق باشی. 🌟",
            "بعداً می‌بینمت! هر سوالی داشتی بپرس. 😊",
        ]
        import random
        return True, random.choice(messages), {}
    
    def _thanks(self, data: Dict) -> Tuple[bool, str, Dict]:
        """تشکر"""
        messages = [
            "خواهش می‌کنم! وظیفمه که کمکت کنم. 😊",
            "قربانت! بازم هر کاری داشتی بگو. 🌹",
            "نوکرتم! هر وقت نیاز داشتی من آماده‌ام. 👍",
        ]
        import random
        return True, random.choice(messages), {}
    
    def _help(self, data: Dict) -> Tuple[bool, str, Dict]:
        """نمایش راهنما"""
        message = "🎯 **کارهایی که می‌تونم برات انجام بدم:**\n\n"
        message += "📦 **محصولات:**\n"
        message += "• افزودن محصول جدید\n"
        message += "• جستجوی محصول\n"
        message += "• لیست همه محصولات\n"
        message += "• محصولات جدید\n"
        message += "• محصولات پرفروش\n\n"
        message += "🎨 **تنظیمات ظاهری:**\n"
        message += "• تغییر تم سایت (پیش‌فرض، اقیانوسی، جنگلی، غروب، نیمه‌شب، سایبرپانک، کلاسیک، سلطنتی، نئون، آبنباتی)\n"
        message += "• تغییر رنگ‌بندی\n"
        message += "• تغییر تصویر پس‌زمینه\n\n"
        message += "🛒 **سفارشات:**\n"
        message += "• مشاهده سفارشات جدید\n"
        message += "• تغییر وضعیت سفارش\n"
        message += "• آمار فروش\n\n"
        message += "👥 **کاربران:**\n"
        message += "• مشاهده لیست کاربران\n"
        message += "• ارسال پیام به کاربر\n\n"
        message += "💬 **کافیه بهم بگی چی می‌خوای!**"
        
        return True, message, {}
    
    # ========== عملیات محصولات ==========
    
    def _add_product(self, data: Dict) -> Tuple[bool, str, Dict]:
        """افزودن محصول جدید"""
        product_name = data.get('product_name')
        price = data.get('price')
        
        if not product_name:
            return False, "لطفاً نام محصول رو هم بگو. مثلاً: 'محصول جدید کنسول PS5 با قیمت ۲۵ میلیون تومان اضافه کن'", {}
        
        if not price:
            return False, f"قیمت محصول '{product_name}' رو هم بگو. مثلاً: 'قیمتش ۲۵ میلیون تومان'", {'product_name': product_name}
        
        # پیدا کردن یا ایجاد دسته‌بندی پیش‌فرض
        default_category, _ = Category.objects.get_or_create(
            name='عمومی',
            defaults={
                'type': 'console',
                'game_platform': 'none',
                'is_active': True
            }
        )
        
        # ایجاد محصول
        product = Product.objects.create(
            name=product_name,
            category=default_category,
            price=price,
            description=f'محصول {product_name}',
            is_available=True,
            is_new=True
        )
        
        message = f"✅ محصول '{product_name}' با قیمت {price:,} تومان با موفقیت اضافه شد!\n"
        message += f"🆔 شناسه محصول: {product.id}\n"
        message += "📝 می‌تونی از طریق پنل ادمین تصویر و توضیحات کامل رو اضافه کنی."
        
        return True, message, {'product_id': product.id, 'product': product}
    
    def _edit_product(self, data: Dict) -> Tuple[bool, str, Dict]:
        """ویرایش محصول"""
        product_name = data.get('product_name')
        price = data.get('price')
        
        if not product_name:
            return False, "کدوم محصول رو می‌خوای ویرایش کنی؟ اسمش رو بگو.", {}
        
        # جستجوی محصول
        products = Product.objects.filter(name__icontains=product_name, is_available=True)
        
        if not products.exists():
            return False, f"محصولی با نام '{product_name}' پیدا نکردم.", {}
        
        if products.count() > 1:
            message = "چندتا محصول با این اسم پیدا کردم:\n"
            for p in products[:5]:
                message += f"• {p.name} - {p.price:,} تومان (کد: {p.id})\n"
            message += "\nلطفاً دقیق‌تر بگو کدوم رو می‌خوای."
            return False, message, {'products': list(products.values('id', 'name', 'price'))}
        
        product = products.first()
        
        if price:
            old_price = product.price
            product.price = price
            product.save()
            message = f"✅ قیمت محصول '{product.name}' از {old_price:,} به {price:,} تومان تغییر کرد."
            return True, message, {'product': product}
        
        return False, f"محصول '{product.name}' رو پیدا کردم. چیو می‌خوای تغییر بدی؟ (قیمت، نام، ...)", {'product': product}
    
    def _delete_product(self, data: Dict) -> Tuple[bool, str, Dict]:
        """حذف محصول"""
        product_name = data.get('product_name')
        
        if not product_name:
            return False, "کدوم محصول رو می‌خوای حذف کنی؟", {}
        
        products = Product.objects.filter(name__icontains=product_name)
        
        if not products.exists():
            return False, f"محصولی با نام '{product_name}' پیدا نکردم.", {}
        
        if products.count() > 1:
            message = "چندتا محصول با این اسم هست. لطفاً با کد محصول مشخص کن:\n"
            for p in products[:5]:
                message += f"• {p.name} - کد: {p.id}\n"
            return False, message, {}
        
        product = products.first()
        product_name_full = product.name
        product.delete()
        
        return True, f"✅ محصول '{product_name_full}' با موفقیت حذف شد.", {}
    
    def _search_product(self, data: Dict) -> Tuple[bool, str, Dict]:
        """جستجوی محصول"""
        product_name = data.get('product_name', '')
        
        products = Product.objects.filter(is_available=True)
        
        if product_name:
            products = products.filter(name__icontains=product_name)
        
        count = products.count()
        
        if count == 0:
            return True, f"🔍 محصولی با جستجوی '{product_name}' پیدا نشد.", {}
        
        message = f"🔍 **{count} محصول پیدا شد:**\n\n"
        for p in products[:10]:
            message += f"• **{p.name}**\n"
            message += f"  💰 قیمت: {p.price:,} تومان\n"
            message += f"  📦 دسته: {p.category.name}\n"
            message += f"  🆔 کد: {p.id}\n"
            message += f"  {'✅ موجود' if p.is_available else '❌ ناموجود'}\n\n"
        
        if count > 10:
            message += f"\n... و {count - 10} محصول دیگر."
        
        return True, message, {'count': count, 'products': list(products[:10].values('id', 'name', 'price'))}
    
    def _list_products(self, data: Dict) -> Tuple[bool, str, Dict]:
        """لیست همه محصولات"""
        return self._search_product({'product_name': ''})
    
    def _new_products(self, data: Dict) -> Tuple[bool, str, Dict]:
        """محصولات جدید"""
        products = Product.objects.filter(is_available=True).order_by('-created_at')[:10]
        
        if not products.exists():
            return True, "هنوز هیچ محصولی ثبت نشده.", {}
        
        message = "🆕 **جدیدترین محصولات:**\n\n"
        for p in products:
            message += f"• **{p.name}** - {p.price:,} تومان\n"
            message += f"  📅 ثبت شده در: {p.created_at.strftime('%Y/%m/%d')}\n\n"
        
        return True, message, {}
    
    def _best_selling(self, data: Dict) -> Tuple[bool, str, Dict]:
        """محصولات پرفروش"""
        # اینجا می‌تونی بر اساس سفارشات تکمیل شده محاسبه کنی
        products = Product.objects.filter(is_available=True).annotate(
            order_count=Count('cartitem__cart__order', filter=Q(cartitem__cart__order__status='completed'))
        ).filter(order_count__gt=0).order_by('-order_count')[:10]
        
        if not products.exists():
            return True, "هنوز فروشی ثبت نشده.", {}
        
        message = "🔥 **پرفروش‌ترین محصولات:**\n\n"
        for i, p in enumerate(products, 1):
            message += f"{i}. **{p.name}** - {p.order_count} عدد فروخته شده\n"
        
        return True, message, {}
    
    # ========== عملیات تنظیمات ==========
    
    def _change_theme(self, data: Dict) -> Tuple[bool, str, Dict]:
        """تغییر تم سایت"""
        theme_code = data.get('theme_code')
        theme_name = data.get('theme', 'پیش‌فرض')
        
        if not self.site_settings:
            self.site_settings = SiteSettings.objects.create()
        
        if theme_code:
            self.site_settings.theme = theme_code
            self.site_settings.enable_custom_colors = False
            self.site_settings.save()  # متد save خودش apply_theme رو صدا می‌زنه
            
            message = f"🎨 تم سایت با موفقیت به '{theme_name}' تغییر کرد!\n"
            message += "رنگ‌بندی جدید اعمال شد. برای دیدن تغییرات صفحه رو Refresh کن."
            return True, message, {'theme': theme_code}
        
        # نمایش تم‌های موجود
        message = "🎨 **تم‌های موجود:**\n\n"
        message += "• پیش‌فرض (بنفش سلطنتی)\n"
        message += "• اقیانوسی (آبی و فیروزه‌ای)\n"
        message += "• جنگلی (سبز و طلایی)\n"
        message += "• غروب (نارنجی و صورتی)\n"
        message += "• نیمه‌شب (آبی تیره و نقره‌ای)\n"
        message += "• سایبرپانک (صورتی و آبی نئون)\n"
        message += "• کلاسیک (قرمز و سفید)\n"
        message += "• سلطنتی (بنفش و طلایی)\n"
        message += "• نئون (سبز و مشکی)\n"
        message += "• آبنباتی (صورتی و آبی روشن)\n\n"
        message += "کدوم تم رو می‌خوای؟ بگو مثلاً 'تم اقیانوسی'"
        
        return False, message, {}
    
    def _change_colors(self, data: Dict) -> Tuple[bool, str, Dict]:
        """تغییر رنگ‌بندی"""
        message = "🎨 برای تغییر دستی رنگ‌ها، باید از بخش 'تنظیمات سایت' در پنل ادمین استفاده کنی.\n"
        message += "اما می‌تونی با گفتن 'تغییر تم' یکی از تم‌های آماده رو انتخاب کنی!"
        return True, message, {}
    
    def _change_background(self, data: Dict) -> Tuple[bool, str, Dict]:
        """تغییر تصویر پس‌زمینه"""
        message = "🖼️ برای تغییر تصویر پس‌زمینه، لطفاً از بخش 'تنظیمات سایت' در پنل ادمین استفاده کن.\n"
        message += "اونجا می‌تونی عکس جدید آپلود کنی و تنظیماتش رو تغییر بدی."
        return True, message, {}
    
    # ========== عملیات سفارشات ==========
    
    def _view_orders(self, data: Dict) -> Tuple[bool, str, Dict]:
        """مشاهده سفارشات"""
        time_period = data.get('time_period', 'امروز')
        
        orders = Order.objects.all()
        
        # فیلتر بر اساس بازه زمانی
        now = timezone.now()
        if time_period == 'امروز':
            orders = orders.filter(created_at__date=now.date())
            period_text = 'امروز'
        elif time_period == 'دیروز':
            orders = orders.filter(created_at__date=now.date() - timedelta(days=1))
            period_text = 'دیروز'
        elif time_period == 'این هفته':
            start_of_week = now.date() - timedelta(days=now.weekday())
            orders = orders.filter(created_at__date__gte=start_of_week)
            period_text = 'این هفته'
        elif time_period == 'این ماه':
            orders = orders.filter(created_at__month=now.month, created_at__year=now.year)
            period_text = 'این ماه'
        else:
            period_text = time_period
        
        # فیلتر وضعیت خاص اگر خواسته شده
        status = data.get('status_code')
        if status:
            orders = orders.filter(status=status)
        
        orders = orders.order_by('-created_at')
        
        count = orders.count()
        total_amount = orders.aggregate(total=Sum('final_amount'))['total'] or 0
        
        if count == 0:
            return True, f"📭 هیچ سفارشی برای {period_text} ثبت نشده.", {}
        
        message = f"📦 **سفارشات {period_text}:**\n"
        message += f"📊 تعداد: {count} سفارش\n"
        message += f"💰 مجموع مبلغ: {total_amount:,} تومان\n\n"
        
        # نمایش ۵ سفارش آخر
        message += "**آخرین سفارشات:**\n"
        for order in orders[:5]:
            status_fa = dict(Order.STATUS_CHOICES).get(order.status, order.status)
            message += f"• {order.order_number}\n"
            message += f"  👤 {order.full_name}\n"
            message += f"  💵 {order.final_amount:,} تومان\n"
            message += f"  📊 {status_fa}\n\n"
        
        if count > 5:
            message += f"\n... و {count - 5} سفارش دیگر."
        
        return True, message, {'count': count, 'total': total_amount}
    
    def _change_order_status(self, data: Dict) -> Tuple[bool, str, Dict]:
        """تغییر وضعیت سفارش"""
        order_number = data.get('order_number')
        status_code = data.get('status_code')
        
        if not order_number:
            # نمایش سفارشات در انتظار
            pending_orders = Order.objects.filter(status='pending').order_by('-created_at')[:5]
            
            if not pending_orders.exists():
                return False, "هیچ سفارش در انتظاری وجود نداره. کدوم سفارش رو می‌خوای تغییر وضعیت بدی؟", {}
            
            message = "📋 **سفارشات در انتظار پرداخت:**\n\n"
            for order in pending_orders:
                message += f"• {order.order_number} - {order.full_name} - {order.final_amount:,} تومان\n"
            
            message += "\nکدوم سفارش رو می‌خوای تغییر وضعیت بدی؟ شماره سفارش رو بگو."
            return False, message, {'pending_orders': list(pending_orders.values('id', 'order_number', 'full_name'))}
        
        # پیدا کردن سفارش
        try:
            order = Order.objects.get(order_number__iexact=order_number)
        except Order.DoesNotExist:
            # جستجو با بخشی از شماره
            orders = Order.objects.filter(order_number__icontains=order_number)
            if orders.exists():
                order = orders.first()
            else:
                return False, f"سفارشی با شماره '{order_number}' پیدا نشد.", {}
        
        if not status_code:
            message = f"سفارش {order.order_number} الان در وضعیت '{order.get_status_display()}' هست.\n"
            message += "می‌تونی به یکی از این وضعیت‌ها تغییرش بدی:\n"
            message += "• پرداخت شده\n"
            message += "• تکمیل شده\n"
            message += "• لغو شده\n"
            message += "• مرجوع شده\n\n"
            message += "کدوم وضعیت رو می‌خوای؟"
            
            return False, message, {'order': {'id': order.id, 'order_number': order.order_number, 'status': order.status}}
        
        # تغییر وضعیت
        old_status = order.get_status_display()
        order.status = status_code
        order.save()
        
        new_status = order.get_status_display()
        
        message = f"✅ وضعیت سفارش {order.order_number} با موفقیت تغییر کرد:\n"
        message += f"از '{old_status}' به '{new_status}'"
        
        return True, message, {'order_id': order.id, 'new_status': new_status}
    
    # ========== عملیات کاربران ==========
    
    def _view_users(self, data: Dict) -> Tuple[bool, str, Dict]:
        """مشاهده کاربران"""
        users = User.objects.filter(is_staff=False).order_by('-date_joined')
        
        total_count = users.count()
        today_count = users.filter(date_joined__date=timezone.now().date()).count()
        
        message = f"👥 **آمار کاربران:**\n"
        message += f"• کل کاربران: {total_count} نفر\n"
        message += f"• ثبت نام امروز: {today_count} نفر\n\n"
        
        message += "**آخرین کاربران ثبت نام کرده:**\n"
        for user in users[:5]:
            try:
                phone = user.profile.phone or 'ثبت نشده'
            except:
                phone = 'ثبت نشده'
            
            message += f"• {user.username}"
            if user.email:
                message += f" - {user.email}"
            if phone != 'ثبت نشده':
                message += f" - {phone}"
            message += f"\n  📅 {user.date_joined.strftime('%Y/%m/%d')}\n\n"
        
        return True, message, {'total': total_count, 'today': today_count}
    
    def _send_message(self, data: Dict) -> Tuple[bool, str, Dict]:
        """ارسال پیام به کاربر"""
        username = data.get('username')
        
        if not username:
            # نمایش کاربران اخیر
            recent_users = User.objects.filter(
                chat_messages__isnull=False
            ).distinct().order_by('-date_joined')[:5]
            
            if recent_users.exists():
                message = "👥 **کاربرانی که اخیراً پیام دادن:**\n\n"
                for user in recent_users:
                    last_msg = user.chat_messages.order_by('-created_at').first()
                    message += f"• {user.username}"
                    if last_msg:
                        message += f" - آخرین پیام: {last_msg.created_at.strftime('%H:%M')}"
                    message += "\n"
            else:
                message = "👥 برای ارسال پیام، نام کاربری رو بگو. مثلاً: 'به کاربر ali پیام بده'"
            
            return False, message, {}
        
        try:
            target_user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            users = User.objects.filter(username__icontains=username)
            if users.exists():
                message = "چندتا کاربر با این اسم پیدا کردم:\n"
                for u in users[:5]:
                    message += f"• {u.username}\n"
                message += "\nدقیقاً کدوم رو می‌خوای؟"
                return False, message, {}
            return False, f"کاربری با نام '{username}' پیدا نشد.", {}
        
        message = f"برای ارسال پیام به {target_user.username}، لطفاً از بخش 'چت ادمین' در پنل استفاده کن.\n"
        message += f"👤 کاربر: {target_user.username}\n"
        if target_user.email:
            message += f"📧 ایمیل: {target_user.email}\n"
        
        return True, message, {'target_user': {'id': target_user.id, 'username': target_user.username}}
    
    # ========== عملیات آمار ==========
    
    def _sales_stats(self, data: Dict) -> Tuple[bool, str, Dict]:
        """آمار فروش"""
        time_period = data.get('time_period', 'امروز')
        
        now = timezone.now()
        
        if time_period == 'امروز':
            start_date = now.date()
            period_text = 'امروز'
        elif time_period == 'دیروز':
            start_date = now.date() - timedelta(days=1)
            period_text = 'دیروز'
        elif time_period == 'این هفته':
            start_date = now.date() - timedelta(days=now.weekday())
            period_text = 'این هفته'
        elif time_period == 'این ماه':
            start_date = now.date().replace(day=1)
            period_text = 'این ماه'
        else:
            start_date = now.date()
            period_text = 'امروز'
        
        orders = Order.objects.filter(created_at__date__gte=start_date, status__in=['paid', 'completed'])
        
        total_sales = orders.aggregate(total=Sum('final_amount'))['total'] or 0
        order_count = orders.count()
        
        # میانگین ارزش سفارش
        avg_order = total_sales / order_count if order_count > 0 else 0
        
        message = f"📊 **آمار فروش {period_text}:**\n\n"
        message += f"🛒 تعداد سفارشات: {order_count} سفارش\n"
        message += f"💰 مجموع فروش: {total_sales:,} تومان\n"
        message += f"📈 میانگین ارزش سفارش: {avg_order:,.0f} تومان\n"
        
        if order_count > 0:
            message += f"\n🎉 تبریک! {period_text} فروش خوبی داشتی!"
        else:
            message += f"\n😊 {period_text} هنوز فروشی ثبت نشده."
        
        return True, message, {
            'period': period_text,
            'total_sales': total_sales,
            'order_count': order_count,
            'avg_order': avg_order
        }
    
    def _site_settings(self, data: Dict) -> Tuple[bool, str, Dict]:
        """نمایش تنظیمات سایت"""
        if not self.site_settings:
            self.site_settings = SiteSettings.objects.create()
        
        message = "⚙️ **تنظیمات فعلی سایت:**\n\n"
        message += f"🏪 نام فروشگاه: {self.site_settings.site_name}\n"
        message += f"🎨 تم: {self.site_settings.get_theme_display()}\n"
        message += f"📞 تلفن: {self.site_settings.phone1}\n"
        message += f"📱 موبایل: {self.site_settings.mobile}\n"
        message += f"📧 ایمیل: {self.site_settings.email}\n"
        message += f"📍 آدرس: {self.site_settings.address_line1}\n\n"
        
        message += "برای تغییر هر کدوم، به بخش 'تنظیمات سایت' در پنل ادمین مراجعه کن."
        
        return True, message, {}