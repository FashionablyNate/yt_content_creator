import asyncio
from PIL import Image, ImageEnhance, ImageChops, ImageDraw
from take_screenshot import take_screenshot
from reddit import connect, get_post, get_comments
from create_video import create_video

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


reddit = connect()
post = get_post( reddit )
comments = get_comments( post )
asyncio.run( take_screenshot( post, comments ) )
for i in range(0, 6):
    im = Image.open( f'reddit_image_{i}.png' )
    im = add_corners( im, 30 )
    im = change_transparency( im, 0.85 )
    im.save( f'reddit_image_{i}.png' )
create_video( post, comments )