# ai_assistant/handlers/video_handler.py
from typing import Dict, Any
from shop.models import Video
from .base import BaseHandler


class VideoHandler(BaseHandler):
    """مدیریت ویدیوها"""
    
    def handle_intent(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower()
        
        if any(w in msg_lower for w in ['لیست', 'همه', 'نمایش']):
            return self.list_videos()
        
        return self.show_main_menu()
    
    def show_main_menu(self) -> Dict:
        total = Video.objects.filter(is_active=True).count()
        
        text = f"🎬 **مدیریت ویدیوها** ({total} عدد)\n\n"
        text += "• 'لیست ویدیوها' - مشاهده همه\n"
        text += "برای افزودن ویدیو جدید از پنل ادمین استفاده کن.\n"
        
        return {'text': text}
    
    def list_videos(self) -> Dict:
        videos = Video.objects.filter(is_active=True).order_by('-created_at')[:10]
        
        if not videos.exists():
            return {'text': "🎬 هیچ ویدیویی وجود نداره."}
        
        text = f"🎬 **آخرین ویدیوها:**\n\n"
        for v in videos:
            text += f"• **{v.title}**\n"
            text += f"  📅 {v.created_at.strftime('%Y/%m/%d')}\n"
        
        return {'text': text}