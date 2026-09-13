#!/bin/bash

# Quick Start Script for Rick and Morty Character API

set -e

echo "==============================================="
echo "Rick and Morty Character API - Quick Start"
echo "==============================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 is installed"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "==============================================="
echo "Setup Complete!"
echo "==============================================="
echo ""
echo "To start the development server, run:"
echo "  python app.py"
echo ""
echo "To run tests, run:"
echo "  python -m unittest test_app.py -v"
echo ""
echo "To start with gunicorn, run:"
echo "  gunicorn -w 4 -b 0.0.0.0:5000 app:app"
echo ""
echo "To start with Docker Compose, run:"
echo "  docker-compose up -d"
echo ""
echo "API will be available at: http://localhost:5000"
echo ""
