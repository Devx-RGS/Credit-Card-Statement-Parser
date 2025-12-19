The Credit Card Statement Parser is an automated data extraction tool that parses credit card statements from major Indian banks. It eliminates manual data entry by intelligently extracting key information from PDF documents.
What It Does

Automatically detects the issuing bank from PDF content
Extracts 6 key data points:

Card Issuer Name
Masked Card Number
Last 4 Digits
Billing Cycle Period
Payment Due Date
Total Amount Due


Exports data in JSON format
Provides modern UI for easy interaction

Supported Banks
HDFC Bank
ICICI Bank
SBI Card
Axis Bank
Kotak Mahindra Bank

Tech Stack
Python
Flask
PyPDF
Flask CORS
Regex
React JS

How It Works
Step 1: User Uploads PDF
Step 2: Frontend Sends to Backend
Step 3: Backend Extracts Text
Step 4: Detect Bank
Step 5: Extract Data Using Regex
Step 6: Return JSON Response
Step 7: Display Results
