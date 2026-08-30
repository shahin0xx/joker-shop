from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile, ReferralSettings, SiteSettings, AboutUs

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

@receiver(post_migrate)
def create_default_settings(sender, **kwargs):
    if sender.name == 'shop':
        # ایجاد تنظیمات پیش‌فرض دعوت
        ReferralSettings.objects.get_or_create(
            id=1,
            defaults={
                'is_active': True,
                'referrer_discount_type': 'percentage',
                'referrer_discount_amount': 5.00,
                'referrer_credit_amount': 50000,
                'new_user_discount_type': 'percentage',
                'new_user_discount_amount': 5.00,
                'discount_expiry_days': 30
            }
        )
        
        # ایجاد تنظیمات پیش‌فرض سایت
        SiteSettings.objects.get_or_create(
            id=1,
            defaults={
                'site_name': 'JOKERPLAYSTATION نیشابور',
                'site_description': 'اولین و بزرگترین فروشگاه تخصصی پلی استیشن در نیشابور',
                'logo_text': 'JOKERPLAYSTATION',
                'theme': 'default',
                'enable_custom_colors': False,
                'header_bg': '#0A0F1F',
                'header_text': '#FFFFFF',
                'header_accent': '#00FFFF',
                'nav_bg': '#1A1F2F',
                'nav_text': '#FFFFFF',
                'nav_hover': '#00FFFF',
                'dropdown_bg': '#2A2F3F',
                'dropdown_text': '#FFFFFF',
                'dropdown_hover': '#FF00FF',
                'button_primary_bg': '#FF00FF',
                'button_primary_text': '#000000',
                'button_secondary_bg': '#00FFFF',
                'button_secondary_text': '#000000',
                'footer_bg': '#0A0F1F',
                'footer_text': '#C0C0C0',
                'footer_heading': '#00FFFF',
                'accent_1': '#00FFFF',
                'accent_2': '#FF00FF',
                'accent_3': '#FFFF00',
                'cart_badge_bg': '#FF0000',
                'cart_badge_text': '#FFFFFF',
                'loading_1': '#00FFFF',
                'loading_2': '#FF00FF',
                'loading_3': '#FFFF00',
                'address_line1': 'نیشابور، خیابان خیام',
                'address_line2': 'نبش خیام ۲۲',
                'address_city': 'نیشابور',
                'address_state': 'خراسان رضوی',
                'phone1': '۰۵۱-۴۴۳۲۱۲۳۴',
                'mobile': '۰۹۱۵-۱۲۳-۴۵۶۷',
                'email': 'info@jokerplaystation.ir',
                'instagram': 'jokerplaystation',
                'telegram': 'jokerplaystation',
                'whatsapp': '989123456789',
                'min_amount_for_shaba': 10000000,
                'card_number': '6037-9972-4418-1732',
                'card_holder_name': 'محمد تقدیر',
                'shaba_number': 'IR123456789012345678901234',
                'bank_name': 'بانک ملی',
            }
        )
        
        # ایجاد محتوای پیش‌فرض درباره ما
        AboutUs.objects.get_or_create(
            is_active=True,
            defaults={
                'title': 'درباره JOKERPLAYSTATION',
                'content': 'JOKERPLAYSTATION اولین و بزرگترین فروشگاه تخصصی پلی استیشن در نیشابور است. ما با سالها تجربه در زمینه فروش محصولات گیمینگ، کنسول‌های پلی استیشن، بازی‌های اورجینال و لوازم جانبی، همواره تلاش می‌کنیم بهترین خدمات را به مشتریان عزیز ارائه دهیم.\n\nما متعهد به ارائه محصولات اصل با بهترین قیمت و گارانتی معتبر هستیم. تیم ما در JOKERPLAYSTATION همواره آماده پاسخگویی به سوالات شما عزیزان است.',
            }
        )


def user_has_unused_discount_codes(self):
    from .models import DiscountCode
    return self.discountcode_set.filter(is_used=False, expires_at__gte=timezone.now()).exists()

def user_get_unused_discount_codes(self):
    from .models import DiscountCode
    return self.discountcode_set.filter(is_used=False, expires_at__gte=timezone.now())

User.add_to_class('has_unused_discount_codes', user_has_unused_discount_codes)
User.add_to_class('get_unused_discount_codes', user_get_unused_discount_codes)