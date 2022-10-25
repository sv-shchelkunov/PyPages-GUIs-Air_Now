# this modeled after Latitude/longitude spherical geodesy tools
# by Chris Veness at https://www.movable-type.co.uk/scripts/latlong.html

import math as ma

class LatLon():
    def __init__(self, lat, lon, radius=6371e3):
        if ma.isnan(lat):
            raise ValueError(f'invalid latitude {lat}')
        if ma.isnan(lon):
            raise ValueError(f'invalid longitude {lon}')
        if ma.isnan(radius):
            raise ValueError(f'invalid longitude {lon}')

        self.__lat__ = Dms.wrap90(float(lat))
        self.__lon__ = Dms.wrap180(float(lon))
        self.__radius__ = float(radius)
        # end of __init__
    #!
    def getLat(self):
        return self.__lat__
    #!
    def printLat(self):
        print(self.getLat())
    #!
    def getLon(self):
        return self.__lon__
    #!
    def printLon(self):
        print(self.getLon())
    #!
    # returns the destination point from ‘this’ point having travelled the given distance on the
    #   given initial bearing (bearing normally varies around path followed).
    #   Note: "Madison","CT","Latitude":41.2583,"Longitude":-72.5506
    # Args:
    #   distance : float
    #       Distance travelled, in same units as earth radius (default: metres).
    #   bearing : float
    #       Initial bearing in degrees from north.
    #   radius :  float
    #       Mean radius of Earth (defaults to radius in metres). Defaults to 6371e3 m.
    # Returns : Destination point : LatLon(...)
    #
    # Example
    # p1 = LatLon(51.47788, -0.00147)
    # p2 = p1.destinationPoint(7794, 300.7)
    #   Note: result should be p2 = (51.5136°N, 000.0983°W)
    def destinationPoint(self, distance, bearing):
        # sinφ2 = sinφ1⋅cosδ + cosφ1⋅sinδ⋅cosθ
        # tanΔλ = sinθ⋅sinδ⋅cosφ1 / cosδ−sinφ1⋅sinφ2

        δ = distance / self.__radius__; # angular distance in radians
        θ = (float(bearing))* (ma.pi/180.)

        φ1 = self.__lat__* (ma.pi/180.)
        λ1 = self.__lon__* (ma.pi/180.)

        sinφ2 = ma.sin(φ1) * ma.cos(δ) + ma.cos(φ1) * ma.sin(δ) * ma.cos(θ)
        φ2 = ma.asin(sinφ2)
        y = ma.sin(θ) * ma.sin(δ) * ma.cos(φ1)
        x = ma.cos(δ) - ma.sin(φ1) * sinφ2
        λ2 = λ1 + ma.atan2(y, x)

        lat = φ2* (180./ma.pi)
        lon = λ2* (180./ma.pi)

        return LatLon(lat, lon)
        # end of function

    #!
    def areaLatLonBox(self, distance, **kwargs):
        bearings = [0, 90, 180, 270]
        points = [self.destinationPoint(distance, bearing) for bearing in bearings]
        _lats = [point.getLat() for point in points]
        _lons = [point.getLon() for point in points]

        lats = (min(_lats), max(_lats))
        lons = (min(_lons), max(_lons))

        if 'BBOX' in kwargs:
            return '{},{},{},{}'.format(lons[0],lats[0], lons[1],lats[1])
        else:
            return {'lats': lats, 'lons': lons}
        # end of function


class Dms():
    def __init__(self):
        pass

    #!
    # constrains degrees to range 0..360 (e.g. for bearings). Note: -1 => 359, 361 => 1.
    # Args:
    #   degrees : float or int
    #       The number of degrees to constrain.
    # Returns: deg : float
    #       The number of degrees within the range of 0...360.
    @staticmethod
    def wrap360(degrees):
        # wave period: 360, amplitude: 0/360
        _modified_degrees =  ma.fmod(float(degrees), 360)
        if _modified_degrees >=0:
            return _modified_degrees
        else:
            return _modified_degrees + 360
        # end of function (EOFun)
    #!
    # constrains degrees to range -180..+180 (e.g. for longitude). Note: -181 => 179, 181 => -179.
    # Args:
    #  degrees : float or int
    #       The number of degrees to constrain.
    #   kwargs: typical keyword arguments
    #       Not used
    # Returns: deg : float
    #       The number of degrees within the range of -180..+180.
    @staticmethod
    def wrap180(degrees, **kwargs):
        _modified_degrees = Dms.wrap360(degrees + 180) # shift to zero base
        return _modified_degrees - 180 # return back to base = -180
        # end of function (EOFun)
    #!
    # constrains degrees to range -90..+90 (e.g. for latitude). Note: -91 => 89, 91 => -89.
    # Args:
    #  degrees : float or int
    #       The number of degrees to constrain.
    #   kwargs: typical keyword arguments
    #           Not used.
    # Returns: deg : float
    #       The number of degrees within the range of -90..+90.
    @staticmethod
    def wrap90(degrees, **kwargs):
        # wave period: 180, amplitude: -90/+90
        _modified_degrees = Dms.wrap180(degrees*2)
        return _modified_degrees/2
        # end of function
    #!
    # constrains degrees to range -45..+45. Note: -46 => 44 , 46 => -44.
    # Args:
    #  degrees : float or int
    #       The number of degrees to constrain.
    #   kwargs: typical keyword arguments
    #           Not used.
    # Returns: deg : float
    #       The number of degrees within the range of -45..+45.
    @staticmethod
    def wrap45(degrees, **kwargs):
        # wave period: 90, amplitude: -45/+45
        _modified_degrees = Dms.wrap90(degrees*2)
        return _modified_degrees/2
        # end of function
    #!
    # constrains degrees to range -NM..+NM. Note: -NM-1 => NM-1 , NM+1 => -NM+1.
    # Args:
    #  degrees : float or int
    #       The number of degrees to constrain.
    #   kwargs: typical keyword arguments
    #           Not used.
    # Returns: deg : float
    #       The number of degrees within the range of -NM..+Nm.
    @staticmethod
    def wrapNM(degrees, **kwargs):
        if ('NM' in kwargs) and (type(kwargs['NM']) == type(0.0) or type(kwargs['NM']) == type(0)):
            _coeff = 180./float(kwargs['NM'])
            _modified_degrees = Dms.wrap180(degrees*_coeff)
            return _modified_degrees/_coeff
        # end of function

    #!
    @ staticmethod
    def MilesToMeters(miles):
        return 1.60934 * miles * 1000
        # end of function
    # end of class

# screen centering
#:-)
#:-)
#:-)
#:-)
#:-)
#:-)
#:-)
#:-)
#:-]
#:-]
#:-]
#:-]
#:-]
#:-]
#:-]
#:-]
# end of screen centering
