from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.db.models import Q, Count
from django.views.decorators.http import require_GET, require_POST
from datetime import timedelta
from .models import *
from .forms import *
from .utils import send_order_telegram_message
import json
import re
import os
import uuid
from django.conf import settings


# ==================== احراز هویت ====================

def custom_logout_view(request):
    logout(request)
    messages.success(request, 'شما با موفقیت از حساب کاربری خود خارج شدید.')
    return redirect('shop:home')


def register_view(request):
    """ثبت‌نام کاربر با نام و نام خانوادگی و شماره تماس"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                settings_obj = ReferralSettings.objects.first()
                
                referral_code = form.cleaned_data.get('referral_code')
                if referral_code and settings_obj and settings_obj.is_active:
                    try:
                        referrer_profile = UserProfile.objects.get(referral_code=referral_code)
                        
                        discount_code = None
                        if settings_obj.referrer_discount_amount > 0:
                            discount_code = DiscountCode.objects.create(
                                user=referrer_profile.user,
                                code=f"REF-{referral_code}-{user.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                                discount_type=settings_obj.referrer_discount_type,
                                amount=settings_obj.referrer_discount_amount,
                                expires_at=timezone.now() + timedelta(days=settings_obj.discount_expiry_days)
                            )
                        
                        if settings_obj.referrer_credit_amount > 0:
                            referrer_profile.credits += settings_obj.referrer_credit_amount
                            referrer_profile.save()
                        
                        if settings_obj.new_user_discount_amount > 0:
                            DiscountCode.objects.create(
                                user=user,
                                code=f"WELCOME-{user.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                                discount_type=settings_obj.new_user_discount_type,
                                amount=settings_obj.new_user_discount_amount,
                                expires_at=timezone.now() + timedelta(days=settings_obj.discount_expiry_days)
                            )
                            messages.success(request, f'یک کد تخفیف {settings_obj.new_user_discount_amount}{"%" if settings_obj.new_user_discount_type == "percentage" else "تومان"} برای شما ایجاد شد!')
                        
                        ReferralLog.objects.create(
                            referrer=referrer_profile.user,
                            new_user=user,
                            discount_code=discount_code
                        )
                        
                        messages.success(request, 'کد تخفیف برای معرف شما ایجاد شد!')
                        
                    except UserProfile.DoesNotExist:
                        messages.warning(request, 'کد معرف معتبر نیست!')
                
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user_auth = authenticate(username=username, password=password)
                if user_auth is not None:
                    login(request, user_auth)
                    messages.success(request, 'حساب کاربری شما با موفقیت ایجاد شد!')
                    return redirect('shop:home')
                else:
                    messages.error(request, 'خطا در ورود خودکار')
                    return redirect('shop:login')
                    
            except Exception as e:
                messages.error(request, f'خطا در ایجاد حساب کاربری: {str(e)}')
                return render(request, 'shop/register.html', {'form': form})
    else:
        ref_code = request.GET.get('ref', '')
        initial_data = {'referral_code': ref_code}
        form = RegisterForm(initial=initial_data)
    
    return render(request, 'shop/register.html', {'form': form})


def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'خوش آمدید {user.get_full_name() or user.username}!')
            return redirect('shop:home')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است!')
    else:
        form = AuthenticationForm()
    
    return render(request, 'shop/login.html', {'form': form})


# ==================== صفحات اصلی ====================

def home(request):
    try:
        categories = Category.objects.filter(is_active=True)[:8]
        slider_items = Slider.objects.filter(is_active=True).order_by('-created_at')
        products = Product.objects.filter(is_available=True).order_by('-created_at')[:8]
        news = News.objects.filter(is_active=True).order_by('-created_at')[:4]
        videos = Video.objects.filter(is_active=True).order_by('-created_at')[:6]
        
        context = {
            'categories': categories,
            'slider_items': slider_items,
            'products': products,
            'news': news,
            'videos': videos,
        }
        return render(request, 'shop/home.html', context)
    except Exception as e:
        print(f"خطا در ویو home: {e}")
        return render(request, 'shop/home.html', {
            'categories': Category.objects.filter(is_active=True)[:8],
            'slider_items': Slider.objects.filter(is_active=True).order_by('-created_at'),
        })


def about(request):
    """صفحه درباره ما - نمایش محتوای قابل ویرایش"""
    about_content = AboutUs.objects.filter(is_active=True).first()
    if not about_content:
        about_content = AboutUs.objects.create(
            title="درباره ما",
            content="لطفاً محتوای درباره ما را از پنل ادمین وارد کنید."
        )
    return render(request, 'shop/about.html', {'about': about_content})


def terms_view(request):
    return render(request, 'shop/terms.html')


# ==================== دسته‌بندی و محصولات ====================

def category_list(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'shop/category_list.html', {'categories': categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_available=True)
    return render(request, 'shop/category_detail.html', {
        'category': category,
        'products': products
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id, is_available=True)
    related_products = Product.objects.filter(
        category=product.category, 
        is_available=True
    ).exclude(id=id)[:4]
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'related_products': related_products
    })


# ==================== بازی‌ها ====================

def game_list_view(request):
    games = GameList.objects.filter(is_active=True)
    return render(request, 'shop/game_list.html', {'games': games})


def game_list_by_platform(request, platform):
    games = GameList.objects.filter(platform=platform, is_active=True)
    platform_display = dict(GameList.GAME_PLATFORMS).get(platform, '')
    return render(request, 'shop/game_list.html', {
        'games': games,
        'platform': platform_display
    })


def game_detail_view(request, game_id):
    """نمایش جزئیات کامل یک بازی"""
    game = get_object_or_404(GameList, id=game_id, is_active=True)
    
    related_products = Product.objects.filter(
        game_list=game, 
        is_available=True
    ).select_related('category')[:8]
    
    similar_games = GameList.objects.filter(
        platform=game.platform,
        is_active=True
    ).exclude(id=game.id)[:6]
    
    game_features = []
    for feature_key in game.get_features_list():
        for choice in GameList.GAME_FEATURES:
            if choice[0] == feature_key:
                game_features.append({
                    'key': feature_key,
                    'name': choice[1]
                })
                break
    
    context = {
        'game': game,
        'related_products': related_products,
        'similar_games': similar_games,
        'game_features': game_features,
    }
    
    return render(request, 'shop/game_detail.html', context)


def simple_game_detail(request, game_id):
    game = GameList.objects.filter(id=game_id).first()
    if game:
        return HttpResponse(
            f"<h1>{game.name}</h1>"
            f"<p>پلتفرم: {game.get_platform_display()}</p>"
            f"<p>ID: {game.id}</p>"
        )
    else:
        return HttpResponse("<h1>بازی پیدا نشد</h1>")


# ==================== پروفایل کاربر ====================

@login_required
def profile_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    discount_codes = DiscountCode.objects.filter(user=request.user)
    referral_settings = ReferralSettings.objects.first()
    referral_logs = ReferralLog.objects.filter(referrer=request.user)
    
    if request.method == 'POST':
        user_profile.full_name = request.POST.get('full_name', '')
        user_profile.phone = request.POST.get('phone', '')
        user_profile.address = request.POST.get('address', '')
        user_profile.postal_code = request.POST.get('postal_code', '')
        user_profile.save()
        
        if request.POST.get('full_name'):
            name_parts = request.POST.get('full_name', '').strip().split(' ', 1)
            request.user.first_name = name_parts[0]
            request.user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            request.user.save()
        
        messages.success(request, 'اطلاعات پروفایل با موفقیت به‌روزرسانی شد.')
        return redirect('shop:profile')
    
    return render(request, 'shop/profile.html', {
        'profile': user_profile,
        'discount_codes': discount_codes,
        'referral_settings': referral_settings,
        'referral_logs': referral_logs
    })


# ==================== سبد خرید ====================

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity += quantity
        cart_item.save()
        message = f'تعداد {product.name} در سبد خرید افزایش یافت'
    except CartItem.DoesNotExist:
        CartItem.objects.create(cart=cart, product=product, quantity=quantity)
        message = f'{product.name} به سبد خرید اضافه شد'
    
    messages.success(request, message)
    return redirect('shop:cart')


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'shop/cart.html', {'cart': cart})


@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        elif action == 'remove':
            cart_item.delete()
            messages.success(request, 'محصول از سبد خرید حذف شد')
    
    return redirect('shop:cart')


# ==================== سیستم تکمیل سفارش چندمرحله‌ای ====================

@login_required
def checkout_step1(request):
    """مرحله اول: اطلاعات گیرنده"""
    cart = get_object_or_404(Cart, user=request.user)
    
    if cart.items.count() == 0:
        messages.warning(request, 'سبد خرید شما خالی است')
        return redirect('shop:cart')
    
    draft_order = Order.objects.filter(user=request.user, status='draft', cart=cart).first()
    
    initial_data = {}
    if draft_order and draft_order.full_name:
        initial_data = {
            'full_name': draft_order.full_name,
            'phone': draft_order.phone,
            'address': draft_order.address,
            'postal_code': draft_order.postal_code,
        }
    else:
        try:
            profile = request.user.profile
            initial_data = {
                'full_name': profile.full_name,
                'phone': profile.phone,
                'address': profile.address,
                'postal_code': profile.postal_code,
            }
        except Exception:
            pass
    
    if request.method == 'POST':
        form = CheckoutStep1Form(request.POST)
        if form.is_valid():
            if not draft_order:
                draft_order = Order.objects.create(
                    user=request.user,
                    cart=cart,
                    total_amount=cart.total_price(),
                    final_amount=cart.total_price(),
                    status='draft'
                )
            
            draft_order.full_name = form.cleaned_data['full_name']
            draft_order.phone = form.cleaned_data['phone']
            draft_order.address = form.cleaned_data['address']
            draft_order.postal_code = form.cleaned_data['postal_code']
            draft_order.save()
            
            return redirect('shop:checkout_step2')
    else:
        form = CheckoutStep1Form(initial=initial_data)
    
    return render(request, 'shop/checkout_step1.html', {
        'cart': cart,
        'form': form,
        'order': draft_order,
    })


@login_required
def checkout_step2(request):
    """مرحله دوم: کد تخفیف"""
    cart = get_object_or_404(Cart, user=request.user)
    draft_order = Order.objects.filter(user=request.user, status='draft', cart=cart).first()
    
    if not draft_order:
        messages.warning(request, 'لطفاً ابتدا اطلاعات گیرنده را وارد کنید.')
        return redirect('shop:checkout_step1')
    
    if cart.items.count() == 0:
        messages.warning(request, 'سبد خرید شما خالی است')
        return redirect('shop:cart')
    
    initial_total = cart.total_price()
    discount_amount = 0
    
    if draft_order.discount_code:
        if draft_order.discount_code.discount_type == 'percentage':
            discount_amount = (initial_total * draft_order.discount_code.amount) / 100
        else:
            discount_amount = draft_order.discount_code.amount
        final_amount = max(initial_total - discount_amount, 0)
    else:
        final_amount = initial_total
    
    if request.method == 'POST':
        form = CheckoutStep2Form(request.POST, user=request.user)
        if form.is_valid():
            discount_code = form.cleaned_data.get('discount_code')
            
            if discount_code:
                draft_order.discount_code = discount_code
                if discount_code.discount_type == 'percentage':
                    discount_amount = (initial_total * discount_code.amount) / 100
                else:
                    discount_amount = discount_code.amount
                final_amount = max(initial_total - discount_amount, 0)
                draft_order.final_amount = final_amount
                draft_order.save()
                messages.success(request, 'کد تخفیف با موفقیت اعمال شد.')
            else:
                draft_order.discount_code = None
                draft_order.final_amount = initial_total
                draft_order.save()
            
            return redirect('shop:checkout_step3')
    else:
        form = CheckoutStep2Form(user=request.user, initial={
            'discount_code': draft_order.discount_code.code if draft_order.discount_code else ''
        })
    
    site_settings = SiteSettings.objects.first()
    min_amount_for_shaba = site_settings.min_amount_for_shaba if site_settings else 10000000
    payment_method = 'shaba' if final_amount >= min_amount_for_shaba else 'card'
    
    return render(request, 'shop/checkout_step2.html', {
        'cart': cart,
        'form': form,
        'order': draft_order,
        'initial_total': initial_total,
        'final_amount': final_amount,
        'discount_amount': discount_amount,
        'payment_method': payment_method,
        'site_settings': site_settings,
        'min_amount_for_shaba': min_amount_for_shaba,
    })


@login_required
def checkout_step3(request):
    """مرحله سوم: آپلود رسید و نهایی‌سازی سفارش"""
    cart = get_object_or_404(Cart, user=request.user)
    draft_order = Order.objects.filter(user=request.user, status='draft', cart=cart).first()
    
    if not draft_order:
        messages.warning(request, 'لطفاً ابتدا اطلاعات گیرنده را وارد کنید.')
        return redirect('shop:checkout_step1')
    
    if not draft_order.full_name or not draft_order.phone:
        messages.warning(request, 'لطفاً اطلاعات گیرنده را کامل کنید.')
        return redirect('shop:checkout_step1')
    
    if cart.items.count() == 0:
        messages.warning(request, 'سبد خرید شما خالی است')
        return redirect('shop:cart')
    
    initial_total = cart.total_price()
    discount_amount = 0
    
    if draft_order.discount_code:
        if draft_order.discount_code.discount_type == 'percentage':
            discount_amount = (initial_total * draft_order.discount_code.amount) / 100
        else:
            discount_amount = draft_order.discount_code.amount
    final_amount = max(initial_total - discount_amount, 0)
    draft_order.final_amount = final_amount
    draft_order.save()
    
    site_settings = SiteSettings.objects.first()
    min_amount_for_shaba = site_settings.min_amount_for_shaba if site_settings else 10000000
    payment_method = 'shaba' if final_amount >= min_amount_for_shaba else 'card'
    
    if request.method == 'POST':
        form = CheckoutStep3Form(request.POST, request.FILES)
        if form.is_valid():
            draft_order.status = 'pending'
            draft_order.save()
            
            if not draft_order.order_number:
                draft_order.order_number = f"ORD-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
                draft_order.save()
            
            PaymentReceipt.objects.create(
                order=draft_order,
                receipt_image=form.cleaned_data['receipt_image'],
                payment_method=payment_method
            )
            
            if draft_order.discount_code:
                draft_order.discount_code.is_used = True
                draft_order.discount_code.save()
            
            try:
                send_order_telegram_message(draft_order)
                messages.info(request, 'اطلاعات سفارش به پشتیبانی ارسال شد.')
            except Exception as e:
                print(f"خطا در ارسال به تلگرام: {e}")
            
            cart.items.all().delete()
            
            messages.success(request, f'سفارش شما با شماره {draft_order.order_number} ثبت شد. پس از تایید پرداخت، سفارش شما ارسال خواهد شد.')
            return redirect('shop:order_detail', order_id=draft_order.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = CheckoutStep3Form()
    
    return render(request, 'shop/checkout_step3.html', {
        'cart': cart,
        'form': form,
        'order': draft_order,
        'initial_total': initial_total,
        'final_amount': final_amount,
        'discount_amount': discount_amount,
        'payment_method': payment_method,
        'site_settings': site_settings,
        'min_amount_for_shaba': min_amount_for_shaba,
    })


@login_required
def checkout_cancel(request):
    """لغو فرآیند تسویه حساب"""
    cart = get_object_or_404(Cart, user=request.user)
    draft_order = Order.objects.filter(user=request.user, status='draft', cart=cart).first()
    
    if draft_order:
        draft_order.delete()
        messages.info(request, 'فرآیند ثبت سفارش لغو شد.')
    
    return redirect('shop:cart')


@login_required
def validate_discount_code(request):
    """اعتبارسنجی کد تخفیف با AJAX"""
    if request.method == 'POST':
        try:
            if request.headers.get('Content-Type') == 'application/json':
                data = json.loads(request.body)
                code = data.get('code')
            else:
                code = request.POST.get('code')
            
            if not code:
                return JsonResponse({'valid': False, 'message': 'کد تخفیف را وارد کنید'})
            
            try:
                discount = DiscountCode.objects.get(
                    code=code,
                    is_used=False,
                    expires_at__gte=timezone.now(),
                    user=request.user
                )
                
                return JsonResponse({
                    'valid': True,
                    'discount_type': discount.discount_type,
                    'amount': float(discount.amount),
                    'message': 'کد تخفیف معتبر است'
                })
            except DiscountCode.DoesNotExist:
                return JsonResponse({
                    'valid': False,
                    'message': 'کد تخفیف معتبر نیست یا منقضی شده است'
                })
        except Exception as e:
            return JsonResponse({'valid': False, 'message': str(e)})
    
    return JsonResponse({'valid': False, 'message': 'درخواست نامعتبر'})


# ==================== سفارشات ====================

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST' and request.FILES.get('receipt_image'):
        receipt_image = request.FILES['receipt_image']
        PaymentReceipt.objects.create(
            order=order,
            receipt_image=receipt_image
        )
        order.status = 'paid'
        order.save()
        
        try:
            send_order_telegram_message(order)
            messages.info(request, 'رسید پرداخت به پشتیبانی ارسال شد.')
        except Exception as e:
            print(f"خطا در ارسال به تلگرام: {e}")
        
        messages.success(request, 'رسید پرداخت با موفقیت آپلود شد')
        return redirect('shop:order_detail', order_id=order.id)
    
    return render(request, 'shop/order_detail.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).exclude(status='draft').order_by('-created_at')
    draft_orders = Order.objects.filter(user=request.user, status='draft')
    return render(request, 'shop/order_history.html', {
        'orders': orders,
        'draft_orders': draft_orders
    })


@login_required
def continue_order(request, order_id):
    """ادامه سفارش ناتمام"""
    order = get_object_or_404(Order, id=order_id, user=request.user, status='draft')
    return redirect('shop:checkout_step1')


# ==================== جستجو ====================

def search_view(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'categories': [], 'products': [], 'games': []})
    
    categories = Category.objects.filter(
        Q(name__icontains=query),
        is_active=True
    ).values('id', 'name', 'slug', 'type')
    
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_available=True
    ).select_related('category').values('id', 'name', 'price', 'category__name')
    
    games = GameList.objects.filter(
        Q(name__icontains=query),
        is_active=True
    ).values('id', 'name', 'platform')
    
    categories_list = list(categories)
    products_list = list(products)
    games_list = list(games)
    
    for product in products_list:
        product['category_name'] = product.pop('category__name')
    
    return JsonResponse({
        'categories': categories_list,
        'products': products_list,
        'games': games_list
    })


def search_results_view(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('shop:home')
    
    categories = Category.objects.filter(
        Q(name__icontains=query),
        is_active=True
    )
    
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_available=True
    ).select_related('category')
    
    games = GameList.objects.filter(
        Q(name__icontains=query),
        is_active=True
    )
    
    return render(request, 'shop/search_results.html', {
        'query': query,
        'categories': categories,
        'products': products,
        'games': games
    })


# ==================== چت و پشتیبانی ====================

@login_required
def chat_view(request):
    """چت برای کاربران عادی - فقط با ادمین"""
    if request.user.is_staff:
        return redirect('shop:admin_chat')
    
    chat_messages = ChatMessage.objects.filter(user=request.user).order_by('created_at')
    
    return render(request, 'shop/chat.html', {
        'chat_messages': chat_messages,
    })


@login_required
@require_GET
def chat_messages_api(request):
    """دریافت پیام‌های جدید کاربر با AJAX"""
    last_id = request.GET.get('last_id', 0)
    try:
        last_id = int(last_id)
    except (ValueError, TypeError):
        last_id = 0

    messages_qs = ChatMessage.objects.filter(
        user=request.user,
        id__gt=last_id
    ).order_by('created_at')

    # علامت‌گذاری پیام‌های ادمین به عنوان خوانده شده
    ChatMessage.objects.filter(
        user=request.user,
        is_admin=True,
        is_read=False
    ).update(is_read=True)

    messages_data = []
    for msg in messages_qs:
        messages_data.append({
            'id': msg.id,
            'message': msg.message or '',
            'is_admin': msg.is_admin,
            'image_url': msg.image.url if msg.image else None,
            'video_url': msg.video.url if msg.video else None,
            'created_at': timezone.localtime(msg.created_at).strftime('%H:%M'),
        })

    return JsonResponse({'messages': messages_data})


@login_required
@require_POST
def chat_send_api(request):
    """ارسال پیام کاربر با AJAX"""
    message_text = request.POST.get('message', '').strip()
    file = request.FILES.get('file')

    if not message_text and not file:
        return JsonResponse({'success': False, 'error': 'پیام خالی است'}, status=400)

    chat_message = ChatMessage(
        user=request.user,
        message=message_text or None,
        is_admin=False,
    )

    if file:
        if file.content_type.startswith('image/'):
            chat_message.image = file
        elif file.content_type.startswith('video/'):
            chat_message.video = file

    chat_message.save()

    return JsonResponse({
        'success': True,
        'message': {
            'id': chat_message.id,
            'message': chat_message.message or '',
            'is_admin': False,
            'image_url': chat_message.image.url if chat_message.image else None,
            'video_url': chat_message.video.url if chat_message.video else None,
            'created_at': timezone.localtime(chat_message.created_at).strftime('%H:%M'),
        }
    })


@login_required
def admin_chat_view(request):
    """پنل چت مخصوص ادمین"""
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی به این صفحه را ندارید.')
        return redirect('shop:home')
    
    users_with_messages = User.objects.filter(
        chat_messages__isnull=False,
        is_staff=False
    ).distinct().order_by('-date_joined')
    
    if not users_with_messages.exists():
        users_with_messages = User.objects.filter(is_staff=False).order_by('-date_joined')
    
    users_list = []
    for user in users_with_messages:
        try:
            profile = user.profile
            phone = profile.phone if profile and profile.phone else 'ثبت نشده'
        except Exception:
            phone = 'ثبت نشده'
        
        last_message = ChatMessage.objects.filter(user=user).order_by('-created_at').first()
        unread_count = ChatMessage.objects.filter(
            user=user, 
            is_admin=False, 
            is_read=False
        ).count()
        
        users_list.append({
            'user': user,
            'phone': phone,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    selected_user_id = request.GET.get('user_id')
    selected_user = None
    user_messages = []
    
    if selected_user_id:
        try:
            selected_user = User.objects.get(id=selected_user_id)
            user_messages = ChatMessage.objects.filter(user=selected_user).order_by('created_at')
            
            ChatMessage.objects.filter(
                user=selected_user,
                is_admin=False,
                is_read=False
            ).update(is_read=True)
        except User.DoesNotExist:
            messages.error(request, 'کاربر مورد نظر یافت نشد.')
            return redirect('shop:admin_chat')
    
    return render(request, 'shop/admin_chat.html', {
        'users': users_list,
        'selected_user': selected_user,
        'user_messages': user_messages,
    })


@login_required
def admin_chat_messages_api(request):
    """دریافت پیام‌های جدید کاربر برای ادمین"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'دسترسی ندارید'}, status=403)

    user_id = request.GET.get('user_id')
    last_id = request.GET.get('last_id', 0)

    if not user_id:
        return JsonResponse({'messages': []})

    try:
        last_id = int(last_id)
    except (ValueError, TypeError):
        last_id = 0

    target_user = get_object_or_404(User, id=user_id)

    messages_qs = ChatMessage.objects.filter(
        user=target_user,
        id__gt=last_id
    ).order_by('created_at')

    # علامت‌گذاری پیام‌های کاربر به عنوان خوانده شده
    ChatMessage.objects.filter(
        user=target_user,
        is_admin=False,
        is_read=False
    ).update(is_read=True)

    messages_data = []
    for msg in messages_qs:
        messages_data.append({
            'id': msg.id,
            'message': msg.message or '',
            'is_admin': msg.is_admin,
            'image_url': msg.image.url if msg.image else None,
            'video_url': msg.video.url if msg.video else None,
            'created_at': timezone.localtime(msg.created_at).strftime('%H:%M'),
        })

    return JsonResponse({'messages': messages_data})


@login_required
@require_POST
def admin_chat_send_api(request):
    """ارسال پیام ادمین با AJAX"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'دسترسی ندارید'}, status=403)

    user_id = request.POST.get('user_id')
    message_text = request.POST.get('message', '').strip()
    file = request.FILES.get('file')

    if not user_id:
        return JsonResponse({'success': False, 'error': 'کاربر انتخاب نشده'}, status=400)

    if not message_text and not file:
        return JsonResponse({'success': False, 'error': 'پیام خالی است'}, status=400)

    target_user = get_object_or_404(User, id=user_id)

    chat_message = ChatMessage(
        user=target_user,
        message=message_text or None,
        is_admin=True,
    )

    if file:
        if file.content_type.startswith('image/'):
            chat_message.image = file
        elif file.content_type.startswith('video/'):
            chat_message.video = file

    chat_message.save()

    return JsonResponse({
        'success': True,
        'message': {
            'id': chat_message.id,
            'message': chat_message.message or '',
            'is_admin': True,
            'image_url': chat_message.image.url if chat_message.image else None,
            'video_url': chat_message.video.url if chat_message.video else None,
            'created_at': timezone.localtime(chat_message.created_at).strftime('%H:%M'),
        }
    })


@staff_member_required
def admin_send_message(request, user_id=None):
    users = User.objects.filter(is_active=True).exclude(is_staff=True)
    selected_user = None
    
    if user_id:
        selected_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = ChatMessageForm(request.POST, request.FILES)
        user_id = request.POST.get('user_id')
        selected_user = get_object_or_404(User, id=user_id) if user_id else None
        
        if form.is_valid() and selected_user:
            chat_message = form.save(commit=False)
            chat_message.user = selected_user
            chat_message.is_admin = True
            chat_message.save()
            messages.success(request, f'پیام به {selected_user.username} ارسال شد.')
            return redirect('shop:admin_send_message', user_id=selected_user.id)
    else:
        form = ChatMessageForm()
    
    messages_list = []
    if selected_user:
        messages_list = ChatMessage.objects.filter(user=selected_user).order_by('-created_at')[:50]
    
    return render(request, 'shop/admin_send_message.html', {
        'users': users,
        'selected_user': selected_user,
        'form': form,
        'messages': messages_list
    })


# ==================== کلاس‌های مبتنی بر ویو ====================

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, 'شما دسترسی به این صفحه را ندارید.')
        return redirect('shop:home')


class VideoListView(ListView):
    model = Video
    template_name = 'shop/video_list.html'
    context_object_name = 'videos'
    paginate_by = 12
    
    def get_queryset(self):
        return Video.objects.filter(is_active=True).order_by('-created_at')


class VideoDetailView(DetailView):
    model = Video
    template_name = 'shop/video_detail.html'
    context_object_name = 'video'
    
    def get_queryset(self):
        return Video.objects.filter(is_active=True)


class VideoUploadView(StaffRequiredMixin, CreateView):
    model = Video
    form_class = VideoForm
    template_name = 'shop/video_upload.html'
    success_url = reverse_lazy('shop:video_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'ویدیو با موفقیت آپلود شد.')
        return super().form_valid(form)


class NewsListView(ListView):
    model = News
    template_name = 'shop/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10
    
    def get_queryset(self):
        return News.objects.filter(is_active=True).order_by('-created_at')


class NewsDetailView(DetailView):
    model = News
    template_name = 'shop/news_detail.html'
    context_object_name = 'news'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return News.objects.filter(is_active=True)
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views += 1
        obj.save()
        return obj


class NewsCreateView(StaffRequiredMixin, CreateView):
    model = News
    form_class = NewsForm
    template_name = 'shop/news_create.html'
    success_url = reverse_lazy('shop:news_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'خبر با موفقیت ایجاد شد.')
        return super().form_valid(form)


class NewsUpdateView(StaffRequiredMixin, UpdateView):
    model = News
    form_class = NewsForm
    template_name = 'shop/news_update.html'
    success_url = reverse_lazy('shop:news_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'خبر با موفقیت بروزرسانی شد.')
        return super().form_valid(form)


# ==================== تنظیمات دعوت ====================

@login_required
@user_passes_test(lambda u: u.is_staff)
def referral_settings_view(request):
    settings_obj = ReferralSettings.objects.first()
    if not settings_obj:
        settings_obj = ReferralSettings.objects.create()
    
    if request.method == 'POST':
        settings_obj.is_active = request.POST.get('is_active') == 'on'
        settings_obj.referrer_discount_type = request.POST.get('referrer_discount_type')
        settings_obj.referrer_discount_amount = request.POST.get('referrer_discount_amount')
        settings_obj.referrer_credit_amount = request.POST.get('referrer_credit_amount')
        settings_obj.new_user_discount_type = request.POST.get('new_user_discount_type')
        settings_obj.new_user_discount_amount = request.POST.get('new_user_discount_amount')
        settings_obj.discount_expiry_days = request.POST.get('discount_expiry_days')
        settings_obj.save()
        
        messages.success(request, 'تنظیمات با موفقیت به‌روزرسانی شد.')
        return redirect('shop:referral_settings')
    
    return render(request, 'shop/referral_settings.html', {'settings': settings_obj})


# ==================== پنل مخفی ====================

ADMIN_LOCK_FILE = os.path.join(settings.BASE_DIR, '.admin_locked')


def is_admin_locked():
    """بررسی می‌کند که آیا پنل ادمین قفل شده است یا نه"""
    return os.path.exists(ADMIN_LOCK_FILE)


def admin_access_middleware(get_response):
    """
    میدلور برای بستن دسترسی به ادمین
    """
    def middleware(request):
        if request.path.startswith('/admin/') and not request.user.is_superuser:
            if is_admin_locked():
                return render(request, 'shop/admin_locked.html', status=403)
        return get_response(request)
    return middleware


def hidden_panel(request):
    """
    صفحه مخفی برای قفل/باز کردن پنل ادمین
    آدرس: /hidden-panel/
    """
    SECRET_KEY = "JOKER2024"
    
    auth_key = request.GET.get('key') or request.COOKIES.get('secret_key')
    
    if auth_key != SECRET_KEY:
        return render(request, 'shop/fake_404.html', status=404)
    
    is_locked = is_admin_locked()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'lock_admin':
            with open(ADMIN_LOCK_FILE, 'w') as f:
                f.write(f'locked_at_{timezone.now().isoformat()}')
            messages.success(request, '✅ پنل ادمین با موفقیت قفل شد!')
            return redirect('/hidden-panel/?key=' + SECRET_KEY)
        
        elif action == 'unlock_admin':
            if os.path.exists(ADMIN_LOCK_FILE):
                os.remove(ADMIN_LOCK_FILE)
            messages.success(request, '✅ قفل پنل ادمین باز شد.')
            return redirect('/hidden-panel/?key=' + SECRET_KEY)
    
    response = render(request, 'shop/hidden_panel.html', {
        'is_locked': is_locked,
        'secret_key': SECRET_KEY,
    })
    response.set_cookie('secret_key', SECRET_KEY, max_age=3600 * 24 * 30)
    return response


def admin_locked_page(request):
    """
    صفحه ترسناکی که وقتی کسی می‌خواد بره تو ادمین می‌بینه
    """
    return render(request, 'shop/admin_locked.html', status=403)