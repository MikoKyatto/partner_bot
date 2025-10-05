"""
Health check utilities for the bot
"""
import logging
import os
import sqlite3
from typing import Dict, Any, List
from datetime import datetime

from utils.sheets import test_connection
from utils.database import get_approved_users, get_pending_users

logger = logging.getLogger(__name__)

class HealthChecker:
    """Health check utilities"""
    
    @staticmethod
    def check_database() -> Dict[str, Any]:
        """Check database health"""
        try:
            db_path = 'users.db'
            if not os.path.exists(db_path):
                return {
                    'status': 'error',
                    'message': 'Database file not found',
                    'details': {'path': db_path}
                }
            
            # Test database connection
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM users WHERE approved = 1")
                approved_users = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM users WHERE approved = 0")
                pending_users = cursor.fetchone()[0]
            
            return {
                'status': 'healthy',
                'message': 'Database is accessible',
                'details': {
                    'total_users': total_users,
                    'approved_users': approved_users,
                    'pending_users': pending_users,
                    'file_size': os.path.getsize(db_path)
                }
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'error',
                'message': f'Database error: {str(e)}',
                'details': {}
            }
    
    @staticmethod
    def check_google_sheets() -> Dict[str, Any]:
        """Check Google Sheets connection"""
        try:
            if not os.path.exists('credentials.json'):
                return {
                    'status': 'error',
                    'message': 'Credentials file not found',
                    'details': {'path': 'credentials.json'}
                }
            
            # Test connection
            is_connected = test_connection()
            
            if is_connected:
                return {
                    'status': 'healthy',
                    'message': 'Google Sheets connection successful',
                    'details': {}
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Google Sheets connection failed',
                    'details': {}
                }
                
        except Exception as e:
            logger.error(f"Google Sheets health check failed: {e}")
            return {
                'status': 'error',
                'message': f'Google Sheets error: {str(e)}',
                'details': {}
            }
    
    @staticmethod
    def check_file_system() -> Dict[str, Any]:
        """Check file system health"""
        try:
            required_files = [
                'main.py',
                'requirements.txt',
                '.env',
                'credentials.json'
            ]
            
            missing_files = []
            file_sizes = {}
            
            for file_path in required_files:
                if os.path.exists(file_path):
                    file_sizes[file_path] = os.path.getsize(file_path)
                else:
                    missing_files.append(file_path)
            
            if missing_files:
                return {
                    'status': 'error',
                    'message': f'Missing required files: {", ".join(missing_files)}',
                    'details': {
                        'missing_files': missing_files,
                        'existing_files': file_sizes
                    }
                }
            
            return {
                'status': 'healthy',
                'message': 'All required files present',
                'details': {
                    'file_sizes': file_sizes
                }
            }
            
        except Exception as e:
            logger.error(f"File system health check failed: {e}")
            return {
                'status': 'error',
                'message': f'File system error: {str(e)}',
                'details': {}
            }
    
    @staticmethod
    def check_environment() -> Dict[str, Any]:
        """Check environment variables"""
        try:
            required_vars = [
                'BOT_TOKEN',
                'SHEETS_ID',
                'ADMIN_USER_ID',
                'ADMIN_GROUP_ID'
            ]
            
            missing_vars = []
            env_vars = {}
            
            for var in required_vars:
                value = os.getenv(var)
                if value:
                    env_vars[var] = '***' if 'TOKEN' in var or 'ID' in var else value
                else:
                    missing_vars.append(var)
            
            if missing_vars:
                return {
                    'status': 'error',
                    'message': f'Missing environment variables: {", ".join(missing_vars)}',
                    'details': {
                        'missing_vars': missing_vars,
                        'existing_vars': env_vars
                    }
                }
            
            return {
                'status': 'healthy',
                'message': 'All required environment variables present',
                'details': {
                    'env_vars': env_vars
                }
            }
            
        except Exception as e:
            logger.error(f"Environment health check failed: {e}")
            return {
                'status': 'error',
                'message': f'Environment error: {str(e)}',
                'details': {}
            }
    
    @classmethod
    def run_all_checks(cls) -> Dict[str, Any]:
        """Run all health checks"""
        checks = {
            'database': cls.check_database(),
            'google_sheets': cls.check_google_sheets(),
            'file_system': cls.check_file_system(),
            'environment': cls.check_environment()
        }
        
        # Determine overall status
        overall_status = 'healthy'
        for check_name, check_result in checks.items():
            if check_result['status'] == 'error':
                overall_status = 'unhealthy'
                break
        
        return {
            'status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'checks': checks,
            'summary': {
                'total_checks': len(checks),
                'healthy_checks': sum(1 for c in checks.values() if c['status'] == 'healthy'),
                'error_checks': sum(1 for c in checks.values() if c['status'] == 'error')
            }
        }
    
    @classmethod
    def get_status_summary(cls) -> str:
        """Get a simple status summary"""
        health = cls.run_all_checks()
        
        if health['status'] == 'healthy':
            return "✅ All systems healthy"
        else:
            error_checks = [name for name, check in health['checks'].items() 
                          if check['status'] == 'error']
            return f"❌ Issues found: {', '.join(error_checks)}"

def main():
    """Main function for health check"""
    print("🏥 Lethai Bot Health Check")
    print("=" * 30)
    
    health = HealthChecker.run_all_checks()
    
    print(f"Overall Status: {health['status'].upper()}")
    print(f"Timestamp: {health['timestamp']}")
    print()
    
    for check_name, check_result in health['checks'].items():
        status_icon = "✅" if check_result['status'] == 'healthy' else "❌"
        print(f"{status_icon} {check_name.replace('_', ' ').title()}: {check_result['message']}")
        
        if check_result['details']:
            for key, value in check_result['details'].items():
                print(f"   {key}: {value}")
        print()
    
    print(f"Summary: {health['summary']['healthy_checks']}/{health['summary']['total_checks']} checks passed")
    
    if health['status'] == 'unhealthy':
        exit(1)
    else:
        exit(0)

if __name__ == "__main__":
    main()



