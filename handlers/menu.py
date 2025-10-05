"""
User menu command handlers for Lethai Concierge Referral Bot
"""
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from config import config
from utils.sheets import get_balance
from utils.qr_code import generate_qr_code_bytes
from utils.database import is_user_approved

logger = logging.getLogger(__name__)

router = Router()

def get_main_menu() -> ReplyKeyboardMarkup:
    """Create main menu keyboard"""
    buttons = [
        [KeyboardButton(text=button) for button in row]
        for row in config.KEYBOARDS['main_menu']
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@router.message(lambda message: message.text == "Моя реферальная ссылка")
async def get_referral_link(message: Message):
    """Handle request for referral link and QR code"""
    if not is_user_approved(message.from_user.id):
        await message.answer(config.MESSAGES['approval_waiting'])
        return

    partnercode = str(message.from_user.id)
    link = config.get_referral_link(partnercode)
    qr_bytes = generate_qr_code_bytes(partnercode)

    if not qr_bytes:
        await message.answer(config.MESSAGES['error_qr'])
        return

    await message.answer(config.MESSAGES['referral_link'].format(link=link))
    await message.answer_photo(
        photo=qr_bytes,
        caption="Ваш реферальный QR-код"
    )

@router.message(lambda message: message.text == "Посмотреть баланс")
async def check_balance(message: Message):
    """Handle balance check request"""
    if not is_user_approved(message.from_user.id):
        await message.answer(config.MESSAGES['approval_waiting'])
        return

    partnercode = str(message.from_user.id)
    balance = get_balance(partnercode)

    if balance is None:
        await message.answer(config.MESSAGES['error_balance'])
        return

    await message.answer(
        config.MESSAGES['balance_info'].format(balance=balance),
        reply_markup=get_main_menu()
    )

@router.message(lambda message: message.text == "Поддержка")
async def contact_support(message: Message):
    """Handle support request"""
    if not is_user_approved(message.from_user.id):
        await message.answer(config.MESSAGES['approval_waiting'])
        return

    await message.answer(
        config.MESSAGES['support_info'],
        reply_markup=get_main_menu()
    )