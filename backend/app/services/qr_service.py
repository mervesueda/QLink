"""
services/qr_service.py – QR kod üretim servisi.

qrcode[pil] kütüphanesi ile PNG formatında QR kod üretir.
Servis katmanında olduğu için API handler'larından bağımsız test edilebilir.
"""

import io

import qrcode
from qrcode.image.pil import PilImage


def generate_qr_png(content: str) -> bytes:
    """
    Verilen içeriği QR koda dönüştürür ve PNG bytes olarak döner.

    Args:
        content: QR'a encode edilecek string (URL, metin, e-posta)

    Returns:
        PNG formatında QR kod görüntüsü (bytes)
    """
    qr = qrcode.QRCode(
        version=1,           # 1-40 arası; 1 en küçük boyut
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # %15 hata düzeltme
        box_size=10,         # Her piksel kutusunun boyutu
        border=4,            # Kenar boşluğu (minimum 4 öneridir)
    )
    qr.add_data(content)
    qr.make(fit=True)  # Version'u içeriğe göre otomatik ayarla

    img: PilImage = qr.make_image(fill_color="black", back_color="white")

    # Belleğe PNG olarak yaz, dosya sistemi kullanma
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.read()
