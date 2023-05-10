import os
from playwright.async_api import async_playwright

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

        # Take a screenshot of the specific post
        if target_post:
            await target_post.screenshot( path=f'reddit_image_{i}.png' )
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

            # Take a screenshot of the specific comment
            target_comment = await page.query_selector( "shreddit-comment" )
            if target_comment:
                screenshot_path = f'reddit_image_{i}.png'
                i += 1
                await page.screenshot( path=screenshot_path, clip=await target_comment.bounding_box() )
                print( f'Screenshot saved: { os.path.abspath( screenshot_path ) }' )
            else:
                print( f"No element found for selector: shreddit-comment for permalink: { comment.permalink }" )

        # Close the browser
        await browser.close()