import os
import json
import time
import pandas as pd
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

CSV_PATH = "output24.csv"
OUTPUT_DIR = "json_papers_24"
PAPER_YEAR = "2024"
WAIT_TIME = 4  # seconds to wait for content to load

AUTHOR_GROUP_SELECTOR = "authorGroup"
AUTHOR_SELECTOR = "author"

options = uc.ChromeOptions()
driver = uc.Chrome(options=options)

os.makedirs(OUTPUT_DIR, exist_ok=True)
df = pd.read_csv(CSV_PATH)

for i, row in df.iterrows():
    url = row['Content Url']
    session = row['session']
    title = row['title']
    authors_list = []

    try:
        print(f"🔎 [{i+1}/{len(df)}] Processing: {url}")
        driver.get(url)
        time.sleep(WAIT_TIME)

        # Extract author names
        author_group = driver.find_element(By.CLASS_NAME,AUTHOR_GROUP_SELECTOR)
        authors = author_group.find_elements(By.CLASS_NAME,AUTHOR_SELECTOR)
        for author in authors:
            authors_list.append(author.text)

       # Extract content in visual order (headings, paragraphs, bullet points)
        elements = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6, p, li")
        output_lines = []

        for el in elements:
            tag = el.tag_name.lower()
            text = el.text.strip()
            if not text:
                continue

            if tag.startswith("h"):
                level = int(tag[1])
                output_lines.append("#" * level + " " + text)
            elif tag == "li":
                output_lines.append("- " + text)
            else:
                output_lines.append(text)

        CONTENT = "\n".join(output_lines)

        if not CONTENT.strip():
            print("⚠️ Empty content, skipping...")
            continue

        # Create filename from DOI suffix
        paper_id = url.split("/")[-1].replace(".", "_")
        FILE_NAME = f"{paper_id}.json"
        filepath = os.path.join(OUTPUT_DIR, FILE_NAME)

        # Save JSON
        paper_data = {
            "title": title,
            "session": session,
            "year": PAPER_YEAR,
            "url": url,
            "authors": authors_list,
            "text": CONTENT,
                            }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(paper_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved to {filepath}")

    except Exception as e:
        print(f"❌ Failed to process {url}: {e}")

driver.quit()
