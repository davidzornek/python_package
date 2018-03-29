import json
from collections import namedtuple
from deprecation import deprecated

import geojson
import pygeoj
import shapely
import geopandas as gpd
from shapely import geometry

from math import sin, cos, sqrt, atan2, radians, degrees


box_tuple = namedtuple('box', 'lng_min, lat_min, lng_max, lat_max')


def miles_to_km(miles):
    '''Convert miles to kilometers.

    Keyword arguments:
    miles -- a distance measurement in miles
    '''
    km_per_mile = 1.60934
    return miles * km_per_mile


def parse_shape(geojson_str):
    '''Parse a string representation of geojson into a shapely Shape.

    Keyword arguments:
    geojson_str -- a string that can be parsed into a geojson feature
    '''
    geojson_feature = json.loads(geojson_str)
    return shapely.geometry.asShape(geojson_feature)


def merge_polygon_groups(data, group_column, polygon_column='polygon', aggfunc='first'):
    '''Merge neighborhood polygons that belong to the same city. Returns a
    geopandas dataframe, in which polygons are shapely Shapes.

    Keyword arguments:
    data -- a pandas dataframe resultant from querying area manager for urban
    neighborhood polygons and the city each belongs to. Assumes that the
    polygons are represented as geojson strings. 

    group_column -- a string indicating which column to group by.

    polygon_column -- a string indicating which column contains the polygons.
    Defaults to `'polygon'`.

    aggfunc -- a string indicating which aggregation function to apply to columns
    other than the group- and polygon-columns. Defaults to `'first'`. 
    '''

    data[polygon_column] = data[polygon_column].apply(parse_shape)
    
    return gpd.GeoDataFrame(
        data,
        geometry=polygon_column
    ).dissolve(
        by=group_column,
        aggfunc=aggfunc,
        as_index=False
    )


def buffer_polygons(data, buffer_miles,
                    polygon_column='polygon',
                    buffered_polygon_column='buffered_polygon'):
    '''Buffer each polygon in a dataframe by a specified amount. Assumes
    that the polygons are specified in degrees of latitude and longitude.
    Returns a dataframe.

    Keyword arguments:
    data -- a geodataframe with a column of shapely Shapes.

    buffer_miles -- how many miles around the polygons to buffer.

    polygon_column -- a string indicating which column contains the polygons. 
    Defaults to `'polygon'`.

    buffered_polygon_column -- a string indicating which column to write the buffered
    polygons into
    '''

    km = miles_to_km(buffer_miles)
    degrees = get_radius(km)

    data[buffered_polygon_column] = data[polygon_column].apply(
        lambda s: s.buffer(degrees)
    )

    return data


@deprecated(details='use merge_polygon_groups instead')
def merge_mls_polygons(data, region):
    '''Merges MLS polygons into a larger regional polygon, returning a
    geojson Feature.

    Keyword arguments:
    data -- a pandas dataframe resultant from querying mls data frames from
    mls manager and joining assigned regions onto them. This description will
    change once region assignments are incorporated into mls manager directly.

    region -- a string indicating which region the user wishes to merge.
    Current regions are 'northeast', 'chicago', 'florida', 'california', and
    'other'
    '''

    regional_data = data.loc[data['region'] == region]

    null_shape = {'type': 'MultiPolygon',
                  'coordinates': []}
    merged = shapely.geometry.asShape(null_shape)

    for row in regional_data.itertuples():
        poly = parse_shape(row[4])
        merged = merged.union(poly)

    response = geojson.Feature(geometry=merged, properties={})

    return response


def get_bounding_box(feature):
    '''Creates a bounding box for a given geojson feature.
    Returns a named quadruple.

    Keyword arguments:
    feature -- a geojson Feature
    '''

    collection = geojson.FeatureCollection([feature])
    geo = pygeoj.load(data=collection)
    lng_min, lat_min, lng_max, lat_max = geo[0].geometry.bbox

    box = box_tuple(lng_min=lng_min, lat_min=lat_min,
                    lng_max=lng_max, lat_max=lat_max)

    return box


def get_box_dimensions(box):
    '''Calculates width and height of a box, in units of geographic degrees.
    Returns a pair width, height of floats.

    Keyword arguments:
    box -- a box represented as a named quadruple, as produced by
    get_bounding_box()
    '''

    w = abs(box.lng_min - box.lng_max)
    h = abs(box.lat_min - box.lat_max)

    return w, h


def haversine(points):
    '''Calculates the haversine distance between two geographic
    points. Distance is returned in km.

    Keyword arguments:
    points - a tuple or list of geographic points encoded as names
    duples. Duple attributes must be named 'lat' and 'lng'
    '''

    # distance of the earth in km
    r = 6371.0

    # convert angles to radians
    lat1, lng1, lat2, lng2 = map(radians, [points[0].lat, points[0].lng,
                                           points[1].lat, points[1].lng])

    # the haversine formula
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlng/2)**2
    c = 2*atan2(sqrt(a), sqrt(1-a))
    km = c*r

    return km


# def reverse_haversine(point, lng, km=40):
#     # We save this function to enhance later by allowing the user to
#     # translate the cartesian distance between any two arbitrary points
#     # into spherical distance. Doesn't need review at this time.

#     '''Translates the radius of a circle centered at a given geographic
#     location from kilometers into degrees.

#     Keyword arguments:
#     center -- the center of the circle, passed as a named tuple with
#     parameters lat and lng.
#     km -- desired radius in km. Defaults to 40, Yelp's maximum radius.
#     '''

#     r = 6371.0  # radius of Earth in km

#     c = km/r
#     a = sin(c)**2

#     radius = 2*asin(sqrt(a))

#     return degrees(radius)


def get_radius(km=40):
    '''Calculates the angular radius of a geographic circle.

    Keyword arguments:
    km -- desired cartesian radius in km. Defaults to 40, Yelp's
    maximum radius.
    '''
    r = 6371.0  # radius of Earth in km
    return degrees(2*km/r)

 
def grow_shape(shape, buffer, return_box=False):
    '''Grows a shapely Shape by a specified buffer. Returns either a geojson
    multipolygon or a box, depending on the value of return_box.

    Keyword arguments:
    shape -- a shapely Shape
    buffer -- the radius to grow the polygon by, in units of geographic
    degrees
    return_box -- a boolean specifying what sort of object the user wishes
    to receive. Returns a bounding box for the grown polygon if True. Defaults
    to False.
    '''

    shape = shape.buffer(buffer)
    geo = geojson.MultiPolygon(geometry=shape, properties={})

    if return_box:
        geo = get_bounding_box(geo)

    return geo


def grow_polygon(feature, buffer, return_box=False):
    '''Grows a polygon by a specified buffer. Returns either a geojson
    multipolygon or a box, depending on the value of return_box.

    Keyword arguments:
    feature -- a geojson feature
    buffer -- the radius to grow the polygon by, in units of geographic
    degrees
    return_box -- a boolean specifying what sort of object the user wishes
    to receive. Returns a bounding box for the grown polygon if True. Defaults
    to False.
    '''

    shape = shapely.geometry.asShape(feature['geometry'])
    return grow_shape(shape, buffer, return_box)   
