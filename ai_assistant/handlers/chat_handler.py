# ai_assistant/handlers/chat_handler.py
from typing import Dict, Any
from django.contrib.auth.models import User
from shop.models import ChatMessage as ShopChatMessage
from ..conversation_state import ConversationStep
from .base import BaseHandler


class ChatHandler(BaseHandler):
    """مدیریت چت و ارسال پیام"""
    
    def handle_intent(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower()
        
        if any(w in msg_lower for w in ['ارسال', 'بفرست', 'send']):
            return self.start_send_message(message)
        
        if any(w in msg_lower for w in ['مشاهده', 'لیست', 'show']):
            return self.show_messages(message)
        
        return self.show_main_menu()
    
    def show_main_menu(self) -> Dict:
        unread = ShopChatMessage.objects.filter(is_admin=False, is_read=False).count()
        
        text = "💬 **مدیریت پیام‌ها**\n\n"
        text += f"📬 پیام‌های خوانده نشده: {unread}\n\n"
        text += "**عملیات:**\n"
        text += "• 'ارسال پیام به [نام کاربری]'\n"
        text += "• 'مشاهده پیام‌های [نام کاربری]'\n"
        text += "• 'پیام‌های خوانده نشده'"
        
        return {'text': text}
    
    def start_send_message(self, message: str) -> Dict:
        # استخراج نام کاربری
        msg_lower = message.lower()
        for word in ['ارسال', 'پیام', 'به', 'بفرست', 'send', 'message', 'to']:
            msg_lower = msg_lower.replace(word, '')
        
        username = msg_lower.strip()
        
        if username:
            try:
                user = User.objects.get(username__iexact=username)
                self.conversation.update_step(ConversationStep.SENDING_MESSAGE_TEXT, {
                    'target_user_id': user.id,
                    'target_username': user.username
                })
                
                return {'text': f"💬 **ارسال پیام به {user.username}**\n\nلطفاً متن پیام رو وارد کن:"}
                
            except User.DoesNotExist:
                return {'text': f"❌ کاربر '{username}' پیدا نشد."}
        else:
            return {'text': "💬 لطفاً نام کاربری رو بگو:\nمثال: 'ارسال پیام به ali'"}
    
    def process_send_message_text(self, message: str, data: Dict) -> Dict:
        """پردازش متن پیام"""
        target_user = User.objects.get(id=data['target_user_id'])
        
        ShopChatMessage.objects.create(
            user=target_user,
            message=message,
            is_admin=True,
            is_read=False
        )
        
        self.conversation.reset()
        
        return {
            'text': f"✅ پیام با موفقیت به **{target_user.username}** ارسال شد!\n\n"
                   f"📝 متن: _{message[:100]}{'...' if len(message) > 100 else ''}_\n\n"
                   "کار دیگه‌ای می‌خوای؟",
            'actions': self._get_main_actions()
        }
    
    def show_messages(self, message: str) -> Dict:
        msg_lower = message.lower()
        
        # استخراج نام کاربری
        for word in ['مشاهده', 'پیام', 'های', 'show', 'messages', 'of']:
            msg_lower = msg_lower.replace(word, '')
        
        username = msg_lower.strip()
        
        if username:
            try:
                user = User.objects.get(username__iexact=username)
                messages = ShopChatMessage.objects.filter(user=user).order_by('-created_at')[:20]
                
                text = f"💬 **پیام‌های {user.username}**\n\n"
                
                if messages.exists():
                    for msg in messages:
                        sender = "👑 ادمین" if msg.is_admin else "👤 کاربر"
                        status = "✅" if msg.is_read else "📬"
                        text += f"{status} **{sender}**: {msg.message[:50]}...\n"
                        text += f"  📅 {msg.created_at.strftime('%Y/%m/%d %H:%M')}\n\n"
                else:
                    text += "هیچ پیامی وجود نداره."
                
                return {'text': text}
                
            except User.DoesNotExist:
                return {'text': f"❌ کاربر '{username}' پیدا نشد."}
        else:
            # نمایش کاربرانی که پیام دارن
            users_with_messages = User.objects.filter(
                chat_messages__isnull=False
            ).distinct().order_by('-date_joined')[:10]
            
            if users_with_messages.exists():
                text = "💬 **کاربرانی که پیام دارن:**\n\n"
                for u in users_with_messages:
                    unread = u.chat_messages.filter(is_admin=False, is_read=False).count()
                    text += f"• **{u.username}**"
                    if unread > 0:
                        text += f" ({unread} پیام جدید 📬)"
                    text += "\n"
                
                text += "\nبرای مشاهده پیام‌ها بگو: 'مشاهده پیام‌های [نام کاربری]'"
            else:
                text = "💬 هیچ پیامی وجود نداره."
            
            return {'text': text}