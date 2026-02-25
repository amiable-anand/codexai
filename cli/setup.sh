#!/bin/bash

# CodexAI CLI Setup Script

echo "======================================"
echo "  CodexAI CLI Tool Setup"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.9 or higher is required"
    echo "   Current version: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""

# Check for .env file
if [ ! -f "../.env" ]; then
    echo "⚠️  Warning: .env file not found in project root"
    echo "   Please create a .env file with your Azure credentials"
    echo "   See .env.template for required variables"
    echo ""
fi

# Make the upload script executable
chmod +x codexai_upload.py

echo "======================================"
echo "  Setup Complete!"
echo "======================================"
echo ""
echo "Usage:"
echo "  python3 codexai_upload.py /path/to/your/project"
echo ""
echo "Or with a custom name:"
echo "  python3 codexai_upload.py /path/to/your/project --name 'MyProject'"
echo ""