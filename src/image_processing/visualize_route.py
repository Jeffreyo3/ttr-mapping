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
DOT_SIZE = 20
LINE_WIDTH = 10

# Font sizes
FONT_SIZE = 64
SCORE_FONT_SIZE = 106

# Rendering
ANTIALIASING_SCALE = 3

# Header text
HEADER_TEXT_PADDING = 40  # pixels on each side
HEADER_TEXT_Y_OFFSET = 10  # pixels up from vertical center

# Score circle
CIRCLE_RADIUS_MULTIPLIER = 0.84  # relative to SCORE_FONT_SIZE
CIRCLE_EDGE_PADDING = 20  # pixels from edge
CIRCLE_FILL_ALPHA = 150
CIRCLE_BORDER_WIDTH_DIVISOR = 1.5  # LINE_WIDTH / this value
SCORE_TEXT_VERTICAL_OFFSET = 0.12  # relative to text height

# Geographic positioning for score circle
LON_LEFT_THIRD_PERCENT = 0.333
LON_LEFT_QUARTER_PERCENT = 0.25
LON_RIGHT_QUARTER_PERCENT = 0.25


def lat_lon_to_pixel(
    lat: float,
    lon: float,
    image_width: int,
    image_height: int,
    bounds: dict,
) -> tuple[float, float]:
    """Convert latitude/longitude to pixel coordinates on the image."""
    pixel_x = (
        (lon - bounds["min_lon"]) / (bounds["max_lon"] - bounds["min_lon"])
    ) * image_width
    pixel_y = ((bounds["max_lat"] - lat) / (bounds["max_lat"] - bounds["min_lat"])) * (
        image_height - HEADER_HEIGHT
    ) + HEADER_HEIGHT
    return (pixel_x, pixel_y)


def _calculate_circle_x_position(
    coord_a: dict,
    coord_b: dict,
    bounds: dict,
    image_width: int,
    circle_radius: int,
) -> int:
    """Calculate horizontal position of score circle based on city locations."""
    lon_range = bounds["max_lon"] - bounds["min_lon"]
    lon_midpoint = (bounds["min_lon"] + bounds["max_lon"]) / 2
    left_third = bounds["min_lon"] + lon_range * LON_LEFT_THIRD_PERCENT
    left_quarter = bounds["min_lon"] + lon_range * LON_LEFT_QUARTER_PERCENT
    right_quarter = bounds["max_lon"] - lon_range * LON_RIGHT_QUARTER_PERCENT

    # Check if one location is in left 1/4 and the other is in right 1/4
    one_left_one_right = (
        coord_a["lon"] < left_quarter and coord_b["lon"] > right_quarter
    ) or (coord_b["lon"] < left_quarter and coord_a["lon"] > right_quarter)

    # Check if one location is in left half and the other is not in right 1/4
    one_left_one_not_right_quarter = (
        coord_a["lon"] < lon_midpoint and coord_b["lon"] <= right_quarter
    ) or (coord_b["lon"] < lon_midpoint and coord_a["lon"] <= right_quarter)

    if one_left_one_right:
        # One on left 1/4, one on right 1/4: center the score
        return image_width // 2
    elif one_left_one_not_right_quarter:
        # One in left half, other not in right 1/4: place score on right
        return image_width - circle_radius - CIRCLE_EDGE_PADDING
    elif coord_a["lon"] < left_third and coord_b["lon"] < left_third:
        # Both cities are in left 1/3, place score on right
        return image_width - circle_radius - CIRCLE_EDGE_PADDING
    else:
        # Default: place score on left
        return circle_radius + CIRCLE_EDGE_PADDING


def _load_font(font_path: str, size: int) -> ImageFont.FreeTypeFont:
    """Load font with fallback to default if custom font unavailable."""
    try:
        return ImageFont.truetype(font_path, size=size)
    except (OSError, FileNotFoundError):
        return ImageFont.load_default(size=int(size * 0.6))


def _draw_curved_line(
    draw: ImageDraw.ImageDraw,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: tuple[int, int, int],
    width: int,
    curve_amount: float = 0.1,
) -> None:
    """
    Draw a curved line between two points using quadratic Bezier curve.

    Args:
        draw: ImageDraw object
        x1, y1: Start point coordinates
        x2, y2: End point coordinates
        color: Line color (RGB tuple)
        width: Line width
        curve_amount: Curve intensity (0.1 = 10% of line distance)
    """
    # Calculate midpoint
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2

    # Vector from point 1 to point 2
    dx = x2 - x1
    dy = y2 - y1

    # Perpendicular vector (rotated 90 degrees)
    perp_x = -dy
    perp_y = dx

    # Normalize and scale perpendicular vector for curve control point
    length = (perp_x**2 + perp_y**2) ** 0.5
    if length > 0:
        perp_x = (perp_x / length) * length * curve_amount
        perp_y = (perp_y / length) * length * curve_amount

    # Control point for the curve (offset from midpoint)
    ctrl_x = mid_x + perp_x
    ctrl_y = mid_y + perp_y

    # Draw curved line as a series of line segments
    num_segments = 20
    points = []
    for i in range(num_segments + 1):
        t = i / num_segments
        # Quadratic Bezier formula: B(t) = (1-t)²P0 + 2(1-t)tC + t²P1
        px = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * ctrl_x + t**2 * x2
        py = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * ctrl_y + t**2 * y2
        points.append((px, py))

    draw.line(points, fill=color, width=width)


def _draw_header_text(
    draw: ImageDraw.ImageDraw,
    header_text: str,
    image_width: int,
) -> tuple[int, int]:
    """Draw header text with automatic font scaling if needed."""
    font = _load_font(str(FONT_PATH), FONT_SIZE)
    bbox = draw.textbbox((0, 0), header_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Scale down font if text exceeds image width (with padding)
    max_text_width = image_width - HEADER_TEXT_PADDING
    if text_width > max_text_width:
        scale_factor = max_text_width / text_width
        new_font_size = int(FONT_SIZE * scale_factor)
        font = _load_font(str(FONT_PATH), new_font_size)
        # Recalculate dimensions with new font
        bbox = draw.textbbox((0, 0), header_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

    text_x = (image_width - text_width) // 2
    text_y = (HEADER_HEIGHT - text_height) // 2 - HEADER_TEXT_Y_OFFSET

    draw.text((text_x, text_y), header_text, fill=BLACK, font=font)


def _draw_score_circle(
    img: Image.Image,
    circle_x: int,
    circle_y: int,
    circle_radius: int,
    score_text: str,
    image_width: int,
    image_height: int,
) -> None:
    """Draw the score circle with text in the bottom corner."""
    # Draw white circle with transparency
    circle_img = Image.new(
        "RGBA",
        (image_width, image_height),
        (0, 0, 0, 0),
    )
    circle_draw = ImageDraw.Draw(circle_img)
    circle_draw.ellipse(
        [
            (circle_x - circle_radius, circle_y - circle_radius),
            (circle_x + circle_radius, circle_y + circle_radius),
        ],
        fill=(255, 255, 255, CIRCLE_FILL_ALPHA),
        outline=DARK_GREEN,
        width=int(LINE_WIDTH / CIRCLE_BORDER_WIDTH_DIVISOR),
    )
    img.paste(circle_img, (0, 0), circle_img)


def _visualize_single_route(
    route: Route,
    output_image_path: str,
    base_img: Image.Image,
    image_width: int,
    image_height: int,
    city_map: dict,
    bounds: dict,
) -> None:
    """Helper function to visualize a single route."""
    # Use the pre-loaded base image (convert to RGB for each route to avoid modifying shared state)
    img = base_img.convert("RGB")

    draw = ImageDraw.Draw(img)

    # Draw white header box with transparency
    header_img = Image.new("RGBA", (image_width, HEADER_HEIGHT), (255, 255, 255, 102))
    img.paste(header_img, (0, 0), header_img)

    # Draw header text
    header_text = f"{route.a.value} <> {route.b.value}"
    _draw_header_text(draw, header_text, image_width)

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
    x1, y1 = lat_lon_to_pixel(
        coord_a["lat"], coord_a["lon"], image_width, image_height, bounds
    )
    x2, y2 = lat_lon_to_pixel(
        coord_b["lat"], coord_b["lon"], image_width, image_height, bounds
    )

    # Draw at higher resolution for antialiasing, then scale down
    scaled_width = image_width * ANTIALIASING_SCALE
    scaled_height = image_height * ANTIALIASING_SCALE
    scaled_img = img.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
    scaled_draw = ImageDraw.Draw(scaled_img)

    # Draw curved line
    _draw_curved_line(
        scaled_draw,
        x1 * ANTIALIASING_SCALE,
        y1 * ANTIALIASING_SCALE,
        x2 * ANTIALIASING_SCALE,
        y2 * ANTIALIASING_SCALE,
        DARK_GREEN,
        LINE_WIDTH * ANTIALIASING_SCALE,
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
    img = scaled_img.resize((image_width, image_height), Image.Resampling.LANCZOS)

    # Draw score circle
    draw = ImageDraw.Draw(img)
    score_text = str(route.value)

    # Circle parameters - fixed size consistent for all scores
    circle_radius = int(SCORE_FONT_SIZE * CIRCLE_RADIUS_MULTIPLIER)

    # Determine score position based on longitude
    circle_x = _calculate_circle_x_position(
        coord_a, coord_b, bounds, image_width, circle_radius
    )
    circle_y = image_height - circle_radius - CIRCLE_EDGE_PADDING

    _draw_score_circle(
        img, circle_x, circle_y, circle_radius, score_text, image_width, image_height
    )

    # Draw score text on top
    score_font = _load_font(str(FONT_PATH), SCORE_FONT_SIZE)
    bbox = draw.textbbox((0, 0), score_text, font=score_font)
    score_text_width = bbox[2] - bbox[0]
    score_text_height = bbox[3] - bbox[1]

    text_x = circle_x - score_text_width // 2
    text_y = (
        circle_y
        - score_text_height // 2
        - score_text_height // 2
        + int(score_text_height * SCORE_TEXT_VERTICAL_OFFSET)
    )
    draw.text((text_x, text_y), score_text, fill=BLACK, font=score_font)

    # Save the image
    img.save(output_image_path, "JPEG", quality=100)


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

    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load the map image once
    base_img = Image.open(map_path)
    IMAGE_WIDTH, IMAGE_HEIGHT = base_img.size
    print(f"Map dimensions loaded: {IMAGE_WIDTH}x{IMAGE_HEIGHT}")

    # Generate individual images and collect their paths
    image_paths = []
    for route in routes:
        image_path = OUTPUT_DIR / f"{route.a.name}_{route.b.name}.jpeg"
        _visualize_single_route(
            route,
            str(image_path),
            base_img,
            IMAGE_WIDTH,
            IMAGE_HEIGHT,
            city_map,
            bounds,
        )
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
