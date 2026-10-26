# ai_assistant/handlers/user_handler.py
from typing import Dict, Any, List
from django.contrib.auth.models import User
from shop.models import UserProfile
from ..conversation_state import ConversationStep
from .base import BaseHandler


class UserHandler(BaseHandler):
    """مدیریت کامل کاربران"""
    
    def handle_intent(self, message: str) -> Dict[str, Any]:
        """تشخیص و اجرای عملیات کاربر"""
        msg_lower = message.lower()
        
        # لیست کاربران
        if any(w in msg_lower for w in ['لیست', 'همه', 'نمایش']):
            return self.list_users()
        
        # افزودن کاربر
        if any(w in msg_lower for w in ['اضافه', 'جدید', 'ایجاد', 'ساخت', 'add', 'new']):
            return self.start_add_user(message)
        
        # ویرایش کاربر
        if any(w in msg_lower for w in ['ویرایش', 'تغییر', 'ادیت', 'edit']):
            return self.start_edit_user(message)
        
        # حذف کاربر
        if any(w in msg_lower for w in ['حذف', 'پاک', 'delete', 'remove']):
            return self.delete_user(message)
        
        # تغییر رمز
        if any(w in msg_lower for w in ['رمز', 'password', 'پسورد']):
            return self.change_password(message)
        
        # فعال/غیرفعال
        if any(w in msg_lower for w in ['فعال', 'غیرفعال', 'active', 'deactive']):
            return self.toggle_active(message)
        
        # ادمین/کاربر عادی
        if any(w in msg_lower for w in ['ادمین', 'admin', 'staff']):
            return self.toggle_staff(message)
        
        # افزایش/کاهش اعتبار
        if any(w in msg_lower for w in ['اعتبار', 'credit', 'کیف پول']):
            return self.manage_credits(message)
        
        # جستجو
        if any(w in msg_lower for w in ['جستجو', 'پیدا', 'search', 'find']):
            return self.search_user(message)
        
        # اطلاعات یک کاربر خاص
        username = self._extract_username(message)
        if username:
            try:
                user = User.objects.get(username__iexact=username)
                return self.show_user_info(user)
            except:
                pass
        
        # منوی اصلی کاربران
        return self.show_main_menu()
    
    def _extract_username(self, text: str) -> str:
        """استخراج نام کاربری"""
        # حذف کلمات کلیدی
        keywords = ['کاربر', 'user', 'ویرایش', 'حذف', 'تغییر', 'رمز', 'اطلاعات']
        for kw in keywords:
            text = text.lower().replace(kw, '')
        return text.strip()
    
    def show_main_menu(self) -> Dict:
        """نمایش منوی اصلی کاربران"""
        total = User.objects.filter(is_staff=False).count()
        active = User.objects.filter(is_staff=False, is_active=True).count()
        staff = User.objects.filter(is_staff=True).count()
        
        text = "👥 **مدیریت کاربران**\n\n"
        text += f"📊 **آمار:**\n"
        text += f"• کاربران عادی: {total} (فعال: {active})\n"
        text += f"• ادمین‌ها: {staff}\n\n"
        text += "**عملیات قابل انجام:**\n"
        text += "• 👤 **'کاربر جدید بساز'** - افزودن کاربر\n"
        text += "• ✏️ **'ویرایش کاربر [نام]'** - ویرایش کامل\n"
        text += "• 🔐 **'تغییر رمز کاربر [نام]'**\n"
        text += "• ✅ **'فعال/غیرفعال کردن کاربر [نام]'**\n"
        text += "• 👑 **'ادمین کردن کاربر [نام]'**\n"
        text += "• 💰 **'افزایش اعتبار کاربر [نام] [مبلغ]'**\n"
        text += "• 🗑️ **'حذف کاربر [نام]'**\n"
        text += "• 📋 **'لیست همه کاربران'**\n"
        text += "• 🔍 **'جستجوی کاربر [نام]'**"
        
        return {'text': text}
    
    def list_users(self, filter_type: str = 'all') -> Dict:
        """لیست کاربران"""
        if filter_type == 'admin':
            users = User.objects.filter(is_staff=True)
            title = "👑 **ادمین‌ها**"
        elif filter_type == 'active':
            users = User.objects.filter(is_active=True, is_staff=False)
            title = "✅ **کاربران فعال**"
        elif filter_type == 'inactive':
            users = User.objects.filter(is_active=False, is_staff=False)
            title = "❌ **کاربران غیرفعال**"
        else:
            users = User.objects.all()
            title = "👥 **همه کاربران**"
        
        users = users.order_by('-date_joined')[:20]
        
        text = f"{title} ({users.count()} نفر نمایش داده شده)\n\n"
        for u in users:
            status = "✅" if u.is_active else "❌"
            admin_badge = " 👑" if u.is_staff else ""
            text += f"• {status}{admin_badge} **{u.username}**"
            if u.email:
                text += f" - {u.email}"
            text += f"\n  🆔 {u.id} | 📅 {u.date_joined.strftime('%Y/%m/%d')}\n"
        
        return {'text': text, 'actions': [
            {'text': '👑 ادمین‌ها', 'action': 'filter_admin'},
            {'text': '✅ فعال‌ها', 'action': 'filter_active'},
            {'text': '❌ غیرفعال‌ها', 'action': 'filter_inactive'},
            {'text': '👥 همه', 'action': 'filter_all'}
        ]}
    
    def start_add_user(self, message: str) -> Dict:
        """شروع فرآیند افزودن کاربر"""
        self.conversation.update_step(ConversationStep.ADDING_USER_USERNAME, {})
        
        text = "👤 **افزودن کاربر جدید**\n\n"
        text += "لطفاً **نام کاربری** رو وارد کن:\n"
        text += "(فقط حروف انگلیسی، اعداد و زیرخط)"
        
        return {'text': text}
    
    def process_add_user_step(self, step: ConversationStep, message: str, data: Dict) -> Dict:
        """پردازش مراحل افزودن کاربر"""
        
        if step == ConversationStep.ADDING_USER_USERNAME:
            username = message.strip()
            
            # بررسی تکراری نبودن
            if User.objects.filter(username=username).exists():
                return {'text': f"❌ نام کاربری **{username}** قبلاً ثبت شده. یه نام دیگه انتخاب کن:"}
            
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                return {'text': "❌ نام کاربری فقط می‌تونه شامل حروف انگلیسی، اعداد و زیرخط باشه. دوباره وارد کن:"}
            
            data['username'] = username
            self.conversation.update_step(ConversationStep.ADDING_USER_EMAIL, data)
            
            return {'text': f"✅ نام کاربری: **{username}**\n\nلطفاً **ایمیل** رو وارد کن:"}
        
        if step == ConversationStep.ADDING_USER_EMAIL:
            email = message.strip()
            
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                return {'text': "❌ ایمیل نامعتبره. دوباره وارد کن:"}
            
            if User.objects.filter(email=email).exists():
                return {'text': "❌ این ایمیل قبلاً ثبت شده. یه ایمیل دیگه وارد کن:"}
            
            data['email'] = email
            self.conversation.update_step(ConversationStep.ADDING_USER_PASSWORD, data)
            
            return {'text': f"✅ ایمیل: **{email}**\n\nلطفاً **رمز عبور** رو وارد کن:\n(حداقل ۸ کاراکتر)"}
        
        if step == ConversationStep.ADDING_USER_PASSWORD:
            password = message.strip()
            
            if len(password) < 8:
                return {'text': "❌ رمز عبور باید حداقل ۸ کاراکتر باشه. دوباره وارد کن:"}
            
            data['password'] = password
            self.conversation.update_step(ConversationStep.ADDING_USER_FULLNAME, data)
            
            return {'text': "✅ رمز عبور ثبت شد.\n\nلطفاً **نام کامل** رو وارد کن:\n(یا بگو 'بعدی')"}
        
        if step == ConversationStep.ADDING_USER_FULLNAME:
            if message.lower() not in ['بعدی', 'skip']:
                data['full_name'] = message
            
            self.conversation.update_step(ConversationStep.ADDING_USER_PHONE, data)
            
            return {'text': "📱 لطفاً **شماره تلفن** رو وارد کن:\n(یا بگو 'بعدی')"}
        
        if step == ConversationStep.ADDING_USER_PHONE:
            if message.lower() not in ['بعدی', 'skip']:
                phone = self._extract_phone(message)
                if phone:
                    data['phone'] = phone
                else:
                    return {'text': "❌ شماره تلفن نامعتبره. با ۰۹ شروع بشه و ۱۱ رقم باشه.\nدوباره وارد کن یا بگو 'بعدی':"}
            
            self.conversation.update_step(ConversationStep.ADDING_USER_IS_ADMIN, data)
            
            return {'text': "👑 این کاربر **ادمین** باشه؟ (بله/خیر)"}
        
        if step == ConversationStep.ADDING_USER_IS_ADMIN:
            is_admin = message.lower() in ['بله', 'آره', 'yes']
            data['is_admin'] = is_admin
            
            # ایجاد کاربر نهایی
            return self._create_user(data)
        
        return {'text': "❌ خطا در پردازش"}
    
    def _create_user(self, data: Dict) -> Dict:
        """ایجاد نهایی کاربر"""
        try:
            user = User.objects.create_user(
                username=data['username'],
                email=data.get('email', ''),
                password=data['password']
            )
            
            user.first_name = data.get('full_name', '')[:30]
            user.is_staff = data.get('is_admin', False)
            user.save()
            
            # پروفایل
            profile = user.profile
            if data.get('phone'):
                profile.phone = data['phone']
            if data.get('full_name'):
                profile.full_name = data['full_name']
            profile.save()
            
            text = f"🎉 **کاربر با موفقیت ایجاد شد!**\n\n"
            text += f"👤 نام کاربری: **{user.username}**\n"
            text += f"📧 ایمیل: {user.email or 'ندارد'}\n"
            text += f"👑 ادمین: {'✅' if user.is_staff else '❌'}\n"
            text += f"🔐 رمز: {data['password']}\n\n"
            text += "کار دیگه‌ای می‌خوای انجام بدی؟"
            
            self.conversation.reset()
            return {'text': text}
            
        except Exception as e:
            self.conversation.reset()
            return {'text': f"❌ خطا در ایجاد کاربر: {str(e)}"}
    
    def start_edit_user(self, message: str) -> Dict:
        """شروع ویرایش کاربر"""
        username = self._extract_username(message)
        
        if username:
            users = User.objects.filter(username__icontains=username)
            if users.count() == 1:
                return self.show_user_edit_options(users.first())
            elif users.count() > 1:
                text = f"🔍 **{users.count()} کاربر پیدا شد:**\n\n"
                for i, u in enumerate(users[:10], 1):
                    text += f"**{i}.** {u.username}\n"
                text += "\nشماره رو بگو:"
                self.conversation.update_step(ConversationStep.EDITING_USER_SELECT, {
                    'usernames': [u.username for u in users[:10]]
                })
                return {'text': text}
            else:
                return {'text': f"❌ کاربر '{username}' پیدا نشد."}
        else:
            return {'text': "👤 لطفاً نام کاربری رو بگو:\nمثال: 'ویرایش کاربر ali'"}
    
    def show_user_info(self, user: User) -> Dict:
        """نمایش اطلاعات کامل یک کاربر"""
        profile = user.profile
        
        text = f"👤 **اطلاعات کاربر: {user.username}**\n\n"
        text += f"🆔 شناسه: {user.id}\n"
        text += f"👤 نام کاربری: **{user.username}**\n"
        text += f"📧 ایمیل: {user.email or 'ندارد'}\n"
        text += f"📝 نام کامل: {user.get_full_name() or profile.full_name or 'ندارد'}\n"
        text += f"📱 تلفن: {profile.phone or 'ندارد'}\n"
        text += f"📍 آدرس: {profile.address or 'ندارد'}\n"
        text += f"📮 کد پستی: {profile.postal_code or 'ندارد'}\n"
        text += f"✅ وضعیت: {'فعال' if user.is_active else 'غیرفعال'}\n"
        text += f"👑 ادمین: {'بله' if user.is_staff else 'خیر'}\n"
        text += f"💰 اعتبار: {profile.credits:,} تومان\n"
        text += f"🔗 کد معرف: {profile.referral_code}\n"
        text += f"📅 تاریخ عضویت: {user.date_joined.strftime('%Y/%m/%d %H:%M')}\n"
        text += f"🕐 آخرین ورود: {user.last_login.strftime('%Y/%m/%d %H:%M') if user.last_login else 'ندارد'}\n\n"
        text += "**عملیات قابل انجام:**\n"
        text += "• 'ویرایش این کاربر'\n"
        text += "• 'تغییر رمز'\n"
        text += "• 'فعال/غیرفعال کردن'\n"
        text += "• 'افزایش اعتبار'\n"
        text += "• 'حذف کاربر'"
        
        return {'text': text, 'actions': [
            {'text': '✏️ ویرایش', 'action': 'edit'},
            {'text': '🔐 تغییر رمز', 'action': 'change_password'},
            {'text': '💰 افزایش اعتبار', 'action': 'add_credit'}
        ]}
    
    def show_user_edit_options(self, user: User) -> Dict:
        """نمایش گزینه‌های ویرایش کاربر"""
        profile = user.profile
        
        text = f"✏️ **ویرایش کاربر: {user.username}**\n\n"
        text += f"**اطلاعات فعلی:**\n"
        text += f"1️⃣ نام کاربری: **{user.username}**\n"
        text += f"2️⃣ ایمیل: **{user.email or 'ندارد'}**\n"
        text += f"3️⃣ نام کامل: **{user.get_full_name() or profile.full_name or 'ندارد'}**\n"
        text += f"4️⃣ تلفن: **{profile.phone or 'ندارد'}**\n"
        text += f"5️⃣ آدرس: **{profile.address or 'ندارد'}**\n"
        text += f"6️⃣ کد پستی: **{profile.postal_code or 'ندارد'}**\n"
        text += f"7️⃣ وضعیت: **{'✅ فعال' if user.is_active else '❌ غیرفعال'}**\n"
        text += f"8️⃣ ادمین: **{'👑 بله' if user.is_staff else '❌ خیر'}**\n"
        text += f"9️⃣ اعتبار: **{profile.credits:,} تومان**\n"
        text += f"🔟 تغییر رمز\n\n"
        text += "**شماره مورد نظر رو بگو** (می‌تونی چندتا رو با کاما جدا کنی):"
        
        self.conversation.update_step(ConversationStep.EDITING_USER_CHOOSE_FIELD, {
            'user_id': user.id,
            'username': user.username
        })
        
        return {'text': text}
    
    def process_edit_user_field(self, message: str, data: Dict) -> Dict:
        """پردازش انتخاب فیلد برای ویرایش"""
        user = User.objects.get(id=data['user_id'])
        profile = user.profile
        
        # استخراج شماره‌های انتخاب شده
        numbers = re.findall(r'\d+', message)
        if not numbers:
            return {'text': "❌ لطفاً شماره مورد نظر رو بگو."}
        
        for num in numbers:
            field = int(num)
            
            if field == 1:  # نام کاربری
                self.conversation.update_step(ConversationStep.EDITING_USER_USERNAME, data)
                return {'text': f"نام کاربری فعلی: **{user.username}**\n\nلطفاً **نام کاربری جدید** رو وارد کن:"}
            
            elif field == 2:  # ایمیل
                self.conversation.update_step(ConversationStep.EDITING_USER_EMAIL, data)
                return {'text': f"ایمیل فعلی: **{user.email or 'ندارد'}**\n\nلطفاً **ایمیل جدید** رو وارد کن:"}
            
            elif field == 3:  # نام کامل
                self.conversation.update_step(ConversationStep.EDITING_USER_FULLNAME, data)
                return {'text': f"نام کامل فعلی: **{profile.full_name or 'ندارد'}**\n\nلطفاً **نام کامل جدید** رو وارد کن:"}
            
            elif field == 4:  # تلفن
                self.conversation.update_step(ConversationStep.EDITING_USER_PHONE, data)
                return {'text': f"تلفن فعلی: **{profile.phone or 'ندارد'}**\n\nلطفاً **شماره تلفن جدید** رو وارد کن:"}
            
            elif field == 5:  # آدرس
                self.conversation.update_step(ConversationStep.EDITING_USER_ADDRESS, data)
                return {'text': f"آدرس فعلی: **{profile.address or 'ندارد'}**\n\nلطفاً **آدرس جدید** رو وارد کن:"}
            
            elif field == 6:  # کد پستی
                self.conversation.update_step(ConversationStep.EDITING_USER_POSTAL, data)
                return {'text': f"کد پستی فعلی: **{profile.postal_code or 'ندارد'}**\n\nلطفاً **کد پستی جدید** رو وارد کن:"}
            
            elif field == 7:  # فعال/غیرفعال
                user.is_active = not user.is_active
                user.save()
                self.conversation.reset()
                return {'text': f"✅ وضعیت کاربر به **{'فعال' if user.is_active else 'غیرفعال'}** تغییر کرد.\n\nکار دیگه‌ای می‌خوای؟"}
            
            elif field == 8:  # ادمین
                user.is_staff = not user.is_staff
                user.save()
                self.conversation.reset()
                return {'text': f"✅ کاربر **{'ادمین 👑' if user.is_staff else 'کاربر عادی'}** شد.\n\nکار دیگه‌ای می‌خوای؟"}
            
            elif field == 9:  # اعتبار
                self.conversation.update_step(ConversationStep.EDITING_USER_CREDIT, data)
                return {'text': f"اعتبار فعلی: **{profile.credits:,} تومان**\n\nلطفاً **مبلغ جدید** رو وارد کن (برای افزایش مثبت، برای کاهش منفی):\nمثال: +50000 یا -10000"}
            
            elif field == 10:  # تغییر رمز
                self.conversation.update_step(ConversationStep.EDITING_USER_PASSWORD, data)
                return {'text': f"🔐 **تغییر رمز کاربر {user.username}**\n\nلطفاً **رمز جدید** رو وارد کن:"}
        
        return {'text': "❌ شماره نامعتبر."}
    
    def process_edit_user_value(self, step: ConversationStep, message: str, data: Dict) -> Dict:
        """پردازش مقدار جدید برای ویرایش"""
        user = User.objects.get(id=data['user_id'])
        profile = user.profile
        
        if step == ConversationStep.EDITING_USER_USERNAME:
            new_username = message.strip()
            if User.objects.filter(username=new_username).exclude(id=user.id).exists():
                return {'text': "❌ این نام کاربری قبلاً ثبت شده. یه نام دیگه انتخاب کن:"}
            user.username = new_username
            user.save()
            text = f"✅ نام کاربری به **{new_username}** تغییر کرد."
            
        elif step == ConversationStep.EDITING_USER_EMAIL:
            new_email = message.strip()
            if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                return {'text': "❌ این ایمیل قبلاً ثبت شده. یه ایمیل دیگه وارد کن:"}
            user.email = new_email
            user.save()
            text = f"✅ ایمیل به **{new_email}** تغییر کرد."
            
        elif step == ConversationStep.EDITING_USER_FULLNAME:
            profile.full_name = message.strip()
            profile.save()
            text = f"✅ نام کامل به **{message.strip()}** تغییر کرد."
            
        elif step == ConversationStep.EDITING_USER_PHONE:
            phone = self._extract_phone(message)
            if phone:
                profile.phone = phone
                profile.save()
                text = f"✅ تلفن به **{phone}** تغییر کرد."
            else:
                return {'text': "❌ شماره تلفن نامعتبره."}
            
        elif step == ConversationStep.EDITING_USER_ADDRESS:
            profile.address = message.strip()
            profile.save()
            text = f"✅ آدرس به‌روزرسانی شد."
            
        elif step == ConversationStep.EDITING_USER_POSTAL:
            profile.postal_code = message.strip()
            profile.save()
            text = f"✅ کد پستی به **{message.strip()}** تغییر کرد."
            
        elif step == ConversationStep.EDITING_USER_CREDIT:
            amount = self._extract_number(message)
            if amount is None:
                return {'text': "❌ لطفاً مبلغ رو به عدد وارد کن."}
            
            if '-' in message:
                amount = -amount
            
            profile.credits += amount
            profile.save()
            text = f"✅ اعتبار کاربر {amount:+,} تومان تغییر کرد.\nاعتبار فعلی: **{profile.credits:,} تومان**"
            
        elif step == ConversationStep.EDITING_USER_PASSWORD:
            password = message.strip()
            if len(password) < 8:
                return {'text': "❌ رمز عبور باید حداقل ۸ کاراکتر باشه."}
            user.set_password(password)
            user.save()
            text = f"✅ رمز عبور کاربر **{user.username}** با موفقیت تغییر کرد.\n🔐 رمز جدید: **{password}**"
        
        else:
            return {'text': "❌ خطا در پردازش."}
        
        self.conversation.reset()
        return {'text': text + "\n\nکار دیگه‌ای می‌خوای انجام بدی؟"}
    
    def delete_user(self, message: str) -> Dict:
        """حذف کاربر"""
        username = self._extract_username(message)
        
        if not username:
            return {'text': "🗑️ لطفاً نام کاربری رو بگو:\nمثال: 'حذف کاربر ali'"}
        
        try:
            user = User.objects.get(username__iexact=username)
            
            # تایید حذف
            self.conversation.update_step(ConversationStep.DELETING_USER_CONFIRM, {
                'user_id': user.id,
                'username': user.username
            })
            
            return {'text': self._confirm_action(f"حذف کاربر **{user.username}**")}
            
        except User.DoesNotExist:
            return {'text': f"❌ کاربر '{username}' پیدا نشد."}
    
    def change_password(self, message: str) -> Dict:
        """تغییر رمز کاربر"""
        username = self._extract_username(message)
        
        if username:
            try:
                user = User.objects.get(username__iexact=username)
                self.conversation.update_step(ConversationStep.EDITING_USER_PASSWORD, {
                    'user_id': user.id,
                    'username': user.username
                })
                return {'text': f"🔐 **تغییر رمز کاربر {user.username}**\n\nلطفاً **رمز جدید** رو وارد کن:"}
            except User.DoesNotExist:
                return {'text': f"❌ کاربر '{username}' پیدا نشد."}
        else:
            return {'text': "🔐 لطفاً نام کاربری رو بگو:\nمثال: 'تغییر رمز کاربر ali'"}
    
    def toggle_active(self, message: str) -> Dict:
        """فعال/غیرفعال کردن کاربر"""
        username = self._extract_username(message)
        
        if username:
            try:
                user = User.objects.get(username__iexact=username)
                user.is_active = not user.is_active
                user.save()
                return {'text': f"✅ کاربر **{user.username}** {'فعال ✅' if user.is_active else 'غیرفعال ❌'} شد."}
            except User.DoesNotExist:
                return {'text': f"❌ کاربر '{username}' پیدا نشد."}
        else:
            return {'text': "لطفاً نام کاربری رو بگو:\nمثال: 'فعال کردن کاربر ali'"}
    
    def toggle_staff(self, message: str) -> Dict:
        """ادمین/کاربر عادی کردن"""
        username = self._extract_username(message)
        
        if username:
            try:
                user = User.objects.get(username__iexact=username)
                if user == self.user:
                    return {'text': "❌ نمی‌تونی دسترسی خودت رو تغییر بدی!"}
                user.is_staff = not user.is_staff
                user.save()
                return {'text': f"✅ کاربر **{user.username}** {'ادمین 👑' if user.is_staff else 'کاربر عادی'} شد."}
            except User.DoesNotExist:
                return {'text': f"❌ کاربر '{username}' پیدا نشد."}
        else:
            return {'text': "لطفاً نام کاربری رو بگو:\nمثال: 'ادمین کردن کاربر ali'"}
    
    def manage_credits(self, message: str) -> Dict:
        """مدیریت اعتبار کاربر"""
        parts = message.split()
        username = None
        amount = None
        
        for i, part in enumerate(parts):
            if part in ['اعتبار', 'credit'] and i + 1 < len(parts):
                username = parts[i + 1]
            if self._extract_number(part):
                amount = self._extract_number(part)
                if '-' in part or 'کاهش' in message:
                    amount = -amount
        
        if username:
            try:
                user = User.objects.get(username__iexact=username)
                
                if amount is None:
                    self.conversation.update_step(ConversationStep.EDITING_USER_CREDIT, {
                        'user_id': user.id,
                        'username': user.username
                    })
                    return {'text': f"اعتبار فعلی: **{user.profile.credits:,} تومان**\n\nلطفاً مبلغ رو وارد کن:"}
                
                user.profile.credits += amount
                user.profile.save()
                return {'text': f"✅ اعتبار کاربر **{user.username}** {amount:+,} تومان تغییر کرد.\nاعتبار فعلی: **{user.profile.credits:,} تومان**"}
                
            except User.DoesNotExist:
                return {'text': f"❌ کاربر '{username}' پیدا نشد."}
        else:
            return {'text': "💰 لطفاً نام کاربری و مبلغ رو بگو:\nمثال: 'افزایش اعتبار کاربر ali 50000'"}
    
    def search_user(self, message: str) -> Dict:
        """جستجوی کاربر"""
        query = self._extract_username(message)
        
        if not query:
            return {'text': "🔍 لطفاً عبارت جستجو رو بگو."}
        
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(profile__full_name__icontains=query) |
            Q(profile__phone__icontains=query)
        ).distinct()[:15]
        
        if users.exists():
            text = f"🔍 **نتایج جستجو برای '{query}':**\n\n"
            for u in users:
                text += f"• **{u.username}**"
                if u.email:
                    text += f" - {u.email}"
                text += f"\n  {'✅' if u.is_active else '❌'} {'👑' if u.is_staff else '👤'}\n"
            
            return {'text': text}
        else:
            return {'text': f"❌ هیچ کاربری با '{query}' پیدا نشد."}