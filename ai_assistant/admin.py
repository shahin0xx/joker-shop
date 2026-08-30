# ai_assistant/admin.py
from django.contrib import admin
from .models import ChatSession, ChatMessage

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['role', 'content', 'intent', 'action_taken', 'action_success', 'created_at']
    can_delete = False
    max_num = 0
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_id', 'message_count', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'session_id']
    readonly_fields = ['user', 'session_id', 'created_at', 'updated_at']
    inlines = [ChatMessageInline]
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'تعداد پیام‌ها'
    
    def has_add_permission(self, request):
        return False


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'content_short', 'intent', 'action_success', 'created_at']
    list_filter = ['role', 'intent', 'action_success', 'created_at']
    search_fields = ['content', 'session__user__username']
    readonly_fields = ['session', 'role', 'content', 'intent', 'action_taken', 'action_success', 'created_at']
    
    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_short.short_description = 'متن پیام'
    
    def has_add_permission(self, request):
        return False