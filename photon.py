# Simulates real and apparent position of an object moving near or faster than the waves it makes
# Wave speed is assumed to be 1.0; other speeds are floating point multiples of wave speed
# Using pygame and some code borrowed from an "alien invasion" project example to avoid re-inventing the wheel
import sys
#import pygame
from types import List, Tuple, Iterable, Optional, Union

def run_simulation():
    # initiate the simulation and create a screen object
#    pygame.init()
#    screen = pygame.display.set_mode((1200,800))
#    pygame.dplay.set_caption("Fast Particle Simulation")
    pass

    # Main loop for the program


class Source:
    
    def get_position(self) -> (float, float):
        return Tuple(self.position)

    def set_position(self, position:Iterable(float)):
        self.position = List(position)

#  Class for a single "photon" (or phonon, etc.) emitted by a source, for the fixed observer case
#  The photon has a position, a direction, an origin, and a time of emission
#  Can also have energy and/or frequency or individual speed, though not used in simple cases
#  These properties are used in more complex simulations involving refractive, dipersive, Doppler shift, etc.
#  The origin and direction are set when the photon is created and generally not intended to chamge

class Photon:

    def __init__(self, origin:Iterable[float], direction:Iterable[float], origin_time:float, speed:Optional[float]=None,
        freq:Optional[float]=None, energy:Optional[float]=None):

        assert 2 <= len(origin) <= 3, "Origin should be a 2D or 3D point"
        assert len(origin) == len(direction), "Origin and direction dimensions do not match"
        assert speed == None or speed > 0.0, "Speed must be positive"
        self.origin = Tuple(origin)
        self.direction = Tuple(direction) / sum(direction^2)^0.5
        self.origin_time = origin_time
        self.position = Tuple(origin)
        self.speed = speed

        if energy != None: self.energy = energy
        if freq != None:
            assert freq != 0.0, "Cannot have zero frequency"
            self.frequency = freq
            self.period = 1.0 / freq
            if speed != None:
                self.speed = speed
                self.wavelength = speed / freq
                self.k = 1.0 / self.wavelength

    def set_direction(self, direction:Iterable[float]):
        assert len(direction) == len(self.direction), "Direction dimensions do not match"
        self.direction = Tuple(direction) / sum(direction^2)^0.5
    def set_direction(self, dir_x:float, dir_y:float, dir_z:Optional[float]=None):
        if dir_z == None: self.direction = (dir_x,dir_y) / (dir_x^2 + dir_y^2)^0.5
        else: self.direction = (dir_x,dir_y,dir_z) / (dir_x^2 + dir_y^2 + dir_z^2)^0.5

    def set_position(self, position:Iterable[float]):
        assert len(position) == len(self.position), "Position dimensions do not match"
        self.position = Tuple(position)
    def set_position(self, pos_x:float, pos_y:float, pos_z:Optional[float]=None):
        if pos_z == None: self.set_position((pos_x, pos_y))
        else: self.set_position((pos_x,pos_y,pos_z))
    
    def get_position(self) -> Union[Tuple[float,float],Tuple[float,float,float]]: return self.position
    def get_origin(self) -> Union[Tuple[float,float],Tuple[float,float,float]]: return self.origin
    def get_origin_time(self) -> float: return self.origin_time
    def get_direction(self) -> Union[Tuple[float,float],Tuple[float,float,float]]: return self.direction
    def get_speed(self) -> float: return self.speed

    def get_frequency(self) -> float: return self.frequency
    def get_period(self) -> float: return self.period
    def get_wavelength(self) -> float: return self.wavelength
    def get_wavenumber(self) -> float: return self.k

    def update_position(self, speed:float=None) -> Union[Tuple[Tuple[float,float],Tuple[float,float]],Tuple[Tuple[float,float,float],Tuple[float,float,float]]]:
        old_position = self.position
        if speed != None:
            assert speed > 0, "Speed should be positive"
            self.position = self.position + speed * self.direction
        else:
            assert self.speed != None, "Speed value missing"
            self.position = self.position + self.speed * self.direction
        return (old_position, self.position)


# Class for a single wave front emitted by the source.  Used in the more complex case involving a moving observer.
class Wave:

    def __init__(self, origin:Iterable[float], origin_time:float, freq:Optional[float]=None, speed:Optional[float]=None):
        assert 2 <= len(origin) <= 3, "Origin must be a 2D or 3D point"
        assert speed == None or speed > 0, "Wave must have positive speed"
        self.origin = Tuple(origin)
        self.origin_time = origin_time
        self.radius = 0.0
        self.shifted_origin = Tuple(origin)
        if freq != None:
            assert freq != 0.0, "Wave cannot have zero frequency"
            self.frequency = freq
            self.period = 1.0 / freq
            if speed != None:
                assert speed > 0.0, "Wave speed must be positive"
                self.speed = speed
                self.wavelength = self.speed / self.frequency
                self.k = 1.0 / self.wavelength
        elif speed != None:
            self.speed = speed

    def set_shifted_origin(self, shifted_origin:Iterable[float]):
        assert len(origin) == len(shifted_origin), "Origin and shifted origin dimensions must match"
        self.shifted_origin = Tuple(shifted_origin)
    def set_radius(self, radius:float):
        assert radius >=0, "Radius should not be negative"
        self.radius = radius

    def get_origin(self) -> Tuple[float]: return self.origin
    def get_origin_time(self) -> float: return self.origin_time
    def get_radius(self) -> float: return self.radius
    def get_speed(self) -> float: return self.speed
    def get_shifted_origin(self) -> float: return self.shifted_origin
    def get_origin_offset(self) -> float: return self.shifted_origin - self.origin

    def shift_and_expand(self, shift_vector:Tuple[float], speed:float=None) -> (Tuple[float],Tuple[float],float,float):
        assert len(self.origin) == len(shift_vector), "Origin and shift direction dimensions do not match"
        old_position = self.shifted_position
        self.shifted_origin = self.shifted_origin + shift_vector
        (origin,old_radius,new_radius) = self.expand(speed)
        return (old_position,self.shifted_position,old_radius,new_radius)
    def expand(self, speed:float=None) -> (Tuple[float],float,float):
        old_radius = self.radius
        if speed != None:
            assert speed >=0, "Wave speed must be positive"
            self.radius = self.radius + speed
        else:
            assert self.speed != None, "Wave speed missing"
            self.radius = self.radius + self.speed
        return (self.shifted_center,old_radius,self.radius)
