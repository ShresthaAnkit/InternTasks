import asyncio
from playwright.async_api import async_playwright, Playwright
import pprint
import json
link = 'https://www.yhdfa.vn/product/E/A01/SAD01-22?productModel='
product = {}
async def run(playwright: Playwright):    
    # Initial Preparation
    browser = await playwright.firefox.launch(headless=True)
    context = await browser.new_context(java_script_enabled=True,user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    page = await context.new_page()
    await page.goto(link,wait_until="domcontentloaded")
    product['title'] = (await page.locator("span.el-breadcrumb__inner").nth(4).text_content()).strip()
    images_locator = page.locator('div.el-carousel__item > img')
    images = []    
    
    for i in range(await images_locator.count()):                
        data_src = await images_locator.nth(i).get_attribute('data-src')
        while data_src == None:
            data_src = await images_locator.nth(i).get_attribute('data-src')
        images.append(data_src)
    product['product_images'] = images

    parameter_box_locator = page.locator('div.filterItem.parameter')
    if await parameter_box_locator.count()>0:
        parameter_title = (await parameter_box_locator.locator('p').text_content()).strip()
        parameter_dict = {}        
        parameter_locator = parameter_box_locator.locator('.characteristic .item.mgbt-10')
        for i in range(await parameter_locator.count()):                
            parameter_name = (await parameter_locator.nth(i).locator('span.name').text_content()).strip()            
            parameter_option_list = []
            parameter_options_locator = parameter_locator.nth(i).locator('.el-scrollbar__view.el-select-dropdown__list > li')
            for j in range(await parameter_options_locator.count()):
                parameter_option = await parameter_options_locator.nth(j).text_content()
                parameter_option_list.append(parameter_option.strip())
            parameter_dict[parameter_name] = parameter_option_list
        product[parameter_title.strip()] = parameter_dict

    product_box_locator = page.locator('div.filterItem.product')
    if await product_box_locator.count()>0:
        product_title = (await product_box_locator.locator('p').text_content()).strip()
        product_dict = {}
        product_locator = product_box_locator.locator('.characteristic .item.productSelect')
        for i in range(await product_locator.count()):                
            product_name = (await product_locator.nth(i).locator('span.name').text_content()).strip()            
            product_option_list = []
            product_options_locator = product_locator.nth(i).locator('.el-scrollbar__view.el-select-dropdown__list > li')
            for j in range(await product_options_locator.count()):
                product_option = await product_options_locator.nth(j).text_content()
                product_option_list.append(product_option.strip())
            product_dict[product_name] = product_option_list
        product[product_title.strip()] = product_dict

    table_locator = page.locator('div.productTabs')
    detail_locator = table_locator.locator('div.technicalDrawing .imgBox')
    table_dict = {}
    detail_list = ['material_drawing','parameter']
    detail_dict = {}
    for i in range(await detail_locator.count()):                
        img_locator = detail_locator.nth(i).locator('img')
        img_list = []
        for j in range(await img_locator.count()):
            src = await img_locator.nth(j).get_attribute('data-src')     
            if src == None:
                src = await img_locator.nth(j).get_attribute('src')    
                while src == None:
                    src = await img_locator.nth(j).get_attribute('src')   
            img_list.append(src)
        detail_dict[detail_list[i]] = img_list
    table_dict['detail'] = detail_dict

    optional_machining_locator = table_locator.locator('div.optionalMachiningImage')
    if await optional_machining_locator.count()>0:
        table_dict['optionalMachiningImages'] = await optional_machining_locator.locator('img').get_attribute('data-src')
    product['table_images'] = table_dict

    formatted_output = json.dumps(product, indent=4, ensure_ascii=False)
    with open('Web Scraping/data.json', "w") as file:
        json.dump(product, file, indent=4)
    print(formatted_output)
    
    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())