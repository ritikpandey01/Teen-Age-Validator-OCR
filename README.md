# Aadhaar OCR Age Validator

This is a backend-only Python project that extracts personal information from Aadhaar card images using Tesseract OCR. It focuses on **teen verification** by extracting the **name** and **date of birth**, calculating age, and checking if the user is under 18.

⚠️ Note: This project does not include any frontend or UI. My role was focused only on the backend development and OCR logic.

---

## 👨‍💻 My Role

I developed the complete backend pipeline which:

- Reads Aadhaar images from a folder
- Extracts raw text using Tesseract OCR
- Uses pattern matching (regex) to identify name and date of birth
- Calculates the user's age
- Verifies if the user qualifies as a teen (age < 18)

---

## 🔧 Tech Stack

- **Python**
- **Tesseract OCR** (via `pytesseract`)
- **Regex** for pattern matching
- **Pillow** and **OpenCV** for image handling

---

## 📂 Folder Structure

