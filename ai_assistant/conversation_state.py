# ai_assistant/conversation_state.py
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from django.core.cache import cache
import json


class ConversationStep(Enum):
    """تمام مراحل مکالمه"""
    IDLE = "idle"
    
    # ========== کاربران ==========
    ADDING_USER_USERNAME = "adding_user_username"
    ADDING_USER_EMAIL = "adding_user_email"
    ADDING_USER_PASSWORD = "adding_user_password"
    ADDING_USER_FULLNAME = "adding_user_fullname"
    ADDING_USER_PHONE = "adding_user_phone"
    ADDING_USER_IS_ADMIN = "adding_user_is_admin"
    
    EDITING_USER_SELECT = "editing_user_select"
    EDITING_USER_CHOOSE_FIELD = "editing_user_choose_field"
    EDITING_USER_USERNAME = "editing_user_username"
    EDITING_USER_EMAIL = "editing_user_email"
    EDITING_USER_FULLNAME = "editing_user_fullname"
    EDITING_USER_PHONE = "editing_user_phone"
    EDITING_USER_ADDRESS = "editing_user_address"
    EDITING_USER_POSTAL = "editing_user_postal"
    EDITING_USER_CREDIT = "editing_user_credit"
    EDITING_USER_PASSWORD = "editing_user_password"
    DELETING_USER_CONFIRM = "deleting_user_confirm"
    
    # ========== محصولات ==========
    ADDING_PRODUCT_NAME = "adding_product_name"
    ADDING_PRODUCT_CATEGORY = "adding_product_category"
    ADDING_PRODUCT_GAME = "adding_product_game"
    ADDING_PRODUCT_PRICE = "adding_product_price"
    ADDING_PRODUCT_IS_NEW = "adding_product_is_new"
    ADDING_PRODUCT_DESCRIPTION = "adding_product_description"
    ADDING_PRODUCT_IMAGE = "adding_product_image"
    ADDING_PRODUCT_CONFIRM = "adding_product_confirm"
    
    EDITING_PRODUCT_SELECT = "editing_product_select"
    EDITING_PRODUCT_CHOOSE_FIELD = "editing_product_choose_field"
    EDITING_PRODUCT_NAME = "editing_product_name"
    EDITING_PRODUCT_CATEGORY = "editing_product_category"
    EDITING_PRODUCT_GAME = "editing_product_game"
    EDITING_PRODUCT_PRICE = "editing_product_price"
    EDITING_PRODUCT_IS_NEW = "editing_product_is_new"
    EDITING_PRODUCT_AVAILABLE = "editing_product_available"
    EDITING_PRODUCT_DESCRIPTION = "editing_product_description"
    EDITING_PRODUCT_IMAGE = "editing_product_image"
    DELETING_PRODUCT_CONFIRM = "deleting_product_confirm"
    
    # ========== سفارشات ==========
    VIEWING_ORDER_DETAIL = "viewing_order_detail"
    CHANGING_ORDER_STATUS = "changing_order_status"
    
    # ========== تخفیف ==========
    ADDING_DISCOUNT_CODE = "adding_discount_code"
    ADDING_DISCOUNT_TYPE = "adding_discount_type"
    ADDING_DISCOUNT_AMOUNT = "adding_discount_amount"
    ADDING_DISCOUNT_EXPIRY = "adding_discount_expiry"
    ADDING_DISCOUNT_USER = "adding_discount_user"
    DELETING_DISCOUNT_CONFIRM = "deleting_discount_confirm"
    
    # ========== دسته‌بندی ==========
    ADDING_CATEGORY_NAME = "adding_category_name"
    ADDING_CATEGORY_TYPE = "adding_category_type"
    ADDING_CATEGORY_PLATFORM = "adding_category_platform"
    EDITING_CATEGORY_SELECT = "editing_category_select"
    DELETING_CATEGORY_CONFIRM = "deleting_category_confirm"
    
    # ========== بازی ==========
    ADDING_GAME_NAME = "adding_game_name"
    ADDING_GAME_PLATFORM = "adding_game_platform"
    EDITING_GAME_SELECT = "editing_game_select"
    DELETING_GAME_CONFIRM = "deleting_game_confirm"
    
    # ========== اخبار ==========
    ADDING_NEWS_TITLE = "adding_news_title"
    ADDING_NEWS_CONTENT = "adding_news_content"
    ADDING_NEWS_IMAGE = "adding_news_image"
    EDITING_NEWS_SELECT = "editing_news_select"
    DELETING_NEWS_CONFIRM = "deleting_news_confirm"
    
    # ========== ویدیو ==========
    ADDING_VIDEO_TITLE = "adding_video_title"
    ADDING_VIDEO_DESCRIPTION = "adding_video_description"
    ADDING_VIDEO_THUMBNAIL = "adding_video_thumbnail"
    DELETING_VIDEO_CONFIRM = "deleting_video_confirm"
    
    # ========== اسلایدر ==========
    ADDING_SLIDER_IMAGE = "adding_slider_image"
    DELETING_SLIDER_CONFIRM = "deleting_slider_confirm"
    
    # ========== تم و پس‌زمینه ==========
    CHANGING_THEME = "changing_theme"
    CHANGING_BACKGROUND = "changing_background"
    
    # ========== تنظیمات ==========
    EDITING_SETTINGS_FIELD = "editing_settings_field"
    
    # ========== چت و پیام ==========
    SENDING_MESSAGE_USER = "sending_message_user"
    SENDING_MESSAGE_TEXT = "sending_message_text"


@dataclass
class ConversationContext:
    """ذخیره اطلاعات مکالمه فعلی"""
    step: ConversationStep = ConversationStep.IDLE
    data: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)
    
    def to_dict(self):
        return {
            'step': self.step.value,
            'data': self.data,
            'history': self.history[-20:]  # ۲۰ پیام آخر
        }
    
    @classmethod
    def from_dict(cls, data):
        ctx = cls()
        ctx.step = ConversationStep(data.get('step', 'idle'))
        ctx.data = data.get('data', {})
        ctx.history = data.get('history', [])
        return ctx


class ConversationManager:
    """مدیریت وضعیت مکالمه با استفاده از cache"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.cache_key = f"ai_conversation_{user_id}"
        self.ttl = 7200  # 2 ساعت
    
    def get_context(self) -> ConversationContext:
        """دریافت وضعیت فعلی"""
        data = cache.get(self.cache_key)
        if data:
            return ConversationContext.from_dict(json.loads(data))
        return ConversationContext()
    
    def save_context(self, context: ConversationContext):
        """ذخیره وضعیت"""
        cache.set(self.cache_key, json.dumps(context.to_dict(), ensure_ascii=False), self.ttl)
    
    def reset(self):
        """ریست وضعیت"""
        cache.delete(self.cache_key)
    
    def add_to_history(self, role: str, content: str):
        """اضافه کردن به تاریخچه"""
        ctx = self.get_context()
        ctx.history.append({
            'role': role,
            'content': content,
        })
        self.save_context(ctx)
    
    def update_step(self, step: ConversationStep, data: Dict = None):
        """به‌روزرسانی مرحله"""
        ctx = self.get_context()
        ctx.step = step
        if data:
            ctx.data.update(data)
        self.save_context(ctx)
    
    def get_pending_step(self) -> Optional[ConversationStep]:
        """دریافت مرحله در انتظار"""
        ctx = self.get_context()
        if ctx.step != ConversationStep.IDLE:
            return ctx.step
        return None