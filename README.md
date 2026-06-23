Batman's Image Resizer - How it works
A web app that resizes an uploaded image to the correct dimensions for a chosen social media platform and use case (e.g. Instagram Story, Linkedin banner, Whatsapp Profile Picture, X bannner). Built with Flask(Python) on the backend and vanilla JavaScript on the frontend

All image processing happens on the server. the browser job is only to collect input file, and display the result.

Setup

pip install flask pillow

make sure your folder looks like this:
  project/
├── app.py
└── templates/
    └── index.html

run
python app.py

open your browser to the port indiciated in cli

use
1. Upload an image
2. Pick a platform
3. Pick a use case (e.g. "profile Picture"
4. Click Resize
