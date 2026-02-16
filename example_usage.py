#!/usr/bin/env python3
"""
Example usage of the invoice generator
"""

from generate_invoices import InvoiceGenerator

# Create generator instance (normal mode)
generator = InvoiceGenerator(output_dir="example_invoices")

# Create generator with dangerous HTML injection for pen testing
generator_dangerous = InvoiceGenerator(output_dir="example_invoices_dangerous", inject_dangerous_html=True)

# Generate a single invoice
print("Generating single invoice...")
result = generator.generate_invoice(
    entity_id=1,
    document_id=100,
    num_pages=1,
    rotation=0,
    offset_x=0,
    offset_y=0
)
print(f"Generated: {result['pdf_path']}")

# Generate a rotated multi-page invoice
print("\nGenerating rotated multi-page invoice...")
result = generator.generate_invoice(
    entity_id=2,
    document_id=101,
    num_pages=3,
    rotation=-10,  # Rotated 10 degrees counter-clockwise
    offset_x=15,
    offset_y=-10
)
print(f"Generated: {result['pdf_path']}")

# Generate a batch with custom ratios
print("\nGenerating batch of 20 invoices...")
results = generator.generate_batch(
    count=20,
    multi_page_ratio=0.5,   # 50% will be multi-page
    rotation_ratio=0.3,      # 30% will be rotated
    offset_ratio=0.25        # 25% will be off-center
)

print(f"\nTotal generated: {len(results)}")

# Generate pen testing invoices with dangerous payloads
print("\n" + "="*60)
print("GENERATING PEN TESTING INVOICES WITH DANGEROUS PAYLOADS")
print("="*60)
print("\nGenerating batch of 10 invoices with dangerous payloads...")
print("  - HTML injection (XSS, iframe, script tags)")
print("  - SQL injection (UNION, DROP TABLE, authentication bypass)")
print("  - CSV formula injection (Excel formulas, command execution)")
results_dangerous = generator_dangerous.generate_batch(
    count=10,
    multi_page_ratio=0.3,
    rotation_ratio=0.2,
    offset_ratio=0.2
)

print(f"\nTotal dangerous invoices generated: {len(results_dangerous)}")
print("⚠️  These files contain dangerous payloads for security testing:")
print("   - HTML: XSS attacks, script injection, iframe hijacking")
print("   - SQL: Database injection, authentication bypass, DROP TABLE")
print("   - CSV: Formula injection, command execution in spreadsheets")
print("   Files are labeled with '_dangerous_' in the filename")
