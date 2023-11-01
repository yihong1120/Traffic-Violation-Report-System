# from PIL import Image
# import pytesseract

# def ocr_core(filename):
#     """
#     This function will handle the core OCR processing of images.
#     """
#     text = pytesseract.image_to_string(Image.open(filename), lang='chi_tra')  # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
#     return text

# print(ocr_core('img_recognition.jpg'))



import re

def extract_info(text):
    # Extract date and time
    date_time_match = re.search(r'\d{4}年\d{1,2}月\d{1,2}日 \d{2}:\d{2}', text)
    date_time = date_time_match.group() if date_time_match else None

    # Extract postal code
    postal_code_match = re.search(r'\d{6}', text)
    postal_code = postal_code_match.group() if postal_code_match else None

    # Extract address
    address_match = re.search(r'\w+路\d+號', text)
    address = address_match.group() if address_match else None

    return date_time, postal_code, address

text = """
2023年9月22日 23:01 六
404018 TXG 廁記

wsgas 學士路95號
4 設匿院 Q
"""

date_time, postal_code, address = extract_info(text)
print(f"Date and Time: {date_time}")
print(f"Postal Code: {postal_code}")
print(f"Address: {address}")



# This is a simplified example, you would need a complete mapping for all postal codes
postal_code_mapping = {
    '404018': '台中市北區'
}

def get_address(postal_code, street_address):
    city_district = postal_code_mapping.get(postal_code)
    if city_district:
        return city_district + street_address
    else:
        return None

postal_code = '404018'
street_address = '學士路95號'
full_address = get_address(postal_code, street_address)

if full_address:
    print(f"Full Address: {full_address}")
else:
    print("Postal code not found in the mapping.")



def create_postal_code_mapping():
    mapping = {
        '100': '臺北市中正區',
        '103': '臺北市大同區',
        '104': '臺北市中山區',
        '105': '臺北市松山區',
        # ... add all other postal codes
    }
    return mapping

def get_address(postal_code, street_address, mapping):
    city_district = mapping.get(postal_code)
    if city_district:
        return city_district + street_address
    else:
        return None

postal_code_mapping = create_postal_code_mapping()

postal_code = '104'
street_address = '學士路95號'
full_address = get_address(postal_code, street_address, postal_code_mapping)

if full_address:
    print(f"Full Address: {full_address}")
else:
    print("Postal code not found in the mapping.")