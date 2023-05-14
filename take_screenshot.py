import os
from playwright.async_api import async_playwright
from better_profanity import profanity
from PIL import Image, ImageEnhance, ImageDraw

def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

def change_transparency(image, transparency_ratio):
    # Convert the image to "RGBA" mode if it's not already
    image_rgba = image.convert("RGBA")

    # Split the image into its individual color channels
    red_channel, green_channel, blue_channel, alpha_channel = image_rgba.split()

    # Multiply the alpha channel by the desired transparency_ratio
    alpha_channel = ImageEnhance.Brightness(alpha_channel).enhance(transparency_ratio)

    # Merge the color channels and the modified alpha channel back into a single image
    result = Image.merge("RGBA", (red_channel, green_channel, blue_channel, alpha_channel))

    return result

# Define an asynchronous function to take screenshots of a Reddit post and its comments
async def take_screenshot_post( post ):

    image_path = os.path.join( "posts", f"{post.id}", "images", f"image_{post.id}.png" )

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

        nsfw_dialog = await page.query_selector( '#modal-dialog' )
        if nsfw_dialog:
            # Wait for the button to be present on the page
            try:
                await page.wait_for_selector( "#secondary-button", timeout=10000 )
            except Exception as e:
                print( f"Error waiting for button: {e}" )

            # Click the button to toggle the comment thread
            button = await page.query_selector( "#secondary-button" )
            if button:
                await button.click()
                print( "NSFW passed" )

        # Wait for the target post to be present on the page
        try:
            await page.wait_for_selector( "shreddit-post", timeout=10000 )
        except Exception as e:
            print( f"Error waiting for post: {e}" )

        # Get the target post using the provided selector
        target_post = await page.query_selector( "shreddit-post" )

        # Get the inner HTML of an element
        title_html = await page.eval_on_selector('div[slot="title"]', 'element => element.innerHTML')
        if await page.query_selector( 't3_13b0vaf-post-rtjson-content' ):
            body_html = await page.eval_on_selector("#t3_13b0vaf-post-rtjson-content", 'element => element.innerHTML')

        profanity.load_censor_words()
        title_html = profanity.censor( title_html )
        if await page.query_selector( 't3_13b0vaf-post-rtjson-content' ):
            body_html = profanity.censor( body_html )

        # Set the inner HTML of the element to the processed HTML
        await page.eval_on_selector('div[slot="title"]', '(element, html) => element.innerHTML = html', title_html)
        if await page.query_selector( 't3_13b0vaf-post-rtjson-content' ):
            await page.eval_on_selector("#t3_13b0vaf-post-rtjson-content", '(element, html) => element.innerHTML = html', body_html)

        # Take a screenshot of the specific post
        if target_post:
            await target_post.screenshot( path=image_path )
        else:
            print( f"No element found for selector: shreddit-post" )

        await browser.close()
    im = Image.open( image_path )
    im = add_corners( im, 30 )
    im = change_transparency( im, 0.85 )
    im.save( image_path )
    return image_path

async def take_screenshot_comment( post, comment ):

    image_path = os.path.join( "posts", f"{post.id}", "images", f"image_{comment.id}.png" )

    if os.path.exists( image_path ):
        return image_path

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
        await page.goto( f'https://reddit.com{comment.permalink}', timeout=0 )

        # Add a custom style to increase the font size of comments
        await page.add_style_tag(content="#-post-rtjson-content { font-weight: bold;font-size: 18px; }")

        # Wait for the comment to be present on the page
        try:
            await page.wait_for_selector( "shreddit-comment", timeout=10000 )
        except Exception as e:
            print( f"Error waiting for comment to load: {e}" )

        if await page.is_visible( 'shreddit-comment[author="[deleted]"]' ):
            raise ValueError("Comment has been deleted.")

        await page.wait_for_selector('#comment-fold-button', timeout=5000)

        # Click the button to toggle the comment thread
        button = await page.query_selector("#comment-fold-button")
        if button:
            await button.click()

        # Wait for the target comment to be present on the page
        await page.wait_for_selector( "shreddit-comment", timeout=10000 )

        # Get the inner HTML of the comment
        original_html = await page.eval_on_selector("#-post-rtjson-content", 'element => element.innerHTML')

        # censor content
        profanity.load_censor_words()
        new_html = profanity.censor(original_html)

        # Set the inner HTML of the element to the censored result
        await page.eval_on_selector("#-post-rtjson-content", '(element, html) => element.innerHTML = html', new_html)

        # Take a screenshot of the specific comment
        target_comment = await page.query_selector("shreddit-comment")
        if target_comment:
            await page.screenshot(path=image_path, clip=await target_comment.bounding_box())
            print(f'Screenshot saved: {os.path.abspath(image_path)}')
        else:
            print(f"No element found for selector: shreddit-comment for permalink: {comment.permalink}")

        # Close the browser
        await browser.close()
    im = Image.open( image_path )
    im = add_corners( im, 30 )
    im = change_transparency( im, 0.85 )
    im.save( image_path )
    return image_path