def create_order(playwright, ref_number):
    success = False
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    # Open new page
    page = context.new_page()

    # Go to https://hl-display-1600-test.gung.io/
    page.goto("https://hl-display-1600-test.gung.io/")

    # Go to https://hl-display-1600-test.gung.io/login?redirectUrl=%2F
    page.goto("https://hl-display-1600-test.gung.io/login?redirectUrl=%2F")

    # Click button:has-text("Changer de langue")
    page.click("button:has-text(\"Changer de langue\")")

    # Click button:has-text("English")
    page.click("button:has-text(\"English\")")

    # Click input[type="text"]
    page.click("input[type=\"text\"]")

    # Fill input[type="text"]
    page.fill("input[type=\"text\"]", "ithl@poland")

    # Click input[type="password"]
    page.click("input[type=\"password\"]")

    # Fill input[type="password"]
    page.fill("input[type=\"password\"]", "Gun44an74!")

    # Click button:has-text("Login")
    # with page.expect_navigation(url="https://hl-display-1600-test.gung.io/categories"):
    with page.expect_navigation():
        page.click("button:has-text(\"Login\")")

    # Click text=Products
    # with page.expect_navigation(url="https://hl-display-1600-test.gung.io/products"):
    with page.expect_navigation():
        page.click("text=Products")

    # Click button:has-text("Add")
    page.click("button:has-text(\"Add\")")

    # Click button:has-text("Add")
    page.click("button:has-text(\"Add\")")

    # Click text=31,06 € In stockMore info >> :nth-match(button, 2)
    page.click("text=31,06 € In stockMore info >> :nth-match(button, 2)")

    # Click a:has-text("2")
    # with page.expect_navigation(url="https://hl-display-1600-test.gung.io/checkout"):
    with page.expect_navigation():
        page.click("a:has-text(\"2\")")

    # Click text=Continue to shipping
    page.click("text=Continue to shipping")

    # Click input[name="oh.kundbestnr"]
    page.click("input[name=\"oh.kundbestnr\"]")

    # Fill input[name="oh.kundbestnr"]
    page.fill("input[name=\"oh.kundbestnr\"]", ref_number)

    # Press Tab
    page.press("input[name=\"oh.kundbestnr\"]", "Tab")

    # Click button:has-text("Confirm")
    page.click("button:has-text(\"Confirm\")")

    # Click text=Confirm order
    page.click("text=Confirm order")

    # Click text=Thank you for your order!
    page.click("text=Thank you for your order!", timeout=60000)

    # ---------------------
    context.close()
    browser.close()

    success = True

    return success

# playwright codegen http://hl-display-1600-test.gung.io
