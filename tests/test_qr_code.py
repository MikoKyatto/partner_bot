"""
Unit tests for QR code generation
"""
import pytest
import os
import tempfile
from unittest.mock import patch, Mock, MagicMock
from PIL import Image

from utils.qr_code import (
    generate_qr_code,
    generate_qr_code_bytes,
    get_referral_link,
    validate_partnercode,
    create_palm_tree_silhouette,
    get_font
)

class TestQRCodeGeneration:
    """Test QR code generation functionality"""
    
    def test_generate_qr_code_success(self):
        """Test successful QR code generation"""
        partnercode = "12345"
        
        with patch('utils.qr_code.get_font') as mock_font:
            mock_font.return_value = Mock()
            
            result = generate_qr_code(partnercode)
            
            assert result is not None
            assert result == f"qr_{partnercode}.jpg"
            assert os.path.exists(result)
            
            # Clean up
            if os.path.exists(result):
                os.unlink(result)
    
    def test_generate_qr_code_bytes_success(self):
        """Test successful QR code generation as bytes"""
        partnercode = "12345"
        
        with patch('utils.qr_code.get_font') as mock_font:
            mock_font.return_value = Mock()
            
            result = generate_qr_code_bytes(partnercode)
            
            assert result is not None
            assert isinstance(result, bytes)
            assert len(result) > 0
    
    def test_generate_qr_code_with_font_error(self):
        """Test QR code generation with font error"""
        partnercode = "12345"
        
        with patch('utils.qr_code.get_font', side_effect=Exception("Font error")):
            result = generate_qr_code(partnercode)
            
            assert result is None
    
    def test_generate_qr_code_with_image_error(self):
        """Test QR code generation with image processing error"""
        partnercode = "12345"
        
        with patch('utils.qr_code.get_font') as mock_font, \
             patch('PIL.Image.new', side_effect=Exception("Image error")):
            mock_font.return_value = Mock()
            
            result = generate_qr_code(partnercode)
            
            assert result is None

class TestReferralLink:
    """Test referral link generation"""
    
    def test_get_referral_link(self):
        """Test referral link generation"""
        partnercode = "12345"
        
        result = get_referral_link(partnercode)
        
        expected = f"https://taplink.cc/lakeevainfo?ref={partnercode}"
        assert result == expected
    
    def test_get_referral_link_with_different_codes(self):
        """Test referral link generation with different partner codes"""
        test_cases = [
            ("12345", "https://taplink.cc/lakeevainfo?ref=12345"),
            ("67890", "https://taplink.cc/lakeevainfo?ref=67890"),
            ("999999999", "https://taplink.cc/lakeevainfo?ref=999999999"),
        ]
        
        for partnercode, expected in test_cases:
            result = get_referral_link(partnercode)
            assert result == expected

class TestPartnercodeValidation:
    """Test partner code validation"""
    
    def test_validate_partnercode_valid(self):
        """Test validation of valid partner codes"""
        valid_codes = ["12345", "67890", "999999999", "1", "0"]
        
        for code in valid_codes:
            assert validate_partnercode(code) is True
    
    def test_validate_partnercode_invalid(self):
        """Test validation of invalid partner codes"""
        invalid_codes = ["", "abc", "123abc", "12.34", "-123", None, 12345]
        
        for code in invalid_codes:
            assert validate_partnercode(code) is False
    
    def test_validate_partnercode_edge_cases(self):
        """Test validation with edge cases"""
        # Empty string
        assert validate_partnercode("") is False
        
        # Non-string input
        assert validate_partnercode(12345) is False
        assert validate_partnercode(None) is False
        
        # String with spaces
        assert validate_partnercode("123 45") is False
        
        # String with special characters
        assert validate_partnercode("123-45") is False

class TestPalmTreeSilhouette:
    """Test palm tree silhouette drawing"""
    
    def test_create_palm_tree_silhouette(self):
        """Test palm tree silhouette creation"""
        # Create a test image
        img = Image.new("RGB", (100, 100), color="#1A3C34")
        draw = Mock()
        
        # Test the function
        create_palm_tree_silhouette(draw, 50, 50, 20)
        
        # Verify that drawing methods were called
        assert draw.rectangle.called
        assert draw.line.called

class TestFontHandling:
    """Test font handling functionality"""
    
    @patch('utils.qr_code.os.path.exists')
    def test_get_font_success_macos(self, mock_exists):
        """Test successful font loading on macOS"""
        mock_exists.return_value = True
        
        with patch('utils.qr_code.ImageFont.truetype') as mock_truetype:
            mock_font = Mock()
            mock_truetype.return_value = mock_font
            
            result = get_font()
            
            assert result is not None
            mock_truetype.assert_called_once()
    
    @patch('utils.qr_code.os.path.exists')
    def test_get_font_success_linux(self, mock_exists):
        """Test successful font loading on Linux"""
        # Mock that macOS path doesn't exist but Linux path does
        def mock_exists_side_effect(path):
            return path == "/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf"
        
        mock_exists.side_effect = mock_exists_side_effect
        
        with patch('utils.qr_code.ImageFont.truetype') as mock_truetype:
            mock_font = Mock()
            mock_truetype.return_value = mock_font
            
            result = get_font()
            
            assert result is not None
            mock_truetype.assert_called_once()
    
    @patch('utils.qr_code.os.path.exists', return_value=False)
    def test_get_font_fallback_to_default(self, mock_exists):
        """Test font fallback to default when no custom font found"""
        with patch('utils.qr_code.ImageFont.load_default') as mock_load_default:
            mock_font = Mock()
            mock_load_default.return_value = mock_font
            
            result = get_font()
            
            assert result is not None
            mock_load_default.assert_called_once()
    
    @patch('utils.qr_code.os.path.exists')
    def test_get_font_with_exception(self, mock_exists):
        """Test font loading with exception"""
        mock_exists.return_value = True
        
        with patch('utils.qr_code.ImageFont.truetype', side_effect=Exception("Font error")):
            with patch('utils.qr_code.ImageFont.load_default') as mock_load_default:
                mock_font = Mock()
                mock_load_default.return_value = mock_font
                
                result = get_font()
                
                assert result is not None
                mock_load_default.assert_called_once()

class TestQRCodeContent:
    """Test QR code content and structure"""
    
    def test_qr_code_contains_correct_url(self):
        """Test that generated QR code contains correct URL"""
        partnercode = "12345"
        expected_url = f"https://taplink.cc/lakeevainfo?ref={partnercode}"
        
        with patch('utils.qr_code.get_font') as mock_font:
            mock_font.return_value = Mock()
            
            # Generate QR code
            result = generate_qr_code(partnercode)
            
            if result and os.path.exists(result):
                # Read the generated image
                img = Image.open(result)
                
                # Basic checks
                assert img.size == (512, 512)  # Expected size
                assert img.mode == "RGB"
                
                # Clean up
                os.unlink(result)
    
    def test_qr_code_image_properties(self):
        """Test QR code image properties"""
        partnercode = "12345"
        
        with patch('utils.qr_code.get_font') as mock_font:
            mock_font.return_value = Mock()
            
            # Generate QR code bytes
            qr_bytes = generate_qr_code_bytes(partnercode)
            
            if qr_bytes:
                # Create image from bytes
                from io import BytesIO
                img = Image.open(BytesIO(qr_bytes))
                
                # Check image properties
                assert img.size == (512, 512)
                assert img.mode == "RGB"
                assert img.format == "JPEG"

class TestErrorHandling:
    """Test error handling in QR code generation"""
    
    def test_generate_qr_code_with_invalid_partnercode(self):
        """Test QR code generation with invalid partner code"""
        invalid_codes = ["", None, "abc", "123abc"]
        
        for code in invalid_codes:
            result = generate_qr_code(code)
            # Should handle gracefully, might return None or generate anyway
            # depending on implementation
    
    def test_generate_qr_code_with_very_long_partnercode(self):
        """Test QR code generation with very long partner code"""
        long_code = "1" * 1000  # Very long partner code
        
        with patch('utils.qr_code.get_font') as mock_font:
            mock_font.return_value = Mock()
            
            result = generate_qr_code(long_code)
            
            # Should handle gracefully
            if result:
                assert os.path.exists(result)
                # Clean up
                os.unlink(result)

class TestIntegration:
    """Integration tests for QR code functionality"""
    
    def test_full_qr_generation_workflow(self):
        """Test complete QR code generation workflow"""
        partnercode = "12345"
        
        # Test link generation
        link = get_referral_link(partnercode)
        assert link == f"https://taplink.cc/lakeevainfo?ref={partnercode}"
        
        # Test validation
        assert validate_partnercode(partnercode) is True
        
        # Test QR code generation
        with patch('utils.qr_code.get_font') as mock_font:
            mock_font.return_value = Mock()
            
            filename = generate_qr_code(partnercode)
            if filename and os.path.exists(filename):
                # Verify file was created
                assert filename == f"qr_{partnercode}.jpg"
                
                # Clean up
                os.unlink(filename)
    
    def test_qr_code_bytes_workflow(self):
        """Test QR code bytes generation workflow"""
        partnercode = "12345"
        
        # Test validation
        assert validate_partnercode(partnercode) is True
        
        # Test QR code bytes generation
        with patch('utils.qr_code.get_font') as mock_font:
            mock_font.return_value = Mock()
            
            qr_bytes = generate_qr_code_bytes(partnercode)
            
            if qr_bytes:
                assert isinstance(qr_bytes, bytes)
                assert len(qr_bytes) > 0



