import qrcode
import base64
from io import BytesIO


# https://pypi.org/project/qrcode/
def qr(data):
    _qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    _qr.add_data(data)
    _qr.make(fit=True)

    image = _qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return "<img class=\"responsive-image\" src='data:image/png;base64, " + base64.b64encode(buffer.getvalue()).decode() + "'>"
