from io import BytesIO
from pathlib import Path

import PIL
from PIL import Image, ImageDraw, ImageFont

from src.api.weather_api import WeatherResponse


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    pil_fonts_dir = Path(PIL.__file__).resolve().parent / "fonts"
    candidates = [
        pil_fonts_dir / "DejaVuSans-Bold.ttf",
        pil_fonts_dir / "DejaVuSans.ttf",
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/Library/Fonts/Arial.ttf"),
    ]

    for font_path in candidates:
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size)
            except OSError:
                continue

    return ImageFont.load_default()


def _pick_gradient(temp_c: float, cloud: int) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    if temp_c <= 0:
        start, end = (14, 48, 88), (90, 160, 214)
    elif temp_c <= 15:
        start, end = (32, 84, 130), (124, 162, 194)
    elif temp_c <= 28:
        start, end = (238, 162, 84), (255, 208, 122)
    else:
        start, end = (227, 96, 49), (255, 165, 80)

    cloud_factor = min(max(cloud, 0), 100) / 100
    darken = int(40 * cloud_factor)
    return (
        max(start[0] - darken, 0),
        max(start[1] - darken, 0),
        max(start[2] - darken, 0),
    ), (
        max(end[0] - darken, 0),
        max(end[1] - darken, 0),
        max(end[2] - darken, 0),
    )


def _draw_weather_icon(draw: ImageDraw.ImageDraw, temp_c: float, cloud: int, width: int) -> None:
    icon_center_x = width - 210
    icon_center_y = 180
    sun_color = (255, 213, 110)
    cloud_color = (236, 240, 245)
    cloud_shadow = (177, 186, 197)

    if cloud < 50:
        draw.ellipse(
            [icon_center_x - 90, icon_center_y - 90,
                icon_center_x + 90, icon_center_y + 90],
            fill=sun_color,
        )
        if temp_c > 30:
            draw.ellipse(
                [icon_center_x - 45, icon_center_y - 45,
                    icon_center_x + 45, icon_center_y + 45],
                fill=(255, 235, 160),
            )
    else:
        draw.ellipse(
            [icon_center_x - 70, icon_center_y - 70,
                icon_center_x + 70, icon_center_y + 70],
            fill=(255, 220, 125),
        )

    cloud_x = width - 350
    cloud_y = 190
    draw.ellipse([cloud_x, cloud_y, cloud_x + 130,
                 cloud_y + 95], fill=cloud_shadow)
    draw.ellipse([cloud_x + 70, cloud_y - 35, cloud_x +
                 220, cloud_y + 85], fill=cloud_shadow)
    draw.ellipse([cloud_x + 180, cloud_y, cloud_x +
                 320, cloud_y + 95], fill=cloud_shadow)
    draw.rounded_rectangle([cloud_x + 35, cloud_y + 45, cloud_x +
                           280, cloud_y + 120], radius=30, fill=cloud_shadow)

    draw.ellipse([cloud_x - 8, cloud_y - 8, cloud_x +
                 122, cloud_y + 87], fill=cloud_color)
    draw.ellipse([cloud_x + 62, cloud_y - 43, cloud_x +
                 212, cloud_y + 77], fill=cloud_color)
    draw.ellipse([cloud_x + 172, cloud_y - 8, cloud_x +
                 312, cloud_y + 87], fill=cloud_color)
    draw.rounded_rectangle([cloud_x + 27, cloud_y + 37, cloud_x +
                           272, cloud_y + 112], radius=30, fill=cloud_color)


def render_weather_card(weather_info: WeatherResponse) -> bytes:
    width, height = 1280, 720
    temp_c = weather_info["current"]["temp_c"]
    cloud = weather_info["current"]["cloud"]
    start_color, end_color = _pick_gradient(temp_c, cloud)

    img = Image.new("RGB", (width, height), start_color)
    draw = ImageDraw.Draw(img)

    for y in range(height):
        blend = y / max(height - 1, 1)
        row_color = (
            int(start_color[0] * (1 - blend) + end_color[0] * blend),
            int(start_color[1] * (1 - blend) + end_color[1] * blend),
            int(start_color[2] * (1 - blend) + end_color[2] * blend),
        )
        draw.line([(0, y), (width, y)], fill=row_color)

    draw.rounded_rectangle(
        [55, 55, width - 55, height - 55],
        radius=36,
        fill=(14, 22, 37),
        outline=(255, 255, 255),
        width=2,
    )

    _draw_weather_icon(draw, temp_c, cloud, width)

    title_font = _load_font(76)
    big_font = _load_font(170)
    text_font = _load_font(62)
    meta_font = _load_font(44)
    wind_font = _load_font(40)

    city = weather_info["location"]["name"]
    country = weather_info["location"]["country"]
    condition = weather_info["current"]["condition"]["text"]
    humidity = weather_info["current"]["humidity"]
    wind_kph = weather_info["current"]["wind_kph"]

    draw.text((95, 75), f"{city}, {country}",
              font=title_font, fill=(255, 255, 255))
    draw.text((95, 165), f"{temp_c:.1f} C",
              font=big_font, fill=(255, 255, 255))
    draw.text((95, 355), condition, font=text_font, fill=(237, 241, 246))

    draw.rounded_rectangle([95, 480, 560, 690], radius=24, fill=(65, 83, 107))
    draw.text((125, 510), "Humidity", font=meta_font, fill=(226, 232, 240))
    draw.text((125, 555), f"{humidity}%", font=text_font, fill=(255, 255, 255))

    draw.text((125, 630), f"Wind: {wind_kph:.1f} kph",
              font=wind_font, fill=(255, 255, 255))

    draw.rounded_rectangle([610, 480, 1185, 690],
                           radius=24, fill=(65, 83, 107))
    draw.text((640, 510), "Cloudiness", font=meta_font, fill=(226, 232, 240))
    draw.text((640, 555), f"{cloud}%", font=text_font, fill=(255, 255, 255))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
