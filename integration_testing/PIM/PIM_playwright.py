import time

def check_product_in_pim(playwright, config):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()

    # Open new page
    page = context.new_page()

    # Go to https://sso.productmarketingcloud.com/account/login?returnurl=https://inrivereuw.productmarketingcloud.com/
    page.goto(config['pim_url'])

    # Click [placeholder="Email"]
    page.click("[placeholder=\"Email\"]")

    # Fill [placeholder="Email"]
    page.fill("[placeholder=\"Email\"]", config['pim_username'])

    # Click button:has-text("Sign in")
    page.click("button:has-text(\"Sign in\")")
    # assert page.url == "https://forms.productmarketingcloud.com/?returnUrl=https%3A%2F%2Finrivereuw.productmarketingcloud.com%2F"

    # Click [placeholder="Password"]
    page.click("[placeholder=\"Password\"]")

    # Fill [placeholder="Password"]
    page.fill("[placeholder=\"Password\"]", config['pim_password'])

    # Click text=Submit
    page.click("text=Submit")
    # assert page.url == "https://inriver2euw.productmarketingcloud.com/app/dashboard"

    # Click text=Welcome, Dawid!
    page.click("text=Welcome, Dawid!")

    # Go to https://inriver2euw.productmarketingcloud.com/app/enrich#entity/121545/details
    page.goto(config['pim_entity_url'])
    
    # product_name = page.text_content("span:has(span.truncate)")
    # product_details = page.inner_html("#inriver-fields-form-area")

    product_name = page.text_content('[class="truncate"]')
    product_Assortment = page.text_content("span:right-of(p:has-text(\"Assortment\"))")
    product_Status = page.text_content("span:right-of(:text('Product Status'))") 
    product_Owner = page.text_content("span:right-of(:text('Product Owner'))") 
    product_Trademark = page.text_content("span:right-of(:text('Trademark'))") 
    product_Function = page.text_content("span:right-of(:text('Product Function: Main'))") 
    product_Attribute = page.text_content("span:right-of(:text('Attribute group (Jeeves)'))") 

    product_info = {
        "Name": product_name.strip(),
        "Assortment": product_Assortment,
        "Status": product_Status,
        "Owner": product_Owner,
        "Trademark": product_Trademark,
        "Function": product_Function,
        "Attribute": product_Attribute
    }

    # ---------------------
    context.close()
    browser.close()
    # return product_name
    return product_info

def change_product_in_pim(playwright, config, original_value):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()

    # Open new page
    page = context.new_page()

    # Go to https://sso.productmarketingcloud.com/account/login?returnurl=https://inrivereuw.productmarketingcloud.com/
    page.goto(config['pim_url'])

    # Click [placeholder="Email"]
    page.click("[placeholder=\"Email\"]")

    # Fill [placeholder="Email"]
    page.fill("[placeholder=\"Email\"]", config['pim_username'])

    # Click button:has-text("Sign in")
    page.click("button:has-text(\"Sign in\")")
    # assert page.url == "https://forms.productmarketingcloud.com/?returnUrl=https%3A%2F%2Finrivereuw.productmarketingcloud.com%2F"

    # Click [placeholder="Password"]
    page.click("[placeholder=\"Password\"]")

    # Fill [placeholder="Password"]
    page.fill("[placeholder=\"Password\"]", config['pim_password'])

    # Click text=Submit
    page.click("text=Submit")
    # assert page.url == "https://inriver2euw.productmarketingcloud.com/app/dashboard"

    # Click text=Welcome, Dawid!
    page.click("text=Welcome, Dawid!")

    # Go to https://inriver2euw.productmarketingcloud.com/app/enrich#entity/121545/details
    page.goto(config['pim_entity_url'])

    if original_value is False:
        # Click input[name="Fields_1_Value"]
        page.click("input[name=\"Fields_1_Value\"]")
        
        # Fill input[name="Fields_1_Value"]
        page.fill("input[name=\"Fields_1_Value\"]", "")
        
        # Press Tab
        page.press("input[name=\"Fields_1_Value\"]", "Tab")

        # Fill input[name="Fields_1_Value"]
        page.fill("input[name=\"Fields_1_Value\"]", "Auto test to Jeeves")

        # Change Assortment to BASE
        page.click("button:right-of(p:has-text(\"Assortment\"))")    
        page.click("text=BASE")
    
        # Change Product status to Pending
        page.click("button:right-of(:text('Product Status'))")
        page.click("text=Pending")
        
        # Change Product Owner to Agnieszka Czajczynska
        page.click("button:right-of(:text('Product Owner'))")
        page.click("text=Agnieszka Czajczynska")

        # Change Tradmark to iDisplay™
        page.click("button:right-of(:text('Trademark'))")
        page.click("text=iDisplay™")
        
        # Change Item class to Helec
        page.click("button:right-of(:text('Item Class (Jeeves)'))")
        page.click("text=Helec")

        # Change Key concept to Fresh
        page.click("button:right-of(:text('Key concept'))")
        page.click("text=Fresh")

        # Change System to Digital screens
        page.click("button:right-of(:text('System'))")
        page.click("text=Digital screens")

        # Change English product headline
        page.click(".js-locale-string-edit-button:right-of(:text('Product Headline'))")
        page.click("textarea[name=\"Fields.17.Value\"]")
        page.fill("textarea[name=\"Fields.17.Value\"]", "Fixture kit for banners for automated test")
    else:
        # Change Key concept to None
        page.click("button:right-of(:text('Key concept'))")
        page.click("text=None")

        # Change System to Profiles for posters
        page.click("button:right-of(:text('System'))")
        page.click("text=Profiles for posters")

        # Change English product headline
        page.click(".js-locale-string-edit-button:right-of(:text('Product Headline'))")
        page.click("textarea[name=\"Fields.17.Value\"]")
        page.fill("textarea[name=\"Fields.17.Value\"]", "Fixture kit for banners")
    
    # Click #entity-detail-settings-save-all-button
    page.click("#entity-detail-settings-save-all-button")

    # ---------------------
    context.close()
    browser.close()

def test(playwright, config):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    # Open new page
    page = context.new_page()

    # Go to https://sso.productmarketingcloud.com/account/login?returnurl=https://inrivereuw.productmarketingcloud.com/
    page.goto(config['pim_url'])

    # Click [placeholder="Email"]
    page.click("[placeholder=\"Email\"]")

    # Fill [placeholder="Email"]
    page.fill("[placeholder=\"Email\"]", config['pim_username'])

    # Click button:has-text("Sign in")
    page.click("button:has-text(\"Sign in\")")
    # assert page.url == "https://forms.productmarketingcloud.com/?returnUrl=https%3A%2F%2Finrivereuw.productmarketingcloud.com%2F"

    # Click [placeholder="Password"]
    page.click("[placeholder=\"Password\"]")

    # Fill [placeholder="Password"]
    page.fill("[placeholder=\"Password\"]", config['pim_password'])

    # Click text=Submit
    page.click("text=Submit")
    # assert page.url == "https://inriver2euw.productmarketingcloud.com/app/dashboard"

    # Click text=Welcome, Dawid!
    page.click("text=Welcome, Dawid!")

    # Go to https://inriver2euw.productmarketingcloud.com/app/enrich#entity/121545/details
    page.goto(config['pim_entity_url'])

    # Click Assortment dropdown
    # page.click("button:has-text(\"Other\")")
    page.click(".js-locale-string-edit-button:right-of(:text('Product Headline'))")
    page.click("textarea[name=\"Fields.17.Value\"]")
    page.fill("textarea[name=\"Fields.17.Value\"]", "Its alive :)")
    # product_name = page.text_content('[class="truncate"]')
    # page.click("button:right-of(p:has-text(\"Assortment\"))")
    # page.click("text=BASE")

    # product_Status = page.text_content("span:right-of(:text('Product Status'))") 
    # product_Owner = page.text_content("span:right-of(:text('Product Owner'))") 
    # product_Trademark = page.text_content("span:right-of(:text('Trademark'))") 
    # product_Item_Class = page.text_content("span:right-of(:text('Item Class (Jeeves)'))") 
    # product_Function = page.text_content("span:right-of(:text('Product Function: Main'))") 
    # product_Attribute = page.text_content("span:right-of(:text('Attribute group (Jeeves)'))") 

    # Click #entity-detail-settings-save-all-button
    # page.click("#entity-detail-settings-save-all-button")
    time.sleep(20)
    # ---------------------
    context.close()
    browser.close()

# playwright codegen https://inriver2euw.productmarketingcloud.com/app/dashboard