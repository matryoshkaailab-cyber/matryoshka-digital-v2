#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time

email = "matryoshka.ai.lab@gmail.com"
password = "Jktu220587"

print("Starting browser...")
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        executable_path='/usr/bin/google-chrome',
        args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--lang=ru-RU']
    )
    context = browser.new_context(
        locale='ru-RU',
        timezone_id='Europe/Moscow',
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport={'width': 1920, 'height': 1080}
    )
    page = context.new_page()

    # Login - go directly to Gmail auth
    print("Going to Gmail auth...")
    page.goto("https://accounts.google.com/InteractiveLogin?continue=https://mail.google.com/mail/u/0/&service=mail", wait_until="domcontentloaded")
    time.sleep(3)
    page.screenshot(path="/root/matryoshka/g7_01.png")
    print(f"URL: {page.url}")
    
    # If not logged in, login
    if 'identifier' in page.url:
        print("Need to login...")
        page.fill('#identifierId', email)
        page.click('#identifierNext')
        time.sleep(6)
        
        if 'challenge/pwd' in page.url:
            page.click('#password')
            page.keyboard.type(password, delay=50)
            time.sleep(1)
            page.click('#passwordNext')
            time.sleep(6)
    
    page.screenshot(path="/root/matryoshka/g7_02.png")
    print(f"URL after: {page.url}")
    
    # Navigate to Gmail
    page.goto("https://mail.google.com/mail/u/0/", wait_until="domcontentloaded")
    time.sleep(8)
    page.screenshot(path="/root/matryoshka/g7_03.png")
    print(f"Gmail URL: {page.url}")
    
    # Get emails
    try:
        page.wait_for_timeout(5000)
        emails = page.evaluate('''() => {
            const rows = document.querySelectorAll('tr');
            return Array.from(rows).slice(0, 5).map(row => {
                const tds = row.querySelectorAll('td');
                if (tds.length < 3) return null;
                return Array.from(tds).map(td => td.innerText.replace(/\\n/g, ' ')).join(' || ');
            }).filter(x => x);
        }''')
        
        if emails:
            print(f"Found {len(emails)} emails:")
            for i, em in enumerate(emails[:3]):
                print(f"  {i+1}: {em[:250]}")
            with open('/root/matryoshka/emails_list.txt', 'w') as f:
                f.write('\n'.join(emails))
        else:
            print("No emails found")
            
    except Exception as e:
        print(f"Error: {e}")

    browser.close()
    print("Done")
