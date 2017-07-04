from osgeo import osr
import math

def transfer(westlon, eastlon, northlat, southlat):
    wgs84_wkt = """
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]]"""
    wgs84SpatialRef = osr.SpatialReference()
    wgs84SpatialRef.ImportFromWkt(wgs84_wkt)

    antarctic_wkt = """
    PROJCS["PS",
    GEOGCS["unknown",
        DATUM["unknown",
            SPHEROID["unnamed",6378137,298.2571643544928]],
        PRIMEM["Greenwich",0],
        UNIT["degree",0.0174532925199433]],
    PROJECTION["Polar_Stereographic"],
    PARAMETER["latitude_of_origin",90],
    PARAMETER["central_meridian",0],
    PARAMETER["scale_factor",1],
    PARAMETER["false_easting",0],
    PARAMETER["false_northing",0],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]]]"""
    antarcticSpatialRef = osr.SpatialReference()
    antarcticSpatialRef.ImportFromWkt(antarctic_wkt)

    melon = 0.5*(eastlon+westlon)

    tx1 = osr.CoordinateTransformation(wgs84SpatialRef, antarcticSpatialRef)
    (x1, y1, tmp) = tx1.TransformPoint(westlon, southlat)
    (x2, y2, tmp) = tx1.TransformPoint(eastlon, southlat)
    (x3, y3, tmp) = tx1.TransformPoint(melon, northlat)
    x4 = 0.5*(x1+x2)
    y4 = 0.5*(y1+y2)

    longdis = x3**2+y3**2
    shortdis = x4**2+y4**2
    ratio = math.sqrt(longdis/shortdis)

    x5 = ratio*x1
    y5 = ratio*y1
    x6 = ratio*x2
    y6 = ratio*y2

    maxx = max([x1,x2,x5,x6])
    minx = min([x1,x2,x5,x6])
    maxy = max([y1,y2,y5,y6])
    miny = min([y1,y2,y5,y6])

    return minx, maxy, maxx, miny


if __name__ == '__main__':
    print transfer(-30, 30, -60, -63)