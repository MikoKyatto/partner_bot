"""
Start command and registration flow handlers
"""
import logging
import os
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from utils.database import save_user, get_user, is_user_approved
from utils.sheets import add_partnercode
from keyboards.admin import get_admin_keyboard

logger = logging.getLogger(__name__)

def get_admin_group_id() -> str:
    """Get admin group ID from environment"""
    return os.getenv('ADMIN_GROUP_ID', '-1003016595712')

# FSM States
class Register(StatesGroup):
    phone = State()
    name = State()

router = Router()

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Get the main menu keyboard for approved users"""
    keyboard = [
        [KeyboardButton(text="Моя реферальная ссылка")],
        [KeyboardButton(text="Посмотреть баланс")],
        [KeyboardButton(text="Поддержка")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

@router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    """Handle /start command"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin
        from handlers.admin import is_admin
        if is_admin(user_id):
            await message.answer(
                "👑 Welcome, Administrator!\n\n"
                "You have access to administrative functions.\n"
                "Use the buttons below or commands:\n\n"
                "/admin - Admin panel for user approvals\n"
                "/stats - System statistics\n"
                "/users - List approved users\n"
                "/health - System health check\n\n"
                "Note: Admins do not receive referral codes.",
                reply_markup=get_admin_keyboard()
            )
            return
        
        # Check if user already exists
        user = get_user(user_id)
        
        if user:
            if user['approved']:
                # User is approved, show main menu
                await message.answer(
                    "Добро пожаловать в реферальную систему Lethai! 🏝️\n\n"
                    "Выберите действие из меню ниже:",
                    reply_markup=get_main_menu_keyboard()
                )
            else:
                # User exists but not approved
                await message.answer(
                    "Ожидайте подтверждения в реферальной системе.\n"
                    "Мы уведомим вас, как только ваша заявка будет рассмотрена."
                )
        else:
            # New user, start registration
            await message.answer(
                "🏝️ Добро пожаловать в реферальную систему Lethai!\n\n"
                "Для регистрации поделитесь своим контактом, нажав кнопку ниже:",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
            )
            await state.set_state(Register.phone)
            
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.answer(
            "Произошла ошибка. Попробуйте позже или обратитесь в поддержку."
        )

@router.message(Register.phone, F.contact)
async def process_contact(message: types.Message, state: FSMContext):
    """Process contact sharing"""
    try:
        contact = message.contact
        
        # Validate contact
        if not contact.phone_number:
            await message.answer(
                "Не удалось получить номер телефона. Попробуйте еще раз:",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
            )
            return
        
        # Store phone number
        await state.update_data(phone=contact.phone_number)
        
        # Ask for name
        await message.answer(
            "Отлично! Теперь введите ваше имя:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Register.name)
        
    except Exception as e:
        logger.error(f"Error processing contact: {e}")
        await message.answer(
            "Произошла ошибка при обработке контакта. Попробуйте еще раз."
        )

@router.message(Register.phone)
async def invalid_contact(message: types.Message, state: FSMContext):
    """Handle invalid contact input"""
    await message.answer(
        "Пожалуйста, поделитесь контактом, нажав кнопку:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )

@router.message(Register.name)
async def process_name(message: types.Message, state: FSMContext):
    """Process name input and complete registration"""
    try:
        name = message.text.strip()
        
        # Validate name
        if not name or len(name) < 2:
            await message.answer(
                "Пожалуйста, введите корректное имя (минимум 2 символа):"
            )
            return
        
        if len(name) > 50:
            await message.answer(
                "Имя слишком длинное. Пожалуйста, введите имя до 50 символов:"
            )
            return
        
        # Get phone from state
        data = await state.get_data()
        phone = data.get('phone')
        
        if not phone:
            await message.answer(
                "Ошибка: номер телефона не найден. Начните регистрацию заново командой /start"
            )
            await state.clear()
            return
        
        # Save user to database
        user_id = message.from_user.id
        success = save_user(user_id, name, phone, approved=False)
        
        if success:
            # Notify admin group
            try:
                await message.bot.send_message(
                    chat_id=get_admin_group_id(),
                    text=f"🆕 Новая регистрация в реферальной системе:\n\n"
                         f"👤 ID: {user_id}\n"
                         f"📝 Имя: {name}\n"
                         f"📱 Телефон: {phone}\n\n"
                         f"Используйте /admin для рассмотрения заявки."
                )
            except Exception as e:
                logger.error(f"Error sending notification to admin group: {e}")
            
            # Confirm registration to user
            await message.answer(
                "✅ Регистрация успешно завершена!\n\n"
                "Ожидайте подтверждения в реферальной системе.\n"
                "Мы уведомим вас, как только ваша заявка будет рассмотрена."
            )
        else:
            await message.answer(
                "Произошла ошибка при сохранении данных. Попробуйте позже или обратитесь в поддержку."
            )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error processing name: {e}")
        await message.answer(
            "Произошла ошибка при обработке имени. Попробуйте еще раз."
        )

@router.message(F.text == "Моя реферальная ссылка")
async def show_referral_link(message: types.Message):
    """Show user's referral link and QR code"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin - admins don't have referral codes
        from handlers.admin import is_admin
        if is_admin(user_id):
            await message.answer(
                "⚠️ Administrators do not have referral codes.\n"
                "This feature is only for regular users."
            )
            return
        
        # Check if user is approved
        if not is_user_approved(user_id):
            await message.answer(
                "Ожидайте подтверждения в реферальной системе.\n"
                "Реферальная ссылка будет доступна после одобрения заявки."
            )
            return
        
        # Generate referral link
        from utils.qr_code import get_referral_link, generate_qr_code_bytes
        
        referral_link = get_referral_link(str(user_id))
        
        # Generate QR code
        qr_bytes = generate_qr_code_bytes(str(user_id))
        
        if qr_bytes:
            # Send QR code image with caption
            await message.answer_photo(
                photo=types.BufferedInputFile(qr_bytes, filename="qr_code.jpg"),
                caption=f"🔗 Ваша реферальная ссылка:\n\n{referral_link}\n\n"
                       f"Поделитесь этой ссылкой с друзьями и получайте бонусы за каждую регистрацию! 🎁"
            )
        else:
            # Fallback to text only
            await message.answer(
                f"🔗 Ваша реферальная ссылка:\n\n{referral_link}\n\n"
                f"Поделитесь этой ссылкой с друзьями и получайте бонусы за каждую регистрацию! 🎁"
            )
            
    except Exception as e:
        logger.error(f"Error showing referral link: {e}")
        await message.answer(
            "Произошла ошибка при генерации реферальной ссылки. Попробуйте позже."
        )

@router.message(F.text == "Посмотреть баланс")
async def show_balance(message: types.Message):
    """Show user's balance"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin - admins don't have balance
        from handlers.admin import is_admin
        if is_admin(user_id):
            await message.answer(
                "⚠️ Administrators do not have a balance.\n"
                "This feature is only for regular users."
            )
            return
        
        # Check if user is approved
        if not is_user_approved(user_id):
            await message.answer(
                "Ожидайте подтверждения в реферальной системе.\n"
                "Баланс будет доступен после одобрения заявки."
            )
            return
        
        # Get balance from Google Sheets
        from utils.sheets import get_balance
        
        balance = get_balance(str(user_id))
        
        # Create inline keyboard for withdrawal
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="💸 Вывести баланс",
                    url=f"https://t.me/LakeevaaaThai?start=withdraw_{user_id}"
                )]
            ]
        )
        
        await message.answer(
            f"💰 Ваш текущий баланс: {balance:.2f} ₽\n\n"
            f"Баланс обновляется автоматически при поступлении новых рефералов.",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error showing balance: {e}")
        await message.answer(
            "Ошибка при загрузке баланса, попробуйте позже."
        )

@router.message(F.text == "Поддержка")
async def show_support(message: types.Message):
    """Show support information"""
    await message.answer(
        "🆘 Поддержка Lethai\n\n"
        "По всем вопросам обращайтесь к нашему менеджеру:\n"
        "@LakeevaaaThai\n\n"
        "Мы поможем вам с любыми вопросами по реферальной программе! 💬"
    )

@router.message(F.text == "📊 Статистика")
async def admin_stats_button(message: types.Message):
    """Handle admin statistics button"""
    from handlers.admin import is_admin
    if not is_admin(message.from_user.id):
        return
    # Redirect to stats command
    from handlers.admin import admin_stats
    await admin_stats(message)

@router.message(F.text == "👥 Список пользователей")
async def admin_users_button(message: types.Message):
    """Handle admin users list button"""
    from handlers.admin import is_admin
    if not is_admin(message.from_user.id):
        return
    # Redirect to users command
    from handlers.admin import list_users
    await list_users(message)

@router.message(F.text == "⚙️ Админ панель")
async def admin_panel_button(message: types.Message):
    """Handle admin panel button"""
    from handlers.admin import is_admin
    if not is_admin(message.from_user.id):
        return
    # Redirect to admin command
    from handlers.admin import admin_panel
    await admin_panel(message)

@router.message(F.text == "🏥 Здоровье системы")
async def health_check_button(message: types.Message):
    """Handle health check button"""
    from handlers.admin import is_admin
    if not is_admin(message.from_user.id):
        return
    # Redirect to health command
    from handlers.admin import health_check
    await health_check(message)

@router.message(F.text & ~F.text.startswith('/'))
async def handle_other_messages(message: types.Message, state: FSMContext):
    """Handle other messages (excluding commands)"""
    current_state = await state.get_state()
    
    if current_state:
        # User is in registration flow
        if current_state == Register.phone:
            await invalid_contact(message, state)
        elif current_state == Register.name:
            await process_name(message, state)
    else:
        # User is not in any state, show help
        user_id = message.from_user.id
        user = get_user(user_id)
        
        if user and user['approved']:
            await message.answer(
                "Используйте меню ниже для навигации:",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await message.answer(
                "Для начала работы используйте команду /start"
            )
