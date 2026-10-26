# ai_assistant/handlers/game_handler.py
from typing import Dict, Any
from shop.models import GameList
from .base import BaseHandler


class GameHandler(BaseHandler):
    """مدیریت بازی‌ها"""
    
    def handle_intent(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower()
        
        if any(w in msg_lower for w in ['لیست', 'همه', 'نمایش']):
            return self.list_games()
        
        return self.show_main_menu()
    
    def show_main_menu(self) -> Dict:
        total = GameList.objects.filter(is_active=True).count()
        
        text = f"🎮 **مدیریت بازی‌ها** ({total} عدد)\n\n"
        text += "• 'لیست بازی‌ها' - مشاهده همه\n"
        text += "• 'بازی جدید' - ایجاد (از طریق افزودن محصول)\n"
        
        return {'text': text}
    
    def list_games(self) -> Dict:
        games = GameList.objects.filter(is_active=True)
        
        if not games.exists():
            return {'text': "🎮 هیچ بازی وجود نداره."}
        
        text = f"🎮 **بازی‌ها ({games.count()} عدد):**\n\n"
        
        for platform in ['playstation', 'xbox', 'pc']:
            platform_games = games.filter(platform=platform)
            if platform_games.exists():
                platform_name = {'playstation': 'پلی استیشن', 'xbox': 'ایکس باکس', 'pc': 'کامپیوتر'}.get(platform, platform)
                text += f"**{platform_name}:**\n"
                for g in platform_games[:10]:
                    text += f"• {g.name}\n"
                text += "\n"
        
        return {'text': text}