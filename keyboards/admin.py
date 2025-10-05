"""
Admin keyboard for Lethai Concierge Referral Bot
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """
    Get admin keyboard with admin-specific actions
    
    Returns:
        ReplyKeyboardMarkup: Admin keyboard
    """
    keyboard = [
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="👥 Список пользователей")],
        [KeyboardButton(text="⚙️ Админ панель")],
        [KeyboardButton(text="🏥 Здоровье системы")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
