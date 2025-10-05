"""
Unit tests for database operations
"""
import pytest
import sqlite3
import os
import tempfile
from unittest.mock import patch, Mock

from utils.database import (
    init_database,
    save_user,
    get_user,
    update_user_approval,
    get_pending_users,
    get_approved_users,
    is_user_approved,
    delete_user
)

class TestDatabaseInitialization:
    """Test database initialization"""
    
    def test_init_database_success(self):
        """Test successful database initialization"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            with patch('utils.database.DATABASE_PATH', db_path):
                init_database()
                
                # Check if database was created
                assert os.path.exists(db_path)
                
                # Check if table was created
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
                    result = cursor.fetchone()
                    assert result is not None
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_init_database_error(self):
        """Test database initialization with error"""
        with patch('utils.database.DATABASE_PATH', '/invalid/path/database.db'):
            with pytest.raises(sqlite3.Error):
                init_database()

class TestUserOperations:
    """Test user database operations"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        with patch('utils.database.DATABASE_PATH', db_path):
            init_database()
            yield db_path
        
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_save_user_success(self, temp_db):
        """Test successful user saving"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            result = save_user(12345, "Test User", "+1234567890", False)
            
            assert result is True
            
            # Verify user was saved
            user = get_user(12345)
            assert user is not None
            assert user['telegram_id'] == 12345
            assert user['name'] == "Test User"
            assert user['phone'] == "+1234567890"
            assert user['approved'] is False
    
    def test_save_user_duplicate(self, temp_db):
        """Test saving duplicate user"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            # Save user first time
            result1 = save_user(12345, "Test User", "+1234567890", False)
            assert result1 is True
            
            # Try to save same user again
            result2 = save_user(12345, "Another User", "+0987654321", True)
            assert result2 is False
    
    def test_get_user_success(self, temp_db):
        """Test successful user retrieval"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            # Save user first
            save_user(12345, "Test User", "+1234567890", False)
            
            # Get user
            user = get_user(12345)
            
            assert user is not None
            assert user['telegram_id'] == 12345
            assert user['name'] == "Test User"
            assert user['phone'] == "+1234567890"
            assert user['approved'] is False
    
    def test_get_user_not_found(self, temp_db):
        """Test getting non-existent user"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            user = get_user(99999)
            
            assert user is None
    
    def test_update_user_approval_success(self, temp_db):
        """Test successful user approval update"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            # Save user first
            save_user(12345, "Test User", "+1234567890", False)
            
            # Update approval
            result = update_user_approval(12345, True)
            
            assert result is True
            
            # Verify update
            user = get_user(12345)
            assert user['approved'] is True
            assert user['approved_at'] is not None
    
    def test_update_user_approval_not_found(self, temp_db):
        """Test updating approval for non-existent user"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            result = update_user_approval(99999, True)
            
            assert result is False
    
    def test_get_pending_users(self, temp_db):
        """Test getting pending users"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            # Save multiple users with different approval statuses
            save_user(12345, "User 1", "+1111111111", False)
            save_user(12346, "User 2", "+2222222222", True)
            save_user(12347, "User 3", "+3333333333", False)
            
            pending_users = get_pending_users()
            
            assert len(pending_users) == 2
            assert all(user['approved'] is False for user in pending_users)
            assert any(user['telegram_id'] == 12345 for user in pending_users)
            assert any(user['telegram_id'] == 12347 for user in pending_users)
    
    def test_get_approved_users(self, temp_db):
        """Test getting approved users"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            # Save multiple users with different approval statuses
            save_user(12345, "User 1", "+1111111111", False)
            save_user(12346, "User 2", "+2222222222", True)
            save_user(12347, "User 3", "+3333333333", True)
            
            approved_users = get_approved_users()
            
            assert len(approved_users) == 2
            assert all(user['approved'] is True for user in approved_users)
            assert any(user['telegram_id'] == 12346 for user in approved_users)
            assert any(user['telegram_id'] == 12347 for user in approved_users)
    
    def test_is_user_approved_true(self, temp_db):
        """Test checking approved user"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            save_user(12345, "Test User", "+1234567890", True)
            
            result = is_user_approved(12345)
            
            assert result is True
    
    def test_is_user_approved_false(self, temp_db):
        """Test checking unapproved user"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            save_user(12345, "Test User", "+1234567890", False)
            
            result = is_user_approved(12345)
            
            assert result is False
    
    def test_is_user_approved_not_found(self, temp_db):
        """Test checking non-existent user"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            result = is_user_approved(99999)
            
            assert result is False
    
    def test_delete_user_success(self, temp_db):
        """Test successful user deletion"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            # Save user first
            save_user(12345, "Test User", "+1234567890", False)
            
            # Delete user
            result = delete_user(12345)
            
            assert result is True
            
            # Verify deletion
            user = get_user(12345)
            assert user is None
    
    def test_delete_user_not_found(self, temp_db):
        """Test deleting non-existent user"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            result = delete_user(99999)
            
            assert result is False

class TestErrorHandling:
    """Test error handling in database operations"""
    
    def test_save_user_database_error(self):
        """Test user saving with database error"""
        with patch('utils.database.DATABASE_PATH', '/invalid/path/database.db'):
            result = save_user(12345, "Test User", "+1234567890", False)
            
            assert result is False
    
    def test_get_user_database_error(self):
        """Test user retrieval with database error"""
        with patch('utils.database.DATABASE_PATH', '/invalid/path/database.db'):
            user = get_user(12345)
            
            assert user is None
    
    def test_update_user_approval_database_error(self):
        """Test user approval update with database error"""
        with patch('utils.database.DATABASE_PATH', '/invalid/path/database.db'):
            result = update_user_approval(12345, True)
            
            assert result is False
    
    def test_get_pending_users_database_error(self):
        """Test getting pending users with database error"""
        with patch('utils.database.DATABASE_PATH', '/invalid/path/database.db'):
            users = get_pending_users()
            
            assert users == []
    
    def test_get_approved_users_database_error(self):
        """Test getting approved users with database error"""
        with patch('utils.database.DATABASE_PATH', '/invalid/path/database.db'):
            users = get_approved_users()
            
            assert users == []

class TestDataIntegrity:
    """Test data integrity and edge cases"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        with patch('utils.database.DATABASE_PATH', db_path):
            init_database()
            yield db_path
        
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_save_user_with_special_characters(self, temp_db):
        """Test saving user with special characters in name"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            result = save_user(12345, "Тест Пользователь 🏝️", "+1234567890", False)
            
            assert result is True
            
            user = get_user(12345)
            assert user['name'] == "Тест Пользователь 🏝️"
    
    def test_save_user_with_long_name(self, temp_db):
        """Test saving user with very long name"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            long_name = "A" * 1000  # Very long name
            result = save_user(12345, long_name, "+1234567890", False)
            
            assert result is True
            
            user = get_user(12345)
            assert user['name'] == long_name
    
    def test_save_user_with_international_phone(self, temp_db):
        """Test saving user with international phone number"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            result = save_user(12345, "Test User", "+7-123-456-7890", False)
            
            assert result is True
            
            user = get_user(12345)
            assert user['phone'] == "+7-123-456-7890"
    
    def test_multiple_users_order(self, temp_db):
        """Test that users are returned in correct order"""
        with patch('utils.database.DATABASE_PATH', temp_db):
            # Save users in specific order
            save_user(12345, "User 1", "+1111111111", False)
            save_user(12346, "User 2", "+2222222222", False)
            save_user(12347, "User 3", "+3333333333", False)
            
            pending_users = get_pending_users()
            
            # Should be ordered by created_at ASC
            assert len(pending_users) == 3
            assert pending_users[0]['telegram_id'] == 12345
            assert pending_users[1]['telegram_id'] == 12346
            assert pending_users[2]['telegram_id'] == 12347



