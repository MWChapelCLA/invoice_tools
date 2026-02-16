# Invoice Generator - Quick Reference

## Installation

### DevContainer Setup

If you're in the DevContainer:

```bash
cd generate_pdf_scripts
bash setup_and_test.sh
```

### Manual Setup

```bash
cd generate_pdf_scripts
pip install -r requirements.txt
```

## Quick Start Examples

### Generate 10 invoices (default)
```bash
python3 generate_invoices.py
```

### Generate 50 invoices
```bash
python3 generate_invoices.py -n 50
```

### Generate 100 invoices with more variations
```bash
python3 generate_invoices.py -n 100 --multi-page-ratio 0.4 --rotation-ratio 0.3 --offset-ratio 0.3
```

### Custom output directory
```bash
python3 generate_invoices.py -n 25 -o my_test_invoices
```

### Generate pen testing invoices with dangerous HTML ⚠️
```bash
python3 generate_invoices.py -n 50 --dangerous-html -o pen_test_invoices
```
**Warning**: Only use in controlled testing environments. See [PENTESTING.md](PENTESTING.md) for details.

## What Gets Generated

Each invoice includes:

✓ **PDF Document**
- Professional invoice layout
- 1-4 pages (configurable)
- Line items with descriptions, quantities, prices
- Subtotal, tax, shipping, and total
- Optional rotation (-15° to +15°)
- Optional off-center positioning

✓ **JSON Metadata**
- Complete invoice data matching your schema
- Entity ID and Document ID
- Extracted data payload
- Processing steps and timestamps
- File paths and references

## Output Structure

```
generated_invoices/
├── pdfs/
│   ├── invoice_12345_1791003.pdf
│   └── ...
├── json/
│   ├── invoice_12345_1791003.json
│   └── ...
└── generation_summary.json
```

## Invoice Features

- **20 Company Names**: Realistic business names
- **20 Product Types**: Various items with realistic pricing
- **20 US Cities**: Addresses across multiple states
- **Random Dates**: Between 2020-2026
- **Random Quantities**: 1-10 items per line
- **Tax Calculation**: 5-9.5% tax rates
- **Optional Shipping**: $0-25 shipping costs
- **PO Numbers**: 50% chance of having a PO number

## Variation Options

| Option | Default | Description |
|--------|---------|-------------|
| `--multi-page-ratio` | 0.3 | 30% will be 2-4 pages |
| `--rotation-ratio` | 0.2 | 20% will be rotated ±5-15° |
| `--offset-ratio` | 0.2 | 20% will be off-center |

## Programmatic Usage

```python
from generate_invoices import InvoiceGenerator

# Normal mode
generator = InvoiceGenerator(output_dir="my_invoices")

# Pen testing mode with dangerous HTML
generator_pentest = InvoiceGenerator(
    output_dir="pen_test_invoices",
    inject_dangerous_html=True
)

# Single invoice
result = generator.generate_invoice(
    entity_id=1,
    document_id=100,
    num_pages=2,
    rotation=-10,
    offset_x=15,
    offset_y=-10
)

# Batch generation
results = generator.generate_batch(
    count=50,
    multi_page_ratio=0.5,
    rotation_ratio=0.3,
    offset_ratio=0.25
)

# Pen testing batch
results_pentest = generator_pentest.generate_batch(count=20)
```

## Testing the Script

Run the automated setup and test:
```bash
./setup_and_test.sh
```

Or run the example:
```bash
python3 example_usage.py
```

## Common Use Cases

**Testing Document AI**: Generate diverse invoices for OCR/extraction testing
```bash
python3 generate_invoices.py -n 100 --rotation-ratio 0.3 --offset-ratio 0.3
```

**QA Dataset**: Create a varied test dataset
```bash
python3 generate_invoices.py -n 500 --multi-page-ratio 0.5
```

**Load Testing**: Generate large batches for performance testing
```bash
python3 generate_invoices.py -n 1000
```

**Training Data**: Create clean, well-formatted invoices
```bash
python3 generate_invoices.py -n 200 --rotation-ratio 0 --offset-ratio 0
```

**Security Testing**: Generate invoices with dangerous HTML payloads ⚠️
```bash
python3 generate_invoices.py -n 100 --dangerous-html -o security_test
```
See [PENTESTING.md](PENTESTING.md) for comprehensive security testing documentation.

## Tips

- Start with small batches (10-20) to verify output
- Adjust ratios based on your testing needs
- Check `generation_summary.json` for overview
- PDFs and JSONs are linked by invoice number
- All data is randomly generated each time
