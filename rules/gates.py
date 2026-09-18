"""Shared direction rules for one-way gate tiles."""

GATE_DIRECTIONS = {
    "one_way_up": (0, -1),
    "one_way_right": (1, 0),
    "one_way_down": (0, 1),
    "one_way_left": (-1, 0),
}


def movement_direction(dx, dy):
    """Return a cardinal direction for the dominant movement axis."""
    if abs(dx) >= abs(dy) and dx:
        return (1 if dx > 0 else -1, 0)
    if dy:
        return (0, 1 if dy > 0 else -1)
    return (0, 0)


def gate_allows(gate_name, dx, dy):
    """Whether movement follows the arrow shown on this gate."""
    allowed = GATE_DIRECTIONS.get(gate_name)
    return allowed is None or movement_direction(dx, dy) == allowed
