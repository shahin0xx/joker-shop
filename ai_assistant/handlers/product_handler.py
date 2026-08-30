# ai_assistant/handlers/product_handler.py
from typing import Dict, Any
from shop.models import Product, Category, GameList
from ..conversation_state import ConversationStep
from .base import BaseHandler


class ProductHandler(BaseHandler):
    """مدیریت محصولات"""
    
    def handle_intent(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower()
        
        if any(w in msg_lower for w in ['لیست', 'همه', 'نمایش']):
            return self.list_products()
        
        if any(w in msg_lower for w in ['اضافه', 'جدید', 'ایجاد', 'add', 'new']):
            return self.start_add_product()
        
        if any(w in msg_lower for w in ['ویرایش', 'تغییر', 'edit']):
            return self.start_edit_product(message)
        
        if any(w in msg_lower for w in ['حذف', 'پاک', 'delete']):
            return self.delete_product(message)
        
        if any(w in msg_lower for w in ['جستجو', 'پیدا', 'search']):
            return self.search_product(message)
        
        if any(w in msg_lower for w in ['موجودی', 'available']):
            return self.toggle_availability(message)
        
        return self.show_main_menu()
    
    def show_main_menu(self) -> Dict:
        total = Product.objects.filter(is_available=True).count()
        out_of_stock = Product.objects.filter(is_available=False).count()
        
        text = "📦 **مدیریت محصولات**\n\n"
        text += f"📊 محصولات فعال: {total} | ناموجود: {out_of_stock}\n\n"
        text += "**عملیات:**\n"
        text += "• 'محصول جدید' - افزودن\n"
        text += "• 'لیست محصولات' - مشاهده\n"
        text += "• 'ویرایش محصول [نام]'\n"
        text += "• 'تغییر موجودی محصول [نام]'\n"
        text += "• 'حذف محصول [نام]'\n"
        text += "• 'جستجوی محصول [نام]'"
        
        return {'text': text}
    
    def list_products(self) -> Dict:
        products = Product.objects.filter(is_available=True).order_by('-created_at')[:15]
        total = Product.objects.count()
        
        if not products.exists():
            return {'text': "📦 هیچ محصولی وجود نداره.\n\nمی‌خوای 'محصول جدید' اضافه کنی؟"}
        
        text = f"📦 **لیست محصولات ({total} عدد)**\n\n"
        for p in products:
            status = "✅" if p.is_available else "❌"
            text += f"• {status} **{p.name}** - {p.price:,} تومان | {p.category.name}\n"
            text += f"  🆔 کد: {p.id}\n"
        
        return {'text': text}
    
    def start_add_product(self) -> Dict:
        self.conversation.update_step(ConversationStep.ADDING_PRODUCT_NAME, {})
        
        text = "📦 **افزودن محصول جدید**\n\n"
        text += "لطفاً **نام محصول** رو وارد کن:"
        
        return {'text': text}
    
    def process_add_product_step(self, step: ConversationStep, message: str, data: Dict) -> Dict:
        msg_lower = message.lower()
        
        if step == ConversationStep.ADDING_PRODUCT_NAME:
            name = message.strip()
            if len(name) < 2:
                return {'text': "❌ لطفاً یه نام معتبر وارد کن."}
            data['name'] = name
            
            categories = Category.objects.filter(is_active=True)
            if categories.exists():
                text = f"✅ نام: **{name}**\n\n📂 **دسته‌بندی:**\n\n"
                for i, cat in enumerate(categories[:15], 1):
                    text += f"**{i}.** {cat.name}\n"
                text += "\nشماره رو بگو یا 'ساخت دسته جدید':"
                self.conversation.update_step(ConversationStep.ADDING_PRODUCT_CATEGORY, data)
                return {'text': text}
            else:
                cat = Category.objects.create(name='عمومی', type='console', game_platform='none', is_active=True)
                data['category_id'] = cat.id
                return self._goto_game_step(data)
        
        elif step == ConversationStep.ADDING_PRODUCT_CATEGORY:
            if msg_lower in ['ساخت دسته جدید', 'جدید']:
                self.conversation.update_step(ConversationStep.ADDING_CATEGORY_NAME, data)
                return {'text': "📂 لطفاً نام دسته‌بندی جدید رو وارد کن:"}
            
            try:
                idx = int(message) - 1
                categories = Category.objects.filter(is_active=True)
                if 0 <= idx < categories.count():
                    cat = categories[idx]
                    data['category_id'] = cat.id
                    data['category_name'] = cat.name
                    return self._goto_game_step(data)
            except:
                pass
            
            cats = Category.objects.filter(name__icontains=message, is_active=True)
            if cats.exists():
                if cats.count() == 1:
                    cat = cats.first()
                    data['category_id'] = cat.id
                    data['category_name'] = cat.name
                    return self._goto_game_step(data)
                else:
                    text = f"🔍 **{cats.count()} دسته‌بندی پیدا شد:**\n\n"
                    for i, c in enumerate(cats[:10], 1):
                        text += f"**{i}.** {c.name}\n"
                    text += "\nشماره رو بگو:"
                    return {'text': text}
            
            return {'text': "❌ دسته‌بندی پیدا نشد. دوباره شماره رو بگو."}
        
        elif step == ConversationStep.ADDING_PRODUCT_GAME:
            if msg_lower in ['بعدی', 'skip', 'رد کردن']:
                data['game_id'] = None
                return self._goto_price_step(data)
            
            if msg_lower in ['بازی جدید', 'جدید']:
                self.conversation.update_step(ConversationStep.ADDING_GAME_NAME, data)
                return {'text': "🎮 لطفاً نام بازی رو وارد کن:"}
            
            try:
                idx = int(message) - 1
                games = GameList.objects.filter(is_active=True)
                if 0 <= idx < games.count():
                    game = games[idx]
                    data['game_id'] = game.id
                    data['game_name'] = game.name
                    return self._goto_price_step(data)
            except:
                pass
            
            return {'text': "❌ بازی پیدا نشد. شماره رو بگو یا 'بعدی'."}
        
        elif step == ConversationStep.ADDING_PRODUCT_PRICE:
            price = self._extract_price(message)
            if price and price > 0:
                data['price'] = price
                text = f"✅ قیمت: **{price:,} تومان**\n\n🆕 محصول جدیده؟ (بله/خیر)"
                self.conversation.update_step(ConversationStep.ADDING_PRODUCT_IS_NEW, data)
                return {'text': text}
            else:
                return {'text': "❌ لطفاً قیمت رو به عدد بگو."}
        
        elif step == ConversationStep.ADDING_PRODUCT_IS_NEW:
            data['is_new'] = msg_lower in ['بله', 'آره', 'yes']
            text = "📝 **توضیحات** رو وارد کن (یا بگو 'بعدی'):"
            self.conversation.update_step(ConversationStep.ADDING_PRODUCT_DESCRIPTION, data)
            return {'text': text}
        
        elif step == ConversationStep.ADDING_PRODUCT_DESCRIPTION:
            if msg_lower not in ['بعدی', 'skip']:
                data['description'] = message
            else:
                data['description'] = f"محصول {data.get('name', '')}"
            
            return self._create_product(data)
        
        return {'text': "❌ خطا در پردازش."}
    
    def _goto_game_step(self, data: Dict) -> Dict:
        games = GameList.objects.filter(is_active=True)
        
        text = f"📦 محصول: **{data.get('name')}**\n📂 دسته‌بندی: **{data.get('category_name')}**\n\n"
        
        if games.exists():
            text += "🎮 **بازی مرتبط (اختیاری):**\n\n"
            for i, g in enumerate(games[:15], 1):
                text += f"**{i}.** {g.name} ({g.get_platform_display()})\n"
            text += "\nشماره رو بگو، یا 'بعدی'، یا 'بازی جدید':"
            self.conversation.update_step(ConversationStep.ADDING_PRODUCT_GAME, data)
            return {'text': text}
        else:
            data['game_id'] = None
            return self._goto_price_step(data)
    
    def _goto_price_step(self, data: Dict) -> Dict:
        text = f"📦 محصول: **{data.get('name')}**\n"
        text += f"📂 دسته‌بندی: **{data.get('category_name')}**\n"
        if data.get('game_name'):
            text += f"🎮 بازی: **{data.get('game_name')}**\n"
        text += "\n💰 **قیمت** رو وارد کن (مثال: ۲۵ میلیون):"
        
        self.conversation.update_step(ConversationStep.ADDING_PRODUCT_PRICE, data)
        return {'text': text}
    
    def _create_product(self, data: Dict) -> Dict:
        try:
            cat = Category.objects.get(id=data['category_id'])
            game = GameList.objects.get(id=data['game_id']) if data.get('game_id') else None
            
            product = Product.objects.create(
                name=data['name'],
                category=cat,
                game_list=game,
                price=data['price'],
                description=data.get('description', ''),
                is_available=True,
                is_new=data.get('is_new', True)
            )
            
            text = f"🎉 **محصول ثبت شد!**\n\n"
            text += f"📦 **{product.name}**\n"
            text += f"📂 {cat.name}\n"
            if game:
                text += f"🎮 {game.name}\n"
            text += f"💰 {product.price:,} تومان\n"
            text += f"🆔 کد: {product.id}\n\n"
            text += "🖼️ می‌خوای عکس آپلود کنی؟ (بله/خیر)"
            
            self.conversation.update_step(ConversationStep.ADDING_PRODUCT_IMAGE, {'product_id': product.id})
            
            return {'text': text, 'actions': [
                {'text': '🖼️ آپلود عکس', 'action': 'upload_image'},
                {'text': '⏭️ بعداً', 'action': 'later'}
            ]}
            
        except Exception as e:
            self.conversation.reset()
            return {'text': f"❌ خطا: {str(e)}"}
    
    def start_edit_product(self, message: str) -> Dict:
        return {'text': "✏️ لطفاً نام یا کد محصول رو بگو:\nمثال: 'ویرایش محصول ps5'"}
    
    def delete_product(self, message: str) -> Dict:
        return {'text': "🗑️ لطفاً نام یا کد محصول رو بگو:\nمثال: 'حذف محصول ps5'"}
    
    def search_product(self, message: str) -> Dict:
        query = message.lower()
        for w in ['جستجو', 'پیدا', 'کن', 'search', 'find']:
            query = query.replace(w, '')
        query = query.strip()
        
        if not query:
            return {'text': "🔍 لطفاً نام محصول رو بگو."}
        
        products = Product.objects.filter(name__icontains=query, is_available=True)[:10]
        
        if products.exists():
            text = f"🔍 **نتایج برای '{query}':**\n\n"
            for p in products:
                text += f"• **{p.name}** - {p.price:,} تومان | کد: {p.id}\n"
            return {'text': text}
        else:
            return {'text': f"❌ محصولی با '{query}' پیدا نشد."}
    
    def toggle_availability(self, message: str) -> Dict:
        return {'text': "📦 لطفاً نام یا کد محصول رو بگو تا موجودی رو تغییر بدم."}