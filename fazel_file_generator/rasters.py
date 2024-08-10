from astropy.table import QTable


def spiral(n, origin=False):
    """Spiral raster scan for (n+1)^2 points.

    E.g., for n=1,

      2 1 8
      3 0 7
      4 5 6

    Parameters
    ----------
    n : int
        Number of points away from origin in each direction.
    origin : bool or None
        Whether to return to the origin (diagonally) in the end.
        (would add a 10th point in center for n=1).
        If `None`, exclude the origin and the start and end
        (with the logic that those get done as part of the fazel
        file already).
    """
    x = y = 0
    scan = [(x, y)] if origin is not None else []
    dx = -1
    dy = 1
    m = 0
    for i in range(n*2):
        m += 1
        for j in range(m):
            y += dy
            scan.append((x, y))
        for j in range(m):
            x += dx
            scan.append((x, y))
        dx = -dx
        dy = -dy
    for j in range(m):
        y += dy
        scan.append((x, y))
    if origin is not False:
        for j in range(n if origin is not None else n-1):
            x += dx
            y -= dy
            scan.append((x, y))
    return QTable(rows=scan, names=["x", "y"], dtype=["f", "f"])


def zigzag(n, origin=False):
    """Zig-zag scan for (n+1)^2 points.

    E.g., for n=1,

    0 5 6
    1 4 7
    2 3 8

    Parameters
    ----------
    n : int
        Number of points away from origin in each direction.
    origin : bool or None
        Whether to start from and return to the origin (diagonally).
        (for n=1, this would add an extra point at the origin at the
        start and end, i.e., 11 points in total).
        If `None`, exclude the origin and the start and end
        (with the logic that those get done as part of the fazel
        file already, so this would mean 9 points in total).
    """
    dx = -1
    dy = 1
    scan = []
    for j in range(0 if origin is True else 1, 0 if origin is False else n):
        scan.append((j*dx, j*dy))
    dx = -dx
    for i in range(-n, n+1):
        dy = -dy
        for j in range(-n, n+1):
            scan.append((i*dx, j*dy))
    for i in range(0 if origin is False else n-1, -1 if origin is True else 0, -1):
        scan.append((i*dx, i*dy))
    return QTable(rows=scan, names=["x", "y"], dtype=["f", "f"])
