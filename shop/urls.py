# shop/urls.py

from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # صفحات اصلی
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('terms/', views.terms_view, name='terms'),
    
    # دسته‌بندی‌ها
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('categories/', views.category_list, name='category_list'),
    
    # لیست بازی‌ها
    path('games-list/', views.game_list_view, name='game_list'),
    path('games-list/<str:platform>/', views.game_list_by_platform, name='game_list_by_platform'),
    path('game-details/<int:game_id>/', views.game_detail_view, name='game_detail'),
    
    # احراز هویت
    path('register/', views.register_view, name='register'),
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    
    # پروفایل کاربر
    path('profile/', views.profile_view, name='profile'),
    
    # محصولات
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    
    # سبد خرید
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    
    # تسویه حساب (مسیر قدیمی برای سازگاری)
    path('checkout/', views.checkout_step1, name='checkout'),  # اضافه کردن این خط برای سازگاری
    
    # تسویه حساب چند مرحله‌ای جدید
    path('checkout/step1/', views.checkout_step1, name='checkout_step1'),
    path('checkout/step2/', views.checkout_step2, name='checkout_step2'),
    path('checkout/step3/', views.checkout_step3, name='checkout_step3'),
    path('checkout/cancel/', views.checkout_cancel, name='checkout_cancel'),
    
    # سفارشات
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/', views.order_history, name='order_history'),
    path('order/continue/<int:order_id>/', views.continue_order, name='continue_order'),
    path('validate-discount/', views.validate_discount_code, name='validate_discount'),
    
    # چت و پشتیبانی
    path('chat/', views.chat_view, name='chat'),
    path('admin-panel/chat/', views.admin_chat_view, name='admin_chat'),
    
    # جستجو
    path('search/', views.search_results_view, name='search_results'),
    path('search/ajax/', views.search_view, name='search_ajax'),
    
    # ویدیوها
    path('videos/', views.VideoListView.as_view(), name='video_list'),
    path('videos/<int:pk>/', views.VideoDetailView.as_view(), name='video_detail'),
    path('videos/upload/', views.VideoUploadView.as_view(), name='video_upload'),
    
    # اخبار
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<slug:slug>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('news/create/', views.NewsCreateView.as_view(), name='news_create'),
    path('news/<slug:slug>/update/', views.NewsUpdateView.as_view(), name='news_update'),
    
    # تنظیمات دعوت
    path('admin-panel/referral-settings/', views.referral_settings_view, name='referral_settings'),
    path('hidden-panel/', views.hidden_panel, name='hidden_panel'),
]