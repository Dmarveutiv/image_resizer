from flask import Flask, request, render_template, send_file
from PIL import Image
import io

app = Flask(__name__) #creating an instance of Flask
Sizes = {
	'Twitter / x':{
	'Profile Picture': (400, 400),
	'Header / banner': (1500, 500),
	'In-feed Image': (1600, 900),
	},

	'Whatsapp': {
	'Status' : (1080, 1920),
	'Profile Picture' : (500, 500),
		'Shared image' : (1600, 900),
	},

	'Youtube': {
	'Thumbnail':(1280, 720),
	'Channel Art': (2560, 1440),
	'Profile Picture':(800, 500)
	},
	'Facebook':{
	'Feed Post':(1200, 600),
	'Cover Photo':(851, 315),
    'Profile Picture':(180, 180),
    'Story' : (1080, 1920)
	},

	"instagram": {
        "Feed post (square)": (1080, 1080),
        "Feed post (portrait)": (1080, 1350),
        "Story / Reel": (1080, 1920),
        "Profile picture": (320, 320),
    },

    'Pinterest':{
    'Standar Pin' : (1000, 1500),
    'Square Pin' : (1000, 1000),
    'Idea Pin': (1080, 1920),
    'Board Cover Image': (222, 150)
    },
    'Linkedin':{
        'Profile photo' : (400, 400),
        'Profile banner' : (1584, 396),
        'Featured Section': (1200, 627)
    },
    'TikTok':{
		'Video Cover' : (1080, 1920),
		'Profile picture' : (200, 200),
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

    width, height = Size[platform][use_case]

    img = Image.open(file)
    img = img.convert("RGB")

    img.thumbnail((width, height))  

    output = io.BytesIO()
    img.save(output, format="JPEG", quality=92)
    output.seek(0)

    filename = f"{platform}_{use_case.replace(' ', '_')}.jpg"
    return send_file(output, mimetype="image/jpeg",
                     as_attachment=True,
                     download_name=filename)
if __name__ == "__main__":
    app.run(debug=True)
