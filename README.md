# 🔍 Aadhaar OCR Verification System

**Backend-only project** - Verifies Aadhaar card details using OCR technology. No frontend/UI included.

Takes an Aadhaar image and user details, then validates if they match using intelligent text extraction and fuzzy matching algorithms.

---

## ✨ What it does

- 📸 **Image Processing** - Reads and preprocesses Aadhaar card images
- 🔤 **OCR Extraction** - Extracts name, date of birth, and Aadhaar number using Tesseract
- ✅ **Smart Matching** - Compares extracted data with provided details
- 📅 **Age Calculation** - Calculates current age and determines if person is a teen
- 🎯 **Fuzzy Matching** - Handles name variations and spelling differences

---

## 🛠️ Setup

### 1️⃣ Install Tesseract OCR

**Windows:**
- Download from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- Add to PATH environment variable

**Mac:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt install tesseract-ocr
```

### 2️⃣ Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Manual installation:**
```bash
pip install opencv-python pytesseract fuzzywuzzy python-dateutil numpy
```

---

## 📁 Project Structure

```
aadhaar-ocr-verification/
├── backend/
│   └── main.py         # Main verification script
├── input/
│   ├── input.json      # User details to verify
│   └── x.png          # Aadhaar card image
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

---

## 🚀 Usage

### Step 1: Prepare Input Data
Create `input/input.json` with user details:
```json
{
  "name": "John Doe",
  "dob": "15/08/1995",
  "aadhaar": "1234 5678 9012"
}
```

### Step 2: Add Aadhaar Image
Place your Aadhaar card image as `input/x.png`

### Step 3: Run Verification
```bash
cd backend
python main.py
```

### Step 4: Check Results
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

---

## ⚙️ How it Works

1. **🖼️ Image Preprocessing** - Enhances image quality for better OCR accuracy
2. **📝 Text Extraction** - Uses Tesseract OCR with multiple extraction techniques
3. **🔍 Pattern Recognition** - Identifies name, DOB, and Aadhaar using regex patterns
4. **✨ Smart Verification** - Matches extracted data with input using fuzzy algorithms
5. **📊 Age Analysis** - Calculates current age and categorizes age groups

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python** | Core programming language |
| **OpenCV** | Image processing and preprocessing |
| **Tesseract OCR** | Optical character recognition |
| **FuzzyWuzzy** | Intelligent string matching |
| **python-dateutil** | Date parsing and manipulation |
| **NumPy** | Numerical operations |

---

## 💼 Features

- ✅ **High Accuracy OCR** - Advanced preprocessing for better text extraction
- ✅ **Flexible Matching** - Handles spelling variations in names
- ✅ **Date Intelligence** - Supports multiple date formats
- ✅ **Error Handling** - Comprehensive validation and error messages
- ✅ **Age Detection** - Automatic age calculation and categorization
- ✅ **Backend Focus** - Pure logic implementation without UI dependencies

---

## ⚠️ Important Notes

- **Image Quality**: Better image quality = higher accuracy
- **Supported Formats**: PNG, JPG, JPEG images supported
- **Privacy**: All processing is done locally, no data sent externally
- **Accuracy**: OCR accuracy depends on image clarity and lighting
- **Use Case**: Designed for verification, not data extraction from poor quality images

---

## 🔧 Development

### Project Architecture
- **Backend-only design** - Focus on core verification logic
- **Modular approach** - Separate functions for each verification step
- **Extensible code** - Easy to add new verification methods

### Future Enhancements
- Support for multiple Aadhaar card formats
- Batch processing capabilities
- API endpoint integration
- Enhanced preprocessing algorithms

---

## 📄 Requirements.txt

```txt
opencv-python
pytesseract
fuzzywuzzy
python-dateutil
numpy
Pillow
```

---

**Built with ❤️ for accurate Aadhaar verification using modern OCR technology.**

*This is a backend-focused project emphasizing OCR accuracy and intelligent data matching.*
