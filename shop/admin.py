from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django import forms
from .models import *


# ==================== فرم‌های سفارشی ====================

class GameListAdminForm(forms.ModelForm):
    """فرم ادمین برای GameList با ویژگی‌های تیک‌زدنی و فارسی"""
    
    features = forms.MultipleChoiceField(
        choices=GameList.GAME_FEATURES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'features-checkbox-grid',
        }),
        label="ویژگی‌های بازی",
        help_text="ویژگی‌های مورد نظر را انتخاب کنید"
    )
    
    # فیلد تاریخ با ویجت و فرمت مشخص
    release_date = forms.DateField(
        required=False,
        label="تاریخ انتشار",
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'vDateField',
            },
            format='%Y-%m-%d'
        ),
        input_formats=['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y'],
        help_text="تاریخ را به فرمت YYYY-MM-DD وارد کنید (مثال: 2024-01-15)"
    )
    
    class Meta:
        model = GameList
        # لیست صریح فیلدها به جای '__all__' برای جلوگیری از تداخل با fieldsets
        fields = [
            'name', 'platform', 'image',
            'description', 'story_summary', 'features',
            'developer', 'publisher', 'release_date', 'trailer_url',
            'rating', 'is_active',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # اگر بازی قبلاً ذخیره شده، ویژگی‌های فعلی را نمایش بده
        if self.instance and self.instance.pk and self.instance.features:
            initial_features = self.instance.get_features_list()
            self.initial['features'] = initial_features
        # برای فرمت درست تاریخ در حالت ویرایش
        if self.instance and self.instance.pk and self.instance.release_date:
            self.initial['release_date'] = self.instance.release_date.strftime('%Y-%m-%d')
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # ویژگی‌های انتخاب شده را به صورت رشته کاما جدا ذخیره کن
        features = self.cleaned_data.get('features', [])
        instance.features = ','.join(features)
        if commit:
            instance.save()
            self.save_m2m()
        return instance


# ==================== Inlineها ====================

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'پروفایل کاربر'
    fields = [
        'referral_code',
        'credits',
        'full_name',
        'phone',
        'address',
        'postal_code',
        'created_at',
        'updated_at'
    ]
    readonly_fields = ['referral_code', 'created_at', 'updated_at']
    extra = 0


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'total_price']
    can_delete = False
    
    def total_price(self, obj):
        return f'{obj.total_price():,} تومان'
    total_price.short_description = 'قیمت کل'


class PaymentReceiptInline(admin.StackedInline):
    model = PaymentReceipt
    extra = 0
    readonly_fields = ['receipt_image', 'payment_method', 'uploaded_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


# ==================== Admin: User ====================

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email')}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


# ==================== Admin: SiteSettings ====================

class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'theme', 'enable_custom_colors', 'show_colors', 'updated_at']
    list_filter = ['theme', 'enable_custom_colors']
    search_fields = ['site_name']
    
    fieldsets = (
        ('اطلاعات عمومی سایت', {
            'fields': ('site_name', 'site_description', 'logo_text'),
        }),
        ('تم و رنگ‌بندی', {
            'fields': ('theme', 'enable_custom_colors'),
        }),
        ('پس‌زمینه سایت', {
            'fields': ('background_image', 'background_overlay_opacity', 'background_fixed'),
        }),
        ('رنگ‌بندی هدر', {
            'fields': ('header_bg', 'header_text', 'header_accent'),
        }),
        ('رنگ‌بندی منو', {
            'fields': ('nav_bg', 'nav_text', 'nav_hover'),
        }),
        ('رنگ‌بندی زیرمنو', {
            'fields': ('dropdown_bg', 'dropdown_text', 'dropdown_hover'),
        }),
        ('رنگ‌بندی دکمه‌ها', {
            'fields': ('button_primary_bg', 'button_primary_text', 'button_secondary_bg', 'button_secondary_text'),
        }),
        ('رنگ‌بندی فوتر', {
            'fields': ('footer_bg', 'footer_text', 'footer_heading'),
        }),
        ('رنگ‌های تاکیدی', {
            'fields': ('accent_1', 'accent_2', 'accent_3'),
        }),
        ('رنگ‌های ویژه', {
            'fields': ('cart_badge_bg', 'cart_badge_text', 'loading_1', 'loading_2', 'loading_3'),
        }),
        ('آدرس فروشگاه', {
            'fields': ('address_line1', 'address_line2', 'address_city', 'address_state', 'address_postal_code'),
        }),
        ('اطلاعات تماس', {
            'fields': ('phone1', 'phone2', 'mobile', 'email'),
        }),
        ('شبکه‌های اجتماعی', {
            'fields': ('instagram', 'telegram', 'discord', 'whatsapp'),
        }),
        ('تنظیمات پرداخت', {
            'fields': ('min_amount_for_shaba', 'card_number', 'card_holder_name', 'shaba_number', 'bank_name'),
        }),
    )
    
    def show_colors(self, obj):
        colors = [
            obj.header_bg, obj.header_accent, obj.nav_bg,
            obj.button_primary_bg, obj.footer_bg, obj.accent_1
        ]
        html = '<div style="display: flex; gap: 5px;">'
        for color in colors[:5]:
            html += f'<div style="width: 20px; height: 20px; background: {color}; border-radius: 4px; border: 1px solid #fff;"></div>'
        html += '</div>'
        return mark_safe(html)
    show_colors.short_description = 'نمونه رنگ‌ها'
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


# ==================== Admin: Category ====================

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'game_platform', 'products_count', 'is_active', 'created_at']
    list_filter = ['type', 'game_platform', 'is_active', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    list_per_page = 25
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'type', 'game_platform', 'is_active')
        }),
        ('تصویر و اسلاگ', {
            'fields': ('image', 'slug')
        }),
    )
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'تعداد محصولات'


# ==================== Admin: GameList ====================

class GameListAdmin(admin.ModelAdmin):
    form = GameListAdminForm
    
    list_display = ['name', 'platform', 'developer', 'release_date', 'rating', 'is_active', 'created_at']
    list_filter = ['platform', 'is_active', 'release_date', 'created_at']
    search_fields = ['name', 'developer', 'publisher', 'description', 'story_summary']
    list_editable = ['is_active', 'rating']
    list_per_page = 25
    date_hierarchy = 'release_date'
    
    fieldsets = (
        ('اطلاعات اصلی بازی', {
            'fields': ('name', 'platform', 'image', 'is_active')
        }),
        ('توضیحات و داستان', {
            'fields': ('description', 'story_summary')
        }),
        ('ویژگی‌های بازی', {
            'fields': ('features',),
            'classes': ('wide',),
            'description': 'ویژگی‌های مورد نظر را انتخاب کنید'
        }),
        ('اطلاعات انتشار', {
            'fields': ('developer', 'publisher', 'release_date', 'trailer_url')
        }),
        ('امتیاز', {
            'fields': ('rating',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'تعداد محصولات مرتبط'


# ==================== Admin: Product ====================

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'game_list', 'price_display', 'is_available', 'is_new', 'created_at']
    list_filter = ['is_available', 'is_new', 'category', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_available', 'is_new']
    list_per_page = 25
    autocomplete_fields = ['category', 'game_list']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'category', 'game_list', 'price', 'is_available', 'is_new')
        }),
        ('توضیحات و تصویر', {
            'fields': ('description', 'image')
        }),
    )
    
    def price_display(self, obj):
        return f'{obj.price:,} تومان'
    price_display.short_description = 'قیمت'
    price_display.admin_order_field = 'price'


# ==================== Admin: Cart ====================

class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price_display', 'total_quantity', 'created_at']
    search_fields = ['user__username']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]
    
    def total_price_display(self, obj):
        return f'{obj.total_price():,} تومان'
    total_price_display.short_description = 'قیمت کل'
    total_price_display.admin_order_field = 'id'
    
    def total_quantity(self, obj):
        return obj.total_quantity()
    total_quantity.short_description = 'تعداد اقلام'
    
    def has_add_permission(self, request):
        return False


class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity', 'total_price_display']
    search_fields = ['cart__user__username', 'product__name']
    list_filter = ['cart__user']
    autocomplete_fields = ['cart', 'product']
    
    def total_price_display(self, obj):
        return f'{obj.total_price():,} تومان'
    total_price_display.short_description = 'قیمت کل'
    total_price_display.admin_order_field = 'quantity'


# ==================== Admin: Order ====================

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'full_name', 'show_amount', 'status_colored', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'order_number', 'full_name', 'phone']
    readonly_fields = ['order_number', 'total_amount', 'final_amount', 'created_at', 'updated_at']
    list_per_page = 25
    inlines = [PaymentReceiptInline]
    
    fieldsets = (
        ('اطلاعات سفارش', {
            'fields': ('order_number', 'user', 'status', 'discount_code')
        }),
        ('مبالغ', {
            'fields': ('total_amount', 'final_amount'),
        }),
        ('اطلاعات گیرنده', {
            'fields': ('full_name', 'phone', 'address', 'postal_code'),
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def show_amount(self, obj):
        return f'{obj.final_amount:,} تومان'
    show_amount.short_description = 'مبلغ'
    show_amount.admin_order_field = 'final_amount'
    
    def status_colored(self, obj):
        colors = {
            'draft': '#888888',
            'pending': '#FFA500',
            'paid': '#00FFFF',
            'completed': '#00FF00',
            'cancelled': '#FF0000',
        }
        texts = {
            'draft': 'پیش‌نویس',
            'pending': 'در انتظار پرداخت',
            'paid': 'پرداخت شده',
            'completed': 'تکمیل شده',
            'cancelled': 'لغو شده',
        }
        return mark_safe(
            f'<span style="color: {colors.get(obj.status, "#FFFFFF")}; '
            f'background: rgba(0,0,0,0.5); padding: 3px 8px; border-radius: 12px;">'
            f'{texts.get(obj.status, obj.status)}</span>'
        )
    status_colored.short_description = 'وضعیت'
    status_colored.admin_order_field = 'status'
    
    actions = ['mark_as_paid', 'mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='paid')
        self.message_user(request, f'{updated} سفارش به وضعیت "پرداخت شده" تغییر یافت.')
    mark_as_paid.short_description = 'تغییر وضعیت به پرداخت شده'
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} سفارش به وضعیت "تکمیل شده" تغییر یافت.')
    mark_as_completed.short_description = 'تغییر وضعیت به تکمیل شده'
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} سفارش به وضعیت "لغو شده" تغییر یافت.')
    mark_as_cancelled.short_description = 'تغییر وضعیت به لغو شده'


# ==================== Admin: PaymentReceipt ====================

class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'payment_method', 'image_preview', 'uploaded_at']
    list_filter = ['payment_method', 'uploaded_at']
    search_fields = ['order__order_number']
    readonly_fields = ['order', 'receipt_image', 'payment_method', 'uploaded_at', 'image_preview_large']
    
    fieldsets = (
        ('اطلاعات رسید', {
            'fields': ('order', 'payment_method', 'uploaded_at')
        }),
        ('تصویر رسید', {
            'fields': ('receipt_image', 'image_preview_large')
        }),
    )
    
    def order_link(self, obj):
        url = reverse('admin:shop_order_change', args=[obj.order.id])
        return mark_safe(f'<a href="{url}">{obj.order.order_number}</a>')
    order_link.short_description = 'سفارش'
    
    def image_preview(self, obj):
        if obj.receipt_image:
            return mark_safe(f'<img src="{obj.receipt_image.url}" style="width: 50px; height: 50px; border-radius: 5px;" />')
        return 'ندارد'
    image_preview.short_description = 'پیش‌نمایش'
    
    def image_preview_large(self, obj):
        if obj.receipt_image:
            return mark_safe(f'<img src="{obj.receipt_image.url}" style="max-width: 400px; max-height: 400px; border-radius: 10px;" />')
        return 'تصویری وجود ندارد'
    image_preview_large.short_description = 'پیش‌نمایش بزرگ'
    
    def has_add_permission(self, request):
        return False


# ==================== Admin: DiscountCode ====================

class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'user', 'discount_display', 'show_status', 'expires_at', 'created_at']
    list_filter = ['is_used', 'discount_type', 'expires_at', 'created_at']
    search_fields = ['code', 'user__username']
    autocomplete_fields = ['user']
    date_hierarchy = 'expires_at'
    
    fieldsets = (
        ('اطلاعات کد', {
            'fields': ('code', 'user', 'discount_type', 'amount', 'is_used', 'expires_at')
        }),
        ('تاریخ ایجاد', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at']
    
    def discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return f'{obj.amount}%'
        return f'{obj.amount:,.0f} تومان'
    discount_display.short_description = 'مقدار تخفیف'
    discount_display.admin_order_field = 'amount'
    
    def show_status(self, obj):
        if obj.is_used:
            return mark_safe('<span style="color: #FF0000;">✅ استفاده شده</span>')
        return mark_safe('<span style="color: #00FF00;">🟢 فعال</span>')
    show_status.short_description = 'وضعیت'
    show_status.admin_order_field = 'is_used'
    
    actions = ['mark_as_used', 'mark_as_unused']
    
    def mark_as_used(self, request, queryset):
        updated = queryset.update(is_used=True)
        self.message_user(request, f'{updated} کد تخفیف به وضعیت "استفاده شده" تغییر یافت.')
    mark_as_used.short_description = 'تغییر وضعیت به استفاده شده'
    
    def mark_as_unused(self, request, queryset):
        updated = queryset.update(is_used=False)
        self.message_user(request, f'{updated} کد تخفیف به وضعیت "فعال" تغییر یافت.')
    mark_as_unused.short_description = 'تغییر وضعیت به فعال'


# ==================== Admin: ChatMessage ====================

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'message_short', 'get_sender', 'get_read', 'created_at']
    list_filter = ['is_admin', 'is_read', 'created_at']
    search_fields = ['user__username', 'message']
    readonly_fields = ['created_at', 'full_message_display']
    list_per_page = 50
    
    fieldsets = (
        ('اطلاعات پیام', {
            'fields': ('user', 'is_admin', 'is_read', 'created_at')
        }),
        ('محتوا', {
            'fields': ('message', 'image', 'video', 'full_message_display')
        }),
    )
    
    def message_short(self, obj):
        if obj.message:
            return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
        elif obj.image:
            return '[عکس]'
        elif obj.video:
            return '[فیلم]'
        return '[بدون متن]'
    message_short.short_description = 'پیام'
    
    def full_message_display(self, obj):
        result = []
        if obj.message:
            result.append(
                f'<div style="margin-bottom: 10px; padding: 10px; background: #333; '
                f'border-radius: 5px; color: #fff;"><strong>متن پیام:</strong><br>{obj.message}</div>'
            )
        if obj.image:
            result.append(
                f'<div style="margin-bottom: 10px;"><strong>تصویر:</strong><br>'
                f'<img src="{obj.image.url}" style="max-width: 300px; border-radius: 5px;" /></div>'
            )
        if obj.video:
            result.append(
                f'<div style="margin-bottom: 10px;"><strong>فیلم:</strong><br>'
                f'<video src="{obj.video.url}" controls style="max-width: 300px; border-radius: 5px;"></video></div>'
            )
        if not result:
            return 'محتوا وجود ندارد'
        return mark_safe(''.join(result))
    full_message_display.short_description = 'مشاهده کامل'
    
    def get_sender(self, obj):
        return 'ادمین' if obj.is_admin else 'کاربر'
    get_sender.short_description = 'فرستنده'
    get_sender.admin_order_field = 'is_admin'
    
    def get_read(self, obj):
        return 'خوانده شده' if obj.is_read else 'خوانده نشده'
    get_read.short_description = 'وضعیت'
    get_read.admin_order_field = 'is_read'
    
    actions = ['mark_read', 'mark_unread']
    
    def mark_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} پیام به وضعیت "خوانده شده" تغییر یافت.')
    mark_read.short_description = 'علامت‌گذاری به عنوان خوانده شده'
    
    def mark_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} پیام به وضعیت "خوانده نشده" تغییر یافت.')
    mark_unread.short_description = 'علامت‌گذاری به عنوان خوانده نشده'


# ==================== Admin: Video ====================

class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'thumbnail_preview', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at', 'video_preview']
    
    fieldsets = (
        ('اطلاعات ویدیو', {
            'fields': ('title', 'description', 'is_active')
        }),
        ('فایل‌ها', {
            'fields': ('video_file', 'thumbnail', 'video_preview')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return mark_safe(f'<img src="{obj.thumbnail.url}" style="width: 50px; height: 50px; border-radius: 5px;" />')
        return 'ندارد'
    thumbnail_preview.short_description = 'تصویر'
    
    def video_preview(self, obj):
        if obj.video_file:
            return mark_safe(f'<video src="{obj.video_file.url}" controls style="max-width: 400px; max-height: 300px; border-radius: 10px;"></video>')
        return 'ویدیویی وجود ندارد'
    video_preview.short_description = 'پیش‌نمایش ویدیو'


# ==================== Admin: News ====================

class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'views', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'created_at', 'updated_at', 'content_preview']
    list_editable = ['is_active']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('عنوان و محتوا', {
            'fields': ('title', 'content', 'content_preview')
        }),
        ('تصویر و اسلاگ', {
            'fields': ('image', 'slug')
        }),
        ('وضعیت و آمار', {
            'fields': ('is_active', 'views')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="width: 50px; height: 50px; border-radius: 5px;" />')
        return 'ندارد'
    image_preview.short_description = 'تصویر'
    
    def content_preview(self, obj):
        if obj.content:
            return mark_safe(
                f'<div style="background: #f5f5f5; padding: 10px; border-radius: 5px; '
                f'max-height: 200px; overflow-y: auto; color: #000;">{obj.content}</div>'
            )
        return 'محتوا وارد نشده'
    content_preview.short_description = 'پیش‌نمایش محتوا'


# ==================== Admin: Slider ====================

class SliderAdmin(admin.ModelAdmin):
    list_display = ['id', 'image_preview', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'image_preview_large']
    
    fieldsets = (
        ('تصویر اسلاید', {
            'fields': ('image', 'image_preview_large', 'is_active')
        }),
        ('تاریخ ایجاد', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="width: 50px; height: 50px; border-radius: 5px;" />')
        return 'ندارد'
    image_preview.short_description = 'تصویر'
    
    def image_preview_large(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-width: 600px; max-height: 300px; border-radius: 10px;" />')
        return 'تصویری وجود ندارد'
    image_preview_large.short_description = 'پیش‌نمایش بزرگ'


# ==================== Admin: ReferralSettings ====================

class ReferralSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'referrer_discount_display', 'new_user_discount_display', 'updated_at']
    list_editable = ['is_active']
    
    fieldsets = (
        ('وضعیت سیستم', {
            'fields': ('is_active',)
        }),
        ('تنظیمات جایزه معرف', {
            'fields': ('referrer_discount_type', 'referrer_discount_amount', 'referrer_credit_amount')
        }),
        ('تنظیمات جایزه کاربر جدید', {
            'fields': ('new_user_discount_type', 'new_user_discount_amount')
        }),
        ('تنظیمات عمومی', {
            'fields': ('discount_expiry_days',)
        }),
    )
    
    def referrer_discount_display(self, obj):
        if obj.referrer_discount_type == 'percentage':
            return f'{obj.referrer_discount_amount}٪'
        return f'{obj.referrer_discount_amount:,.0f} تومان'
    referrer_discount_display.short_description = 'تخفیف معرف'
    
    def new_user_discount_display(self, obj):
        if obj.new_user_discount_type == 'percentage':
            return f'{obj.new_user_discount_amount}٪'
        return f'{obj.new_user_discount_amount:,.0f} تومان'
    new_user_discount_display.short_description = 'تخفیف کاربر جدید'
    
    def has_add_permission(self, request):
        return not ReferralSettings.objects.exists()


# ==================== Admin: ReferralLog ====================

class ReferralLogAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'new_user', 'discount_code_link', 'created_at']
    list_filter = ['created_at']
    search_fields = ['referrer__username', 'new_user__username']
    readonly_fields = ['referrer', 'new_user', 'discount_code', 'created_at']
    
    def discount_code_link(self, obj):
        if obj.discount_code:
            url = reverse('admin:shop_discountcode_change', args=[obj.discount_code.id])
            return mark_safe(f'<a href="{url}">{obj.discount_code.code}</a>')
        return '—'
    discount_code_link.short_description = 'کد تخفیف'
    
    def has_add_permission(self, request):
        return False


# ==================== Admin: AboutUs ====================

class AboutUsAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['title', 'content']
    fieldsets = (
        ('محتوای درباره ما', {
            'fields': ('title', 'content', 'image', 'is_active')
        }),
        ('تاریخ بروزرسانی', {
            'fields': ('updated_at',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ['updated_at']
    
    def has_add_permission(self, request):
        return not AboutUs.objects.exists()


# ==================== ثبت در ادمین ====================

admin.site.register(AboutUs, AboutUsAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(SiteSettings, SiteSettingsAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(GameList, GameListAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(PaymentReceipt, PaymentReceiptAdmin)
admin.site.register(DiscountCode, DiscountCodeAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(Slider, SliderAdmin)
admin.site.register(ReferralSettings, ReferralSettingsAdmin)
admin.site.register(ReferralLog, ReferralLogAdmin)

admin.site.site_header = 'پنل مدیریت JOKERPLAYSTATION'
admin.site.site_title = 'مدیریت فروشگاه'
admin.site.index_title = 'داشبورد مدیریت'
admin.site.site_url = '/'