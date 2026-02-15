from math import asin, cos, radians, sin, sqrt

EARTH_RADIUS_M = 6371000


def haversine_distance_m(lat1: float, lng1: float, lat2: float, lng2: float) -> int:
    lat1_rad = radians(lat1)
    lng1_rad = radians(lng1)
    lat2_rad = radians(lat2)
    lng2_rad = radians(lng2)

    d_lat = lat2_rad - lat1_rad
    d_lng = lng2_rad - lng1_rad

    a = sin(d_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(d_lng / 2) ** 2
    c = 2 * asin(sqrt(a))
    return int(EARTH_RADIUS_M * c)


def build_distance_matrix(locations: list[tuple[float, float]]) -> list[list[int]]:
    size = len(locations)
    matrix: list[list[int]] = []
    for i in range(size):
        origin_lat, origin_lng = locations[i]
        row: list[int] = []
        for j in range(size):
            if i == j:
                row.append(0)
                continue
            destination_lat, destination_lng = locations[j]
            row.append(haversine_distance_m(origin_lat, origin_lng, destination_lat, destination_lng))
        matrix.append(row)
    return matrix
