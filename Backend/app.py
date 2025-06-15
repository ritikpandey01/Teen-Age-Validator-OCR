import cv2
import pytesseract
import re
import numpy as np
from datetime import datetime
from fuzzywuzzy import fuzz
from dateutil.parser import parse
from typing import Dict, Union, Optional, Tuple
import json
import sys

# Configure Tesseract path (update this to your installation path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class AadhaarVerifier:
    """Advanced Aadhaar verification system with improved OCR and validation"""
    
    def __init__(self):
        # Configure Tesseract parameters
        self.tesseract_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz/:,-. '
        
        # Name validation parameters
        self.min_name_similarity = 75  # Fuzzy matching threshold for names
        self.max_name_length = 40      # Maximum expected name length
        
        # Date formats to try
        self.date_formats = [
            '%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%Y/%m/%d',
            '%d-%b-%Y', '%d/%b/%Y', '%d-%B-%Y', '%d/%B/%Y'
        ]
        
        # Aadhaar number validation regex
        self.aadhaar_regex = re.compile(r'\b(\d{4}\s?\d{4}\s?\d{4})\b')
        
        # Name extraction patterns
        self.name_patterns = [
            r'(?:Name|name|नाम|NAME)\s*[:]?\s*([^\n]+)',  # English and Hindi
            r'To\s+(.+)',                                   # Common in Aadhaar letters
            r'(?:Mr\.?|Ms\.?|Mrs\.?|Shri|Smt|Km)\s+(.+)',  # Common prefixes
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)$'          # Capitalized names
        ]
    
    def preprocess_image(self, img: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Apply multiple preprocessing techniques to enhance OCR accuracy"""
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. Simple thresholding
        _, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 2. Adaptive thresholding
        thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)
        
        # 3. Denoising
        denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
        
        # 4. Edge-preserving filtering
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)
        
        return thresh1, thresh2, filtered
    
    def extract_text(self, img: np.ndarray) -> str:
        """Extract text from image using multiple OCR approaches"""
        # Try with different preprocessing and configurations
        texts = []
        
        # Standard extraction
        texts.append(pytesseract.image_to_string(img, lang='eng', config=self.tesseract_config))
        
        # Try with inverted image (for white text on dark background)
        inverted = cv2.bitwise_not(img)
        texts.append(pytesseract.image_to_string(inverted, lang='eng', config=self.tesseract_config))
        
        # Try with different page segmentation modes
        for psm in [4, 6, 11]:  # Different PSM modes that might work better
            texts.append(pytesseract.image_to_string(img, lang='eng', config=f'--psm {psm}'))
        
        # Combine all results with line breaks
        return "\n".join([t for t in texts if t.strip()])
    
    def extract_name(self, text: str, input_name: str) -> Optional[str]:
        """Enhanced name extraction with multiple patterns and validation"""
        best_match = None
        best_score = 0
        
        # Try all name patterns
        for pattern in self.name_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                candidate = match.group(1).strip()
                # Validate candidate name
                if self.validate_name_candidate(candidate, input_name):
                    score = fuzz.ratio(input_name.lower(), candidate.lower())
                    if score > best_score:
                        best_match = candidate
                        best_score = score
        
        # If no pattern match, try line-by-line fuzzy matching
        if best_score < self.min_name_similarity:
            for line in text.split('\n'):
                line = line.strip()
                if 3 < len(line) < self.max_name_length and not re.search(r'\d', line):
                    score = fuzz.partial_ratio(input_name.lower(), line.lower())
                    if score > best_score:
                        best_match = line
                        best_score = score
        
        return best_match if best_score >= self.min_name_similarity else None
    
    def validate_name_candidate(self, candidate: str, input_name: str) -> bool:
        """Validate if a candidate name is plausible"""
        # Check basic conditions
        if not candidate or len(candidate) > self.max_name_length:
            return False
        
        # Check if it contains mostly letters and spaces
        if not re.match(r'^[A-Za-z\s\-\.]+$', candidate):
            return False
        
        # Check similarity with input name
        input_first_name = input_name.split()[0].lower()
        candidate_first_name = candidate.split()[0].lower()
        
        return (fuzz.ratio(input_first_name, candidate_first_name) > 60 or
                input_first_name in candidate.lower())
    
    def extract_dob(self, text: str) -> Optional[str]:
        """Extract and validate date of birth with multiple formats"""
        # First try structured patterns
        date_patterns = [
            r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b',  # dd-mm-yyyy
            r'\b(\d{4}[/-]\d{2}[/-]\d{2})\b',  # yyyy-mm-dd
            r'\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b',  # 12 Mar 2005
            r'\b(?:DOB|Dob|dob|Date of Birth|जन्म तिथि)\s*[:]?\s*([^\n]+)'  # With label
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                try:
                    # Parse with dateutil which handles many formats
                    parsed_date = parse(date_str, dayfirst=True)
                    return parsed_date.strftime('%d-%m-%Y')
                except ValueError:
                    continue
        
        return None
    
    def extract_aadhaar(self, text: str) -> Optional[str]:
        """Extract and validate Aadhaar number"""
        # Try standard pattern
        match = self.aadhaar_regex.search(text)
        if match:
            aadhaar = match.group(1).replace(' ', '')
            # Basic validation (Aadhaar doesn't start with 0 or 1)
            if len(aadhaar) == 12 and aadhaar[0] not in ['0', '1']:
                return aadhaar
        
        # Try with label
        label_patterns = [
            r'(?:Aadhaar|Aadhar|आधार|UID)\s*(?:Number|No\.?)?\s*[:]?\s*(\d{4}\s?\d{4}\s?\d{4})',
            r'\d{4}\s?\d{4}\s?\d{4}(?=\s*\(?\d{1,2}\)?)'  # Followed by (optional) version
        ]
        
        for pattern in label_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                aadhaar = match.group(1).replace(' ', '')
                if len(aadhaar) == 12 and aadhaar[0] not in ['0', '1']:
                    return aadhaar
        
        return None
    
    def verify_details(self, extracted: Dict[str, Optional[str]], 
                      input_name: str, input_dob: str, input_aadhaar: str) -> Dict[str, bool]:
        """Verify extracted details against input details"""
        results = {
            'name_match': False,
            'dob_match': False,
            'aadhaar_match': False
        }
        
        # Name verification (fuzzy matching)
        if extracted['name'] and input_name:
            similarity = fuzz.token_sort_ratio(input_name.lower(), extracted['name'].lower())
            results['name_match'] = similarity >= self.min_name_similarity
        
        # DOB verification (multiple formats)
        if extracted['dob'] and input_dob:
            try:
                # Normalize both dates
                extracted_date = parse(extracted['dob'], dayfirst=True)
                input_date = parse(input_dob, dayfirst=True)
                results['dob_match'] = extracted_date == input_date
            except ValueError:
                results['dob_match'] = False
        
        # Aadhaar verification (exact match after normalization)
        if extracted['aadhaar'] and input_aadhaar:
            results['aadhaar_match'] = (
                extracted['aadhaar'].replace(' ', '') == 
                input_aadhaar.replace(' ', '')
            )
        
        results['all_match'] = all(results.values())
        
        return results
    
    def calculate_age(self, dob_str: Optional[str]) -> Optional[int]:
        """Calculate age from DOB string"""
        if not dob_str:
            return None
        
        try:
            dob = parse(dob_str, dayfirst=True)
            today = datetime.now()
            age = today.year - dob.year
            if (today.month, today.day) < (dob.month, dob.day):
                age -= 1
            return age
        except ValueError:
            return None
    
    def verify_aadhaar(self, image_path: str, 
                      input_name: str, input_dob: str, input_aadhaar: str) -> Dict[str, Union[bool, str, int, Dict]]:
        """Main verification method"""
        try:
            # Read the image
            img = cv2.imread(image_path)
            if img is None:
                return {'error': 'Could not read image file'}
            
            # Preprocess image
            thresh1, thresh2, filtered = self.preprocess_image(img)
            
            # Extract text from all versions
            texts = [
                self.extract_text(thresh1),
                self.extract_text(thresh2),
                self.extract_text(filtered)
            ]
            
            # Combine text with markers for debugging
            combined_text = "\n---\n".join(texts)
            print("Extracted Text from all methods:")
            print(combined_text)
            print("-" * 50)
            
            # Extract details using the best available text
            extracted = {
                'name': None,
                'dob': None,
                'aadhaar': None
            }
            
            # Try each text version until we find good matches
            for text in texts:
                if not extracted['name']:
                    extracted['name'] = self.extract_name(text, input_name)
                if not extracted['dob']:
                    extracted['dob'] = self.extract_dob(text)
                if not extracted['aadhaar']:
                    extracted['aadhaar'] = self.extract_aadhaar(text)
                
                # If we found all details, stop early
                if all(extracted.values()):
                    break
            
            # Verify matches
            verification = self.verify_details(extracted, input_name, input_dob, input_aadhaar)
            
            # Calculate age
            age = self.calculate_age(extracted['dob'])
            is_teen = age is not None and 13 <= age < 20
            
            return {
                'success': True,
                'all_match': verification['all_match'],
                'name_match': verification['name_match'],
                'dob_match': verification['dob_match'],
                'aadhaar_match': verification['aadhaar_match'],
                'age': age,
                'is_teen': is_teen,
                'extracted': extracted,
                'debug_text': combined_text  # For troubleshooting
            }
        
        except Exception as e:
            return {
                'error': f"Verification failed: {str(e)}",
                'success': False
            }

# Example usage
if __name__ == "__main__":
    # Load input from JSON file
    json_file_path = "input/input.json"  # Path to your JSON file
    try:
        with open(json_file_path, 'r') as file:
            input_data = json.load(file)
        
        # Extract details from JSON
        input_name = input_data.get('name', '')
        input_dob = input_data.get('dob', '')
        input_aadhaar = input_data.get('aadhaar', '')
        
        # Validate that all required fields are present
        if not all([input_name, input_dob, input_aadhaar]):
            raise ValueError("Missing required fields in JSON file")
    
    except FileNotFoundError:
        print(f"Error: Could not find {json_file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: {json_file_path} contains invalid JSON")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

    verifier = AadhaarVerifier()
    
    # Use the JSON data in verification
    result = verifier.verify_aadhaar(
        image_path="input/x.png",
        input_name=input_name,
        input_dob=input_dob,
        input_aadhaar=input_aadhaar
    )
    
    if not result.get('success', False):
        print(f"Error: {result.get('error', 'Unknown error')}")
    else:
        print("\nAdvanced Aadhaar Verification Results:")
        print(f"All details match: {'Yes' if result['all_match'] else 'No'}")
        print(f"Name matches: {'Yes' if result['name_match'] else 'No'} ({result['extracted']['name'] or 'Not found'})")
        print(f"DOB matches: {'Yes' if result['dob_match'] else 'No'} ({result['extracted']['dob'] or 'Not found'})")
        print(f"Aadhaar matches: {'Yes' if result['aadhaar_match'] else 'No'} ({result['extracted']['aadhaar'] or 'Not found'})")


        print("\nExtracted Details:")
        print(f"Name: {result['extracted']['name'] or 'Not found'}")
        print(f"DOB: {result['extracted']['dob'] or 'Not found'}")
        print(f"Aadhaar: {result['extracted']['aadhaar'] or 'Not found'}")
        
        if result['age'] is not None:
            print(f"Age: {result['age']} ({'Teen' if result['is_teen'] else 'Not teen'})")
        
        debug = input("\nShow debug text? (y/n): ").lower()
        if debug == 'y':
            print("\nDebug Text:")
            print(result.get('debug_text', 'No debug text available'))

from image_recognition.image_recognizer import ImageRecognizer

class AadhaarVerifier:
    def __init__(self, image_recognition_model_path=None):
        # ... existing initialization code ...
        
        # Initialize image recognizer if path provided
        self.image_recognizer = None
        if image_recognition_model_path:
            try:
                self.image_recognizer = ImageRecognizer(image_recognition_model_path)
            except Exception as e:
                print(f"Warning: Could not load image recognition model: {str(e)}")

    def verify_aadhaar(self, image_path: str, 
                      input_name: str, input_dob: str, input_aadhaar: str,
                      run_image_recognition: bool = False) -> Dict[str, Union[bool, str, int, Dict]]:
        """
        Updated verification method with optional image recognition
        """
        # ... existing verification code ...
        
        # Add image recognition if requested and model is available
        image_recognition_results = None
        if run_image_recognition and self.image_recognizer:
            try:
                image_recognition_results = self.image_recognizer.predict(image_path)
            except Exception as e:
                image_recognition_results = {"error": str(e)}
        
        # Add to return dictionary
        result = {
            # ... existing results ...
            'image_recognition': image_recognition_results
        }
        
        return result