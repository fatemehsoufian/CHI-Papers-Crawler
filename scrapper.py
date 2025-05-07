import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import undetected_chromedriver as uc

START_URL = "https://dl.acm.org/doi/proceedings/10.1145/3613904"
SESSION_SELECTOR = ".toc__section.accordion-tabbed__tab"
OPEN_SESSION_SELECTOR = ".toc__section.accordion-tabbed__tab.js--open"
PAPER_SELECTOR = ".issue-item__title"
SESSION_TITLE_SELECTOR = ".section__title.accordion-tabbed__control.left-bordered-title"
SESSIONS_SECTION_SELECTOR = ".accordion.sections"

def start_driver():
    """
    Initialize and return an undetected Chrome WebDriver instance.

    Uses undetected_chromedriver with default options to help bypass bot detection mechanisms.
    """
    options = uc.ChromeOptions()
    return uc.Chrome(options=options)

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

def expand_session(web_element: WebElement,expand:bool):
    """
    Expand or collapse a session element based on its current state and the desired action.

    Parameters:
        web_element (WebElement): The session element to interact with.
        expand (bool): If True, the function will expand the session if it is collapsed.
                       If False, it will collapse the session if it is expanded.

    Behavior:
        - If the current state doesn't match the desired state, it performs a click to toggle it.
        - Logs the action taken (expanded, collapsed, or already in desired state).
    """
    is_expanded = web_element.find_element(By.CSS_SELECTOR,SESSION_TITLE_SELECTOR)\
                                        .get_attribute("aria-expanded")

    if (is_expanded == "false" and expand):
        session.click()
        print("🔽 Expanded")
        time.sleep(2)
    elif(is_expanded == "true" and not expand):
        session.click()
        print("🔼 Collapsed")
        time.sleep(2)
    elif (is_expanded == "true" and expand):
        print("✅ Already expanded")
    elif(is_expanded == "false" and not expand):
        print("✅ Already collapsed")
driver = start_driver()
driver.get(START_URL)
time.sleep(4)
accept_cookies()

paper_info = []

elements = driver.find_elements(By.CSS_SELECTOR, SESSION_SELECTOR)
sessions = [el for el in elements if "SESSION" in el.text]
print(f"📚 Found {len(sessions)} sessions")

sessions_section = driver.find_element(By.CSS_SELECTOR, SESSIONS_SECTION_SELECTOR)

for session in sessions:
    expand_session(session,True)
    time.sleep(5)

    open_elements = sessions_section.find_elements(By.CSS_SELECTOR,OPEN_SESSION_SELECTOR)
    open_session =  [el for el in open_elements if  el.text.startswith("SESSION")]

    if len(open_session)==1:
        current_session = open_session[0]
    else:
        current_session = open_session[1]

    papers = current_session.find_elements(By.CSS_SELECTOR, PAPER_SELECTOR)
    session_title = current_session.find_element(By.CSS_SELECTOR,SESSION_TITLE_SELECTOR).text

    for paper in papers:
        try:
            title = paper.text.strip()
            link = paper.find_element(By.TAG_NAME, "a").get_attribute("href")
            session_name = session_title[len("SESSION: "):].strip()

            paper_info.append({"session":session_name , "title": title, "URL": link})
            print(f"✅ Added paper titled '{title}' under session: {session_name}")
        except Exception as e:
            print("⚠️ Error reading paper:", e)
    expand_session(session,False)
    time.sleep(5)

driver.quit()

# Save to CSV
df = pd.DataFrame(paper_info)
CSV_FILE_NAME = "papers_CHI24.csv"
df.to_csv(CSV_FILE_NAME, index=False)

print(f"✅ Scraping complete. Saved {len(df)} papers to {CSV_FILE_NAME}")
