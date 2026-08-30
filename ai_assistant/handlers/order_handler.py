# ai_assistant/handlers/order_handler.py
from typing import Dict, Any
from shop.models import Order
from .base import BaseHandler


class OrderHandler(BaseHandler):
    """مدیریت سفارشات"""
    
    def handle_intent(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower()
        
        if any(w in msg_lower for w in ['در انتظار', 'pending']):
            return self.show_pending_orders()
        
        if any(w in msg_lower for w in ['همه', 'لیست', 'all']):
            return self.show_all_orders()
        
        if any(w in msg_lower for w in ['تغییر', 'وضعیت', 'status']):
            return self.change_order_status(message)
        
        return self.show_main_menu()
    
    def show_main_menu(self) -> Dict:
        pending = Order.objects.filter(status='pending').count()
        paid = Order.objects.filter(status='paid').count()
        completed = Order.objects.filter(status='completed').count()
        
        text = "🛒 **مدیریت سفارشات**\n\n"
        text += f"📊 در انتظار: {pending} | پرداخت شده: {paid} | تکمیل: {completed}\n\n"
        text += "**عملیات:**\n"
        text += "• 'سفارشات در انتظار'\n"
        text += "• 'لیست همه سفارشات'\n"
        text += "• 'تغییر وضعیت سفارش [شماره] به [وضعیت]'"
        
        return {'text': text}
    
    def show_pending_orders(self) -> Dict:
        orders = Order.objects.filter(status='pending').order_by('-created_at')[:10]
        
        if not orders.exists():
            return {'text': "✅ هیچ سفارش در انتظاری وجود نداره!"}
        
        text = f"⏳ **سفارشات در انتظار ({Order.objects.filter(status='pending').count()} عدد):**\n\n"
        for o in orders:
            text += f"• **{o.order_number}**\n"
            text += f"  👤 {o.full_name} | 💰 {o.final_amount:,} تومان\n"
            text += f"  📅 {o.created_at.strftime('%Y/%m/%d %H:%M')}\n\n"
        
        return {'text': text}
    
    def show_all_orders(self) -> Dict:
        orders = Order.objects.all().order_by('-created_at')[:15]
        
        text = f"🛒 **آخرین سفارشات:**\n\n"
        for o in orders:
            status_emoji = {'pending': '⏳', 'paid': '✅', 'completed': '🎉', 'cancelled': '❌'}.get(o.status, '📦')
            text += f"{status_emoji} **{o.order_number}** - {o.full_name} - {o.final_amount:,} تومان\n"
        
        return {'text': text}
    
    def change_order_status(self, message: str) -> Dict:
        return {'text': "🔄 لطفاً شماره سفارش و وضعیت جدید رو بگو:\nمثال: 'تغییر وضعیت سفارش ORD-123 به تکمیل شده'"}