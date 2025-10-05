"""
Configuration settings for Lethai Concierge Referral Bot
"""
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration class"""
    
    # Bot settings
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    BOT_NAME: str = "Lethai Concierge Referral Bot"
    BOT_VERSION: str = "1.0.0"
    
    # Admin settings
    ADMIN_USER_ID: int = int(os.getenv('ADMIN_USER_ID', '1454702347'))
    ADMIN_GROUP_ID: str = os.getenv('ADMIN_GROUP_ID', '-1003016595712')
    
    # Google Sheets settings
    SHEETS_ID: str = os.getenv('SHEETS_ID', '18dY652fOqEJ6EC1ppMlMF0Obzlzu32xxVXt5AJ9415A')
    SHEET_NAME: str = 'Лист1'
    CREDENTIALS_PATH: str = os.getenv('CREDENTIALS_PATH', 'credentials.json')
    
    # Database settings
    DATABASE_PATH: str = 'users.db'
    
    # Referral settings
    REFERRAL_BASE_URL: str = 'https://taplink.cc/lakeevainfo'
    SUPPORT_USERNAME: str = '@LakeevaaaThai'
    
    # QR Code settings
    QR_SIZE: int = 400
    IMAGE_SIZE: int = 512
    BACKGROUND_COLOR: str = '#1A3C34'
    TEXT_COLOR: str = '#FFFFFF'
    FONT_SIZE: int = 40
    
    # Rate limiting
    RATE_LIMIT_MESSAGES: int = 10
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = 'bot.log'
    
    # Development settings
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    TESTING: bool = os.getenv('TESTING', 'False').lower() == 'true'
    
    # Validation settings
    MIN_NAME_LENGTH: int = 2
    MAX_NAME_LENGTH: int = 50
    MIN_PHONE_LENGTH: int = 10
    MAX_PHONE_LENGTH: int = 20
    
    # Message templates
    MESSAGES: Dict[str, str] = {
        'welcome': (
            "🏝️ Добро пожаловать в реферальную систему Lethai!\n\n"
            "Для регистрации поделитесь своим контактом, нажав кнопку ниже:"
        ),
        'contact_request': "📱 Поделиться контактом",
        'name_request': "Отлично! Теперь введите ваше имя:",
        'registration_success': (
            "✅ Регистрация успешно завершена!\n\n"
            "Ожидайте подтверждения в реферальной системе.\n"
            "Мы уведомим вас, как только ваша заявка будет рассмотрена."
        ),
        'approval_waiting': (
            "Ожидайте подтверждения в реферальной системе.\n"
            "Мы уведомим вас, как только ваша заявка будет рассмотрена."
        ),
        'approval_success': (
            "🎉 Поздравляем! Ваша заявка одобрена!\n\n"
            "Теперь вы можете использовать реферальную систему Lethai.\n"
            "Используйте команду /start для доступа к меню."
        ),
        'approval_rejected': (
            "❌ К сожалению, ваша заявка была отклонена.\n\n"
            "По вопросам обращайтесь в поддержку: @LakeevaaaThai"
        ),
        'main_menu': (
            "Добро пожаловать в реферальную систему Lethai! 🏝️\n\n"
            "Выберите действие из меню ниже:"
        ),
        'referral_link': (
            "🔗 Ваша реферальная ссылка:\n\n{link}\n\n"
            "Поделитесь этой ссылкой с друзьями и получайте бонусы за каждую регистрацию! 🎁\n\n"
            "💡 Как это работает:\n"
            "• Поделитесь ссылкой с друзьями\n"
            "• Они регистрируются по вашей ссылке\n"
            "• Вы получаете бонус за каждого реферала\n"
            "• Баланс обновляется автоматически"
        ),
        'balance_info': (
            "💰 Ваш текущий баланс: {balance:.2f} ₽\n\n"
            "📊 Баланс обновляется автоматически при поступлении новых рефералов.\n"
            "💬 По вопросам вывода обращайтесь к @LakeevaaaThai"
        ),
        'support_info': (
            "🆘 Поддержка Lethai\n\n"
            "По всем вопросам обращайтесь к нашему менеджеру:\n"
            "@LakeevaaaThai\n\n"
            "Мы поможем вам с любыми вопросами по реферальной программе! 💬\n\n"
            "⏰ Время ответа: обычно в течение 1-2 часов в рабочее время"
        ),
        'error_generic': "Произошла ошибка. Попробуйте позже или обратитесь в поддержку.",
        'error_balance': "Ошибка при загрузке баланса, попробуйте позже.",
        'error_qr': "Произошла ошибка при генерации реферальной ссылки. Попробуйте позже.",
        'error_database': "Ошибка базы данных. Попробуйте позже.",
        'error_sheets': "Ошибка подключения к Google Sheets. Попробуйте позже.",
    }
    
    # Keyboard layouts
    KEYBOARDS: Dict[str, List[List[str]]] = {
        'main_menu': [
            ["Моя реферальная ссылка"],
            ["Посмотреть баланс"],
            ["Поддержка"]
        ],
        'contact_share': [
            ["📱 Поделиться контактом"]
        ]
    }
    
    # Validation patterns
    PATTERNS: Dict[str, str] = {
        'phone': r'^\+?[1-9]\d{1,14}$',
        'name': r'^[a-zA-Zа-яА-ЯёЁ\s\-\.]{2,50}$',
        'telegram_id': r'^\d+$'
    }
    
    # Error messages
    ERRORS: Dict[str, str] = {
        'invalid_name': "Пожалуйста, введите корректное имя (минимум 2 символа):",
        'name_too_long': "Имя слишком длинное. Пожалуйста, введите имя до 50 символов:",
        'invalid_phone': "Не удалось получить номер телефона. Попробуйте еще раз:",
        'contact_required': "Пожалуйста, поделитесь контактом, нажав кнопку:",
        'not_admin': "❌ У вас нет прав администратора.",
        'user_not_found': "❌ Пользователь не найден.",
        'user_already_approved': "❌ Пользователь уже одобрен.",
        'sheets_connection_failed': "❌ Ошибка подключения к Google Sheets.",
        'database_error': "❌ Ошибка базы данных.",
    }
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")
        
        if not cls.SHEETS_ID:
            errors.append("SHEETS_ID is required")
        
        if not cls.ADMIN_USER_ID:
            errors.append("ADMIN_USER_ID is required")
        
        if not cls.ADMIN_GROUP_ID:
            errors.append("ADMIN_GROUP_ID is required")
        
        return errors
    
    @classmethod
    def get_referral_link(cls, partnercode: str) -> str:
        """Generate referral link for partner code"""
        return f"{cls.REFERRAL_BASE_URL}?ref={partnercode}"
    
    @classmethod
    def get_support_link(cls) -> str:
        """Get support contact link"""
        return f"https://t.me/{cls.SUPPORT_USERNAME.replace('@', '')}"
    
    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id == cls.ADMIN_USER_ID

# Create global config instance
config = Config()

# Validate configuration on import
if __name__ == "__main__":
    errors = config.validate()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration is valid")

