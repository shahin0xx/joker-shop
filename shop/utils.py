import requests

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"

def send_order_telegram_message(order):
    try:
        from .models import PaymentReceipt, SiteSettings
        
        settings = SiteSettings.objects.first()
        
        message = f"🎮 **سفارش جدید ثبت شد!**\n"
        message += f"📦 شماره سفارش: {order.order_number}\n"
        message += f"👤 کاربر: {order.user.username}\n"
        message += f"💰 مبلغ اولیه: {order.total_amount:,} تومان\n"
        
        if order.final_amount != order.total_amount:
            message += f"💵 مبلغ نهایی: {order.final_amount:,} تومان\n"
        
        if order.discount_code:
            message += f"🏷 کد تخفیف: {order.discount_code.code}\n"
        
        message += f"📊 وضعیت: {order.get_status_display()}\n\n"
        
        message += f"👤 **اطلاعات گیرنده:**\n"
        message += f"نام: {order.full_name}\n"
        message += f"📞 تلفن: {order.phone}\n"
        message += f"📍 آدرس: {order.address}\n"
        message += f"📮 کد پستی: {order.postal_code}\n\n"
        
        message += "🛒 **محصولات:**\n"
        for item in order.cart.items.all():
            message += f"• {item.product.name} × {item.quantity} = {item.total_price():,} تومان\n"

        receipt = None
        try:
            receipt = PaymentReceipt.objects.filter(order=order).first()
        except:
            pass

        if receipt and receipt.receipt_image:
            try:
                photo_url = receipt.receipt_image.url
                if photo_url.startswith('/'):
                    photo_url = f"http://localhost:8000{photo_url}"
                
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
                data = {
                    "chat_id": TELEGRAM_CHAT_ID,
                    "caption": message,
                    "parse_mode": "Markdown",
                    "photo": photo_url
                }
                response = requests.post(url, data=data, timeout=15)
            except Exception:
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                data = {
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": message + "\n\n⚠️ خطا در آپلود تصویر رسید",
                    "parse_mode": "Markdown",
                }
                response = requests.post(url, data=data, timeout=15)
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",
            }
            response = requests.post(url, data=data, timeout=15)

        return response.status_code == 200

    except Exception as e:
        print(f"خطا در ارسال تلگرام: {e}")
        return False