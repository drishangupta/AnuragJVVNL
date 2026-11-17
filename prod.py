import pandas as pd
from hashids import Hashids
import time
import requests
from PIL import Image, ImageEnhance
from io import BytesIO
import cv2
import numpy as np
import pytesseract

# ---------------- CONFIG ---------------- #

INPUT_FILE = "input.xlsx"     # must have Number column
OUTPUT_FILE = "output.xlsx"

# If Windows and PATH not set:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

BASE_URL = "https://www.bijlimitra.com"

# Hashids config
h = Hashids(
    salt="9vZkqYw1QhX3lB2z+7tHhA6pWm9rJcF0yDqzXnVb5gU=",
    min_length=8
)

# ---------------- CAPTCHA SOLVER ---------------- #

def solve_captcha(captcha_bytes):
    """
    Takes captcha image bytes
    Returns OCR text
    """

    img = Image.open(BytesIO(captcha_bytes))

    # Convert to grayscale
    img = img.convert("L")

    # Increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(3)

    # Resize bigger for better OCR
    img = img.resize((img.width * 4, img.height * 4))

    # Convert to OpenCV
    img_np = np.array(img)

    # Threshold
    _, thresh = cv2.threshold(
        img_np,
        150,
        255,
        cv2.THRESH_BINARY
    )

    # OCR config
    config = (
        r'--oem 3 --psm 8 '
        r'-c tessedit_char_whitelist='
        r'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    )

    text = pytesseract.image_to_string(
        thresh,
        config=config
    )

    captcha_text = text.strip().replace(" ", "")

    return captcha_text


# ---------------- FETCH ACCOUNT DETAILS ---------------- #

def fetch_account_details(number):
    number = int(number)

    # Encode KNO
    encoded = h.encode(number)

    # Step 1: Fetch captcha
    timestamp_ms = int(time.time() * 1000)

    captcha_response = requests.get(
        f"{BASE_URL}/captchaimage?{timestamp_ms}",
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": f"{BASE_URL}/customerLoginPage"
        }
    )

    # Save cookies from captcha response
    cookies = captcha_response.cookies.get_dict()

    # OCR captcha
    captcha_text = solve_captcha(captcha_response.content)

    print(f"\nNumber   : {number}")
    print(f"Encoded  : {encoded}")
    print(f"Captcha  : {captcha_text}")
    print(f"Cookies  : {cookies}")

    # Step 2: Call account details API
    response = requests.get(
        f"{BASE_URL}/accountdetailsByKnoBeforeLogin",
        params={
            "kno": encoded,
            "captcha": captcha_text
        },
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": f"{BASE_URL}/customerLoginPage"
        },
        cookies=cookies
    )

    try:
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            record = data[0]

            amount_due = record.get("amtBeforeDue", "")
            due_date = record.get("duedatecash", "")

            return {
                "Number": number,
                "Amount Due": amount_due,
                "Due Date": due_date
            }

        else:
            return {
                "Number": number,
                "Amount Due": "No Data",
                "Due Date": "No Data"
            }

    except Exception as e:
        return {
            "Number": number,
            "Amount Due": f"ERROR: {str(e)}",
            "Due Date": ""
        }


# ---------------- MAIN ---------------- #

def main():
    df = pd.read_excel(INPUT_FILE)

    if "Number" not in df.columns:
        raise Exception("Excel must contain a 'Number' column")

    results = []

    for number in df["Number"]:
        try:
            result = fetch_account_details(number)
            results.append(result)

        except Exception as e:
            results.append({
                "Number": number,
                "Amount Due": f"ERROR: {str(e)}",
                "Due Date": ""
            })

    # Save output
    output_df = pd.DataFrame(results)
    output_df.to_excel(OUTPUT_FILE, index=False)

    print(f"\nDone! Saved to {OUTPUT_FILE}")


# Run
if __name__ == "__main__":
    main()