"""
Unit tests for bot handlers
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from aiogram import types
from aiogram.fsm.context import FSMContext

from handlers.start import start_command, process_contact, process_name
from handlers.admin import admin_panel, approve_user, reject_user
from handlers.menu import show_referral_link, show_balance

class TestStartHandlers:
    """Test start command handlers"""
    
    @pytest.fixture
    def mock_message(self):
        """Create a mock message"""
        message = Mock(spec=types.Message)
        message.from_user.id = 12345
        message.from_user.username = "testuser"
        message.text = "/start"
        message.answer = AsyncMock()
        message.bot.send_message = AsyncMock()
        return message
    
    @pytest.fixture
    def mock_state(self):
        """Create a mock FSM state"""
        state = Mock(spec=FSMContext)
        state.set_state = AsyncMock()
        state.update_data = AsyncMock()
        state.get_data = AsyncMock()
        state.clear = AsyncMock()
        return state
    
    @pytest.mark.asyncio
    async def test_start_command_new_user(self, mock_message, mock_state):
        """Test start command for new user"""
        with patch('handlers.start.get_user', return_value=None):
            await start_command(mock_message, mock_state)
            
            mock_message.answer.assert_called_once()
            mock_state.set_state.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_command_approved_user(self, mock_message, mock_state):
        """Test start command for approved user"""
        user_data = {
            'telegram_id': 12345,
            'name': 'Test User',
            'phone': '+1234567890',
            'approved': True
        }
        
        with patch('handlers.start.get_user', return_value=user_data):
            await start_command(mock_message, mock_state)
            
            mock_message.answer.assert_called_once()
            # Should not set state for approved user
            mock_state.set_state.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_process_contact(self, mock_message, mock_state):
        """Test contact processing"""
        contact = Mock()
        contact.phone_number = "+1234567890"
        mock_message.contact = contact
        
        await process_contact(mock_message, mock_state)
        
        mock_state.update_data.assert_called_once()
        mock_state.set_state.assert_called_once()
        mock_message.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_name(self, mock_message, mock_state):
        """Test name processing"""
        mock_message.text = "Test User"
        mock_state.get_data.return_value = {"phone": "+1234567890"}
        
        with patch('handlers.start.save_user', return_value=True):
            await process_name(mock_message, mock_state)
            
            mock_state.get_data.assert_called_once()
            mock_state.clear.assert_called_once()
            mock_message.answer.assert_called_once()

class TestAdminHandlers:
    """Test admin command handlers"""
    
    @pytest.fixture
    def mock_message(self):
        """Create a mock message"""
        message = Mock(spec=types.Message)
        message.from_user.id = 1454702347  # Admin ID
        message.answer = AsyncMock()
        return message
    
    @pytest.fixture
    def mock_callback(self):
        """Create a mock callback query"""
        callback = Mock(spec=types.CallbackQuery)
        callback.from_user.id = 1454702347  # Admin ID
        callback.answer = AsyncMock()
        callback.message.edit_text = AsyncMock()
        callback.bot.send_message = AsyncMock()
        return callback
    
    @pytest.mark.asyncio
    async def test_admin_panel_no_pending_users(self, mock_message):
        """Test admin panel with no pending users"""
        with patch('handlers.admin.get_pending_users', return_value=[]):
            await admin_panel(mock_message)
            
            mock_message.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_admin_panel_with_pending_users(self, mock_message):
        """Test admin panel with pending users"""
        pending_users = [
            {
                'telegram_id': 12345,
                'name': 'Test User',
                'phone': '+1234567890',
                'created_at': '2024-01-01 12:00:00'
            }
        ]
        
        with patch('handlers.admin.get_pending_users', return_value=pending_users):
            await admin_panel(mock_message)
            
            mock_message.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_approve_user(self, mock_callback):
        """Test user approval"""
        user_data = {
            'telegram_id': 12345,
            'name': 'Test User',
            'phone': '+1234567890',
            'approved': False
        }
        
        with patch('handlers.admin.get_user', return_value=user_data), \
             patch('handlers.admin.update_user_approval', return_value=True), \
             patch('handlers.admin.add_partnercode', return_value=True):
            
            await approve_user(mock_callback)
            
            mock_callback.answer.assert_called_once()
            mock_callback.message.edit_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_reject_user(self, mock_callback):
        """Test user rejection"""
        user_data = {
            'telegram_id': 12345,
            'name': 'Test User',
            'phone': '+1234567890',
            'approved': False
        }
        
        with patch('handlers.admin.get_user', return_value=user_data):
            await reject_user(mock_callback)
            
            mock_callback.answer.assert_called_once()
            mock_callback.message.edit_text.assert_called_once()

class TestMenuHandlers:
    """Test menu command handlers"""
    
    @pytest.fixture
    def mock_message(self):
        """Create a mock message"""
        message = Mock(spec=types.Message)
        message.from_user.id = 12345
        message.answer = AsyncMock()
        message.answer_photo = AsyncMock()
        return message
    
    @pytest.mark.asyncio
    async def test_show_referral_link_approved_user(self, mock_message):
        """Test showing referral link for approved user"""
        with patch('handlers.menu.is_user_approved', return_value=True), \
             patch('handlers.menu.generate_qr_code_bytes', return_value=b'fake_qr_data'):
            
            await show_referral_link(mock_message)
            
            mock_message.answer_photo.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_show_referral_link_unapproved_user(self, mock_message):
        """Test showing referral link for unapproved user"""
        with patch('handlers.menu.is_user_approved', return_value=False):
            await show_referral_link(mock_message)
            
            mock_message.answer.assert_called_once()
            mock_message.answer_photo.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_show_balance_approved_user(self, mock_message):
        """Test showing balance for approved user"""
        with patch('handlers.menu.is_user_approved', return_value=True), \
             patch('handlers.menu.get_balance', return_value=100.50):
            
            await show_balance(mock_message)
            
            mock_message.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_show_balance_unapproved_user(self, mock_message):
        """Test showing balance for unapproved user"""
        with patch('handlers.menu.is_user_approved', return_value=False):
            await show_balance(mock_message)
            
            mock_message.answer.assert_called_once()

class TestErrorHandling:
    """Test error handling in handlers"""
    
    @pytest.fixture
    def mock_message(self):
        """Create a mock message"""
        message = Mock(spec=types.Message)
        message.from_user.id = 12345
        message.answer = AsyncMock()
        return message
    
    @pytest.mark.asyncio
    async def test_start_command_error(self, mock_message, mock_state):
        """Test start command error handling"""
        with patch('handlers.start.get_user', side_effect=Exception("Database error")):
            await start_command(mock_message, mock_state)
            
            mock_message.answer.assert_called_once()
            # Should handle error gracefully
    
    @pytest.mark.asyncio
    async def test_show_balance_error(self, mock_message):
        """Test balance display error handling"""
        with patch('handlers.menu.is_user_approved', return_value=True), \
             patch('handlers.menu.get_balance', side_effect=Exception("Sheets error")):
            
            await show_balance(mock_message)
            
            mock_message.answer.assert_called_once()
            # Should handle error gracefully

# Integration tests
class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_user_registration_flow(self):
        """Test complete user registration flow"""
        # This would test the full flow from /start to approval
        # Implementation would depend on specific integration requirements
        pass
    
    @pytest.mark.asyncio
    async def test_admin_approval_flow(self):
        """Test complete admin approval flow"""
        # This would test the full flow from registration to approval
        # Implementation would depend on specific integration requirements
        pass



