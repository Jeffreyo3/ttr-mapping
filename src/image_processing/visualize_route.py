from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from src.data_types.route import Route

# Constants
FONT_PATH = (
    Path(__file__).parent.parent / "starting_data" / "fonts" / "CHIPPEWA_FALLS.TTF"
)
MAP_PATH = Path(__file__).parent.parent / "starting_data" / "maps" / "US_MAP.jpg"
OUTPUT_DIR = Path(__file__).parent.parent / "output_data" / "visualized_routes"

# Colors (hex to RGB)
WHITE = (255, 255, 255)
RED = (102, 0, 0)  # #660000
DARK_GREEN = (13, 55, 13)  # #0d370d
BLACK = (0, 0, 0)

# Dimensions
HEADER_HEIGHT = 130
IMAGE_WIDTH = 1029
IMAGE_HEIGHT = 735
DOT_SIZE = 20
LINE_WIDTH = 10
FONT_SIZE = 64
ANTIALIASING_SCALE = 3


def visualize_route(
    route: Route, city_map: dict, output_image_path: str | None = None
) -> None:
    """
    Visualize a route on the US map by drawing a header with city names,
    red dots at each city's coordinates, and a green line connecting them.

    Args:
        route: Route object containing two City objects
        city_map: Dictionary mapping City to Location (from build_map())
        output_image_path: Optional custom output path. Defaults to src/output_data/visualized_routes/{route.a.name}_{route.b.name}.jpeg
    """
    # Determine output path
    if output_image_path is None:
        output_image_path = str(OUTPUT_DIR / f"{route.a.name}_{route.b.name}.jpeg")

    # Load the map image
    img = Image.open(MAP_PATH).convert("RGB")
    img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS)

    draw = ImageDraw.Draw(img)

    # Draw white header box with transparency
    header_img = Image.new("RGBA", (IMAGE_WIDTH, HEADER_HEIGHT), (255, 255, 255, 102))
    img.paste(header_img, (0, 0), header_img)

    # Load font with fallback
    try:
        font = ImageFont.truetype(str(FONT_PATH), size=FONT_SIZE)
    except (OSError, FileNotFoundError):
        font = ImageFont.load_default(size=int(FONT_SIZE * 0.6))

    # Draw header text
    header_text = f"{route.a.value} <> {route.b.value}"
    bbox = draw.textbbox((0, 0), header_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    text_x = (IMAGE_WIDTH - text_width) // 2
    text_y = (HEADER_HEIGHT - text_height) // 2 - 10

    draw.text((text_x, text_y), header_text, fill=BLACK, font=font)

    # Get coordinates from Location objects in city_map
    location_a = city_map[route.a]
    location_b = city_map[route.b]
    coord_a = location_a.coordinates
    coord_b = location_b.coordinates

    if coord_a is None or coord_b is None:
        raise ValueError(
            f"Route cities must have coordinates. "
            f"{route.a.value}: {coord_a}, {route.b.value}: {coord_b}"
        )

    x1, y1 = coord_a["x"], coord_a["y"]
    x2, y2 = coord_b["x"], coord_b["y"]

    # Draw at higher resolution for antialiasing, then scale down
    scaled_width = IMAGE_WIDTH * ANTIALIASING_SCALE
    scaled_height = IMAGE_HEIGHT * ANTIALIASING_SCALE
    scaled_img = img.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
    scaled_draw = ImageDraw.Draw(scaled_img)

    scaled_draw.line(
        [
            (x1 * ANTIALIASING_SCALE, y1 * ANTIALIASING_SCALE),
            (x2 * ANTIALIASING_SCALE, y2 * ANTIALIASING_SCALE),
        ],
        fill=DARK_GREEN,
        width=LINE_WIDTH * ANTIALIASING_SCALE,
    )

    scaled_dot_radius = DOT_SIZE * ANTIALIASING_SCALE / 2.0
    scaled_draw.ellipse(
        [
            (
                x1 * ANTIALIASING_SCALE - scaled_dot_radius,
                y1 * ANTIALIASING_SCALE - scaled_dot_radius,
            ),
            (
                x1 * ANTIALIASING_SCALE + scaled_dot_radius,
                y1 * ANTIALIASING_SCALE + scaled_dot_radius,
            ),
        ],
        fill=RED,
    )
    scaled_draw.ellipse(
        [
            (
                x2 * ANTIALIASING_SCALE - scaled_dot_radius,
                y2 * ANTIALIASING_SCALE - scaled_dot_radius,
            ),
            (
                x2 * ANTIALIASING_SCALE + scaled_dot_radius,
                y2 * ANTIALIASING_SCALE + scaled_dot_radius,
            ),
        ],
        fill=RED,
    )

    # Scale back down with antialiasing
    img = scaled_img.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS)

    # Save the image
    img.save(output_image_path, "JPEG", quality=100)
