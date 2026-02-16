# DevContainer Setup for PDF Generation Scripts

## Overview

The PDF generation scripts are now fully compatible with the VS Code DevContainer environment. The setup handles Python dependencies through a combination of system packages (apt) and pip packages.

## What's Configured

### 1. DevContainer Features

The `.devcontainer/devcontainer.json` includes:
- **Python 3.11**: Installed via the `ghcr.io/devcontainers/features/python:1` feature
- Full Python development environment with pip

### 2. Dependencies

The scripts require:
- **reportlab**: Installed via `python3-reportlab` (apt package, version 3.6.12)
- **PyPDF2**: Installed via pip (version 3.0.1+) for latest transformation features

### 3. Why Not Use Apt for PyPDF2?

The Debian repository contains PyPDF2 version 2.12.1, which has limitations:
- Only supports rotation in 90-degree increments
- Lacks modern transformation features needed for arbitrary rotation angles (-15° to +15°)

The scripts install PyPDF2 3.0.1+ via pip with `--break-system-packages` flag to get:
- Arbitrary rotation angle support using transformation matrices
- Modern PDF manipulation features
- Better compatibility with the invoice generation requirements

## Quick Start

### First Time Setup

```bash
cd /workspace/generate_pdf_scripts
bash setup_and_test.sh
```

This script will:
1. Detect the Debian/Ubuntu environment
2. Install `python3-reportlab` via apt
3. Remove old `python3-pypdf2` if present
4. Install `PyPDF2>=3.0.0` via pip
5. Generate 5 test invoices to verify everything works

### Generate Invoices

```bash
# Generate 10 invoices (default)
python3 generate_invoices.py

# Generate 50 invoices with custom ratios
python3 generate_invoices.py -n 50 --rotation-ratio 0.3 --multi-page-ratio 0.4

# Custom output directory
python3 generate_invoices.py -n 25 -o my_invoices
```

## Technical Notes

### Rotation Implementation

The scripts use PyPDF2's `Transformation` class with custom transformation matrices to achieve arbitrary rotation angles:

```python
# Convert rotation to radians and create transformation matrix
angle_rad = math.radians(rotation)
cos_angle = math.cos(angle_rad)
sin_angle = math.sin(angle_rad)

# Apply transformation: translate to origin, rotate, translate back
transformation = Transformation((cos_angle, sin_angle, -sin_angle, cos_angle, 0, 0))
```

This approach works with PyPDF2 3.0+ but not with the older 2.x versions in Debian repos.

### Package Management

The devcontainer uses Debian's "externally-managed-environment" Python setup (PEP 668). To install packages:
- ✅ Use `apt` for well-maintained Debian packages
- ✅ Use `pip` with `--break-system-packages` for newer versions
- ❌ Don't use virtual environments (unnecessary in containers)

## Troubleshooting

### "Rotation angle must be a multiple of 90" Error

This means the old PyPDF2 version is still active. Fix:

```bash
sudo apt-get remove -y python3-pypdf2
pip3 install --break-system-packages PyPDF2>=3.0.0
python3 -c "import PyPDF2; print(PyPDF2.__version__)"  # Should show 3.0.1 or higher
```

### Import Errors

Verify packages are installed:

```bash
python3 -c "import reportlab; print('reportlab OK')"
python3 -c "import PyPDF2; print('PyPDF2 OK')"
```

### Permissions Issues

All scripts should run as the `node` user in the devcontainer. If you encounter permission issues:

```bash
sudo chown -R node:node /workspace/generate_pdf_scripts
```

## Generated Output

Invoices are created in the output directory (default: `generated_invoices/`):

```
generated_invoices/
├── pdfs/                    # PDF invoice files
│   ├── invoice_12345_1791003.pdf
│   └── ...
├── json/                    # Metadata files matching your schema
│   ├── invoice_12345_1791003.json
│   └── ...
└── generation_summary.json  # Batch generation summary
```

Each invoice includes:
- ✓ Professional layout with line items, totals, tax
- ✓ 1-4 pages (configurable ratio)
- ✓ Optional rotation (-15° to +15°)
- ✓ Optional offset positioning
- ✓ Complete JSON metadata matching document AI schema
