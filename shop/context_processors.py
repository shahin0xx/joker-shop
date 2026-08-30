from .models import SiteSettings

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