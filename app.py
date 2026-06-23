from flask import Flask, request, render_template, send_file
from PIL import Image, ImageOps
import io

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
    'youtube': {
        'Thumbnail': (1280, 720),
        'Channel art': (2560, 1440),
        'Profile picture': (800, 500),
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
}

@app.route("/")
def home():
    return render_template('index.html', platforms=Sizes)

@app.route("/resize", methods=["POST"])
def resize():
    file = request.files["image"]
    platform = request.form["platform"]
    use_case = request.form["use_case"]

    if platform not in Sizes or use_case not in Sizes[platform]:
        return {"error": "invalid platform/use_case"}, 400

    width, height = Sizes[platform][use_case]

    img = Image.open(file)
    img = img.convert("RGB")

    # crop-to-fill instead of thumbnail, so output matches exact target dims
    img = ImageOps.fit(img, (width, height), Image.LANCZOS)

    output = io.BytesIO()
    img.save(output, format="JPEG", quality=92)
    output.seek(0)

    filename = f"{platform}_{use_case.replace(' ', '_').replace('/', '-')}.jpg"
    return send_file(output, mimetype="image/jpeg",
                      as_attachment=True,
                      download_name=filename)

if __name__ == "__main__":
    app.run(debug=True)