import os
from playwright.async_api import async_playwright
from better_profanity import profanity

# Define an asynchronous function to take screenshots of a Reddit post and its comments
async def take_screenshot( post, comments ):
    i = 0
    # Launch an instance of Playwright
    async with async_playwright() as playwright:

        # Select the browser you want to use, for example, 'chromium', 'firefox', or 'webkit'
        browser = await playwright.chromium.launch( headless=True )
        context = await browser.new_context(
            locale="en-us",
            color_scheme="dark",
            device_scale_factor=(1080 // 600) + 1,
        )

        # Navigate to the Reddit post URL
        page = await context.new_page()
        await page.goto( post.url, timeout=0 )

        # Get the target post using the provided selector
        target_post = await page.query_selector( "shreddit-post" )

        # Get the inner HTML of an element
        title_html = await page.eval_on_selector("#post-title-t3_13b0vaf", 'element => element.innerHTML')
        body_html = await page.eval_on_selector("#t3_13b0vaf-post-rtjson-content", 'element => element.innerHTML')

        profanity.load_censor_words()
        title_html = profanity.censor( title_html )
        body_html = profanity.censor( body_html )

        # Set the inner HTML of the element to the processed HTML
        await page.eval_on_selector("#post-title-t3_13b0vaf", '(element, html) => element.innerHTML = html', title_html)
        await page.eval_on_selector("#t3_13b0vaf-post-rtjson-content", '(element, html) => element.innerHTML = html', body_html)

        # Take a screenshot of the specific post
        if target_post:
            await target_post.screenshot( path=f'posts/{post.id}/images/image_{i}.png' )
            i += 1
        else:
            print( f"No element found for selector: shreddit-post" )

        # Iterate over the comments and take screenshots
        for comment in comments:
            await page.goto( f'https://reddit.com{comment.permalink}', timeout=0 )
            # Add a custom style to increase the font size of comments
            await page.add_style_tag(content="#-post-rtjson-content { font-weight: bold;font-size: 18px; }")

            # Wait for the button to be present on the page
            try:
                await page.wait_for_selector( "#comment-fold-button", timeout=5000 )
            except Exception as e:
                print( f"Error waiting for button: {e}" )

            # Click the button to toggle the comment thread
            button = await page.query_selector( "#comment-fold-button" )
            if button:
                await button.click()

            # Wait for the target comment to be present on the page
            try:
                await page.wait_for_selector( "shreddit-comment", timeout=5000 )
            except Exception as e:
                print( f"Error waiting for comment: {e}" )

            # Get the inner HTML of an element
            original_html = await page.eval_on_selector("#-post-rtjson-content", 'element => element.innerHTML')

            profanity.load_censor_words()
            new_html = profanity.censor( original_html )

            # Set the inner HTML of the element to the processed HTML
            await page.eval_on_selector("#-post-rtjson-content", '(element, html) => element.innerHTML = html', new_html)

            # Take a screenshot of the specific comment
            target_comment = await page.query_selector( "shreddit-comment" )
            if target_comment:
                screenshot_path = f'posts/{post.id}/images/image_{i}.png'
                i += 1
                await page.screenshot( path=screenshot_path, clip=await target_comment.bounding_box() )
                print( f'Screenshot saved: { os.path.abspath( screenshot_path ) }' )
            else:
                print( f"No element found for selector: shreddit-comment for permalink: { comment.permalink }" )

        # Close the browser
        await browser.close()