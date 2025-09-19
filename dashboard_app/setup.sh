#!/bin/bash

echo "Setting up Natural Language to SQL Dashboard..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Python detected: $(python3 --version)"

# Create virtual environment
echo
echo "Creating virtual environment..."
cd backend
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check for database
echo
echo "Checking for database..."
if [ -f "../retail_database.db" ]; then
    echo "✓ Database found: retail_database.db"
else
    echo "✗ Database not found: retail_database.db"
    echo "Please ensure the database file is in the project root directory"
fi

# Setup environment file
echo
echo "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file from template"
    echo "Please edit .env file and add your GitHub token"
else
    echo "✓ .env file already exists"
fi

echo
echo "Setup complete!"
echo
echo "Next steps:"
echo "1. Edit backend/.env file and add your GitHub token"
echo "2. Run: cd backend && python app.py"
echo "3. Open frontend/index.html in your web browser"
echo