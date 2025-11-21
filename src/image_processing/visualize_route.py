import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from src.data_types.route import Route

# Constants
FONT_PATH = (
    Path(__file__).parent.parent / "starting_data" / "fonts" / "CHIPPEWA_FALLS.TTF"
)
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
SCORE_FONT_SIZE = 106
ANTIALIASING_SCALE = 3


def visualize_route(
    routes: list[Route],
    city_map: dict,
    map_path: str,
    bounds: dict | None = None,
) -> str:
    """
    Visualize multiple routes on a map by drawing headers with city names,
    red dots at each city's coordinates, and green lines connecting them.
    Generates individual JPEG images for each route and saves them to a zip file.

    Args:
        routes: List of Route objects to visualize
        city_map: Dictionary mapping City to Location (from build_map())
        map_path: Path to the map image file
        bounds: Optional dict with map bounds: {"min_lat": float, "max_lat": float, "min_lon": float, "max_lon": float}
                If not provided, defaults to entire Earth: lat [-90, 90], lon [-180, 180]

    Returns:
        str: Path to the generated zip file containing all route visualizations
    """
    # Default bounds for entire Earth
    if bounds is None:
        bounds = {
            "min_lat": -90.0,  # South pole
            "max_lat": 90.0,  # North pole
            "min_lon": -180.0,  # International Date Line (west)
            "max_lon": 180.0,  # International Date Line (east)
        }

    def lat_lon_to_pixel(lat: float, lon: float) -> tuple[float, float]:
        """Convert latitude/longitude to pixel coordinates on the image."""
        # Calculate pixel position based on bounds
        pixel_x = (
            (lon - bounds["min_lon"]) / (bounds["max_lon"] - bounds["min_lon"])
        ) * IMAGE_WIDTH
        pixel_y = (
            (bounds["max_lat"] - lat) / (bounds["max_lat"] - bounds["min_lat"])
        ) * (IMAGE_HEIGHT - HEADER_HEIGHT) + HEADER_HEIGHT
        return (pixel_x, pixel_y)

    def _visualize_single_route(route: Route, output_image_path: str) -> None:
        """Helper function to visualize a single route."""
        # Load the map image
        img = Image.open(map_path).convert("RGB")
        img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS)

        draw = ImageDraw.Draw(img)

        # Draw white header box with transparency
        header_img = Image.new(
            "RGBA", (IMAGE_WIDTH, HEADER_HEIGHT), (255, 255, 255, 102)
        )
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

        # Convert lat/lon to pixel coordinates
        x1, y1 = lat_lon_to_pixel(coord_a["lat"], coord_a["lon"])
        x2, y2 = lat_lon_to_pixel(coord_b["lat"], coord_b["lon"])

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

        # Draw score circle in bottom right or bottom left
        draw = ImageDraw.Draw(img)
        score_text = str(route.value)

        # Load score font
        try:
            score_font = ImageFont.truetype(str(FONT_PATH), size=SCORE_FONT_SIZE)
        except (OSError, FileNotFoundError):
            score_font = ImageFont.load_default(size=int(SCORE_FONT_SIZE * 0.6))

        bbox = draw.textbbox((0, 0), score_text, font=score_font)
        score_text_width = bbox[2] - bbox[0]
        score_text_height = bbox[3] - bbox[1]

        # Circle parameters (doubled diameter)
        padding = 40
        circle_radius = max(score_text_width, score_text_height) + padding

        # Determine score position based on longitude
        # If both cities are in the right half of the bounds, place on bottom left
        lon_midpoint = (bounds["min_lon"] + bounds["max_lon"]) / 2
        if coord_a["lon"] > lon_midpoint and coord_b["lon"] > lon_midpoint:
            circle_x = circle_radius + 20
        else:
            circle_x = IMAGE_WIDTH - circle_radius - 20

        circle_y = IMAGE_HEIGHT - circle_radius - 20

        # Draw white circle with transparency
        circle_img = Image.new(
            "RGBA",
            (IMAGE_WIDTH, IMAGE_HEIGHT),
            (0, 0, 0, 0),
        )
        circle_draw = ImageDraw.Draw(circle_img)
        circle_draw.ellipse(
            [
                (circle_x - circle_radius, circle_y - circle_radius),
                (circle_x + circle_radius, circle_y + circle_radius),
            ],
            fill=(255, 255, 255, 190),
            outline=DARK_GREEN,
            width=int(LINE_WIDTH / 1.5),
        )
        img.paste(circle_img, (0, 0), circle_img)

        # Draw score text centered in circle, shifted north by half its height
        draw = ImageDraw.Draw(img)
        text_x = circle_x - score_text_width // 2
        text_y = (
            circle_y
            - score_text_height // 2
            - score_text_height // 2
            + int(score_text_height * 0.075)
        )
        draw.text((text_x, text_y), score_text, fill=BLACK, font=score_font)

        # Save the image
        img.save(output_image_path, "JPEG", quality=100)

    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate individual images and collect their paths
    image_paths = []
    for route in routes:
        image_path = OUTPUT_DIR / f"{route.a.name}_{route.b.name}.jpeg"
        _visualize_single_route(route, str(image_path))
        image_paths.append(image_path)

    # Create zip file containing all images
    zip_path = OUTPUT_DIR / "route_visualizations.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for image_path in image_paths:
            zip_file.write(image_path, arcname=image_path.name)

    # Clean up individual JPEG files
    for image_path in image_paths:
        image_path.unlink()

    return str(zip_path)
