import re

def extract_case_references(text):
    """Extract potential case references from email subject/body"""
    references = []
    
    # Pattern 1: Our format XX-###/YY
    pattern1 = r'[A-Z]{1,3}-\d{1,4}/\d{2}'
    references.extend(re.findall(pattern1, text))
    
    # Pattern 2: #12345
    pattern2 = r'#\d{3,6}'
    references.extend(re.findall(pattern2, text))
    
    # Pattern 3: Case 12345 or Matter 12345
    pattern3 = r'(?:Case|Matter|File)\s*[:#]?\s*(\d{3,6})'
    matches = re.findall(pattern3, text, re.IGNORECASE)
    references.extend([f"#{m}" for m in matches])
    
    # Pattern 4: ICC/2024/001 style
    pattern4 = r'[A-Z]{2,4}/\d{4}/\d{3,4}'
    references.extend(re.findall(pattern4, text))
    
    return list(set(references))  # Remove duplicates

def test_patterns():
    """Test the pattern matching"""
    test_texts = [
        "Re: AB-001/26 - Document submission",
        "Urgent: Case #12345 needs review",
        "Matter: 54321 - Response due",
        "ICC/2024/001 - Hearing scheduled",
        "AB-002/26 and CD-003/25 combined"
    ]
    
    for text in test_texts:
        refs = extract_case_references(text)
        print(f"Text: {text}")
        print(f"Found: {refs}\n")

if __name__ == "__main__":
    test_patterns()