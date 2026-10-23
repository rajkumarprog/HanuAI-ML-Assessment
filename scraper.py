
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

try:
    driver.get("https://example.com")
    print("Page title:", driver.title)
    print("Page URL:", driver.current_url)
finally:
    driver.quit()
