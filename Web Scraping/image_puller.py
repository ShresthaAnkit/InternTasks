import asyncio
from playwright.async_api import async_playwright, Playwright
import pprint
import json
import requests
link = 'https://www.yhdfa.vn/product/E/A01/SAD01-22?productModel='

# Function to extract URLs recursively
def extract_urls(obj):
    urls = []
    if isinstance(obj, dict):
        for value in obj.values():
            urls.extend(extract_urls(value))
    elif isinstance(obj, list):
        for item in obj:
            urls.extend(extract_urls(item))
    elif isinstance(obj, str) and obj.startswith("http"):
        urls.append(obj)
    return urls

product = {}
async def run(playwright: Playwright):    
    # Initial Preparation
    browser = await playwright.firefox.launch(headless=True)
    context = await browser.new_context(java_script_enabled=True,user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    page = await context.new_page()
    await page.goto(link,wait_until="domcontentloaded")
    with open('Web Scraping/data.json', "r") as file:
        data = json.load(file)
    table_images = data['table_images']
    cookies = await page.context.cookies()
    headers = {
        "User-Agent": await page.evaluate('navigator.userAgent'),
        "Referer": page.url
    }

    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
        
    # Get all URLs
    all_urls = extract_urls(table_images)
    
    for url in all_urls:
        response = session.get(url, headers=headers)
        with open(f'Web Scraping/images/{url.split("/")[-1]}', 'wb') as file:
            file.write(response.content)
    
    
    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())


