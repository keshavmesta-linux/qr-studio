from datetime import datetime
from flask import Flask, render_template, request
import qrcode
from io import BytesIO
import base64
import re

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    qr_image = None
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    error = None
    content = ""
    fill_color = "#172554"
    box_size = 10

    if request.method == "POST":
        content = request.form.get("content", "").strip()
        fill_color = request.form.get("color", "#172554")
        raw_size = request.form.get("size", "10")

        if not content:
            error = "Please enter text or a URL."
        elif len(content) > 2000:
            error = "Please keep your input under 2000 characters."
        elif not re.fullmatch(r"#[0-9a-fA-F]{6}", fill_color):
            error = "Please select a valid QR color."
        else:
            try:
                box_size = max(6, min(16, int(raw_size)))
                qr = qrcode.QRCode(
                    version=None,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=box_size,
                    border=4
                )
                qr.add_data(content)
                qr.make(fit=True)

                image = qr.make_image(
                    fill_color=fill_color,
                    back_color="white"
                ).convert("RGB")

                buffer = BytesIO()
                image.save(buffer, format="PNG")
                qr_image = base64.b64encode(
                    buffer.getvalue()
                ).decode("utf-8")
            except Exception:
                error = "Couldn't generate the QR code. Try shorter text."

    return render_template(
        "index.html",
        qr_image=qr_image,
        timestamp=timestamp,
        error=error,
        content=content,
        color=fill_color,
        size=box_size
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
