from hashids import Hashids
import time
import requests
from PIL import Image
from io import BytesIO
import easyocr

reader = easyocr.Reader(['en'])


h = Hashids(
    salt="9vZkqYw1QhX3lB2z+7tHhA6pWm9rJcF0yDqzXnVb5gU=",
    min_length=8
)

print(h.encode(211463017971))
print(h.decode("LxR5Q0O0"))

timestamp_ms = int(time.time() * 1000)
print(timestamp_ms)

captcha = requests.get(f"https://www.bijlimitra.com/captchaimage?{timestamp_ms}")

from PIL import Image, ImageEnhance
import cv2
import numpy as np
import pytesseract

# If Windows and PATH not set:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load image
img = Image.open("captcha.png")

# 1. Convert to grayscale
img = img.convert("L")

# 2. Increase contrast
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(3)

# Convert to OpenCV format
img_np = np.array(img)

# 3. Threshold
_, thresh = cv2.threshold(img_np, 150, 255, cv2.THRESH_BINARY)

# 4. OCR config
config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

# OCR
text = pytesseract.image_to_string(thresh, config=config)

print("Detected:", text.strip())

# Show processed image (debug)
cv2.imshow("Processed", thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()