import os
import json
import time
import pandas as pd
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

CSV_PATH = "papers_CHI24.csv"
OUTPUT_DIR = "json_papers"
WAIT_TIME = 4  # seconds to wait for content to load

options = uc.ChromeOptions()
driver = uc.Chrome(options=options)

os.makedirs(OUTPUT_DIR, exist_ok=True)
df = pd.read_csv(CSV_PATH)

for i, row in df.iterrows():
    url = row['Content Url']
    session = row['session']
    title = row['title']

    try:
        print(f"🔎 [{i+1}/{len(df)}] Processing: {url}")
        driver.get(url)
        time.sleep(WAIT_TIME)

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

        content = "\n".join(output_lines)

        if not content.strip():
            print("⚠️ Empty content, skipping...")
            continue

        # Create filename from DOI suffix
        paper_id = url.split("/")[-1].replace(".", "_")
        file_name = f"{paper_id}.json"
        filepath = os.path.join(OUTPUT_DIR, file_name)

        # Save JSON
        paper_data = {
            "url": url,
            "title": title,
            "session": session,
            "text": content,
            "extracted_on": time.strftime("%Y-%m-%d")
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(paper_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved to {filepath}")

    except Exception as e:
        print(f"❌ Failed to process {url}: {e}")

driver.quit()
