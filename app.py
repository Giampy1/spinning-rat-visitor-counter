from email.policy import default
import io
from math import ceil, sqrt
from os.path import exists

from flask import Flask, send_file, request
from PIL import Image, ImageDraw, ImageFont
import humanize
app = Flask(__name__)


num_key_frames = 29

b_gif = Image.open('./assets/rat-spinning.gif')

font = ImageFont.truetype("./assets/Roboto-Bold.ttf", 15)

def add():
    if not exists('count.txt'):
        open('count.txt', 'w')

    with open('count.txt', 'r+') as f:
        lines = f.readlines()
        if len(lines) <= 0:
            f.writelines("1")
            return 1
            
        count = int(lines[0])
        count += 1
        f.truncate(0)
        f.seek(0)
        f.writelines(str(count))
    
    return count

def make_rat(count: int = 1, size: int = 300):
    b_frames = []
    
    for i in range(num_key_frames):
        b_gif.seek(b_gif.n_frames // num_key_frames * i)
        b_frames.append(b_gif.copy())
    
    ordinal = humanize.ordinal(count)
    frames = []
    banner = Image.new("RGBA", (size, size+75), (255, 255, 255))
    draw = ImageDraw.Draw(banner)
    text = f"{ordinal} rat visitor!"
    w, h = draw.textsize(text)
    draw.text((((size-w)/2), ((75-h)/2)), text, fill=(0, 0, 0), font=font)
    
    m_length = ceil(sqrt(count))
    f_size = ceil(size/m_length)
    
    for f in range(len(b_frames)):
        b_frames[f]= b_frames[f].resize((f_size, f_size), resample=Image.NEAREST)

    for f in range(len(b_frames)):
        rat_left = count
        frame = Image.new("RGBA", (size, size+75))
        for y in range(m_length):
            for x in range(m_length):
                rat_left-=1
                if rat_left >= 0:
                    frame.paste(b_frames[f], (x*f_size, y*f_size+75))
        frames.append(Image.alpha_composite(banner.copy(), frame))        

    
    # Convert to Base64
    buffer = io.BytesIO()
    frames[0].save(buffer, format="PNG", quality=50, save_all=True, append_images=frames[1:], loop=0)
    buffer.seek(0)
    
    return buffer

@app.route('/get')
def index():
    size = request.get("size", default=300, type=int)
    count = add()
    b64 = make_rat(count, size)
    
    return send_file(
        b64, download_name=f"{count}-spinning-rat.png", mimetype="image/png"
    )