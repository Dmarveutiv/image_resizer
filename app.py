from flask import Flask, request, render_template, send_file
from PIL import Image
import io
import os

app = Flask(__name__)

Sizes = {
    'twitter': {
        'Profile picture': (400, 400),
        'Header / banner': (1500, 500),
        'In-feed image': (1600, 900),
    },
    'whatsapp': {
        'Status': (1080, 1920),
        'Profile picture': (500, 500),
        'Shared image': (1600, 900),
    },
    'Facebook': {
        'Feed post': (1200, 630),
        'Cover photo': (851, 315),
        'Profile picture': (180, 180),
        'Story': (1080, 1920),
    },
    'instagram': {
        'Feed post (square)': (1080, 1080),
        'Feed post (portrait)': (1080, 1350),
        'Story / Reel': (1080, 1920),
        'Profile picture': (320, 320),
    },
    'pinterest': {
        'Standard pin': (1000, 1500),
        'Square pin': (1000, 1000),
        'Profile picture': (165, 165),
    },
    'linkedin': {
        'Profile banner': (1584, 396),
        'Profile picture': (400, 400),
        'Featured Section': (1200, 627),
    },
    'tiktok': {
        'Video cover': (1080, 1920),
        'Profile picture': (200, 200),
    },
    'snapchat': {
        'Snap / Story': (1080, 1920),
        'Ad image': (1080, 1920),
    },
    'telegram': {
        'Profile picture': (512, 512),
        'Channel banner': (1280, 720),
        'Shared image': (1280, 720),
    },
    'youtube': {
        'Thumbnail': (1280, 720),
        'Channel art': (2560, 1440),
        'Profile Image': (800, 500),
    },
}


def resize_image_with_padding(image, target_width, target_height, preserve_transparency=True):
    """
    Resize image to target dimensions while maintaining aspect ratio.
    - If original is smaller, upscale it
    - If larger, downscale it
    - Pad with transparent or white background as needed
    """
    # Detect if image has transparency
    has_alpha = image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info)
    should_use_transparency = preserve_transparency and has_alpha
    
    # Convert to appropriate mode
    if should_use_transparency:
        image = image.convert('RGBA')
        bg_color = (255, 255, 255, 0)  # Transparent
    else:
        image = image.convert('RGB')
        bg_color = (255, 255, 255)  # White
    
    # Calculate aspect ratio
    original_ratio = image.width / image.height
    target_ratio = target_width / target_height
    
    # Determine scaling strategy to maintain aspect ratio
    if original_ratio > target_ratio:
        # Image is wider - fit to width
        new_width = target_width
        new_height = int(target_width / original_ratio)
    else:
        # Image is taller - fit to height
        new_height = target_height
        new_width = int(target_height * original_ratio)
    
    # Resize the image (handles both upscaling and downscaling)
    resized_img = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create a new image with target dimensions and background color
    if should_use_transparency:
        final_img = Image.new('RGBA', (target_width, target_height), bg_color)
    else:
        final_img = Image.new('RGB', (target_width, target_height), bg_color)
    
    # Paste the resized image centered on the background
    offset_x = (target_width - new_width) // 2
    offset_y = (target_height - new_height) // 2
    
    if should_use_transparency:
        final_img.paste(resized_img, (offset_x, offset_y), resized_img)
    else:
        final_img.paste(resized_img, (offset_x, offset_y))
    
    return final_img, should_use_transparency


def resize_image_crop_to_fill(image, target_width, target_height, preserve_transparency=True):
    """
    Resize image to target dimensions by cropping to fill.
    - Scales image to cover the entire target area
    - Crops excess to match exact target dimensions
    - No padding, uses all available space
    """
    # Detect if image has transparency
    has_alpha = image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info)
    
    # Convert to appropriate mode
    if preserve_transparency and has_alpha:
        image = image.convert('RGBA')
        should_use_transparency = True
    else:
        image = image.convert('RGB')
        should_use_transparency = False
    
    # Calculate aspect ratios
    original_ratio = image.width / image.height
    target_ratio = target_width / target_height
    
    # Determine scaling strategy - scale to cover entire target
    if original_ratio > target_ratio:
        # Image is wider - fit to height (will crop sides)
        new_height = target_height
        new_width = int(target_height * original_ratio)
    else:
        # Image is taller - fit to width (will crop top/bottom)
        new_width = target_width
        new_height = int(target_width / original_ratio)
    
    # Resize the image
    resized_img = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Calculate crop box to center the image
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height
    
    # Crop to exact target dimensions
    final_img = resized_img.crop((left, top, right, bottom))
    
    return final_img, should_use_transparency


@app.route("/")
def home():
    return render_template('index.html', platforms=Sizes)


@app.route("/resize", methods=["POST"])
def resize():
    file = request.files["image"]
    platform = request.form["platform"]
    use_case = request.form["use_case"]
    mode = request.form.get("mode", "pad")  # Default to pad if not specified

    if platform not in Sizes or use_case not in Sizes[platform]:
        return {"error": "invalid platform/use_case"}, 400

    if mode not in ["pad", "crop"]:
        return {"error": "invalid mode - use 'pad' or 'crop'"}, 400

    width, height = Sizes[platform][use_case]

    img = Image.open(file)
    
    # Use appropriate resizing method
    if mode == "crop":
        resized_img, has_transparency = resize_image_crop_to_fill(img, width, height)
    else:  # pad
        resized_img, has_transparency = resize_image_with_padding(img, width, height)

    output = io.BytesIO()
    
    # Use PNG if transparency, otherwise JPEG
    if has_transparency:
        resized_img.save(output, format="PNG")
        file_format = "png"
        mimetype = "image/png"
    else:
        resized_img.save(output, format="JPEG", quality=92)
        file_format = "jpg"
        mimetype = "image/jpeg"
    
    output.seek(0)

    filename = f"{platform}_{use_case.replace(' ', '_').replace('/', '-')}.{file_format}"
    return send_file(output, mimetype=mimetype,
                     as_attachment=True,
                     download_name=filename)


if __name__ == "__main__":
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port, debug=False)
    app.run(host='127.0.0.1', port=5000, debug=True)