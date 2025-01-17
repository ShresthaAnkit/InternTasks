import asyncio
from playwright.async_api import async_playwright, Playwright
import pprint
import json
link = 'https://www.daraz.com.np/products/asta-wolf-apex-150-wireless-earbuds-with-150-hours-playtime-anc-quad-mic-enc-sonic-charge-phantom-mode-turbosync-duo-sync-ipx5-water-resistant-type-c-fast-charging-i157711156-s1131724483.html?pvid=40db0870-f999-453a-bfd7-5e147dbd4f9e&search=jfy&scm=1007.51705.414277.0&spm=a2a0e.tm80335409.just4u.d_157711156'
product = {}
async def run(playwright: Playwright):    
    # Initial Preparation
    browser = await playwright.firefox.launch(headless=False)
    context = await browser.new_context(java_script_enabled=True,user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    page = await context.new_page()
    await page.goto(link,wait_until="domcontentloaded")

    # Retrieve the price waiting until it is available
    price = ""
    max_retries = 5  # Adjust retries based on expected wait time
    retry_delay = 1   # Delay in seconds
    for _ in range(max_retries):
        price_locator = page.locator(".pdp-product-price")
        price = await price_locator.text_content()
        if price and price.strip():
            print('Retrying...')
            break
        await asyncio.sleep(retry_delay)
    # Retrieve the discounted information if any
    actual_price = 0
    discount_percent = 0
    actual_price_locator = price_locator.locator(".origin-block .notranslate.pdp-price.pdp-price_type_deleted.pdp-price_color_lightgray.pdp-price_size_xs")
    if await actual_price_locator.count()>0:
        actual_price = await actual_price_locator.text_content()
    discount_percent_locator = price_locator.locator(".origin-block .pdp-product-price__discount")
    if await discount_percent_locator.count()>0:
        discount_percent = await discount_percent_locator.text_content()
    price_dict = {
        'price':await page.locator(".pdp-product-price .notranslate.pdp-price.pdp-price_type_normal.pdp-price_color_orange.pdp-price_size_xl").text_content(),
    }
    # Only add the actual_price and discount_percent if they are available
    if actual_price:
        price_dict['actual_price'] = actual_price
    if discount_percent:
        price_dict['discount_percent'] = discount_percent
    product['price'] = price_dict
    
    # Retrieve the title
    product['title'] = await page.locator(".pdp-mod-product-badge-title").text_content()            

    # Retrieve the ratings and number_questions_answered
    reviews = page.locator(".pdp-link.pdp-link_size_s.pdp-link_theme_blue.pdp-review-summary__link")    
    review_names = ['rating','num_questions_answered']    
    for i in range(await reviews.count()):
        review = await reviews.nth(i).text_content()
        product[review_names[i]] = review    

    # Retrieve the brand
    product['brand'] = await page.locator(".pdp-link.pdp-link_size_s.pdp-link_theme_blue.pdp-product-brand__brand-link").text_content()

    # Retrieve all the available options for the product
    options = page.locator(".sku-prop")
    options_list = []
    for i in range(await options.count()):    
        option_dict = {}
        option = options.nth(i)
        option_dict['name'] = await option.locator(".section-title").text_content()
        option_dict['value'] = await option.locator(".sku-name").text_content()
        options_list.append(option_dict)
    product['options'] = options_list

    # Retrieve all the images for the product
    primary_images_locator = page.locator(".next-slick-inner.next-slick-initialized .next-slick-list .next-slick-track .next-slick-slide.next-slick-active.item-gallery__thumbnail .item-gallery__image-wrapper .pdp-mod-common-image.item-gallery__thumbnail-image")
    primary_images = []
    for i in range(await primary_images_locator.count()):
        primary_images.append(await primary_images_locator.nth(i).get_attribute("src"))
    product['primary_images'] = primary_images      
    lazy_loader = page.locator(".pdp-block.module .lazyload-wrapper").nth(0)
    for _ in range(5):
        if await lazy_loader.count()>0:
            await page.evaluate("window.scrollBy(0, 300)")  # Scroll down 300px
            await lazy_loader.click()
            await page.wait_for_timeout(100)  # Wait for new content to load

    # Retrieve description of the product
    description_box_locator = page.locator(".pdp-block.pdp-block__additional-information .pdp-block.fixed-width-full.background-2 .pdp-block.module .lazyload-wrapper")
    description_box_title_locator =  description_box_locator.locator(".pdp-mod-section-title.outer-title")
    description_box_highlights_locator = description_box_locator.locator(".html-content.pdp-product-highlights")
    description_box_detail_locator =  description_box_locator.locator(".html-content.detail-content")
    description_box_specs_locator =  description_box_locator.locator(".pdp-mod-specification")    
    description = {}
    if await description_box_title_locator.count()>0:
        description_box_title = await description_box_title_locator.text_content()
        description['title'] = description_box_title
    if await description_box_highlights_locator.count()>0:
        description_box_highlights = await description_box_highlights_locator.text_content()
        description['highlights'] = description_box_highlights
    if await description_box_detail_locator.count()>0:
        description_box_detail = await description_box_detail_locator.text_content()
        description['detail'] = description_box_detail
    if await description_box_specs_locator.count()>0:
        description_box_specs = await description_box_specs_locator.text_content()
        description['specifications'] = description_box_specs
    product['description'] = description
    # Pretty Print the product dictionary
    formatted_output = json.dumps(product, indent=4, ensure_ascii=False)
    print(formatted_output)
    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())