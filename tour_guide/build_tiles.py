from math import ceil
from collections import namedtuple

import shapely.geometry as geometry

from .geometry import get_bounding_box, get_box_dimensions, get_radius

# Used to represent geographic point coordinates.
pt = namedtuple('pt', 'lng, lat')


def count_tiles(box, radius):
    '''Counts the number of circle tiles of a given radius required to
    traverse a box. Returns a pair of integers n, m such that n is the
    number of horizontal tiles and m is the number of vertical tiles,
    with n*m being the total number of tiles required.

    Keyword arguments:
    box -- a box reprsented as a named quadruple, as produced by
    geometry.get_bounding_box()
    radius -- the circle radius in units of geographic degrees
    '''

    w, h = get_box_dimensions(box)

    n = (w-radius)/(2*radius) + 1
    m = (h-radius)/(2*radius) + 1

    return ceil(n), ceil(m)


def get_outer_tiles(feature, radius):
    '''Acquires a set of center points for tangential circles of a given
    radius that will cover a polygon, aside from holes that exist in
    between them. Returns a list of duples of floats, where each duple
    represents (lng, lat) for the center point of a circle.

    Keyword arguments:
    feature -- a geojson feature
    radius -- desired radius for circle tiles, in units of geographic degrees
    '''

    box = get_bounding_box(feature)

    n, m = count_tiles(box, radius)

    center = pt(lat=box.lat_max, lng=box.lng_min)

    polygon = geometry.asShape(feature['geometry'])

    tiles = []
    for i in range(n):
        for j in range(m):
            point = geometry.point.Point(center.lng, center.lat)
            circle = point.buffer(radius)

            if polygon.intersects(circle):
                coordinates = (center.lng, center.lat)
                tiles.append(coordinates)

            center = pt(lat=center.lat - 2*radius, lng=center.lng)

        center = pt(lat=center.lat + 2*m*radius, lng=center.lng + 2*radius)

    return tiles


def get_inner_tiles(outer_tiles, radius):
    '''Give a set of circle tiles as produced by get_outer_tiles(), acquires
    a set of center points for circles of a given radius that will be centered
    on the holes in the provided set. If the given radius is the same radius
    used in get_outer_tiles(), then the combined set of inner and outer tiles
    will provide full geographic coverage for the original polygon, with some
    overlap. Returns a list of duples of floats, where each duple represents
    (lng, lat) for the center point of a circle.

    Keyword arguments:
    outer_tiles -- a list of duples as produced by get_outer_tiles()
    radius -- desired radius for circle tiles, in units of geographic degrees
    '''

    unchecked_tiles = list(outer_tiles)  # makes a copy to modify later

    new_tiles = []

    for duple in outer_tiles:
        lng, lat = duple

        east_lng = round(lng + 2*radius, 5)
        south_lat = round(lat - 2*radius, 5)

        unchecked_tiles = [x for x in unchecked_tiles if x != duple]

        # To determin whether a hole exists, we regard the current circle as
        # the northwest corner of a hypothetical "square" of circles. A hole
        # exists if and only if the hypothetical "square" actually exists. To
        # test for existence, we check whether tiles exist immediately to the
        # east, south and southeast of the current circle.
        southeast_exists = False
        east_exists = False
        south_exists = False

        for tile in unchecked_tiles:
            test_lng, test_lat = tile

            east_test = round(test_lng, 5) == east_lng
            south_test = round(test_lat, 5) == south_lat

            if east_test and south_test:
                southeast_exists = True
            elif east_test and not east_exists:
                east_exists = round(test_lat, 5) == round(lat, 5)
            elif south_test and not south_exists:
                south_exists = round(test_lng, 5) == round(lng, 5)

            if south_exists*east_exists*southeast_exists == 1:
                new_tiles.append((east_lng - radius, south_lat + radius))
                break

    return new_tiles


def build_all_tiles(feature, km):
    '''Essentially a wrapper for get_outer_tiles() and get_inner_tiles(),
    which produces a total set of circle tiles with a given radius that
    will provide full coverage of a given polygon with some overlap.

    Keyword arguments:
    feature -- a geojson feature
    km -- desired radius in km
    '''

    radius = get_radius(km)

    outer_tiles = get_outer_tiles(feature, radius)
    inner_tiles = get_inner_tiles(outer_tiles, radius)

    return list(set().union(inner_tiles, outer_tiles))
