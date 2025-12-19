# Credit Card Statement Parser

An intelligent full-stack web application that automatically extracts key financial details from credit card PDF statements using bank-specific pattern recognition algorithms.
Built to eliminate manual data entry and provide fast, accurate, structured financial data from unstructured PDF documents.

## Features

- Automatic Bank Detection from PDF content
- PDF Parsing using robust text extraction
- Multi-Bank Support (Indian Banks)
- Regex-based Pattern Recognition
- Structured JSON Output

## Extracted Data Fields
The application automatically extracts the following information:

- Card Issuer Name
- Masked Card Number
- Last 4 Digits of Card
- Billing Cycle Period
- Payment Due Date
- Total Amount Due

## Tech Stack
### Backend:
- **Python 3.8+**	Core language
- **Flask 3.0**	REST API framework
- **PyPDF2 3.0**	PDF text extraction
- **Regex (re)**	Pattern recognition
- **Flask-CORS**	Frontend-backend communication

### Frontend:
- **React 18**	Component-based UI
- **JavaScript (ES6+)**	Async API handling
- **CSS3**	Custom dark UI theme
- **Lucide React** Modern icon set
- **Fetch API**	HTTP communication

<img width="1919" height="875" alt="Screenshot 2025-12-19 125132" src="https://github.com/user-attachments/assets/7c28ccbc-2c03-4394-952d-fa535be4818c" />

<img width="1218" height="860" alt="Screenshot 2025-12-19 125205" src="https://github.com/user-attachments/assets/1df0e40c-13a4-4c57-bbb3-350b7e068ed7" />

<img width="1242" height="561" alt="Screenshot 2025-12-19 125215" src="https://github.com/user-attachments/assets/94661595-9877-451c-9d98-c6a173bd21dd" />

## Application Workflow

1. User uploads a credit card statement PDF
2. Frontend sends the file to Flask backend
3. Backend extracts text using PyPDF2
4. Bank is automatically detected
5. Bank-specific regex patterns extract data
6. Structured JSON is returned
7. Frontend displays extracted information
