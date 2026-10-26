from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
import re
from django.utils import timezone

class RegisterForm(UserCreationForm):
    """فرم ثبت‌نام با نام و نام خانوادگی و شماره تماس"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل خود را وارد کنید'})
    )
    first_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام'})
    )
    last_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام خانوادگی'})
    )
    phone = forms.CharField(
        required=True,
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شماره تماس (مثال: 09123456789)'})
    )
    referral_code = forms.CharField(
        required=False,
        max_length=7,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'کد معرف (اختیاری)'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2', 'referral_code']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام کاربری'}),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError('نام کاربری فقط می‌تواند شامل حروف انگلیسی، اعداد و زیرخط باشد.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('این ایمیل قبلاً ثبت شده است.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone = re.sub(r'\s+', '', phone)
        if not re.match(r'^09\d{9}$', phone):
            raise forms.ValidationError('شماره تماس باید با ۰۹ شروع شده و ۱۱ رقم باشد.')
        return phone
    
    def clean_referral_code(self):
        referral_code = self.cleaned_data.get('referral_code')
        settings = ReferralSettings.objects.first()
        if settings and not settings.is_active:
            return None
        if referral_code:
            if not UserProfile.objects.filter(referral_code=referral_code).exists():
                raise forms.ValidationError('کد معرف معتبر نیست.')
        return referral_code
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        
        if commit:
            user.save()
            # ایجاد یا به‌روزرسانی پروفایل با شماره تماس و نام کامل
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get('phone')
            profile.full_name = f"{self.cleaned_data.get('first_name')} {self.cleaned_data.get('last_name')}"
            profile.save()
        
        return user


class CheckoutForm(forms.Form):
    """فرم تسویه حساب (برای تکمیل سفارش)"""
    
    full_name = forms.CharField(
        label='نام و نام خانوادگی گیرنده',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام و نام خانوادگی خود را وارد کنید'})
    )
    phone = forms.CharField(
        label='شماره تماس',
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '۰۹۱۲۳۴۵۶۷۸۹'})
    )
    address = forms.CharField(
        label='آدرس کامل',
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'استان، شهر، خیابان، کوچه، پلاک'})
    )
    postal_code = forms.CharField(
        label='کد پستی',
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'کد پستی ۱۰ رقمی'})
    )
    
    discount_code = forms.CharField(
        label='کد تخفیف',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'کد تخفیف (اختیاری)'})
    )
    
    receipt_image = forms.ImageField(
        label='تصویر رسید پرداخت',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    
    def clean_discount_code(self):
        code = self.cleaned_data.get('discount_code')
        if code:
            try:
                discount = DiscountCode.objects.get(
                    code=code,
                    is_used=False,
                    expires_at__gte=timezone.now(),
                    user=self.user if hasattr(self, 'user') else None
                )
                return discount
            except DiscountCode.DoesNotExist:
                raise forms.ValidationError('کد تخفیف معتبر نیست یا منقضی شده است.')
        return None
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone = re.sub(r'\s+', '', phone)
        if not re.match(r'^09\d{9}$', phone):
            raise forms.ValidationError('شماره تماس باید با ۰۹ شروع شده و ۱۱ رقم باشد.')
        return phone
    
    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        postal_code = re.sub(r'\s+', '', postal_code)
        if not re.match(r'^\d{10}$', postal_code):
            raise forms.ValidationError('کد پستی باید ۱۰ رقم باشد.')
        return postal_code


class CheckoutStep1Form(forms.Form):
    """مرحله اول تسویه حساب - اطلاعات گیرنده"""
    
    full_name = forms.CharField(
        label='نام و نام خانوادگی گیرنده',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام و نام خانوادگی خود را وارد کنید'})
    )
    phone = forms.CharField(
        label='شماره تماس',
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '۰۹۱۲۳۴۵۶۷۸۹'})
    )
    address = forms.CharField(
        label='آدرس کامل',
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'استان، شهر، خیابان، کوچه، پلاک'})
    )
    postal_code = forms.CharField(
        label='کد پستی',
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'کد پستی ۱۰ رقمی'})
    )
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone = re.sub(r'\s+', '', phone)
        if not re.match(r'^09\d{9}$', phone):
            raise forms.ValidationError('شماره تماس باید با ۰۹ شروع شده و ۱۱ رقم باشد.')
        return phone
    
    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        postal_code = re.sub(r'\s+', '', postal_code)
        if not re.match(r'^\d{10}$', postal_code):
            raise forms.ValidationError('کد پستی باید ۱۰ رقم باشد.')
        return postal_code


class CheckoutStep2Form(forms.Form):
    """مرحله دوم تسویه حساب - کد تخفیف"""
    
    discount_code = forms.CharField(
        label='کد تخفیف',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'کد تخفیف (اختیاری)'})
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_discount_code(self):
        code = self.cleaned_data.get('discount_code')
        if code and self.user:
            try:
                discount = DiscountCode.objects.get(
                    code=code,
                    is_used=False,
                    expires_at__gte=timezone.now(),
                    user=self.user
                )
                return discount
            except DiscountCode.DoesNotExist:
                raise forms.ValidationError('کد تخفیف معتبر نیست یا منقضی شده است.')
        return None


class CheckoutStep3Form(forms.Form):
    """مرحله سوم تسویه حساب - آپلود رسید"""
    
    receipt_image = forms.ImageField(
        label='تصویر رسید پرداخت',
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message', 'image', 'video']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'پیام خود را وارد کنید...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'video': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        message = cleaned_data.get('message')
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')
        
        if not message and not image and not video:
            raise forms.ValidationError('حداقل یکی از فیلدهای پیام، عکس یا ویدیو باید پر شود.')
        return cleaned_data


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'video_file', 'thumbnail', 'description', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'video_file': forms.FileInput(attrs={'class': 'form-control'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'image', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class GameFilterForm(forms.Form):
    """فرم فیلتر کردن بازی‌ها"""
    platform = forms.ChoiceField(
        choices=[('', 'همه پلتفرم‌ها')] + GameList.GAME_PLATFORMS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    min_rating = forms.DecimalField(
        required=False,
        min_value=0,
        max_value=5,
        decimal_places=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'placeholder': 'حداقل امتیاز'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'جستجوی نام بازی...'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for feature_key, feature_name in GameList.GAME_FEATURES:
            self.fields[f'feature_{feature_key}'] = forms.BooleanField(
                required=False,
                label=feature_name,
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
            )