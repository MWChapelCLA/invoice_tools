#!/bin/bash
# Quick setup and test script for invoice generator

echo "=== Invoice Generator Setup ==="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Install dependencies
echo ""
echo "Installing dependencies..."
if command -v apt-get &> /dev/null; then
    echo "Detected Debian/Ubuntu system. Installing base dependencies via apt..."
    sudo apt-get update && sudo apt-get install -y python3-reportlab python3-pip
    echo "Installing PyPDF2 via pip to get the latest version..."
    sudo apt-get remove -y python3-pypdf2 2>/dev/null || true
    pip3 install --break-system-packages PyPDF2>=3.0.0
else
    pip install -r requirements.txt
fi

echo ""
echo "=== Running Test Generation ==="
echo ""

# Generate 5 test invoices
python3 generate_invoices.py -n 5 -o test_output

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Test invoices generated in: test_output/"
echo ""
echo "To generate more invoices, run:"
echo "  python3 generate_invoices.py -n 50"
echo ""
echo "For help:"
echo "  python3 generate_invoices.py --help"
