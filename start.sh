#!/bin/bash

echo "=================================="
echo "AI Mask Detection System"
echo "=================================="
echo ""

echo "Checking MongoDB status..."
if command -v mongod &> /dev/null
then
    echo "✓ MongoDB is installed"
else
    echo "✗ MongoDB is not installed. Please install MongoDB first."
    echo "Visit: https://www.mongodb.com/try/download/community"
    exit 1
fi

if pgrep -x "mongod" > /dev/null
then
    echo "✓ MongoDB is running"
else
    echo "⚠ MongoDB is not running. Starting MongoDB..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start mongodb-community
    else
        sudo systemctl start mongodb
    fi
fi

echo ""
echo "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

source venv/bin/activate
echo "✓ Virtual environment activated"

echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "=================================="
echo "Starting Django server..."
echo "=================================="
echo ""
echo "Access the application at:"
echo "http://127.0.0.1:8000/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python manage.py runserver
