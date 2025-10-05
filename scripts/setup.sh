#!/bin/bash

# Setup script for Lethai Concierge Referral Bot
# This script helps with initial setup and configuration

set -e

echo "🏝️  Lethai Concierge Referral Bot Setup"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "Detected macOS system"
    PLATFORM="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_status "Detected Linux system"
    PLATFORM="linux"
else
    print_warning "Unknown operating system: $OSTYPE"
    PLATFORM="unknown"
fi

# Check system requirements
print_header "Checking system requirements..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python $PYTHON_VERSION found"
    
    # Check if Python version is 3.10+
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
        print_status "Python version is compatible"
    else
        print_error "Python 3.10+ is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 is not installed"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    print_status "Docker $DOCKER_VERSION found"
else
    print_error "Docker is not installed"
    print_status "Please install Docker from https://www.docker.com/get-started"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
    print_status "Docker Compose $COMPOSE_VERSION found"
else
    print_error "Docker Compose is not installed"
    exit 1
fi

print_status "All system requirements met!"

# Create necessary directories
print_header "Creating directories..."
mkdir -p data logs
print_status "Created data and logs directories"

# Setup environment file
print_header "Setting up environment configuration..."
if [ ! -f .env ]; then
    if [ -f env.example ]; then
        cp env.example .env
        print_status "Created .env file from template"
        print_warning "Please edit .env file with your configuration:"
        echo "  - BOT_TOKEN: Your Telegram bot token"
        echo "  - SHEETS_ID: Your Google Sheets ID"
        echo "  - ADMIN_USER_ID: Your Telegram user ID"
    else
        print_error "env.example file not found"
        exit 1
    fi
else
    print_status ".env file already exists"
fi

# Check for credentials file
print_header "Checking Google Sheets credentials..."
if [ ! -f credentials.json ]; then
    print_warning "credentials.json file not found"
    echo "Please download your Google service account credentials and save as credentials.json"
    echo "Instructions:"
    echo "1. Go to Google Cloud Console"
    echo "2. Create a service account"
    echo "3. Download the JSON key file"
    echo "4. Save it as credentials.json in this directory"
    echo "5. Share your Google Sheet with the service account email"
else
    print_status "credentials.json file found"
fi

# Install Python dependencies
print_header "Installing Python dependencies..."
if [ -f requirements.txt ]; then
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    print_status "Python dependencies installed"
else
    print_error "requirements.txt file not found"
    exit 1
fi

# Initialize database
print_header "Initializing database..."
python3 -c "from utils.database import init_database; init_database()" 2>/dev/null || {
    print_warning "Could not initialize database (this is normal if dependencies are missing)"
}

# Test Google Sheets connection
print_header "Testing Google Sheets connection..."
if [ -f credentials.json ]; then
    python3 -c "from utils.sheets import test_connection; print('✅ Google Sheets connection successful' if test_connection() else '❌ Google Sheets connection failed')" 2>/dev/null || {
        print_warning "Could not test Google Sheets connection"
    }
else
    print_warning "Skipping Google Sheets test (credentials.json not found)"
fi

# Create systemd service file (Linux only)
if [[ "$PLATFORM" == "linux" ]]; then
    print_header "Creating systemd service file..."
    cat > lethai-bot.service << EOF
[Unit]
Description=Lethai Concierge Referral Bot
After=network.target

[Service]
Type=simple
User=lethai
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/docker-compose up
ExecStop=/usr/bin/docker-compose down
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    print_status "Created lethai-bot.service file"
    print_warning "To install as system service:"
    echo "  sudo cp lethai-bot.service /etc/systemd/system/"
    echo "  sudo systemctl enable lethai-bot"
    echo "  sudo systemctl start lethai-bot"
fi

# Create launch script
print_header "Creating launch script..."
cat > start.sh << 'EOF'
#!/bin/bash
# Launch script for Lethai Concierge Referral Bot

echo "🏝️  Starting Lethai Concierge Referral Bot..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run setup first."
    exit 1
fi

# Check if credentials.json exists
if [ ! -f credentials.json ]; then
    echo "❌ credentials.json file not found. Please add your Google service account credentials."
    exit 1
fi

# Start with Docker Compose
echo "🚀 Starting bot with Docker Compose..."
docker-compose up --build
EOF

chmod +x start.sh
print_status "Created start.sh script"

# Create stop script
cat > stop.sh << 'EOF'
#!/bin/bash
# Stop script for Lethai Concierge Referral Bot

echo "🛑 Stopping Lethai Concierge Referral Bot..."
docker-compose down
echo "✅ Bot stopped"
EOF

chmod +x stop.sh
print_status "Created stop.sh script"

# Final instructions
print_header "Setup Complete! 🎉"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration:"
echo "   - BOT_TOKEN: Your Telegram bot token"
echo "   - SHEETS_ID: Your Google Sheets ID"
echo "   - ADMIN_USER_ID: Your Telegram user ID"
echo ""
echo "2. Add your Google service account credentials as credentials.json"
echo ""
echo "3. Start the bot:"
echo "   ./start.sh"
echo "   # or"
echo "   docker-compose up --build"
echo ""
echo "4. For development:"
echo "   python3 main.py"
echo ""
echo "5. Run tests:"
echo "   python3 -m pytest"
echo ""
echo "📚 See README.md for detailed documentation"
echo "🆘 For support, check the troubleshooting section in README.md"
echo ""
print_status "Happy referring! 🏝️"



