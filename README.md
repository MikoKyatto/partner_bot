# Lethai Concierge Referral Bot 🏝️

A production-ready Telegram bot for the Lethai concierge service referral program. The bot issues unique referral links, generates QR code images, integrates with Google Sheets for balance tracking, and supports admin approval workflow.

## Features

- 🔗 **Unique Referral Links**: Each user gets a personalized referral link (`https://taplink.cc/lakeevainfo?ref=<partnercode>`)
- 📱 **QR Code Generation**: Beautiful QR codes with Lethai branding and palm tree silhouettes
- 📊 **Google Sheets Integration**: Automatic balance tracking and partner management
- 👥 **Admin Panel**: Approve/reject users with inline buttons
- 🗄️ **SQLite Database**: User data storage with approval workflow
- 🐳 **Docker Support**: Containerized for easy deployment
- 🧪 **Unit Tests**: Comprehensive test coverage
- 🔒 **Security**: Environment variables, non-root user, input validation

## Quick Start

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Google Cloud Service Account with Sheets API access
- Telegram Bot Token

### 1. Clone and Setup

```bash
git clone <repository-url>
cd lethai-bot
cp env.example .env
```

### 2. Configure Environment

Edit `.env` file:

```env
BOT_TOKEN=your_bot_token_here
SHEETS_ID=your_google_sheets_id_here
CREDENTIALS_PATH=credentials.json
ADMIN_GROUP_ID=-100UNgKEPL64LxjNDky
ADMIN_USER_ID=1454702347
```

### 3. Google Sheets Setup

1. Create a Google Cloud Project
2. Enable Google Sheets API
3. Create a Service Account
4. Download the JSON credentials file as `credentials.json`
5. Share your Google Sheet with the service account email

### 4. Run with Docker

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f lethai-bot
```

### 5. Run Locally (Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py
```

## Project Structure

```
lethai-bot/
├── handlers/                 # Bot command handlers
│   ├── start.py             # Registration and main menu
│   ├── admin.py             # Admin commands and approval
│   └── menu.py              # User menu commands
├── utils/                   # Utility modules
│   ├── database.py          # SQLite operations
│   ├── sheets.py            # Google Sheets integration
│   └── qr_code.py           # QR code generation
├── tests/                   # Unit tests
│   ├── test_handlers.py     # Handler tests
│   ├── test_sheets.py       # Sheets integration tests
│   ├── test_database.py     # Database tests
│   └── test_qr_code.py      # QR code tests
├── main.py                  # Bot entry point
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── .env                    # Environment variables
├── credentials.json        # Google service account
└── README.md              # This file
```

## Bot Commands

### User Commands

- `/start` - Start registration or access main menu
- **Моя реферальная ссылка** - Get your referral link and QR code
- **Посмотреть баланс** - Check your current balance
- **Поддержка** - Contact support

### Admin Commands

- `/admin` - Access admin panel for user approval
- `/stats` - View system statistics
- `/users` - List all approved users

## User Flow

1. **Registration**: User sends `/start` and shares contact
2. **Approval**: Admin reviews and approves user in admin panel
3. **Access**: Approved users get access to referral features
4. **Referrals**: Users share their unique link and earn bonuses
5. **Balance**: Balance is tracked in Google Sheets automatically

## Google Sheets Integration

The bot integrates with Google Sheets for balance tracking:

- **Sheet Structure**: First column is partnercode (Telegram ID)
- **Balance Calculation**: Sums all numeric values in user's row
- **Auto-Update**: New partnercodes added on approval
- **Manual Tracking**: Supports manual entry of referral bonuses

### Recommended Sheet Structure

| partnercode | date | action | amount1 | amount2 | amount3 |
|-------------|------|--------|---------|---------|---------|
| 12345 | 2024-01-01 | signup | 100.50 | 200.75 | 50.25 |
| 67890 | 2024-01-02 | signup | 300.00 | 150.00 | |

## QR Code Design

Generated QR codes feature:
- **Size**: 512x512 pixels
- **Background**: Dark green (#1A3C34)
- **QR Code**: 400x400 pixels, centered
- **Branding**: "Lethai" text in white
- **Decoration**: Palm tree silhouettes
- **Format**: High-quality JPEG

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_handlers.py

# Run with verbose output
pytest -v
```

## Deployment

### VPS Deployment

1. **Upload files** to your VPS
2. **Configure environment** variables
3. **Run with Docker**:

```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Docker Commands

```bash
# Build image
docker build -t lethai-bot .

# Run container
docker run -d \
  --name lethai-bot \
  --env-file .env \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  -v $(pwd)/data:/app/data \
  lethai-bot

# Stop container
docker stop lethai-bot

# Remove container
docker rm lethai-bot
```

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token | `123456789:ABC...` |
| `SHEETS_ID` | Google Sheets ID | `18dY652fOqEJ6EC1ppMlMF0Obzlzu32xxVXt5AJ9415A` |
| `CREDENTIALS_PATH` | Path to service account JSON | `credentials.json` |
| `ADMIN_GROUP_ID` | Admin notification group | `-100UNgKEPL64LxjNDky` |
| `ADMIN_USER_ID` | Admin user ID | `1454702347` |

### Google Sheets Permissions

The service account needs:
- **Viewer** access to the spreadsheet
- **Editor** access to the specific sheet (Лист1)

## Security

- ✅ Environment variables for sensitive data
- ✅ Non-root Docker user
- ✅ Input validation and sanitization
- ✅ Error handling and logging
- ✅ Rate limiting (via aiogram)
- ✅ SQL injection protection (parameterized queries)

## Monitoring

### Logs

```bash
# View bot logs
docker-compose logs -f lethai-bot

# View specific log level
docker-compose logs -f lethai-bot | grep ERROR
```

### Health Checks

The bot includes health checks:
- Database connectivity
- Google Sheets API access
- Bot token validation

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check BOT_TOKEN in .env
   - Verify bot is running: `docker-compose ps`
   - Check logs: `docker-compose logs lethai-bot`

2. **Google Sheets errors**
   - Verify credentials.json exists
   - Check service account permissions
   - Ensure Sheets API is enabled

3. **Database errors**
   - Check file permissions
   - Verify SQLite installation
   - Check disk space

### Debug Mode

Enable debug logging:

```python
# In main.py, change logging level
logging.basicConfig(level=logging.DEBUG)
```

## Development

### Local Development

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests
pytest

# Run bot in development mode
python main.py
```

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Write tests for new features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is proprietary software for Lethai Concierge Services.

## Support

For technical support:
- Create an issue in the repository
- Contact the development team
- Check the troubleshooting section

---

**Built with ❤️ for Lethai Concierge Services**



