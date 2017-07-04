from osgeo import osr

def getCornerLonLats(lon1, lat1, lon3, lat3):
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
    PARAMETER["latitude_of_origin",-90],
    PARAMETER["central_meridian",0],
    PARAMETER["scale_factor",1],
    PARAMETER["false_easting",0],
    PARAMETER["false_northing",0],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]]]"""
    antarcticSpatialRef = osr.SpatialReference()
    antarcticSpatialRef.ImportFromWkt(antarctic_wkt)

    tx1 = osr.CoordinateTransformation(wgs84SpatialRef, antarcticSpatialRef)
    (x1, y1, tmp) = tx1.TransformPoint(lon1, lat1)
    (x3, y3, tmp) = tx1.TransformPoint(lon3, lat3)

    x2, y2 = x3, y1
    x4, y4 = x1, y3

    print x1, y1
    print x2, y2
    print x3, y3
    print x4, y4

    tx2 = osr.CoordinateTransformation(antarcticSpatialRef, wgs84SpatialRef)
    (lon2, lat2, tmp) = tx2.TransformPoint(x2, y2)
    (lon4, lat4, tmp) = tx2.TransformPoint(x4, y4)

    print lon1, lat1
    print lon2, lat2
    print lon3, lat3
    print lon4, lat4

    return [lon1, lon2, lon3, lon4], [lat1, lat2, lat3, lat4]




if __name__ == '__main__':
    print getCornerLonLats(110, -7, 120, -20)