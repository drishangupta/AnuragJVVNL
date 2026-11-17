import time
import requests
from hashids import Hashids
from PIL import Image
from io import BytesIO

# Hardcoded value
NUMBER = 211463017971

# Encode
h = Hashids(
    salt="9vZkqYw1QhX3lB2z+7tHhA6pWm9rJcF0yDqzXnVb5gU=",
    min_length=8
)

encoded = h.encode(NUMBER)
print("Encoded:", encoded)

# Fetch captcha
timestamp_ms = int(time.time() * 1000)

captcha_response = requests.get(
    f"https://www.bijlimitra.com/captchaimage?{timestamp_ms}",
    headers={
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.bijlimitra.com/customerLoginPage"
    }
)

# Extract JSESSIONID from captcha response
cookies = captcha_response.cookies.get_dict()
print("Cookies:", cookies)

# Save captcha image for OCR
img = Image.open(BytesIO(captcha_response.content))
img.save("captcha.png")
img.show()

captcha_text = input("Enter captcha manually: ").strip()

# API request WITH SAME COOKIE
response = requests.get(
    f"https://www.bijlimitra.com/accountdetailsByKnoBeforeLogin?kno={encoded}&captcha={captcha_text}",
    headers={
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.bijlimitra.com/customerLoginPage"
    },
    cookies=cookies
)

print(response.text)