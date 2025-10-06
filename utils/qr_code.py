import qrcode
import logging
import os
from PIL import Image, ImageDraw, ImageFont
from typing import Optional
import io

logger = logging.getLogger(__name__)

# Design constants
QR_SIZE = 400
IMAGE_SIZE = 512
TEXT_COLOR = "#0a1411"  # Белый текст «Lethai»
FONT_SIZE = 35
QR_OPACITY = 180  # 0..255, степень непрозрачности QR-фон (255 — полностью непрозрачный)

def get_font() -> Optional[ImageFont.FreeTypeFont]:
    """
    Загружает системный шрифт в Docker (DejaVuSans),
    если не найден — возвращает встроенный по умолчанию.
    """
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, FONT_SIZE)
        else:
            logger.warning(f"Font not found at {font_path}, using default font")
            return ImageFont.load_default()
    except Exception as e:
        logger.warning(f"Could not load custom font: {e}")
        return ImageFont.load_default()

def _make_qr_on_transparent_bg(url: str) -> Image.Image:
    """
    Создаёт изображение QR-кода (чёрные модули) на полупрозрачном белом фоне,
    возвращает RGBA изображение нужного размера QR_SIZE×QR_SIZE.
    """
    # Генерация QR (чёрный модули, белый фон)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    base = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    # Теперь сделаем фон (белый) полупрозрачным, сохраняя модули чёрными полностью.
    # То есть: если пиксель белый — он будет иметь альфа QR_OPACITY; если чёрный — альфа = 255.
    data = base.getdata()
    new_data = []
    for (r, g, b, a) in data:
        # Если белый фон (примерно белый) — заменяем на белый полупрозрачный
        if (r, g, b) == (255, 255, 255):
            new_data.append((255, 255, 255, QR_OPACITY))
        else:
            # чёрные модули остаются полностью непрозрачными (альфа=255)
            new_data.append((0, 0, 0, 255))
    base.putdata(new_data)
    # Изменим размер, если надо
    base = base.resize((QR_SIZE, QR_SIZE), resample=Image.LANCZOS)
    return base

def generate_qr_code(partnercode: str) -> Optional[str]:
    try:
        url = f"https://taplink.cc/lakeevainfo?ref={partnercode}"
        qr_img = _make_qr_on_transparent_bg(url)
        
        # Load background
        background_path = os.path.join(os.path.dirname(__file__), 'background.jpg')
        img = Image.open(background_path).convert("RGB")
        if img.size != (IMAGE_SIZE, IMAGE_SIZE):
            img = img.resize((IMAGE_SIZE, IMAGE_SIZE))
        draw = ImageDraw.Draw(img)
        
        # Позиция QR на фоне
        qr_x = (IMAGE_SIZE - QR_SIZE) // 2
        qr_y = (IMAGE_SIZE - QR_SIZE) // 2 - 20
        
        img.paste(qr_img, (qr_x, qr_y), qr_img)  # используем альфа из qr_img
        
        # Текст «Lethai» под QR
        font = get_font()
        text = "Lethai services"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (IMAGE_SIZE - text_width) // 2
        text_y = qr_y + QR_SIZE + 20
        draw.text((text_x, text_y), text, fill=TEXT_COLOR, font=font)
        
        filename = f"qr_{partnercode}.jpg"
        img.save(filename, "JPEG", quality=95)
        logger.info(f"QR code generated successfully: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error generating QR code for partnercode {partnercode}: {e}")
        return None

def generate_qr_code_bytes(partnercode: str) -> Optional[bytes]:
    try:
        url = f"https://taplink.cc/lakeevainfo?ref={partnercode}"
        qr_img = _make_qr_on_transparent_bg(url)
        
        background_path = os.path.join(os.path.dirname(__file__), 'background.jpg')
        img = Image.open(background_path).convert("RGB")
        if img.size != (IMAGE_SIZE, IMAGE_SIZE):
            img = img.resize((IMAGE_SIZE, IMAGE_SIZE))
        draw = ImageDraw.Draw(img)
        
        qr_x = (IMAGE_SIZE - QR_SIZE) // 2
        qr_y = (IMAGE_SIZE - QR_SIZE) // 2 - 20
        img.paste(qr_img, (qr_x, qr_y), qr_img)
        
        font = get_font()
        text = "Lethai services"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (IMAGE_SIZE - text_width) // 2 + 54
        text_y = qr_y + QR_SIZE + 20
        draw.text((text_x, text_y), text, fill=TEXT_COLOR, font=font)
        
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        buf.seek(0)
        logger.info(f"QR code generated as bytes for partnercode {partnercode}")
        return buf.getvalue()
    except Exception as e:
        logger.error(f"Error generating QR code bytes for partnercode {partnercode}: {e}")
        return None

def cleanup_qr_files() -> None:
    try:
        import glob
        qr_files = glob.glob("qr_*.jpg")
        for file in qr_files:
            try:
                os.remove(file)
                logger.info(f"Cleaned up QR file: {file}")
            except OSError as e:
                logger.warning(f"Could not remove QR file {file}: {e}")
    except Exception as e:
        logger.error(f"Error during QR file cleanup: {e}")

def get_referral_link(partnercode: str) -> str:
    return f"https://taplink.cc/lakeevainfo?ref={partnercode}"

def validate_partnercode(partnercode: str) -> bool:
    try:
        return partnercode.isdigit() and len(partnercode) > 0
    except (TypeError, AttributeError):
        return False
