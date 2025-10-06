"""
Google Sheets integration for Lethai Concierge Referral Bot
"""
import asyncio
import logging
from typing import Optional

import gspread
from gspread.exceptions import APIError, SpreadsheetNotFound, WorksheetNotFound
from google.auth.exceptions import DefaultCredentialsError
from google.oauth2.service_account import Credentials

from config import config

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_client() -> gspread.Client:
    """Get authorized gspread client"""
    try:
        credentials = Credentials.from_service_account_file(
            config.CREDENTIALS_PATH,
            scopes=SCOPES
        )
        return gspread.authorize(credentials)
    except FileNotFoundError:
        logger.error(f"Credentials file not found: {config.CREDENTIALS_PATH}")
        raise
    except DefaultCredentialsError as e:
        logger.error(f"Credentials error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating client: {e}")
        raise

def _test_connection_sync() -> bool:
    """Synchronous test of Google Sheets connection"""
    try:
        client = get_client()
        sheet = client.open_by_key(config.SHEETS_ID)
        worksheet = sheet.worksheet(config.SHEET_NAME)
        worksheet.cell(1, 1).value  # Test read access
        return True
    except (SpreadsheetNotFound, WorksheetNotFound):
        logger.error("Spreadsheet or worksheet not found")
        return False
    except APIError as e:
        logger.error(f"API error: {e}")
        return False
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False

def test_connection() -> bool:
    """Test Google Sheets connection (synchronous wrapper for backwards compatibility)"""
    return _test_connection_sync()

async def test_connection_async() -> bool:
    """Test Google Sheets connection (async version)"""
    return await asyncio.to_thread(_test_connection_sync)

def _safe_value(val) -> str:
    """Convert value to string, return '-' if empty"""
    if val is None:
        return "-"
    val_str = str(val).strip()
    return val_str if val_str else "-"

def _add_partnercode_sync(
    partnercode: str,
    name: Optional[str] = None,
    contact: Optional[str] = None,
    username: Optional[str] = None,
    referral_source: Optional[str] = None
) -> bool:
    """
    Synchronous add partner data to Google Sheets
    
    Appends row with: [Partner ID, Name, Contact, Telegram Username, Referral Source]
    """
    try:
        client = get_client()
        sheet = client.open_by_key(config.SHEETS_ID)
        worksheet = sheet.worksheet(config.SHEET_NAME)
        
        # Find if partnercode exists
        cell = worksheet.find(partnercode, in_column=1)
        if cell:
            logger.info(f"Partnercode {partnercode} already exists in row {cell.row}")
            return True
        
        # Format username with @ prefix if not present
        formatted_username = _safe_value(username)
        if formatted_username != "-" and not formatted_username.startswith("@"):
            formatted_username = f"@{formatted_username}"
        
        # Build row data: [Partner ID, Name, Contact, Username, Referral Source]
        row_data = [
            str(partnercode),
            _safe_value(name),
            _safe_value(contact),
            formatted_username,
            _safe_value(referral_source)
        ]
        
        # Append row
        worksheet.append_row(row_data, value_input_option="USER_ENTERED")
        logger.info(f"Added partner {partnercode} with full data to Google Sheets")
        return True
        
    except Exception as e:
        logger.error(f"Error adding partner {partnercode}: {e}")
        return False

def add_partnercode(
    partnercode: str,
    name: Optional[str] = None,
    contact: Optional[str] = None,
    username: Optional[str] = None,
    referral_source: Optional[str] = None
) -> bool:
    """
    Add partner data to Google Sheets (synchronous wrapper)
    
    Args:
        partnercode: Partner ID (Telegram user ID)
        name: Partner name
        contact: Phone or email
        username: Telegram username
        referral_source: Referral code if referred by another user
        
    Returns:
        bool: True if successful
    """
    return _add_partnercode_sync(partnercode, name, contact, username, referral_source)

async def add_partnercode_async(
    partnercode: str,
    name: Optional[str] = None,
    contact: Optional[str] = None,
    username: Optional[str] = None,
    referral_source: Optional[str] = None
) -> bool:
    """Add partner data to Google Sheets (async version)"""
    return await asyncio.to_thread(_add_partnercode_sync, partnercode, name, contact, username, referral_source)

def _get_balance_sync(partnercode: str) -> float:
    """Synchronous get balance for partnercode"""
    try:
        client = get_client()
        sheet = client.open_by_key(config.SHEETS_ID)
        worksheet = sheet.worksheet(config.SHEET_NAME)
        
        # Find row
        cell = worksheet.find(partnercode, in_column=1)
        if not cell:
            logger.warning(f"Partnercode {partnercode} not found")
            return 0.0
        
        # Get row values
        row_values = worksheet.row_values(cell.row)
        if not row_values:
            return 0.0
        
        # Sum numeric values skipping first column
        balance = 0.0
        for value in row_values[1:]:
            try:
                balance += float(value)
            except ValueError:
                continue
        
        logger.info(f"Balance for {partnercode}: {balance}")
        return balance
        
    except Exception as e:
        logger.error(f"Error getting balance for {partnercode}: {e}")
        return 0.0

def get_balance(partnercode: str) -> float:
    """Get balance for partnercode (synchronous wrapper for backwards compatibility)"""
    return _get_balance_sync(partnercode)

async def get_balance_async(partnercode: str) -> float:
    """Get balance for partnercode (async version)"""
    return await asyncio.to_thread(_get_balance_sync, partnercode)

#def _get_worksheet_info_sync() -> dict:
    """Synchronous get worksheet info"""
    try:
        client = get_client()
        sheet = client.open_by_key(config.SHEETS_ID)
        worksheet = sheet.worksheet(config.SHEET_NAME)
        
        all_values = worksheet.get_all_values()
        row_count = len(all_values)
        
        # Count partnercodes (non-empty first column cells, excluding header)
        partnercode_count = sum(1 for row in all_values[1:] if row and row[0])
        
        return {
            'row_count': row_count,
            'partnercode_count': partnercode_count
        }
    except Exception as e:
        logger.error(f"Error getting worksheet info: {e}")
        return {}
def _get_balance_sync(partnercode: str) -> float:
    """Synchronous get balance for partnercode, skipping first 4 columns"""
    try:
        client = get_client()
        sheet = client.open_by_key(config.SHEETS_ID)
        worksheet = sheet.worksheet(config.SHEET_NAME)
        
        # Find row
        cell = worksheet.find(partnercode, in_column=1)
        if not cell:
            logger.warning(f"Partnercode {partnercode} not found")
            return 0.0
        
        # Get row values
        row_values = worksheet.row_values(cell.row)
        if not row_values:
            return 0.0
        
        # Sum numeric values starting from 5th column (index 4)
        balance = 0.0
        for value in row_values[4:]:
            try:
                balance += float(value)
            except ValueError:
                continue
        
        logger.info(f"Balance for {partnercode}: {balance}")
        return balance
        
    except Exception as e:
        logger.error(f"Error getting balance for {partnercode}: {e}")
        return 0.0
        
def get_worksheet_info() -> dict:
    """Get worksheet info (synchronous wrapper for backwards compatibility)"""
    return _get_worksheet_info_sync()

async def get_worksheet_info_async() -> dict:
    """Get worksheet info (async version)"""
    return await asyncio.to_thread(_get_worksheet_info_sync)

if __name__ == "__main__":
    # Test functions
    print("Testing connection...")
    print(f"Connection successful: {test_connection()}")
    
    # Example usage
    test_code = "123456789"
    print(f"Adding test partnercode: {add_partnercode(test_code)}")
    print(f"Balance: {get_balance(test_code)}")
