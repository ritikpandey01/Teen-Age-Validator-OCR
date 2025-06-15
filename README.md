# Aadhaar OCR Verification System

**Backend-only project** - Verifies Aadhaar card details using OCR. No frontend/UI included.

Takes an Aadhaar image and user details, then checks if they match using smart text extraction and fuzzy matching.

## What it does

- Reads Aadhaar card images
- Extracts name, date of birth, and Aadhaar number using OCR
- Matches extracted data with provided details
- Calculates age and checks if person is a teen
- Uses fuzzy matching for names (handles spelling variations)

## Setup

1. **Install Tesseract OCR:**
   - Windows: Download from [here](https://github.com/UB-Mannheim/tesseract/wiki)
   - Mac: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`

2. **Install Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

   Or manually:
   ```bash
   pip install opencv-python pytesseract fuzzywuzzy python-dateutil numpy
   ```

## Project Structure
```
project/
├── backend/
│   └── main.py         # Main verification script
├── input/
│   ├── input.json      # User details to verify
│   └── x.png          # Aadhaar image
└── requirements.txt    # Python dependencies
```

## Usage

1. Create your input file `input/input.json`:
   ```json
   {
     "name": "John Doe",
     "dob": "15/08/1995",
     "aadhaar": "1234 5678 9012"
   }
   ```

2. Put your Aadhaar image as `input/x.png`

3. Run the script:
   ```bash
   cd backend
   python main.py
   ```

4. Output example:
   ```
   Advanced Aadhaar Verification Results:
   All details match: Yes
   Name matches: Yes (JOHN DOE)
   DOB matches: Yes (15-08-1995)
   Aadhaar matches: Yes (123456789012)

   Extracted Details:
   Name: JOHN DOE
   DOB: 15-08-1995
   Aadhaar: 123456789012
   Age: 28 (Not teen)
   ```

## How it works

1. **Image preprocessing** - Cleans up the image for better OCR
2. **Text extraction** - Uses Tesseract OCR with multiple techniques
3. **Data extraction** - Finds name, DOB, and Aadhaar using regex patterns
4. **Verification** - Matches extracted data with input using fuzzy matching
5. **Age calculation** - Calculates current age from DOB

## Tech Stack

- Python
- OpenCV (image processing)
- Tesseract OCR (text extraction)
- FuzzyWuzzy (string matching)
- python-dateutil (date parsing)

## My Role

Built the complete backend system including:
- OCR integration and image preprocessing
- Data extraction logic with regex patterns
- Fuzzy matching algorithms for verification
- Age calculation and teen detection
- Input validation and error handling

*This is a backend-only project focusing on OCR and data verification logic.*


