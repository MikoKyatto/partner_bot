"""
Unit tests for Google Sheets integration
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import gspread

from utils.sheets import (
    get_sheets_client,
    get_worksheet,
    get_balance,
    add_partnercode,
    update_balance,
    get_all_partnercodes,
    test_connection
)

class TestSheetsClient:
    """Test Google Sheets client functionality"""
    
    @patch('utils.sheets.Credentials.from_service_account_file')
    @patch('utils.sheets.gspread.authorize')
    def test_get_sheets_client_success(self, mock_authorize, mock_creds):
        """Test successful client creation"""
        mock_creds.return_value = Mock()
        mock_authorize.return_value = Mock()
        
        client = get_sheets_client()
        
        assert client is not None
        mock_creds.assert_called_once()
        mock_authorize.assert_called_once()
    
    @patch('utils.sheets.os.path.exists', return_value=False)
    def test_get_sheets_client_no_credentials(self, mock_exists):
        """Test client creation with missing credentials file"""
        client = get_sheets_client()
        
        assert client is None
    
    @patch('utils.sheets.Credentials.from_service_account_file')
    def test_get_sheets_client_auth_error(self, mock_creds):
        """Test client creation with authentication error"""
        mock_creds.side_effect = Exception("Auth error")
        
        client = get_sheets_client()
        
        assert client is None

class TestWorksheet:
    """Test worksheet operations"""
    
    @patch('utils.sheets.get_sheets_client')
    def test_get_worksheet_success(self, mock_get_client):
        """Test successful worksheet access"""
        mock_client = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        
        mock_get_client.return_value = mock_client
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        worksheet = get_worksheet()
        
        assert worksheet is not None
        mock_client.open_by_key.assert_called_once()
        mock_spreadsheet.worksheet.assert_called_once()
    
    @patch('utils.sheets.get_sheets_client', return_value=None)
    def test_get_worksheet_no_client(self, mock_get_client):
        """Test worksheet access with no client"""
        worksheet = get_worksheet()
        
        assert worksheet is None

class TestBalanceCalculation:
    """Test balance calculation functionality"""
    
    @patch('utils.sheets.get_worksheet')
    def test_get_balance_success(self, mock_get_worksheet):
        """Test successful balance retrieval"""
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.return_value = [
            ['partnercode', 'amount1', 'amount2', 'amount3'],
            ['12345', '100.50', '200.75', '50.25'],
            ['67890', '300.00', '150.00', '']
        ]
        mock_get_worksheet.return_value = mock_worksheet
        
        balance = get_balance('12345')
        
        assert balance == 351.50  # 100.50 + 200.75 + 50.25
    
    @patch('utils.sheets.get_worksheet')
    def test_get_balance_user_not_found(self, mock_get_worksheet):
        """Test balance retrieval for non-existent user"""
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.return_value = [
            ['partnercode', 'amount1', 'amount2'],
            ['12345', '100.50', '200.75']
        ]
        mock_get_worksheet.return_value = mock_worksheet
        
        balance = get_balance('99999')
        
        assert balance == 0.0
    
    @patch('utils.sheets.get_worksheet')
    def test_get_balance_with_non_numeric_values(self, mock_get_worksheet):
        """Test balance calculation with non-numeric values"""
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.return_value = [
            ['partnercode', 'amount1', 'text', 'amount2', ''],
            ['12345', '100.50', 'some text', '200.75', '']
        ]
        mock_get_worksheet.return_value = mock_worksheet
        
        balance = get_balance('12345')
        
        assert balance == 301.25  # Only numeric values: 100.50 + 200.75
    
    @patch('utils.sheets.get_worksheet')
    def test_get_balance_with_negative_values(self, mock_get_worksheet):
        """Test balance calculation with negative values"""
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.return_value = [
            ['partnercode', 'amount1', 'amount2'],
            ['12345', '100.50', '-50.25']
        ]
        mock_get_worksheet.return_value = mock_worksheet
        
        balance = get_balance('12345')
        
        assert balance == 50.25  # 100.50 + (-50.25)
    
    @patch('utils.sheets.get_worksheet')
    def test_get_balance_with_comma_decimal_separator(self, mock_get_worksheet):
        """Test balance calculation with comma decimal separator"""
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.return_value = [
            ['partnercode', 'amount1', 'amount2'],
            ['12345', '100,50', '200,75']
        ]
        mock_get_worksheet.return_value = mock_worksheet
        
        balance = get_balance('12345')
        
        assert balance == 301.25  # 100.50 + 200.75
    
    @patch('utils.sheets.get_worksheet', return_value=None)
    def test_get_balance_no_worksheet(self, mock_get_worksheet):
        """Test balance retrieval with no worksheet access"""
        balance = get_balance('12345')
        
        assert balance == 0.0

class TestPartnercodeManagement:
    """Test partnercode management functionality"""
    
    @patch('utils.sheets.get_worksheet')
    def test_add_partnercode_success(self, mock_get_worksheet):
        """Test successful partnercode addition"""
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.return_value = [
            ['partnercode', 'date', 'action'],
            ['12345', '2024-01-01', 'signup']
        ]
        mock_worksheet.append_row = Mock()
        mock_get_worksheet.return_value = mock_worksheet
        
        result = add_partnercode('67890')
        
        assert result is True
        mock_worksheet.append_row.assert_called_once()
    
    @patch('utils.sheets.get_worksheet')
    def test_add_partnercode_already_exists(self, mock_get_worksheet):
        """Test adding existing partnercode"""
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.return_value = [
            ['partnercode', 'date', 'action'],
            ['12345', '2024-01-01', 'signup']
        ]
        mock_get_worksheet.return_value = mock_worksheet
        
        result = add_partnercode('12345')
        
        assert result is True  # Should return True for existing partnercode
    
    @patch('utils.sheets.get_worksheet', return_value=None)
    def test_add_partnercode_no_worksheet(self, mock_get_worksheet):
        """Test partnercode addition with no worksheet access"""
        result = add_partnercode('12345')
        
        assert result is False
    
    @patch('utils.sheets.get_worksheet')
    def test_get_all_partnercodes(self, mock_get_worksheet):
        """Test retrieving all partnercodes"""
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.return_value = [
            ['partnercode', 'date', 'action'],
            ['12345', '2024-01-01', 'signup'],
            ['67890', '2024-01-02', 'signup'],
            ['', '2024-01-03', 'signup']  # Empty partnercode should be skipped
        ]
        mock_get_worksheet.return_value = mock_worksheet
        
        partnercodes = get_all_partnercodes()
        
        assert partnercodes == ['12345', '67890']
    
    @patch('utils.sheets.get_worksheet', return_value=None)
    def test_get_all_partnercodes_no_worksheet(self, mock_get_worksheet):
        """Test retrieving partnercodes with no worksheet access"""
        partnercodes = get_all_partnercodes()
        
        assert partnercodes == []

class TestBalanceUpdate:
    """Test balance update functionality"""
    
    @patch('utils.sheets.get_worksheet')
    def test_update_balance_success(self, mock_get_worksheet):
        """Test successful balance update"""
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.return_value = [
            ['partnercode', 'amount1', 'amount2'],
            ['12345', '100.50', '200.75']
        ]
        mock_worksheet.row_values.return_value = ['12345', '100.50', '200.75']
        mock_worksheet.update_cell = Mock()
        mock_get_worksheet.return_value = mock_worksheet
        
        result = update_balance('12345', 50.25, 'referral')
        
        assert result is True
        mock_worksheet.update_cell.assert_called_once()
    
    @patch('utils.sheets.get_worksheet')
    def test_update_balance_user_not_found(self, mock_get_worksheet):
        """Test balance update for non-existent user"""
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.return_value = [
            ['partnercode', 'amount1', 'amount2'],
            ['12345', '100.50', '200.75']
        ]
        mock_get_worksheet.return_value = mock_worksheet
        
        result = update_balance('99999', 50.25, 'referral')
        
        assert result is False
    
    @patch('utils.sheets.get_worksheet', return_value=None)
    def test_update_balance_no_worksheet(self, mock_get_worksheet):
        """Test balance update with no worksheet access"""
        result = update_balance('12345', 50.25, 'referral')
        
        assert result is False

class TestConnectionTest:
    """Test connection testing functionality"""
    
    @patch('utils.sheets.get_worksheet')
    def test_test_connection_success(self, mock_get_worksheet):
        """Test successful connection test"""
        mock_worksheet = Mock()
        mock_worksheet.get.return_value = 'test'
        mock_get_worksheet.return_value = mock_worksheet
        
        result = test_connection()
        
        assert result is True
        mock_worksheet.get.assert_called_once_with('A1')
    
    @patch('utils.sheets.get_worksheet', return_value=None)
    def test_test_connection_failure(self, mock_get_worksheet):
        """Test connection test failure"""
        result = test_connection()
        
        assert result is False
    
    @patch('utils.sheets.get_worksheet')
    def test_test_connection_exception(self, mock_get_worksheet):
        """Test connection test with exception"""
        mock_worksheet = Mock()
        mock_worksheet.get.side_effect = Exception("Connection error")
        mock_get_worksheet.return_value = mock_worksheet
        
        result = test_connection()
        
        assert result is False

class TestErrorHandling:
    """Test error handling in sheets operations"""
    
    @patch('utils.sheets.get_worksheet')
    def test_get_balance_with_exception(self, mock_get_worksheet):
        """Test balance retrieval with exception"""
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.side_effect = Exception("Sheets error")
        mock_get_worksheet.return_value = mock_worksheet
        
        balance = get_balance('12345')
        
        assert balance == 0.0
    
    @patch('utils.sheets.get_worksheet')
    def test_add_partnercode_with_exception(self, mock_get_worksheet):
        """Test partnercode addition with exception"""
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.side_effect = Exception("Sheets error")
        mock_get_worksheet.return_value = mock_worksheet
        
        result = add_partnercode('12345')
        
        assert result is False

# Integration tests
class TestIntegration:
    """Integration tests for sheets functionality"""
    
    @pytest.mark.asyncio
    async def test_full_balance_workflow(self):
        """Test complete balance workflow"""
        # This would test the full workflow from adding partnercode to checking balance
        # Implementation would depend on specific integration requirements
        pass
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent operations on sheets"""
        # This would test concurrent access to sheets
        # Implementation would depend on specific integration requirements
        pass



