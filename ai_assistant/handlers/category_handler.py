# ai_assistant/handlers/category_handler.py
from typing import Dict, Any
from shop.models import Category
from .base import BaseHandler


class CategoryHandler(BaseHandler):
    """مدیریت دسته‌بندی‌ها"""
    
    def handle_intent(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower()
        
        if any(w in msg_lower for w in ['لیست', 'همه', 'نمایش']):
            return self.list_categories()
        
        return self.show_main_menu()
    
    def show_main_menu(self) -> Dict:
        total = Category.objects.filter(is_active=True).count()
        
        text = f"📂 **مدیریت دسته‌بندی‌ها** ({total} عدد)\n\n"
        text += "• 'لیست دسته‌بندی‌ها' - مشاهده همه\n"
        text += "• 'دسته‌بندی جدید' - ایجاد (از طریق افزودن محصول)\n"
        
        return {'text': text}
    
    def list_categories(self) -> Dict:
        categories = Category.objects.filter(is_active=True)
        
        if not categories.exists():
            return {'text': "📂 هیچ دسته‌بندی وجود نداره."}
        
        text = f"📂 **دسته‌بندی‌ها ({categories.count()} عدد):**\n\n"
        for cat in categories:
            text += f"• **{cat.name}** ({cat.get_type_display()}) - {cat.products.count()} محصول\n"
        
        return {'text': text}