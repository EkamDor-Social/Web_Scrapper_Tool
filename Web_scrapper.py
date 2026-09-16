import csv
import re
import time
import pickle
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException,NoSuchWindowException

USERNAME="your_username"
PASSWORD="your_password"
LOGIN_WAIT_SECONDS=50
BATCH_SIZE=20
SEEN_FILE="seen_urls.pkl"
TIMESTAMP=datetime.now().strftime("%Y%m%d%H%M")
OUTPUT_FILE=f"{TIMESTAMP}_instagram_data.csv"
CSV_FIELDS=["type","url","caption","mentions","hashtags","location","timestamp"]
MAX_EMPTY_SCRAPE_ITERATIONS = 2  # how many consecutive loops with 0 scraped before exit
MIN_NEW_LINKS_PER_ITER = 3       # require at least this many new links to consider it a “real” iteration

def create_driver():
    options=webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    driver=webdriver.Chrome(options=options)
    return driver

def setup_csv():
    with open(OUTPUT_FILE,"w",newline="",encoding="utf-8") as f:
        csv.DictWriter(f,fieldnames=CSV_FIELDS).writeheader()

def save_batch_to_csv(batch_data):
    if not batch_data:
        return
    try:
        with open(OUTPUT_FILE,"a",newline="",encoding="utf-8") as f:
            csv.DictWriter(f,fieldnames=CSV_FIELDS).writerows(batch_data)
        print(f"Saved batch: {len(batch_data)}")
    except Exception as e:
        print(f"CSV save error: {e}")
#duplicate reel skipped 
def load_seen_urls():
    try:
        with open(SEEN_FILE,"rb") as f:
            data=pickle.load(f)
            return data if isinstance(data,dict) else {}
    except Exception:
        return {}

def save_seen_urls(seen_urls):
    try:
        with open(SEEN_FILE,"wb") as f:
            pickle.dump(seen_urls,f)
        print("Seen url saved file updated")
    except Exception as e:
        print(f"Seen URL save error: {e}")

def login_instagram(driver):
    print("\n--- PHASE 1: LOGIN ---")
    driver.get("https://www.instagram.com/accounts/login/")
    try:
        wait=WebDriverWait(driver,15)
        username=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"input[name='username'],input[name='email']")))
        username.clear()
        username.send_keys(USERNAME)
        password=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"input[name='password'],input[name='pass']")))
        password.clear()
        password.send_keys(PASSWORD)
        print("Username and password autofilled.")
        print("Press Login manually.")
    except Exception as e:
        print(f"Autofill error: {e}")
        print("Enter credentials manually.")
    print(f"Waiting {LOGIN_WAIT_SECONDS} seconds for login/CAPTCHA/2FA.")
    time.sleep(LOGIN_WAIT_SECONDS)
    print("Login wait completed.")

def open_explore(driver):
    print("\n--- OPENING EXPLORE ---")
    try:
        driver.get("https://www.instagram.com/explore/")
        WebDriverWait(driver,15).until(EC.presence_of_element_located((By.TAG_NAME,"body")))
        driver.execute_script("window.scrollBy(0,900);")
        time.sleep(1.5) 
        driver.execute_script("window.scrollBy(0,900);")
        time.sleep(2.5)
        print("Explore loaded.")
        return True
    except Exception as e:
        print(f"Explore error: {e}")
        return False

def normalize_url(url):
    if not url:
        return ""
    return url.split("?")[0].rstrip("/")

def find_post_links(driver):
    links=[]
    try:
        anchors=driver.find_elements(By.CSS_SELECTOR,"a[href*='/p/'],a[href*='/reel/']")
        for anchor in anchors:
            url=normalize_url(anchor.get_attribute("href"))
            if url and url not in links:
                links.append(url)
    except Exception:
        pass
    return links

def collect_new_links(driver,seen_urls):
    new_links=[]
    for url in find_post_links(driver):
        try:
            seen_urls[url] 
            pass
        except:
            if url not in new_links:
                new_links.append(url)
    return new_links

def extract_caption(driver):
    try:
        meta=driver.find_element(By.CSS_SELECTOR,"meta[property='og:description']")
        text=(meta.get_attribute("content") or "").strip()
        if text:
            match=re.search(r':\s*"([\s\S]*?)"\s*(?:\.|$)',text)
            if match:
                return match.group(1).strip()
            return text
    except Exception:
        pass
    for selector in ["article h1","article div[dir='auto']"]:
        try:
            for element in driver.find_elements(By.CSS_SELECTOR,selector):
                text=element.text.strip()
                if text and len(text)>2:
                    return text
        except Exception:
            pass
    return ""

def extract_timestamp(driver):
    try:
        element=driver.find_element(By.TAG_NAME,"time")
        return element.get_attribute("datetime") or ""
    except Exception:
        return ""

def extract_location(driver):
    try:
        links=driver.find_elements(By.CSS_SELECTOR,"a[href*='/explore/locations/']")
        for link in links:
            text=link.text.strip()
            if text and text.lower() not in ["location","locations"]:
                return text
    except Exception:
        pass
    return ""

def extract_metadata(driver,url):
    caption=extract_caption(driver)
    hashtags=list(dict.fromkeys(re.findall(r"#[A-Za-z0-9_]+",caption)))
    mentions=list(dict.fromkeys(re.findall(r"@[A-Za-z0-9_.]+",caption)))
    return {
        "type":"reel" if "/reel/" in url else "post",
        "url":url,
        "caption":caption,
        "mentions":", ".join(mentions),
        "hashtags":", ".join(hashtags),
        "location":extract_location(driver),
        "timestamp":extract_timestamp(driver)
    }

def scrape_url(driver,url):
    try:
        driver.get(url)
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.TAG_NAME,"body")))
        try:
            WebDriverWait(driver,5).until(EC.presence_of_element_located((By.TAG_NAME,"time")))
        except Exception:
            pass
        return extract_metadata(driver,url)
    except Exception as e:
        print(f"Scrape error: {url}")
        print(e)
        return None

def scrape_feed(driver,duration_minutes,seen_urls):
    print("\n--- PHASE 2: SCRAPING ---")
    start=time.time()
    end=start+(duration_minutes*60)
    batch=[]
    total=0
    scroll_count=0
    empty_scrape_iterations = 0
    while time.time()<end:
        try:
            new_links=collect_new_links(driver,seen_urls)
            if new_links:
                print(f"Found {len(new_links)} new links.")
            if not new_links:
                driver.execute_script("window.scrollBy(0,900);")
                scroll_count+=1
                time.sleep(1.5)
                if scroll_count>=5:
                    print("Refreshing Explore feed...")
                    driver.refresh()
                    WebDriverWait(driver,10).until(EC.presence_of_element_located((By.TAG_NAME,"body")))
                    time.sleep(1.5)
                    scroll_count=0
                continue
            scroll_count=0
            
            scraped_this_iter = 0
            attempted_this_iter = 0
            for url in new_links:
                if time.time()>=end:
                    break
                seen_urls[url]=1
                attempted_this_iter += 1
                data=scrape_url(driver,url)
                if data and data["timestamp"] and data["timestamp"]!="" and data["timestamp"] is not None:
                    print(f"Scraped {total+1}: {url}")
                    batch.append(data)
                    scraped_this_iter+=1
                    total+=1
                    # print(f"Saved in memory: {total}")
                if len(batch)>=BATCH_SIZE:
                    save_batch_to_csv(batch)
                    batch=[]
                    save_seen_urls(seen_urls)
                    time.sleep(1)
                if time.time()>=end:
                    break
            # Update empty-scrape counter
            if attempted_this_iter >= MIN_NEW_LINKS_PER_ITER and scraped_this_iter == 0:
                empty_scrape_iterations += 1
                print(f"No data scraped this iteration (empty_scrape_iterations={empty_scrape_iterations}).")
            else:
                if scraped_this_iter > 0:
                    empty_scrape_iterations = 0
            if empty_scrape_iterations >= MAX_EMPTY_SCRAPE_ITERATIONS:
                print("\n[EARLY EXIT] Repeatedly found new links but could not scrape any data.")
                print("Likely missing HTML tags or changed page structure. Stopping.")
                break
            if time.time()<end:
                driver.get("https://www.instagram.com/explore/")
                WebDriverWait(driver,10).until(EC.presence_of_element_located((By.TAG_NAME,"body")))
                driver.execute_script("window.scrollBy(0,900);")
                time.sleep(2) 
                driver.execute_script("window.scrollBy(0,900);")
                time.sleep(2.5)
        except (NoSuchWindowException,WebDriverException):
            print("Browser closed.")
            break
        except Exception as e:
            print(f"Scraping loop error: {e}")
            try:
                driver.get("https://www.instagram.com/explore/")
                time.sleep(2)
            except Exception:
                break
        if time.time()>end:
            print("Scraping duration completed.")
            print("You can add more time if you want of enter 0 to exit now.")
            user_input = input("Enter 0 to exit now or any other key to continue: ")
            if user_input == "0":
                break
            else:
                print("Continuing scraping...")
                end = time.time() + (duration_minutes * 60)
    if batch:
        save_batch_to_csv(batch)
    save_seen_urls(seen_urls)
    
    print("\n--- COMPLETE ---")
    print(f"Total new items: {total}")
    print(f"CSV: {OUTPUT_FILE}")
    print(f"Total seen URLs: {len(seen_urls)}")
    return total

def main():
    user_input=input("Enter scraping duration in minutes: ")
    start_time = datetime.now()
    try:
        duration=float(user_input)
        if duration<=0:
            print("Duration must be greater than 0.")
            return
    except ValueError:
        print("Invalid input.")
        return
    driver=create_driver()
    try:
        total = 0
        setup_csv()
        print(f"CSV created: {OUTPUT_FILE}")
        seen_urls=load_seen_urls()
        print(f"Previously seen URLs: {len(seen_urls)}")
        login_instagram(driver)
        driver.execute_script("document.documentElement.style.zoom = '75%';")
        if not open_explore(driver):
            return
        print(f"Starting {duration} minute scraper.")
        total = scrape_feed(driver,duration,seen_urls)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Main error: {e}")
    finally:
        try:
            driver.quit()
            
            end_time = datetime.now()
            elapsed_time = end_time - start_time
        
            print(f"\n=======================================================")
            print(f" TOTAL SCRIPT EXECUTION TIME: {elapsed_time}")
            print(f"=======================================================\n")
            
            print(f"\n=======================================================")
            print(f"average time taken per reel :{elapsed_time/total}")
            print(f"=======================================================\n")
            
            
        except Exception:
            pass
        

        

    

if __name__=="__main__":
    
    main()