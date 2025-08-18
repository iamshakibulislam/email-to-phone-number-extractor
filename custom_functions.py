import requests
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def get_snippets(email):

  url = "https://google.serper.dev/search"

  payload = json.dumps({
    "q": f"\"{email}\" phone number"
  })
  headers = {
    'X-API-KEY': 'e2aed72c86b426753ba54facb980396368691ccb',
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  snippets = ""

  for snippet in json.loads(response.text)["organic"]:

    snippets += snippet["snippet"]

  return snippets



#print(get_snippets("kuree@ninalemsparty.com"))




def extract_phone_numbers(text):
    # Regex pattern to find phone numbers:
    # Matches optional +country code (like +88 or +1), 
    # then digits with optional spaces, hyphens or dots between them,
    # ending at word boundary or punctuation (.,;:)
    phone_pattern = re.compile(r'''
        (?:\+?\d{1,3}[\s\-\.]?)?       # optional country code +1 or +88 etc
        (?:\(?\d{2,4}\)?[\s\-\.]?)?    # optional area code in parenthesis (012), (02), etc
        (?:\d{2,4}[\s\-\.]?){2,5}      # main number parts, 2-5 groups of 2-4 digits separated by space/hyphen/dot
        \d+                            # last digits (to ensure number ends with digit)
        ''', re.VERBOSE)

    matches = phone_pattern.findall(text)
    
    # Normalize function: remove +country code, spaces, hyphens, dots, parentheses
    def normalize(number):
        # Remove everything except digits
        digits = re.sub(r'\D', '', number)
        
        # Optionally remove country code if you want fixed-length numbers or starting digits
        # Here, for example, remove leading '88' or '1' if you want to strip country codes like +88, +1
        # Adjust as per your country codes list
        if digits.startswith('88'):
            digits = digits[2:]
        elif digits.startswith('1'):
            digits = digits[1:]
        return digits

    normalized_numbers = []
    for num in matches:
        norm = normalize(num)
        if norm and norm not in normalized_numbers:
            normalized_numbers.append(norm)
    
    return normalized_numbers #returns list of phone numbers found in a python list



def visit_and_extract_phone_info(phone_number):
    """
    this function returns name accociated of the phone number , like John Doe 
    """
    url = f"https://www.zabasearch.com/phone/{phone_number}"
    
    options = Options()
    options.add_argument("--headless")  # headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/115.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        time.sleep(3)  # wait for page to load
        
        xpath = '//*[@id="result-top-content"]/div[1]/table[1]/tbody/tr/td[2]/table[1]/tbody/tr[2]/td/h3'
        try:
            elem = driver.find_element(By.XPATH, xpath)
            text = elem.text.strip()
            return text if text else None
        except NoSuchElementException:
            return None
    finally:
        driver.quit()


