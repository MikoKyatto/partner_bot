#!/bin/bash

# Deployment script for Lethai Concierge Referral Bot
# This script handles production deployment

set -e

echo "🚀 Lethai Concierge Referral Bot - Production Deployment"
echo "========================================================"

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
    echo -e "${BLUE}[DEPLOY]${NC} $1"
}

# Configuration
CONTAINER_NAME="lethai-referral-bot"
IMAGE_NAME="lethai-bot"
BACKUP_DIR="backups"
LOG_DIR="logs"

# Parse command line arguments
ACTION=${1:-"deploy"}
ENVIRONMENT=${2:-"production"}

print_header "Starting deployment process..."

# Check if running as root (not recommended for production)
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root is not recommended for production"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check system requirements
print_header "Checking system requirements..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running"
    exit 1
fi

print_status "System requirements met"

# Check configuration files
print_header "Checking configuration files..."

if [ ! -f .env ]; then
    print_error ".env file not found"
    print_status "Please create .env file with your configuration"
    exit 1
fi

if [ ! -f credentials.json ]; then
    print_error "credentials.json file not found"
    print_status "Please add your Google service account credentials"
    exit 1
fi

print_status "Configuration files found"

# Create necessary directories
print_header "Creating directories..."
mkdir -p $BACKUP_DIR $LOG_DIR data
print_status "Directories created"

# Backup existing database
if [ -f users.db ]; then
    print_header "Backing up existing database..."
    BACKUP_FILE="$BACKUP_DIR/users_$(date +%Y%m%d_%H%M%S).db"
    cp users.db "$BACKUP_FILE"
    print_status "Database backed up to $BACKUP_FILE"
fi

# Build Docker image
print_header "Building Docker image..."
docker-compose build --no-cache
print_status "Docker image built successfully"

# Stop existing containers
print_header "Stopping existing containers..."
docker-compose down 2>/dev/null || true
print_status "Existing containers stopped"

# Start new containers
print_header "Starting new containers..."
docker-compose up -d
print_status "Containers started"

# Wait for container to be ready
print_header "Waiting for bot to be ready..."
sleep 10

# Check container status
print_header "Checking container status..."
if docker-compose ps | grep -q "Up"; then
    print_status "Bot is running successfully"
else
    print_error "Bot failed to start"
    print_status "Checking logs..."
    docker-compose logs lethai-bot
    exit 1
fi

# Health check
print_header "Performing health check..."
sleep 5

# Check if container is responding
if docker-compose ps | grep -q "Up"; then
    print_status "Health check passed"
else
    print_error "Health check failed"
    docker-compose logs lethai-bot
    exit 1
fi

# Show deployment information
print_header "Deployment Information"
echo "Container Name: $CONTAINER_NAME"
echo "Image: $IMAGE_NAME"
echo "Environment: $ENVIRONMENT"
echo "Status: Running"

# Show useful commands
print_header "Useful Commands"
echo "View logs: docker-compose logs -f lethai-bot"
echo "Stop bot: docker-compose down"
echo "Restart bot: docker-compose restart lethai-bot"
echo "Update bot: ./scripts/deploy.sh update"

# Create monitoring script
print_header "Creating monitoring script..."
cat > monitor.sh << 'EOF'
#!/bin/bash
# Monitoring script for Lethai Concierge Referral Bot

echo "📊 Lethai Bot Status"
echo "==================="

# Check container status
if docker-compose ps | grep -q "Up"; then
    echo "✅ Bot Status: Running"
else
    echo "❌ Bot Status: Stopped"
fi

# Check logs for errors
echo ""
echo "📋 Recent Logs (last 10 lines):"
docker-compose logs --tail=10 lethai-bot

# Check resource usage
echo ""
echo "💾 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" lethai-bot

# Check database
if [ -f users.db ]; then
    echo ""
    echo "🗄️  Database:"
    echo "Size: $(du -h users.db | cut -f1)"
    echo "Last modified: $(stat -c %y users.db 2>/dev/null || stat -f %Sm users.db 2>/dev/null)"
fi
EOF

chmod +x monitor.sh
print_status "Created monitoring script"

# Create update script
cat > update.sh << 'EOF'
#!/bin/bash
# Update script for Lethai Concierge Referral Bot

echo "🔄 Updating Lethai Concierge Referral Bot..."

# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

echo "✅ Update complete!"
EOF

chmod +x update.sh
print_status "Created update script"

# Final status
print_header "Deployment Complete! 🎉"
echo ""
echo "Bot is now running in production mode"
echo ""
echo "Quick commands:"
echo "  ./monitor.sh    - Check bot status"
echo "  ./update.sh     - Update bot"
echo "  docker-compose logs -f lethai-bot - View logs"
echo ""
echo "📚 See README.md for detailed documentation"
echo "🆘 For support, check the troubleshooting section"
echo ""
print_status "Happy referring! 🏝️"



