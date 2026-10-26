# ai_assistant/handlers/news_handler.py
from typing import Dict, Any
from shop.models import News
from .base import BaseHandler


class NewsHandler(BaseHandler):
    """مدیریت اخبار"""
    
    def handle_intent(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower()
        
        if any(w in msg_lower for w in ['لیست', 'همه', 'نمایش']):
            return self.list_news()
        
        return self.show_main_menu()
    
    def show_main_menu(self) -> Dict:
        total = News.objects.filter(is_active=True).count()
        
        text = f"📰 **مدیریت اخبار** ({total} عدد)\n\n"
        text += "• 'لیست اخبار' - مشاهده همه\n"
        text += "برای افزودن خبر جدید از پنل ادمین استفاده کن.\n"
        
        return {'text': text}
    
    def list_news(self) -> Dict:
        news = News.objects.filter(is_active=True).order_by('-created_at')[:10]
        
        if not news.exists():
            return {'text': "📰 هیچ خبری وجود نداره."}
        
        text = f"📰 **آخرین اخبار:**\n\n"
        for n in news:
            text += f"• **{n.title}**\n"
            text += f"  📅 {n.created_at.strftime('%Y/%m/%d')} | 👁 {n.views} بازدید\n"
        
        return {'text': text}