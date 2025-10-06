"""
Admin commands and interface for approving/rejecting users
"""
import logging
import os
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from utils.database import get_pending_users, update_user_approval, get_user, get_approved_users
from utils.sheets import add_partnercode
from health import HealthChecker

logger = logging.getLogger(__name__)

router = Router()

def get_admin_user_id() -> int:
    """Get admin user ID from environment"""
    return int(os.getenv('ADMIN_USER_ID', '1454702347'))

def get_admin_group_id() -> str:
    """Get admin group ID from environment"""
    return os.getenv('ADMIN_GROUP_ID', '-1003016595712')

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    admin_user_id = get_admin_user_id()
    logger.info(f"Checking admin status for user {user_id}, admin ID is {admin_user_id}")
    is_admin_result = user_id == admin_user_id
    logger.info(f"User {user_id} admin status: {is_admin_result}")
    return is_admin_result

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    """Show admin panel"""
    try:
        user_id = message.from_user.id
        logger.info(f"🔧 ADMIN COMMAND CALLED by user {user_id}")
        logger.info(f"Message text: {message.text}")
        logger.info(f"Message type: {type(message.text)}")
        
        if not is_admin(user_id):
            logger.warning(f"User {user_id} tried to access admin panel but is not admin")
            await message.answer("❌ У вас нет прав администратора.")
            return
        
        logger.info(f"✅ User {user_id} is admin, showing admin panel")
        
        # Get pending users
        pending_users = get_pending_users()
        
        if not pending_users:
            await message.answer(
                "👥 Админ панель\n\n"
                "📋 Нет пользователей, ожидающих подтверждения."
            )
            return
        
        # Show pending users
        text = "👥 Админ панель\n\n📋 Пользователи, ожидающие подтверждения:\n\n"
        
        for i, user in enumerate(pending_users[:10], 1):  # Limit to 10 users
            text += f"{i}. ID: {user['telegram_id']}\n"
            text += f"   Имя: {user['name']}\n"
            text += f"   Телефон: {user['phone']}\n"
            text += f"   Дата: {user['created_at']}\n\n"
        
        if len(pending_users) > 10:
            text += f"... и еще {len(pending_users) - 10} пользователей\n\n"
        
        # Create inline keyboard for each pending user
        keyboard_buttons = []
        for user in pending_users[:5]:  # Limit to 5 buttons
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"✅ {user['name']} ({user['telegram_id']})",
                    callback_data=f"approve_{user['telegram_id']}"
                ),
                InlineKeyboardButton(
                    text=f"❌ Отклонить",
                    callback_data=f"reject_{user['telegram_id']}"
                )
            ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin panel: {e}")
        await message.answer("Произошла ошибка в админ панели.")

@router.callback_query(F.data.startswith("approve_"))
async def approve_user(callback: CallbackQuery):
    """Approve a user"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ У вас нет прав администратора.", show_alert=True)
            return
        
        # Extract user ID from callback data
        user_id = int(callback.data.split("_")[1])
        
        # Get user info
        user = get_user(user_id)
        if not user:
            await callback.answer("❌ Пользователь не найден.", show_alert=True)
            return
        
        if user['approved']:
            await callback.answer("❌ Пользователь уже одобрен.", show_alert=True)
            return
        
        # Update user approval status
        success = update_user_approval(user_id, True)
        
        if success:
            # Add partnercode to Google Sheets with full user data
            sheets_success = add_partnercode(
                partnercode=str(user_id),
                name=user['name'],
                contact=user['phone'],
                username=callback.from_user.username,
                referral_source=None  # Can be extended later if referral tracking is added
            )
            
            if sheets_success:
                # Notify user
                try:
                    await callback.bot.send_message(
                        chat_id=user_id,
                        text="🎉 Поздравляем! Ваша заявка одобрена!\n\n"
                             "Теперь вы можете использовать реферальную систему Lethai.\n"
                             "Используйте команду /start для доступа к меню."
                    )
                except Exception as e:
                    logger.error(f"Error notifying user {user_id}: {e}")
                
                # Notify admin group
                try:
                    await callback.bot.send_message(
                        chat_id=get_admin_group_id(),
                        text=f"✅ Пользователь одобрен:\n\n"
                             f"👤 ID: {user_id}\n"
                             f"📝 Имя: {user['name']}\n"
                             f"📱 Телефон: {user['phone']}\n"
                             f"🔗 Реферальная ссылка: https://taplink.cc/lakeevainfo?ref={user_id}"
                    )
                except Exception as e:
                    logger.error(f"Error notifying admin group: {e}")
                
                await callback.answer("✅ Пользователь одобрен!", show_alert=True)
                
                # Update the message
                await callback.message.edit_text(
                    f"✅ Пользователь {user['name']} (ID: {user_id}) одобрен!\n\n"
                    f"Реферальная ссылка: https://taplink.cc/lakeevainfo?ref={user_id}"
                )
            else:
                await callback.answer("❌ Ошибка при добавлении в Google Sheets.", show_alert=True)
        else:
            await callback.answer("❌ Ошибка при обновлении статуса пользователя.", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error approving user: {e}")
        await callback.answer("❌ Произошла ошибка при одобрении пользователя.", show_alert=True)

@router.callback_query(F.data.startswith("reject_"))
async def reject_user(callback: CallbackQuery):
    """Reject a user"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ У вас нет прав администратора.", show_alert=True)
            return
        
        # Extract user ID from callback data
        user_id = int(callback.data.split("_")[1])
        
        # Get user info
        user = get_user(user_id)
        if not user:
            await callback.answer("❌ Пользователь не найден.", show_alert=True)
            return
        
        # Notify user
        try:
            await callback.bot.send_message(
                chat_id=user_id,
                text="❌ К сожалению, ваша заявка была отклонена.\n\n"
                     "По вопросам обращайтесь в поддержку: @LakeevaaaThai"
            )
        except Exception as e:
            logger.error(f"Error notifying user {user_id}: {e}")
        
        # Notify admin group
        try:
            await callback.bot.send_message(
                chat_id=get_admin_group_id(),
                text=f"❌ Пользователь отклонен:\n\n"
                     f"👤 ID: {user_id}\n"
                     f"📝 Имя: {user['name']}\n"
                     f"📱 Телефон: {user['phone']}"
            )
        except Exception as e:
            logger.error(f"Error notifying admin group: {e}")
        
        await callback.answer("❌ Пользователь отклонен!", show_alert=True)
        
        # Update the message
        await callback.message.edit_text(
            f"❌ Пользователь {user['name']} (ID: {user_id}) отклонен."
        )
        
    except Exception as e:
        logger.error(f"Error rejecting user: {e}")
        await callback.answer("❌ Произошла ошибка при отклонении пользователя.", show_alert=True)

@router.message(Command("stats"))
async def admin_stats(message: types.Message):
    """Show admin statistics"""
    try:
        user_id = message.from_user.id
        logger.info(f"📊 STATS COMMAND CALLED by user {user_id}")
        
        if not is_admin(user_id):
            await message.answer("❌ У вас нет прав администратора.")
            return
        
        # Get statistics
        pending_users = get_pending_users()
        approved_users = get_approved_users()
        
        # Get Google Sheets info
        from utils.sheets import get_worksheet_info, test_connection
        
        sheets_connected = test_connection()
        sheets_info = get_worksheet_info() if sheets_connected else {}
        
        text = "📊 Статистика реферальной системы\n\n"
        text += f"⏳ Ожидают подтверждения: {len(pending_users)}\n"
        text += f"✅ Одобренных пользователей: {len(approved_users)}\n"
        text += f"📈 Всего зарегистрированных: {len(pending_users) + len(approved_users)}\n\n"
        
        if sheets_connected:
            text += f"📋 Google Sheets:\n"
            text += f"   • Подключение: ✅\n"
            text += f"   • Партнеров в таблице: {sheets_info.get('partnercode_count', 'N/A')}\n"
            text += f"   • Строк в таблице: {sheets_info.get('row_count', 'N/A')}\n"
        else:
            text += f"📋 Google Sheets: ❌ Нет подключения\n"
        
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error in admin stats: {e}")
        await message.answer("Произошла ошибка при получении статистики.")

@router.message(Command("users"))
async def list_users(message: types.Message):
    """List all approved users"""
    try:
        user_id = message.from_user.id
        logger.info(f"👥 USERS COMMAND CALLED by user {user_id}")
        
        if not is_admin(user_id):
            await message.answer("❌ У вас нет прав администратора.")
            return
        
        approved_users = get_approved_users()
        
        if not approved_users:
            await message.answer("📋 Нет одобренных пользователей.")
            return
        
        text = "👥 Одобренные пользователи:\n\n"
        
        for i, user in enumerate(approved_users[:20], 1):  # Limit to 20 users
            text += f"{i}. ID: {user['telegram_id']}\n"
            text += f"   Имя: {user['name']}\n"
            text += f"   Телефон: {user['phone']}\n"
            text += f"   Одобрен: {user['approved_at']}\n"
            text += f"   Ссылка: https://taplink.cc/lakeevainfo?ref={user['telegram_id']}\n\n"
        
        if len(approved_users) > 20:
            text += f"... и еще {len(approved_users) - 20} пользователей\n"
        
        # Split message if too long
        if len(text) > 4000:
            # Send in chunks
            chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for chunk in chunks:
                await message.answer(chunk)
        else:
            await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        await message.answer("Произошла ошибка при получении списка пользователей.")

@router.message(Command("health"))
async def health_check(message: types.Message):
    """Check bot system health"""
    try:
        user_id = message.from_user.id
        logger.info(f"🏥 HEALTH COMMAND CALLED by user {user_id}")
        
        if not is_admin(user_id):
            await message.answer("❌ У вас нет прав администратора.")
            return
        
        # Run health checks
        health = HealthChecker.run_all_checks()
        
        # Build status message
        status_icon = "✅" if health['status'] == 'healthy' else "❌"
        text = f"🏥 Состояние системы: {status_icon} {health['status'].upper()}\n\n"
        text += f"📊 Проверок выполнено: {health['summary']['healthy_checks']}/{health['summary']['total_checks']}\n\n"
        
        for check_name, check_result in health['checks'].items():
            check_icon = "✅" if check_result['status'] == 'healthy' else "❌"
            check_title = check_name.replace('_', ' ').title()
            text += f"{check_icon} {check_title}:\n"
            text += f"   {check_result['message']}\n"
            
            if check_result['details']:
                for key, value in list(check_result['details'].items())[:3]:  # Limit to 3 details
                    text += f"   • {key}: {value}\n"
            text += "\n"
        
        text += f"🕐 Время проверки: {health['timestamp']}"
        
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        await message.answer("Произошла ошибка при проверке состояния системы.")
