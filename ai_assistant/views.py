# ai_assistant/views.py
import json
import uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import ChatSession, ChatMessage
from .admin_assistant import AdminAssistant


def is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def assistant_panel(request):
    """پنل اصلی دستیار هوشمند"""
    ChatSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
    
    session = ChatSession.objects.create(
        user=request.user,
        session_id=str(uuid.uuid4()),
        is_active=True
    )
    
    context = {
        'session_id': session.session_id,
        'user': request.user,
    }
    
    return render(request, 'ai_assistant/panel.html', context)


@login_required
@user_passes_test(is_admin)
@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """API اصلی چت"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        image_data = data.get('image')
        
        session = None
        if session_id:
            try:
                session = ChatSession.objects.get(
                    session_id=session_id,
                    user=request.user,
                    is_active=True
                )
            except ChatSession.DoesNotExist:
                pass
        
        if not session:
            ChatSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
            session = ChatSession.objects.create(
                user=request.user,
                session_id=str(uuid.uuid4()),
                is_active=True
            )
        
        display_message = message if message else "📸 [عکس ارسال شد]"
        ChatMessage.objects.create(
            session=session,
            role='user',
            content=display_message
        )
        
        assistant = AdminAssistant(request.user)
        response = assistant.process_message(message, image_data)
        
        ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=response.get('text', ''),
            action_success=True
        )
        
        session.save()
        
        return JsonResponse({
            'success': True,
            'response': response,
            'session_id': session.session_id,
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'فرمت داده‌ها نامعتبر است'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def init_session(request):
    """ایجاد جلسه جدید"""
    ChatSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
    
    session = ChatSession.objects.create(
        user=request.user,
        session_id=str(uuid.uuid4()),
        is_active=True
    )
    
    assistant = AdminAssistant(request.user)
    response = assistant.process_message("سلام")
    
    ChatMessage.objects.create(
        session=session,
        role='assistant',
        content=response.get('text', ''),
        action_success=True
    )
    
    return JsonResponse({
        'success': True,
        'session_id': session.session_id,
        'response': response,
    })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def end_session(request):
    """پایان جلسه"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        if session_id:
            ChatSession.objects.filter(session_id=session_id, user=request.user).update(is_active=False)
        return JsonResponse({'success': True})
    except:
        return JsonResponse({'success': True})


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def clear_history(request):
    """پاک کردن تاریخچه"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        if session_id:
            ChatSession.objects.filter(session_id=session_id, user=request.user).update(is_active=False)
        return init_session(request)
    except:
        return JsonResponse({'success': False}, status=400)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def get_history(request):
    """دریافت تاریخچه"""
    session_id = request.GET.get('session_id')
    if not session_id:
        return JsonResponse({'success': False, 'messages': []})
    
    try:
        session = ChatSession.objects.get(session_id=session_id, user=request.user)
        messages = session.messages.all().order_by('created_at')
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at.strftime('%H:%M'),
            })
        
        return JsonResponse({'success': True, 'messages': messages_data})
    except ChatSession.DoesNotExist:
        return JsonResponse({'success': False, 'messages': []})


@login_required
@user_passes_test(is_admin)
def quick_actions(request):
    """اکشن‌های سریع"""
    actions = [
        {'id': 'user_add', 'text': '👤 کاربر جدید', 'message': 'کاربر جدید بساز'},
        {'id': 'product_add', 'text': '📦 محصول جدید', 'message': 'محصول جدید اضافه کن'},
        {'id': 'discount_add', 'text': '🏷️ کد تخفیف', 'message': 'کد تخفیف جدید'},
        {'id': 'theme_change', 'text': '🎨 تغییر تم', 'message': 'تغییر تم'},
        {'id': 'stats_view', 'text': '📊 آمار فروش', 'message': 'آمار فروش'},
        {'id': 'orders_view', 'text': '🛒 سفارشات', 'message': 'سفارشات در انتظار'},
        {'id': 'help', 'text': '❓ راهنما', 'message': 'راهنما'},
    ]
    return JsonResponse({'success': True, 'actions': actions})


@login_required
@user_passes_test(is_admin)
def chat_widget(request):
    """ویجت چت"""
    context = {
        'user': request.user,
        'session_id': str(uuid.uuid4()),
    }
    return render(request, 'ai_assistant/widget.html', context)