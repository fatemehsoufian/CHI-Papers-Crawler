"""
Module to fetch and process content URLs for papers.
"""
import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

PAPER_FORMATS_SELECTOR = ".btn.btn--primary.btn--other"
PAPER_HTML_FORMAT_SELECTOR = ".btn.btn--htmlFull.blue"
PAPER_PDF_FORMAT_SELECTOR = ".btn.btn--pdf.red"

options = uc.ChromeOptions()
driver = uc.Chrome(options=options)

def accept_cookies():
    """
    Attempt to accept the cookie consent popup on the current page.
    """
    try:
        btn = driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
        btn.click()
        print("✅ Cookies accepted!")
        time.sleep(5)
    except Exception:
        print("ℹ️ No cookie popup found.")

def get_content_url(paper_url):
    driver.get(paper_url)
    time.sleep(4)
    accept_cookies()
    paper_formats_button = driver.find_element(By.CSS_SELECTOR,PAPER_FORMATS_SELECTOR)
    paper_formats_button.click()
    time.sleep(5)
    try:
        paper_html_format_btn = driver.find_element(By.CSS_SELECTOR,PAPER_HTML_FORMAT_SELECTOR)
        content_url = paper_html_format_btn.get_attribute("href")
        is_html_format = True
    except NoSuchElementException:
        paper_pdf_format_btn = driver.find_element(By.CSS_SELECTOR,PAPER_PDF_FORMAT_SELECTOR)
        content_url = paper_pdf_format_btn.get_attribute("href")
        is_html_format = False

    return content_url, is_html_format

papers_chi = pd.read_csv("papers_CHI24.csv")

papers_chi['Content Url'] = ''
papers_chi['Paper Format'] = ''

for index, row in papers_chi.iterrows():
    print(f"⏳ Processing row {index + 1} of {len(papers_chi)}")
    content_link, content_type = get_content_url(row["URL"])
    papers_chi.at[index, 'Content Url'] = content_link
    papers_chi.at[index, 'Paper Format'] = "html" if content_type else "pdf"
    papers_chi.to_csv("temp.csv",index=False)

driver.quit()

papers_chi.to_csv("output24.csv", index=False)
