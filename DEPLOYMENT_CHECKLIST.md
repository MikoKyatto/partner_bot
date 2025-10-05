# Lethai Concierge Referral Bot - Deployment Checklist

## Pre-Deployment Setup

### 1. Environment Configuration
- [ ] Copy `env.example` to `.env`
- [ ] Set `BOT_TOKEN` with your Telegram bot token
- [ ] Set `SHEETS_ID` with your Google Sheets ID
- [ ] Set `ADMIN_USER_ID` with your Telegram user ID
- [ ] Set `ADMIN_GROUP_ID` with your admin group ID
- [ ] Verify all environment variables are set

### 2. Google Sheets Setup
- [ ] Create Google Cloud Project
- [ ] Enable Google Sheets API
- [ ] Create Service Account
- [ ] Download credentials as `credentials.json`
- [ ] Share your Google Sheet with service account email
- [ ] Verify sheet has correct structure (partnercode in first column)

### 3. Telegram Bot Setup
- [ ] Create bot with @BotFather
- [ ] Get bot token
- [ ] Add bot to admin group
- [ ] Test bot responds to /start command

## Local Development Testing

### 1. System Requirements
- [ ] Python 3.10+ installed
- [ ] Docker and Docker Compose installed
- [ ] Git installed

### 2. Initial Setup
- [ ] Clone repository
- [ ] Run `./scripts/setup.sh`
- [ ] Verify all dependencies installed
- [ ] Test database initialization

### 3. Functionality Testing
- [ ] Test user registration flow
- [ ] Test admin approval workflow
- [ ] Test referral link generation
- [ ] Test QR code generation
- [ ] Test balance checking
- [ ] Test Google Sheets integration

### 4. Unit Tests
- [ ] Run `pytest` - all tests pass
- [ ] Run `pytest --cov=.` - check coverage
- [ ] Fix any failing tests

## Docker Testing

### 1. Build and Test
- [ ] Run `docker-compose build`
- [ ] Run `docker-compose up` - bot starts successfully
- [ ] Test bot functionality in Docker
- [ ] Check logs for errors

### 2. Health Checks
- [ ] Run `python health.py` - all checks pass
- [ ] Test database connectivity
- [ ] Test Google Sheets connection
- [ ] Verify file system access

## Production Deployment

### 1. VPS Preparation
- [ ] Choose VPS provider (DigitalOcean, AWS, etc.)
- [ ] Install Docker and Docker Compose
- [ ] Configure firewall (open necessary ports)
- [ ] Set up SSL certificates (if using webhooks)

### 2. File Transfer
- [ ] Upload project files to VPS
- [ ] Upload `credentials.json` securely
- [ ] Set proper file permissions
- [ ] Verify `.env` file is configured

### 3. Production Deployment
- [ ] Run `./scripts/deploy.sh`
- [ ] Verify containers are running
- [ ] Check logs for errors
- [ ] Test bot functionality

### 4. Monitoring Setup
- [ ] Set up log monitoring
- [ ] Configure health check monitoring
- [ ] Set up backup procedures
- [ ] Test restart procedures

## Post-Deployment Verification

### 1. Bot Functionality
- [ ] Test `/start` command
- [ ] Test user registration
- [ ] Test admin approval
- [ ] Test referral link generation
- [ ] Test balance checking
- [ ] Test support contact

### 2. Admin Functions
- [ ] Test `/admin` command
- [ ] Test user approval/rejection
- [ ] Test `/stats` command
- [ ] Test `/users` command
- [ ] Verify admin notifications

### 3. Google Sheets Integration
- [ ] Verify new users added to sheet
- [ ] Test balance calculation
- [ ] Verify manual entry works
- [ ] Check data consistency

### 4. Error Handling
- [ ] Test with invalid inputs
- [ ] Test network disconnection
- [ ] Test database errors
- [ ] Verify error messages are user-friendly

## Security Checklist

### 1. Access Control
- [ ] Verify admin user ID is correct
- [ ] Test non-admin users cannot access admin functions
- [ ] Verify bot token is secure
- [ ] Check credentials file permissions

### 2. Data Protection
- [ ] Verify user data is stored securely
- [ ] Check database file permissions
- [ ] Verify logs don't contain sensitive data
- [ ] Test input validation

### 3. Network Security
- [ ] Verify HTTPS for webhooks (if used)
- [ ] Check firewall configuration
- [ ] Verify secure file transfer
- [ ] Test rate limiting

## Performance Testing

### 1. Load Testing
- [ ] Test with multiple concurrent users
- [ ] Test database performance
- [ ] Test Google Sheets API limits
- [ ] Monitor memory usage

### 2. Scalability
- [ ] Test with large number of users
- [ ] Verify database performance
- [ ] Check API rate limits
- [ ] Monitor resource usage

## Backup and Recovery

### 1. Backup Procedures
- [ ] Set up database backups
- [ ] Backup configuration files
- [ ] Backup logs
- [ ] Test backup restoration

### 2. Recovery Testing
- [ ] Test database recovery
- [ ] Test configuration recovery
- [ ] Test bot restart procedures
- [ ] Verify data integrity

## Documentation

### 1. User Documentation
- [ ] Update user instructions
- [ ] Document admin procedures
- [ ] Create troubleshooting guide
- [ ] Update contact information

### 2. Technical Documentation
- [ ] Update deployment procedures
- [ ] Document configuration options
- [ ] Create maintenance procedures
- [ ] Update API documentation

## Final Verification

### 1. End-to-End Testing
- [ ] Complete user registration flow
- [ ] Complete admin approval flow
- [ ] Test referral link sharing
- [ ] Verify balance tracking
- [ ] Test support contact

### 2. Production Readiness
- [ ] All tests passing
- [ ] No critical errors in logs
- [ ] Performance meets requirements
- [ ] Security measures in place
- [ ] Monitoring configured
- [ ] Backup procedures tested

## Go-Live Checklist

- [ ] All pre-deployment steps completed
- [ ] All tests passing
- [ ] Production environment ready
- [ ] Monitoring configured
- [ ] Backup procedures in place
- [ ] Support team notified
- [ ] Documentation updated
- [ ] Final verification completed

## Post-Launch Monitoring

### First 24 Hours
- [ ] Monitor bot logs continuously
- [ ] Check for any errors
- [ ] Monitor user registrations
- [ ] Verify admin notifications
- [ ] Check Google Sheets updates

### First Week
- [ ] Monitor performance metrics
- [ ] Check user feedback
- [ ] Verify balance calculations
- [ ] Monitor error rates
- [ ] Review admin actions

### Ongoing
- [ ] Regular log reviews
- [ ] Performance monitoring
- [ ] Security updates
- [ ] Feature enhancements
- [ ] User support

---

**Deployment Date**: _______________
**Deployed By**: _______________
**Verified By**: _______________
**Status**: _______________



