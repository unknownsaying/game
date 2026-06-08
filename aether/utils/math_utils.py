"""
Advanced Math Utilities
Vector/Matrix operations, interpolation, noise, quaternions
"""

import numpy as np
import math
from typing import Union

class Vector2:
    """2D vector class with common operations"""
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.data = np.array([x, y], dtype=float)
    
    @property
    def x(self):
        return self.data[0]
    @x.setter
    def x(self, value):
        self.data[0] = value
    @property
    def y(self):
        return self.data[1]
    @y.setter
    def y(self, value):
        self.data[1] = value
    
    def __add__(self, other):
        return Vector2(*(self.data + other.data))
    def __sub__(self, other):
        return Vector2(*(self.data - other.data))
    def __mul__(self, scalar):
        return Vector2(*(self.data * scalar))
    def __truediv__(self, scalar):
        return Vector2(*(self.data / scalar))
    def dot(self, other):
        return np.dot(self.data, other.data)
    def cross(self, other):
        return np.cross(self.data, other.data)
    def length(self):
        return np.linalg.norm(self.data)
    def normalize(self):
        norm = self.length()
        if norm > 0:
            self.data /= norm
    def normalized(self):
        v = Vector2(*self.data)
        v.normalize()
        return v
    def rotate(self, angle_rad):
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        self.data = np.array([
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        ])
    def angle(self):
        return math.atan2(self.y, self.x)

class Matrix2x2:
    def __init__(self, a=1, b=0, c=0, d=1):
        self.data = np.array([[a, b], [c, d]], dtype=float)
    
    @staticmethod
    def rotation(angle_rad):
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        return Matrix2x2(cos_a, -sin_a, sin_a, cos_a)
    
    def __mul__(self, other):
        if isinstance(other, Matrix2x2):
            return Matrix2x2(*(self.data @ other.data).flatten())
        elif isinstance(other, Vector2):
            return Vector2(*(self.data @ other.data))
    
    def determinant(self):
        return self.data[0,0]*self.data[1,1] - self.data[0,1]*self.data[1,0]

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def lerp(a, b, t):
    return a + (b - a) * t

def smoothstep(edge0, edge1, x):
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3 - 2 * t)

def perlin_noise_2d(x, y, seed=0):
    """Simple 2D value noise for quick use, returns -1..1"""
    n = int(x) + int(y) * 57
    n = (n << 13) ^ n
    return (1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0)

# Additional advanced math
def quaternion_multiply(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return np.array([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2
    ])

def euler_to_quaternion(roll, pitch, yaw):
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    return np.array([w, x, y, z])

def quaternion_to_euler(q):
    w, x, y, z = q
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)
    sinp = 2 * (w * y - z * x)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)
    else:
        pitch = math.asin(sinp)
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    return roll, pitch, yaw