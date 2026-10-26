from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
import random
import string
from django.utils import timezone
import uuid

class SiteSettings(models.Model):
    THEME_CHOICES = [
        ('default', 'تم پیش‌فرض - بنفش سلطنتی'),
        ('ocean', 'تم اقیانوسی - آبی و فیروزه‌ای'),
        ('forest', 'تم جنگلی - سبز و طلایی'),
        ('sunset', 'تم غروب - نارنجی و صورتی'),
        ('midnight', 'تم نیمه‌شب - آبی تیره و نقره‌ای'),
        ('cyberpunk', 'تم سایبرپانک - صورتی و آبی نئون'),
        ('classic', 'تم کلاسیک - قرمز و سفید'),
        ('royal', 'تم سلطنتی - بنفش و طلایی'),
        ('neon', 'تم نئون - سبز و مشکی'),
        ('candy', 'تم آبنباتی - صورتی و آبی روشن'),
    ]
    
    theme = models.CharField(
        max_length=20, 
        choices=THEME_CHOICES, 
        default='default',
        verbose_name="تم آماده",
        help_text="با انتخاب تم، رنگ‌های زیر به صورت خودکار تنظیم می‌شوند"
    )
    
    enable_custom_colors = models.BooleanField(
        default=False, 
        verbose_name="فعال کردن تغییر دستی رنگ‌ها",
        help_text="اگر این گزینه فعال باشد، می‌توانید رنگ‌ها را دستی تغییر دهید. در غیر این صورت رنگ‌ها بر اساس تم تنظیم می‌شوند."
    )
    
    site_name = models.CharField(max_length=100, default="JOKERPLAYSTATION نیشابور", verbose_name="نام سایت")
    site_description = models.TextField(blank=True, verbose_name="توضیحات سایت")
    logo_text = models.CharField(max_length=50, default="JOKERPLAYSTATION", verbose_name="متن لوگو")
    
    background_image = models.ImageField(upload_to='backgrounds/', blank=True, null=True, verbose_name="عکس پس‌زمینه")
    background_overlay_opacity = models.PositiveIntegerField(default=70, verbose_name="درصد تیرگی روی عکس (0-100)")
    background_fixed = models.BooleanField(default=True, verbose_name="ثابت بودن پس‌زمینه")
    
    header_bg = models.CharField(max_length=20, default='#0A0F1F', verbose_name="رنگ پس‌زمینه هدر")
    header_text = models.CharField(max_length=20, default='#FFFFFF', verbose_name="رنگ متن هدر")
    header_accent = models.CharField(max_length=20, default='#00FFFF', verbose_name="رنگ تاکیدی هدر")
    
    nav_bg = models.CharField(max_length=20, default='#1A1F2F', verbose_name="رنگ پس‌زمینه منو")
    nav_text = models.CharField(max_length=20, default='#FFFFFF', verbose_name="رنگ متن منو")
    nav_hover = models.CharField(max_length=20, default='#00FFFF', verbose_name="رنگ هاور منو")
    
    dropdown_bg = models.CharField(max_length=20, default='#2A2F3F', verbose_name="رنگ پس‌زمینه زیرمنو")
    dropdown_text = models.CharField(max_length=20, default='#FFFFFF', verbose_name="رنگ متن زیرمنو")
    dropdown_hover = models.CharField(max_length=20, default='#FF00FF', verbose_name="رنگ هاور زیرمنو")
    
    button_primary_bg = models.CharField(max_length=20, default='#FF00FF', verbose_name="رنگ پس‌زمینه دکمه اصلی")
    button_primary_text = models.CharField(max_length=20, default='#000000', verbose_name="رنگ متن دکمه اصلی")
    button_secondary_bg = models.CharField(max_length=20, default='#00FFFF', verbose_name="رنگ پس‌زمینه دکمه فرعی")
    button_secondary_text = models.CharField(max_length=20, default='#000000', verbose_name="رنگ متن دکمه فرعی")
    
    footer_bg = models.CharField(max_length=20, default='#0A0F1F', verbose_name="رنگ پس‌زمینه فوتر")
    footer_text = models.CharField(max_length=20, default='#C0C0C0', verbose_name="رنگ متن فوتر")
    footer_heading = models.CharField(max_length=20, default='#00FFFF', verbose_name="رنگ عنوان فوتر")
    
    accent_1 = models.CharField(max_length=20, default='#00FFFF', verbose_name="رنگ تاکیدی ۱")
    accent_2 = models.CharField(max_length=20, default='#FF00FF', verbose_name="رنگ تاکیدی ۲")
    accent_3 = models.CharField(max_length=20, default='#FFFF00', verbose_name="رنگ تاکیدی ۳")
    
    cart_badge_bg = models.CharField(max_length=20, default='#FF0000', verbose_name="رنگ پس‌زمینه نشان سبد خرید")
    cart_badge_text = models.CharField(max_length=20, default='#FFFFFF', verbose_name="رنگ متن نشان سبد خرید")
    
    loading_1 = models.CharField(max_length=20, default='#00FFFF', verbose_name="رنگ لودینگ ۱")
    loading_2 = models.CharField(max_length=20, default='#FF00FF', verbose_name="رنگ لودینگ ۲")
    loading_3 = models.CharField(max_length=20, default='#FFFF00', verbose_name="رنگ لودینگ ۳")
    
    address_line1 = models.CharField(max_length=200, default="نیشابور، خیابان خیام", verbose_name="آدرس خط ۱")
    address_line2 = models.CharField(max_length=200, default="نبش خیام ۲۲", verbose_name="آدرس خط ۲", blank=True)
    address_city = models.CharField(max_length=100, default="نیشابور", verbose_name="شهر")
    address_state = models.CharField(max_length=100, default="خراسان رضوی", verbose_name="استان")
    address_postal_code = models.CharField(max_length=20, blank=True, verbose_name="کد پستی")
    
    phone1 = models.CharField(max_length=20, default="۰۵۱-۴۴۳۲۱۲۳۴", verbose_name="تلفن ۱")
    phone2 = models.CharField(max_length=20, blank=True, verbose_name="تلفن ۲")
    mobile = models.CharField(max_length=20, default="۰۹۱۵-۱۲۳-۴۵۶۷", verbose_name="موبایل")
    email = models.EmailField(default="info@jokerplaystation.ir", verbose_name="ایمیل")
    
    instagram = models.CharField(max_length=100, blank=True, default="jokerplaystation", verbose_name="اینستاگرام")
    telegram = models.CharField(max_length=100, blank=True, default="jokerplaystation", verbose_name="تلگرام")
    discord = models.CharField(max_length=100, blank=True, verbose_name="دیسکورد")
    whatsapp = models.CharField(max_length=100, blank=True, default="989123456789", verbose_name="واتساپ")
    

    min_amount_for_shaba = models.PositiveIntegerField(
        default=10000000, 
        verbose_name="حداقل مبلغ برای شماره شبا (تومان)",
        help_text="اگر مبلغ سفارش از این مقدار بیشتر باشد، شماره شبا نمایش داده می‌شود"
    )
    card_number = models.CharField(
        max_length=30, 
        default="6037-9972-4418-1732", 
        verbose_name="شماره کارت",
        help_text="برای مبالغ کمتر از حد مجاز"
    )
    card_holder_name = models.CharField(
        max_length=100, 
        default="محمد تقدیر", 
        verbose_name="نام صاحب کارت"
    )
    shaba_number = models.CharField(
        max_length=30, 
        default="IR123456789012345678901234", 
        verbose_name="شماره شبا",
        help_text="برای مبالغ بیشتر از حد مجاز"
    )
    bank_name = models.CharField(
        max_length=100, 
        default="بانک ملی", 
        verbose_name="نام بانک"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"
    
    def __str__(self):
        return f"تنظیمات سایت - {self.site_name}"
    
    def save(self, *args, **kwargs):
        if not self.enable_custom_colors:
            self.apply_theme(self.theme)
        super().save(*args, **kwargs)
    
    def apply_theme(self, theme):
        themes = {
            'default': {
                'header_bg': '#0A0F1F', 'header_accent': '#00FFFF', 'nav_bg': '#1A1F2F',
                'nav_hover': '#00FFFF', 'dropdown_bg': '#2A2F3F', 'dropdown_hover': '#FF00FF',
                'button_primary_bg': '#FF00FF', 'button_secondary_bg': '#00FFFF',
                'footer_bg': '#0A0F1F', 'footer_heading': '#00FFFF', 'accent_1': '#00FFFF',
                'accent_2': '#FF00FF', 'accent_3': '#FFFF00', 'loading_1': '#00FFFF',
                'loading_2': '#FF00FF', 'loading_3': '#FFFF00',
            },
            'ocean': {
                'header_bg': '#003366', 'header_accent': '#66CCFF', 'nav_bg': '#004488',
                'nav_hover': '#66CCFF', 'dropdown_bg': '#0055AA', 'dropdown_hover': '#99EEFF',
                'button_primary_bg': '#0066CC', 'button_secondary_bg': '#66CCFF',
                'footer_bg': '#002244', 'footer_heading': '#66CCFF', 'accent_1': '#3399FF',
                'accent_2': '#66CCFF', 'accent_3': '#99EEFF', 'loading_1': '#0066CC',
                'loading_2': '#3399FF', 'loading_3': '#66CCFF',
            },
            'forest': {
                'header_bg': '#1A3B1A', 'header_accent': '#7CFC00', 'nav_bg': '#2A4B2A',
                'nav_hover': '#7CFC00', 'dropdown_bg': '#3A5B3A', 'dropdown_hover': '#ADFF2F',
                'button_primary_bg': '#32CD32', 'button_secondary_bg': '#7CFC00',
                'footer_bg': '#0A2B0A', 'footer_heading': '#7CFC00', 'accent_1': '#32CD32',
                'accent_2': '#7CFC00', 'accent_3': '#ADFF2F', 'loading_1': '#228B22',
                'loading_2': '#32CD32', 'loading_3': '#7CFC00',
            },
            'sunset': {
                'header_bg': '#FF4500', 'header_accent': '#FFD700', 'nav_bg': '#FF6347',
                'nav_hover': '#FF69B4', 'dropdown_bg': '#FF8C00', 'dropdown_hover': '#FFA07A',
                'button_primary_bg': '#B22222', 'button_secondary_bg': '#FFA500',
                'footer_bg': '#8B4513', 'footer_heading': '#FFB6C1', 'accent_1': '#FF1493',
                'accent_2': '#FF69B4', 'accent_3': '#FFA07A', 'loading_1': '#FF4500',
                'loading_2': '#FFD700', 'loading_3': '#FF6347',
            },
            'midnight': {
                'header_bg': '#191970', 'header_accent': '#C0C0C0', 'nav_bg': '#000080',
                'nav_hover': '#A9A9A9', 'dropdown_bg': '#2F4F4F', 'dropdown_hover': '#708090',
                'button_primary_bg': '#4B0082', 'button_secondary_bg': '#4682B4',
                'footer_bg': '#0A0A2A', 'footer_heading': '#B0C4DE', 'accent_1': '#1E90FF',
                'accent_2': '#00CED1', 'accent_3': '#4169E1', 'loading_1': '#191970',
                'loading_2': '#C0C0C0', 'loading_3': '#000080',
            },
            'cyberpunk': {
                'header_bg': '#120458', 'header_accent': '#FF00FF', 'nav_bg': '#1E0B5C',
                'nav_hover': '#00FFFF', 'dropdown_bg': '#2A0F6A', 'dropdown_hover': '#FF00FF',
                'button_primary_bg': '#FF00FF', 'button_secondary_bg': '#00FFFF',
                'footer_bg': '#0A0340', 'footer_heading': '#FF00FF', 'accent_1': '#FF00FF',
                'accent_2': '#00FFFF', 'accent_3': '#FFFF00', 'loading_1': '#FF00FF',
                'loading_2': '#00FFFF', 'loading_3': '#FFFF00',
            },
            'classic': {
                'header_bg': '#B22222', 'header_accent': '#FFFFFF', 'nav_bg': '#8B0000',
                'nav_hover': '#F08080', 'dropdown_bg': '#A52A2A', 'dropdown_hover': '#CD5C5C',
                'button_primary_bg': '#DC143C', 'button_secondary_bg': '#F5F5F5',
                'footer_bg': '#2F0F0F', 'footer_heading': '#FFFAFA', 'accent_1': '#FF4500',
                'accent_2': '#B22222', 'accent_3': '#8B0000', 'loading_1': '#B22222',
                'loading_2': '#FFFFFF', 'loading_3': '#8B0000',
            },
            'royal': {
                'header_bg': '#800080', 'header_accent': '#FFD700', 'nav_bg': '#9370DB',
                'nav_hover': '#DAA520', 'dropdown_bg': '#4B0082', 'dropdown_hover': '#8A2BE2',
                'button_primary_bg': '#9932CC', 'button_secondary_bg': '#D4AF37',
                'footer_bg': '#2D1B3A', 'footer_heading': '#F0E68C', 'accent_1': '#BA55D3',
                'accent_2': '#9400D3', 'accent_3': '#8A2BE2', 'loading_1': '#800080',
                'loading_2': '#FFD700', 'loading_3': '#9370DB',
            },
            'neon': {
                'header_bg': '#0F0F0F', 'header_accent': '#00FF00', 'nav_bg': '#1F1F1F',
                'nav_hover': '#32CD32', 'dropdown_bg': '#2F2F2F', 'dropdown_hover': '#7CFC00',
                'button_primary_bg': '#00FF00', 'button_secondary_bg': '#7CFC00',
                'button_secondary_text': '#000000',
                'footer_bg': '#000000', 'footer_heading': '#ADFF2F', 'accent_1': '#7CFC00',
                'accent_2': '#32CD32', 'accent_3': '#228B22', 'loading_1': '#00FF00',
                'loading_2': '#7CFC00', 'loading_3': '#32CD32',
            },
            'candy': {
                'header_bg': '#FF69B4', 'header_accent': '#87CEEB', 'nav_bg': '#FFB6C1',
                'nav_text': '#000000', 'nav_hover': '#B0E0E6',
                'dropdown_bg': '#FFC0CB', 'dropdown_text': '#000000', 'dropdown_hover': '#ADD8E6',
                'button_primary_bg': '#FF1493', 'button_secondary_bg': '#00BFFF',
                'footer_bg': '#DDA0DD', 'footer_text': '#000000', 'footer_heading': '#1E90FF',
                'accent_1': '#FFA07A', 'accent_2': '#98FB98', 'accent_3': '#AFEEEE',
                'loading_1': '#FF69B4', 'loading_2': '#87CEEB', 'loading_3': '#98FB98',
            },
        }
        if theme in themes:
            for key, value in themes[theme].items():
                setattr(self, key, value)
    
    def get_full_address(self):
        address = self.address_line1
        if self.address_line2:
            address += f"، {self.address_line2}"
        address += f"، {self.address_city}، {self.address_state}"
        return address
    
    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            try:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return f"{r}, {g}, {b}"
            except ValueError:
                pass
        return "0, 255, 255"
    
    def get_header_accent_rgb(self):
        return self._hex_to_rgb(self.header_accent)
    
    def get_accent_1_rgb(self):
        return self._hex_to_rgb(self.accent_1)
    
    def get_accent_2_rgb(self):
        return self._hex_to_rgb(self.accent_2)
    
    def get_accent_3_rgb(self):
        return self._hex_to_rgb(self.accent_3)
    
    def get_loading_1_rgb(self):
        return self._hex_to_rgb(self.loading_1)
    
    def get_loading_2_rgb(self):
        return self._hex_to_rgb(self.loading_2)
    
    def get_loading_3_rgb(self):
        return self._hex_to_rgb(self.loading_3)
    
    def get_nav_hover_rgb(self):
        return self._hex_to_rgb(self.nav_hover)
    
    def get_dropdown_hover_rgb(self):
        return self._hex_to_rgb(self.dropdown_hover)
    
    def get_button_primary_bg_rgb(self):
        return self._hex_to_rgb(self.button_primary_bg)
    
    def get_button_secondary_bg_rgb(self):
        return self._hex_to_rgb(self.button_secondary_bg)


class Category(models.Model):
    CATEGORY_TYPES = [
        ('game', 'بازی'),
        ('movie', 'فیلم'),
        ('console', 'کنسول'),
        ('case', 'کیس'),
        ('console_accessory', 'لوازم جانبی کنسول'),
        ('pc_accessory', 'لوازم جانبی کامپیوتر'),
        ('phone_accessory', 'لوازم جانبی گوشی'),
    ]
    
    GAME_PLATFORMS = [
        ('pc', 'کامپیوتر'),
        ('playstation', 'پلی استیشن'),
        ('xbox', 'ایکس باکس'),
        ('none', 'ندارد'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    type = models.CharField(max_length=20, choices=CATEGORY_TYPES, verbose_name="نوع")
    game_platform = models.CharField(max_length=15, choices=GAME_PLATFORMS, default='none', verbose_name="پلتفرم بازی")
    image = models.ImageField(upload_to='categories/', verbose_name="تصویر", blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('shop:category_detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        if self.type == 'game':
            return f"{self.get_game_platform_display()} - {self.name}"
        return self.name
    
    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"


class GameList(models.Model):
    GAME_PLATFORMS = [
        ('pc', 'کامپیوتر'),
        ('playstation', 'پلی استیشن'),
        ('xbox', 'ایکس باکس'),
    ]
    
    GAME_FEATURES = [
        ('open_world', '🌍 جهان باز'),
        ('story_rich', '📖 داستانی'),
        ('action', '⚡ اکشن'),
        ('adventure', '🗺️ ماجراجویی'),
        ('rpg', '🎭 آرپی‌جی'),
        ('strategy', '♟️ استراتژی'),
        ('survival', '🏕️ بقا'),
        ('horror', '👻 ترسناک'),
        ('puzzle', '🧩 پازلی'),
        ('multiplayer', '👥 چند نفره آنلاین'),
        ('coop', '🤝 همکاری'),
        ('singleplayer', '🎮 تک نفره'),
        ('competitive', '🏆 رقابتی'),
        ('sandbox', '🎨 سندباکس'),
        ('racing', '🏎️ مسابقه‌ای'),
        ('sports', '⚽ ورزشی'),
        ('simulation', '🖥️ شبیه‌سازی'),
        ('roguelike', '🔄 روگلایک'),
        ('indie', '🎨 ایندی'),
        ('aaa', '💎 سه‌آ'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="نام بازی")
    platform = models.CharField(max_length=15, choices=GAME_PLATFORMS, verbose_name="پلتفرم")
    image = models.ImageField(upload_to='game_list/', verbose_name="تصویر بازی")
    
    description = models.TextField(blank=True, verbose_name="توضیحات کوتاه")
    story_summary = models.TextField(blank=True, verbose_name="خلاصه داستان")
    features = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name="ویژگی‌های بازی",
        help_text="ویژگی‌های بازی را با کاما جدا کنید (مثال: open_world,story_rich,action)"
    )
    
    developer = models.CharField(max_length=200, blank=True, verbose_name="سازنده")
    publisher = models.CharField(max_length=200, blank=True, verbose_name="ناشر")
    release_date = models.DateField(null=True, blank=True, verbose_name="تاریخ انتشار")
    trailer_url = models.URLField(blank=True, verbose_name="لینک تریلر (یوتیوب)")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0, verbose_name="امتیاز (0-5)")
    
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_features_list(self):
        if self.features:
            return [f.strip() for f in self.features.split(',') if f.strip()]
        return []
    
    def get_feature_display_name(self, feature_key):
        feature_dict = dict(self.GAME_FEATURES)
        return feature_dict.get(feature_key, feature_key)
    
    def get_rating_stars(self):
        full_stars = int(self.rating)
        half_star = self.rating - full_stars >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)
        return {'full': full_stars, 'half': half_star, 'empty': empty_stars}
    
    def __str__(self):
        return f"{self.name} ({self.get_platform_display()})"
    
    class Meta:
        verbose_name = "لیست بازی"
        verbose_name_plural = "لیست بازی‌ها"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    referral_code = models.CharField(max_length=7, unique=True, verbose_name="کد معرف")
    credits = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="اعتبار")
    phone = models.CharField(max_length=15, blank=True, verbose_name="شماره تماس")
    address = models.TextField(blank=True, verbose_name="آدرس")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="کد پستی")
    full_name = models.CharField(max_length=100, blank=True, verbose_name="نام و نام خانوادگی")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
        super().save(*args, **kwargs)
    
    def generate_referral_code(self):
        characters = string.ascii_uppercase + string.digits
        code = ''.join(random.choice(characters) for _ in range(7))
        while UserProfile.objects.filter(referral_code=code).exists():
            code = ''.join(random.choice(characters) for _ in range(7))
        return code
    
    def __str__(self):
        return f"{self.user.username} - {self.referral_code}"


class ReferralSettings(models.Model):
    is_active = models.BooleanField(default=True, verbose_name="فعال بودن سیستم دعوت")
    referrer_discount_type = models.CharField(
        max_length=10, 
        choices=[('percentage', 'درصدی'), ('fixed', 'ثابت')],
        default='percentage',
        verbose_name="نوع تخفیف برای معرف"
    )
    referrer_discount_amount = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=5.00,
        verbose_name="مقدار تخفیف برای معرف (درصد یا مبلغ ثابت)"
    )
    referrer_credit_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        default=50000,
        verbose_name="مقدار اعتبار برای معرف (تومان)"
    )
    new_user_discount_type = models.CharField(
        max_length=10, 
        choices=[('percentage', 'درصدی'), ('fixed', 'ثابت')],
        default='percentage',
        verbose_name="نوع تخفیف برای کاربر جدید"
    )
    new_user_discount_amount = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=5.00,
        verbose_name="مقدار تخفیف برای کاربر جدید (درصد یا مبلغ ثابت)"
    )
    discount_expiry_days = models.PositiveIntegerField(
        default=30,
        verbose_name="مدت اعتبار کد تخفیف (روز)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "تنظیمات دعوت"
        verbose_name_plural = "تنظیمات دعوت"
    
    def __str__(self):
        return f"تنظیمات دعوت - {'فعال' if self.is_active else 'غیرفعال'}"


class ReferralLog(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made', verbose_name="معرف")
    new_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referred_by', verbose_name="کاربر جدید")
    discount_code = models.ForeignKey('DiscountCode', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="کد تخفیف")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "لاگ دعوت"
        verbose_name_plural = "لاگ‌های دعوت"
    
    def __str__(self):
        return f"{self.referrer.username} -> {self.new_user.username}"


class DiscountCode(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'درصدی'),
        ('fixed', 'ثابت'),
    ]
    
    code = models.CharField(max_length=50, unique=True, verbose_name="کد تخفیف")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='percentage', verbose_name="نوع تخفیف")
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=5.00, verbose_name="مبلغ/درصد تخفیف")
    is_used = models.BooleanField(default=False, verbose_name="استفاده شده")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name="تاریخ انقضا")
    
    def __str__(self):
        return f"{self.code} - {self.user.username}"
    
    def apply_discount(self, total_amount):
        if self.discount_type == 'percentage':
            discount_amount = (total_amount * self.amount) / 100
        else:
            discount_amount = self.amount
        return max(total_amount - discount_amount, 0)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="دسته‌بندی")
    game_list = models.ForeignKey(GameList, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name="لیست بازی")
    name = models.CharField(max_length=100, verbose_name="نام محصول")
    description = models.TextField(verbose_name="توضیحات محصول")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="قیمت")
    image = models.ImageField(upload_to='products/', verbose_name="تصویر محصول", blank=True)
    is_available = models.BooleanField(default=True, verbose_name="موجود")
    is_new = models.BooleanField(default=False, verbose_name="محصول جدید")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"
    
    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"سبد خرید {self.user.username}"
    
    def total_price(self):
        return sum(item.total_price() for item in self.items.all())
    
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def total_price(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس (تکمیل نشده)'),
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('completed', 'تکمیل شده'),
        ('cancelled', 'لغو شده'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True, blank=True, verbose_name="شماره سفارش")
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="مبلغ کل")
    discount_code = models.ForeignKey(DiscountCode, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="کد تخفیف")
    final_amount = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="مبلغ نهایی")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="وضعیت")
    
    full_name = models.CharField(max_length=100, blank=True, verbose_name="نام و نام خانوادگی گیرنده")
    phone = models.CharField(max_length=15, blank=True, verbose_name="شماره تماس")
    address = models.TextField(blank=True, verbose_name="آدرس کامل")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="کد پستی")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number and self.status != 'draft':
            self.order_number = f"ORD-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        if not self.final_amount:
            if self.discount_code:
                self.final_amount = self.discount_code.apply_discount(self.total_amount)
            else:
                self.final_amount = self.total_amount
        super().save(*args, **kwargs)
    
    def __str__(self):
        if self.order_number:
            return f"سفارش {self.order_number} - {self.user.username}"
        return f"سفارش ناتمام {self.user.username} - {self.created_at}"
    
    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"


class PaymentReceipt(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='receipt')
    receipt_image = models.ImageField(upload_to='receipts/', verbose_name="تصویر رسید پرداخت")
    payment_method = models.CharField(max_length=20, choices=[('card', 'کارت به کارت'), ('shaba', 'شماره شبا')], default='card', verbose_name="روش پرداخت")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"رسید پرداخت برای سفارش {self.order.order_number}"


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField(verbose_name="پیام", blank=True, null=True)
    image = models.ImageField(upload_to='chat/images/', verbose_name="عکس", blank=True, null=True)
    video = models.FileField(upload_to='chat/videos/', verbose_name="فیلم", blank=True, null=True)
    is_admin = models.BooleanField(default=False, verbose_name="پیام از ادمین")
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "پیام چت"
        verbose_name_plural = "پیام‌های چت"
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


class Video(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان")
    video_file = models.FileField(upload_to='videos/', verbose_name="فایل ویدیو")
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True, verbose_name="تصویر بندانگشتی")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "ویدیو"
        verbose_name_plural = "ویدیوها"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان خبر")
    content = models.TextField(verbose_name="محتوا")
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="تصویر")
    slug = models.SlugField(unique=True, blank=True, verbose_name="اسلاگ")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    views = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while News.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "خبر"
        verbose_name_plural = "اخبار"
        ordering = ['-created_at']


class Slider(models.Model):
    image = models.ImageField(upload_to='slider/', verbose_name="تصویر اسلاید")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "اسلایدر"
        verbose_name_plural = "اسلایدرها"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"اسلاید {self.id}"


# ==================== مدل جدید درباره ما ====================

class AboutUs(models.Model):
    """مدل درباره ما با قابلیت ویرایش از پنل ادمین"""
    title = models.CharField(max_length=200, default="درباره ما", verbose_name="عنوان")
    content = models.TextField(verbose_name="متن درباره ما")
    image = models.ImageField(upload_to='about/', blank=True, null=True, verbose_name="تصویر")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "درباره ما"
        verbose_name_plural = "درباره ما"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # فقط یک رکورد فعال وجود داشته باشد
        if self.is_active:
            AboutUs.objects.filter(is_active=True).exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)