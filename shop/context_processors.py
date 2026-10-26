from .models import SiteSettings, Category

def site_settings(request):
    """
    context processor برای ارسال تنظیمات سایت به همه تمپلیت‌ها
    """
    try:
        settings = SiteSettings.objects.first()
        if not settings:
            settings = SiteSettings.objects.create()
    except:
        settings = None
    
    return {
        'site_settings': settings,
    }

def categories_menu(request):
    """
    context processor برای ارسال دسته‌بندی‌های فعال به همه تمپلیت‌ها
    برای نمایش در منوی کشویی هدر
    """
    try:
        # دسته‌بندی‌های اصلی (فقط ۱۰ تا برای جلوگیری از شلوغی منو)
        categories = Category.objects.filter(is_active=True).order_by('name')[:10]
        
        # گروه‌بندی دسته‌بندی‌ها بر اساس نوع
        categories_by_type = {}
        for category in categories:
            type_display = category.get_type_display()
            if type_display not in categories_by_type:
                categories_by_type[type_display] = []
            categories_by_type[type_display].append(category)
        
        # جدا کردن بازی‌ها بر اساس پلتفرم برای منوی بازی‌ها
        game_categories = {
            'playstation': [],
            'xbox': [],
            'pc': [],
            'none': [],
        }
        for cat in categories:
            if cat.type == 'game':
                platform = cat.game_platform if cat.game_platform else 'none'
                if platform in game_categories:
                    game_categories[platform].append(cat)
    except Exception:
        categories = []
        categories_by_type = {}
        game_categories = {}
    
    return {
        'menu_categories': categories,
        'menu_categories_by_type': categories_by_type,
        'menu_game_categories': game_categories,
    }