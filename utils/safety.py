
def validate_interval(value, minimum=0.1):

    interval = float(value)

    if interval < minimum:
        raise ValueError(
            f"Interval minimum adalah {minimum} detik."
        )

    return interval


def validate_screen_point(point, screen_size):

    x, y = point
    width, height = screen_size

    return (
        0 <= x < width
        and 0 <= y < height
    )
