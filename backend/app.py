from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import re
from io import BytesIO
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Card issuer patterns
CARD_PATTERNS = {
    'hdfc': {
        'name': 'HDFC Bank',
        'identifiers': ['hdfc', 'housing development finance'],
        'patterns': {
            'card_number': [
                r'(?:Card\s+Number|Card\s+No\.?|Account\s+Number)\s*[:\-]?\s*(\d{4}[\s\*X-]*\d{0,4}[\s\*X-]*\d{0,4}[\s\*X-]*\d{4})',
                r'Card\s+ending\s+(?:with|in)\s*(\d{4})',
            ],
            'billing_cycle': [
                r'(?:Statement\s+Period|Billing\s+Cycle|Statement\s+Date)\s*[:\-]?\s*(\d{1,2}[-\/\s][A-Za-z]{3,}[-\/\s]\d{2,4}(?:\s*(?:to|–|-)\s*\d{1,2}[-\/\s][A-Za-z]{3,}[-\/\s]\d{2,4})?)',
                r'(?:Period|Statement)\s*[:\-]?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4}\s*(?:to|–|-)\s*\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})',
            ],
            'due_date': [
                r'(?:Payment\s+Due\s+Date|Due\s+Date|Pay\s+By)\s*[:\-]?\s*(\d{1,2}[-\/\s][A-Za-z]{3,}[-\/\s]\d{2,4})',
                r'(?:Due\s+Date|Payment\s+Due)\s*[:\-]?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})',
            ],
            'total_balance': [
                r'(?:Total\s+Amount\s+Due|Amount\s+Due|Outstanding\s+Balance|Total\s+Due)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
                r'(?:Amount\s+Payable|Payment\s+Amount)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            ]
        }
    },
    'icici': {
        'name': 'ICICI Bank',
        'identifiers': ['icici'],
        'patterns': {
            'card_number': [
                r'(?:Card\s+Number|Credit\s+Card|Card\s+ending\s+with)\s*[:\-]?\s*(\d{4}[\s\*X-]*\d{0,4}[\s\*X-]*\d{0,4}[\s\*X-]*\d{4})',
                r'(?:Card|Account)\s+ending\s+in\s*(\d{4})',
            ],
            'billing_cycle': [
                r'(?:Statement\s+Period|Bill\s+Period|Statement\s+from)\s*[:\-]?\s*(\d{1,2}[-\/\s][A-Za-z]{3,}[-\/\s]\d{2,4}(?:\s*(?:to|–|-)\s*\d{1,2}[-\/\s][A-Za-z]{3,}[-\/\s]\d{2,4})?)',
                r'(?:Period|Statement)\s*[:\-]?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4}\s*(?:to|–|-)\s*\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})',
            ],
            'due_date': [
                r'(?:Payment\s+Due\s+(?:Date|By)|Due\s+Date|Pay\s+by)\s*[:\-]?\s*(\d{1,2}[-\/\s][A-Za-z]{3,}[-\/\s]\d{2,4})',
                r'(?:Due\s+Date)\s*[:\-]?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})',
            ],
            'total_balance': [
                r'(?:Total\s+Amount\s+Due|Minimum\s+Amount\s+Due|Payment\s+Due|Total\s+Outstanding)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            ]
        }
    },
    'sbi': {
        'name': 'SBI Card',
        'identifiers': ['sbi', 'state bank'],
        'patterns': {
            'card_number': [
                r'(?:Card\s+No|Credit\s+Card\s+Number|Card\s+Number)\s*[:\-]?\s*(\d{4}[\s\*X-]*\d{0,4}[\s\*X-]*\d{0,4}[\s\*X-]*\d{4})',
                r'Card\s+ending\s+in\s*(\d{4})',
            ],
            'billing_cycle': [
                r'(?:Statement\s+Date|Bill\s+Date|Period|Statement\s+Period)\s*[:\-]?\s*(\d{1,2}[-\/\s][A-Za-z]{3,}[-\/\s]\d{2,4}(?:\s*(?:to|–|-)\s*\d{1,2}[-\/\s][A-Za-z]{3,}[-\/\s]\d{2,4})?)',
                r'(?:Period)\s*[:\-]?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4}\s*(?:to|–|-)\s*\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})',
            ],
            'due_date': [
                r'(?:Payment\s+Due\s+Date|Due\s+Date|Pay\s+by)\s*[:\-]?\s*(\d{1,2}[-\/\s][A-Za-z]{3,}[-\/\s]\d{2,4})',
                r'(?:Due\s+Date)\s*[:\-]?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})',
            ],
            'total_balance': [
                r'(?:Total\s+Amount\s+Due|Outstanding\s+Amount|Amount\s+Payable)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            ]
        }
    },
    'axis': {
        'name': 'Axis Bank',
        'identifiers': ['axis'],
        'patterns': {
            'card_number': [
                r'(?:Card\s+Number|Card)\s*[:\-]?\s*(\d{4}[\s\*X-]*\d{0,4}[\s\*X-]*\d{0,4}[\s\*X-]*\d{4})',
                r'Card\s+ending\s+(?:with|in)\s*(\d{4})',
            ],
            'billing_cycle': [
                r'(?:Statement\s+Period|Billing\s+Period|Statement\s+Date)\s*[:\-]?\s*(\d{1,2}[-\/\s][A-Za-z]{3,}[-\/\s]\d{2,4}(?:\s*(?:to|–|-)\s*\d{1,2}[-\/\s][A-Za-z]{3,}[-\/\s]\d{2,4})?)',
                r'(?:Period)\s*[:\-]?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4}\s*(?:to|–|-)\s*\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})',
            ],
            'due_date': [
                r'(?:Payment\s+Due\s+Date|Due\s+On|Pay\s+By)\s*[:\-]?\s*(\d{1,2}[-\/\s][A-Za-z]{3,}[-\/\s]\d{2,4})',
                r'(?:Due\s+Date)\s*[:\-]?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})',
            ],
            'total_balance': [
                r'(?:Total\s+Amount\s+Due|Amount\s+Payable|Outstanding)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            ]
        }
    },
    'kotak': {
        'name': 'Kotak Mahindra',
        'identifiers': ['kotak'],
        'patterns': {
            'card_number': [
                r'(?:Card\s+Number|Credit\s+Card)\s*[:\-]?\s*(\d{4}[\s\*X-]*\d{0,4}[\s\*X-]*\d{0,4}[\s\*X-]*\d{4})',
                r'Card\s+ending\s+in\s*(\d{4})',
            ],
            'billing_cycle': [
                r'(?:Statement\s+Date|Bill\s+Date|Statement\s+Period)\s*[:\-]?\s*(\d{1,2}[-\/\s][A-Za-z]{3,}[-\/\s]\d{2,4}(?:\s*(?:to|–|-)\s*\d{1,2}[-\/\s][A-Za-z]{3,}[-\/\s]\d{2,4})?)',
                r'(?:Period)\s*[:\-]?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4}\s*(?:to|–|-)\s*\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})',
            ],
            'due_date': [
                r'(?:Payment\s+Due\s+Date|Due\s+Date)\s*[:\-]?\s*(\d{1,2}[-\/\s][A-Za-z]{3,}[-\/\s]\d{2,4})',
                r'(?:Due\s+Date)\s*[:\-]?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})',
            ],
            'total_balance': [
                r'(?:Total\s+Amount\s+Due|Current\s+Outstanding|Payment\s+Due)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            ]
        }
    }
}

def extract_text_from_pdf(file_bytes):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def detect_card_issuer(text):
    """Detect card issuer from text"""
    text_lower = text.lower()
    
    for issuer_key, issuer_data in CARD_PATTERNS.items():
        for identifier in issuer_data['identifiers']:
            if identifier in text_lower:
                return issuer_key
    
    # Default to HDFC if not detected
    return 'hdfc'

def extract_field(text, patterns):
    """Extract field using multiple regex patterns"""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return None

def extract_last_four_digits(card_number):
    """Extract last 4 digits from card number"""
    if not card_number:
        return None
    
    digits = re.sub(r'[^\d]', '', card_number)
    if len(digits) >= 4:
        return digits[-4:]
    return None

def parse_statement(text, issuer):
    """Parse statement text and extract data"""
    patterns = CARD_PATTERNS[issuer]['patterns']
    
    data = {
        'issuer': CARD_PATTERNS[issuer]['name'],
        'card_number': None,
        'last_four_digits': None,
        'billing_cycle': None,
        'due_date': None,
        'total_balance': None
    }
    
    # Extract card number
    card_number = extract_field(text, patterns['card_number'])
    if card_number:
        data['card_number'] = card_number
        data['last_four_digits'] = extract_last_four_digits(card_number)
    
    # Extract billing cycle
    billing_cycle = extract_field(text, patterns['billing_cycle'])
    if billing_cycle:
        data['billing_cycle'] = billing_cycle
    
    # Extract due date
    due_date = extract_field(text, patterns['due_date'])
    if due_date:
        data['due_date'] = due_date
    
    # Extract total balance
    total_balance = extract_field(text, patterns['total_balance'])
    if total_balance:
        # Clean and format balance
        balance = re.sub(r'[^\d.]', '', total_balance)
        data['total_balance'] = f'₹{balance}'
    
    return data

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@app.route('/api/parse', methods=['POST'])
def parse_pdf():
    """Parse credit card statement PDF"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Read file bytes
        file_bytes = file.read()
        
        # Extract text from PDF
        text = extract_text_from_pdf(file_bytes)
        
        if not text or len(text) < 50:
            return jsonify({
                'error': 'Could not extract sufficient text from PDF. The PDF might be image-based or protected.'
            }), 400
        
        # Detect card issuer
        issuer = detect_card_issuer(text)
        
        # Parse statement
        data = parse_statement(text, issuer)
        
        # Add raw text for debugging (optional)
        data['raw_text_preview'] = text[:500] + '...' if len(text) > 500 else text
        
        # Check if any data was extracted
        extracted_count = sum(1 for v in [data['card_number'], data['billing_cycle'], 
                                         data['due_date'], data['total_balance']] if v)
        
        if extracted_count == 0:
            return jsonify({
                'error': 'Could not extract any information. Please check if this is a valid credit card statement.',
                'raw_text_preview': text[:500]
            }), 400
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        print("Error:", str(e))
        print(traceback.format_exc())
        return jsonify({
            'error': f'Error processing PDF: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🚀 Credit Card Statement Parser Backend")
    print("📍 Server starting on http://localhost:5000")
    print("✅ Supported banks: HDFC, ICICI, SBI, Axis, Kotak")
    app.run(debug=True, port=5000)