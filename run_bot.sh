#!/bin/bash

# Script to run the bot with proper environment variables

echo "🤖 Starting Lethai Concierge Referral Bot..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it from env.example"
    exit 1
fi

# Load environment variables and run the bot
export $(cat .env | xargs) && python3 main.py



