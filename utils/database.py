"""
Database utilities for SQLite operations
"""
import sqlite3
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

DATABASE_PATH = "users.db"

def init_database():
    """Initialize the database and create tables if they don't exist"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    approved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    approved_at TIMESTAMP NULL
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
            
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise

def save_user(telegram_id: int, name: str, phone: str, approved: bool = False) -> bool:
    """
    Save a new user to the database
    
    Args:
        telegram_id: User's Telegram ID
        name: User's name
        phone: User's phone number
        approved: Whether the user is approved
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (telegram_id,))
            if cursor.fetchone():
                logger.warning(f"User {telegram_id} already exists")
                return False
            
            # Insert new user
            cursor.execute("""
                INSERT INTO users (telegram_id, name, phone, approved)
                VALUES (?, ?, ?, ?)
            """, (telegram_id, name, phone, approved))
            
            conn.commit()
            logger.info(f"User {telegram_id} saved successfully")
            return True
            
    except sqlite3.Error as e:
        logger.error(f"Error saving user {telegram_id}: {e}")
        return False

def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
    """
    Get user information by Telegram ID
    
    Args:
        telegram_id: User's Telegram ID
    
    Returns:
        dict: User information or None if not found
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT telegram_id, name, phone, approved, created_at, approved_at
                FROM users WHERE telegram_id = ?
            """, (telegram_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
    except sqlite3.Error as e:
        logger.error(f"Error getting user {telegram_id}: {e}")
        return None

def update_user_approval(telegram_id: int, approved: bool) -> bool:
    """
    Update user approval status
    
    Args:
        telegram_id: User's Telegram ID
        approved: New approval status
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            approved_at = datetime.now().isoformat() if approved else None
            
            cursor.execute("""
                UPDATE users 
                SET approved = ?, approved_at = ?
                WHERE telegram_id = ?
            """, (approved, approved_at, telegram_id))
            
            if cursor.rowcount == 0:
                logger.warning(f"User {telegram_id} not found for approval update")
                return False
            
            conn.commit()
            logger.info(f"User {telegram_id} approval status updated to {approved}")
            return True
            
    except sqlite3.Error as e:
        logger.error(f"Error updating user {telegram_id} approval: {e}")
        return False

def get_pending_users() -> List[Dict[str, Any]]:
    """
    Get all users pending approval
    
    Returns:
        list: List of pending users
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT telegram_id, name, phone, created_at
                FROM users 
                WHERE approved = FALSE
                ORDER BY created_at ASC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
    except sqlite3.Error as e:
        logger.error(f"Error getting pending users: {e}")
        return []

def get_approved_users() -> List[Dict[str, Any]]:
    """
    Get all approved users
    
    Returns:
        list: List of approved users
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT telegram_id, name, phone, approved_at
                FROM users 
                WHERE approved = TRUE
                ORDER BY approved_at ASC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
    except sqlite3.Error as e:
        logger.error(f"Error getting approved users: {e}")
        return []

def is_user_approved(telegram_id: int) -> bool:
    """
    Check if user is approved
    
    Args:
        telegram_id: User's Telegram ID
    
    Returns:
        bool: True if approved, False otherwise
    """
    user = get_user(telegram_id)
    return user['approved'] if user else False

def delete_user(telegram_id: int) -> bool:
    """
    Delete a user from the database
    
    Args:
        telegram_id: User's Telegram ID
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
            
            if cursor.rowcount == 0:
                logger.warning(f"User {telegram_id} not found for deletion")
                return False
            
            conn.commit()
            logger.info(f"User {telegram_id} deleted successfully")
            return True
            
    except sqlite3.Error as e:
        logger.error(f"Error deleting user {telegram_id}: {e}")
        return False



