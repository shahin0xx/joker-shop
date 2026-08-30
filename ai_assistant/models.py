# ai_assistant/models.py
from django.db import models
from django.contrib.auth.models import User

class ChatSession(models.Model):
    """جلسه چت با دستیار هوشمند"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ادمین")
    session_id = models.CharField(max_length=100, unique=True, verbose_name="شناسه جلسه")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان شروع")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین فعالیت")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    
    class Meta:
        verbose_name = "جلسه چت"
        verbose_name_plural = "جلسات چت"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ChatMessage(models.Model):
    """پیام‌های چت با دستیار هوشمند"""
    ROLE_CHOICES = [
        ('user', 'ادمین'),
        ('assistant', 'دستیار'),
        ('system', 'سیستم'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', verbose_name="جلسه")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="نقش")
    content = models.TextField(verbose_name="متن پیام")
    intent = models.CharField(max_length=50, blank=True, null=True, verbose_name="نیت شناسایی شده")
    action_taken = models.CharField(max_length=100, blank=True, null=True, verbose_name="عملیات انجام شده")
    action_success = models.BooleanField(default=True, verbose_name="موفقیت عملیات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ارسال")
    
    class Meta:
        verbose_name = "پیام چت"
        verbose_name_plural = "پیام‌های چت"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.get_role_display()}: {self.content[:50]}"