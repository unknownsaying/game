"""
Advanced Rigid Body Dynamics
Supports 2D and 3D physics with various integration methods
"""

import numpy as np
from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum
import math

class IntegrationMethod(Enum):
    """Numerical integration methods"""
    EULER = "euler"
    VERLET = "verlet"
    RK4 = "rk4"
    SYMPLECTIC = "symplectic"

@dataclass
class Material:
    """Physical material properties"""
    density: float = 1.0
    restitution: float = 0.3
    static_friction: float = 0.5
    dynamic_friction: float = 0.3
    air_resistance: float = 0.01

class RigidBody2D:
    """2D Rigid body with advanced physics"""
    
    def __init__(self, mass: float = 1.0, position: np.ndarray = None):
        self.mass = mass
        self.inv_mass = 1.0 / mass if mass > 0 else 0.0
        
        # Position and orientation
        self.position = position if position is not None else np.zeros(2)
        self.rotation = 0.0  # Radians
        
        # Linear motion
        self.velocity = np.zeros(2)
        self.acceleration = np.zeros(2)
        self.prev_acceleration = np.zeros(2)
        
        # Angular motion
        self.angular_velocity = 0.0
        self.angular_acceleration = 0.0
        self.inertia = mass  # Simplified
        self.inv_inertia = 1.0 / self.inertia if self.inertia > 0 else 0.0
        
        # Damping
        self.linear_damping = 0.01
        self.angular_damping = 0.01
        
        # Accumulated forces
        self.force_accum = np.zeros(2)
        self.torque_accum = 0.0
        
        # State
        self.is_static = mass <= 0
        self.is_kinematic = False
        self.use_gravity = True
        
        # Sleeping
        self.is_sleeping = False
        self.sleep_timer = 0.0
        self.sleep_threshold = 0.5
        
        # Material
        self.material = Material()
        
        # Integration method
        self.integration_method = IntegrationMethod.SYMPLECTIC
        
        # Constraints
        self.constraints = []
        
    def add_force(self, force: np.ndarray, point: np.ndarray = None):
        """Add force to body"""
        self.force_accum += force
        
        if point is not None:
            r = point - self.position
            self.torque_accum += np.cross(r, force)
    
    def add_impulse(self, impulse: np.ndarray, point: np.ndarray = None):
        """Apply instantaneous impulse"""
        self.velocity += impulse * self.inv_mass
        
        if point is not None:
            r = point - self.position
            self.angular_velocity += np.cross(r, impulse) * self.inv_inertia
    
    def add_torque(self, torque: float):
        """Add torque to body"""
        self.torque_accum += torque
    
    def integrate(self, dt: float):
        """Integrate physics forward in time"""
        if self.is_static or self.is_sleeping:
            return
        
        dt = min(dt, 0.1)  # Clamp dt for stability
        
        if self.integration_method == IntegrationMethod.EULER:
            self._euler_integrate(dt)
        elif self.integration_method == IntegrationMethod.VERLET:
            self._verlet_integrate(dt)
        elif self.integration_method == IntegrationMethod.RK4:
            self._rk4_integrate(dt)
        else:
            self._symplectic_integrate(dt)
    
    def _euler_integrate(self, dt: float):
        """Basic Euler integration"""
        # Calculate acceleration
        self.acceleration = self.force_accum * self.inv_mass
        self.angular_acceleration = self.torque_accum * self.inv_inertia
        
        # Apply gravity
        if self.use_gravity:
            self.acceleration += np.array([0.0, 9.81])
        
        # Update position
        self.position += self.velocity * dt + 0.5 * self.acceleration * dt * dt
        self.rotation += self.angular_velocity * dt + 0.5 * self.angular_acceleration * dt * dt
        
        # Update velocity
        self.velocity += self.acceleration * dt
        self.angular_velocity += self.angular_acceleration * dt
        
        # Apply damping
        self.velocity *= (1 - self.linear_damping * dt)
        self.angular_velocity *= (1 - self.angular_damping * dt)
        
        # Clear forces
        self._clear_forces()
    
    def _verlet_integrate(self, dt: float):
        """Verlet integration (good for constraints)"""
        # Store previous acceleration
        self.prev_acceleration = self.acceleration.copy()
        
        # Calculate new acceleration
        self.acceleration = self.force_accum * self.inv_mass
        
        if self.use_gravity:
            self.acceleration += np.array([0.0, 9.81])
        
        # Update position using Verlet
        self.position += self.velocity * dt + 0.5 * self.prev_acceleration * dt * dt
        self.rotation += self.angular_velocity * dt + 0.5 * self.angular_acceleration * dt * dt
        
        # Update velocity
        self.velocity += 0.5 * (self.prev_acceleration + self.acceleration) * dt
        self.angular_velocity += 0.5 * self.angular_acceleration * dt  # Simplified
        
        self._clear_forces()
    
    def _rk4_integrate(self, dt: float):
        """4th order Runge-Kutta integration (high accuracy)"""
        def derivatives(pos, vel, ang_vel):
            return vel, self.force_accum * self.inv_mass, self.torque_accum * self.inv_inertia
        
        # State vector
        state = np.array([
            self.position[0], self.position[1], self.rotation,
            self.velocity[0], self.velocity[1], self.angular_velocity
        ])
        
        # RK4 coefficients
        k1 = dt * np.array(derivatives(state[0:2], state[3:5], state[5]))
        k2 = dt * np.array(derivatives(state[0:2] + k1[0:2]/2, state[3:5] + k1[3:5]/2, state[5] + k1[5]/2))
        k3 = dt * np.array(derivatives(state[0:2] + k2[0:2]/2, state[3:5] + k2[3:5]/2, state[5] + k2[5]/2))
        k4 = dt * np.array(derivatives(state[0:2] + k3[0:2], state[3:5] + k3[3:5], state[5] + k3[5]))
        
        # Update state
        state += (k1 + 2*k2 + 2*k3 + k4) / 6
        
        self.position = state[0:2]
        self.rotation = state[2]
        self.velocity = state[3:5]
        self.angular_velocity = state[5]
        
        self._clear_forces()
    
    def _symplectic_integrate(self, dt: float):
        """Symplectic (semi-implicit) Euler - good for energy conservation"""
        # Calculate acceleration
        self.acceleration = self.force_accum * self.inv_mass
        
        if self.use_gravity:
            self.acceleration += np.array([0.0, 9.81])
        
        # Update velocity first (semi-implicit)
        self.velocity += self.acceleration * dt
        self.angular_velocity += self.angular_acceleration * dt
        
        # Apply damping
        self.velocity *= (1 - self.linear_damping * dt)
        self.angular_velocity *= (1 - self.angular_damping * dt)
        
        # Update position
        self.position += self.velocity * dt
        self.rotation += self.angular_velocity * dt
        
        # Sleep detection
        speed = np.linalg.norm(self.velocity)
        ang_speed = abs(self.angular_velocity)
        
        if speed < self.sleep_threshold * 0.1 and ang_speed < self.sleep_threshold * 0.01:
            self.sleep_timer += dt
            if self.sleep_timer > 1.0:
                self.is_sleeping = True
                self.velocity *= 0
                self.angular_velocity *= 0
        else:
            self.sleep_timer = 0
            self.is_sleeping = False
        
        self._clear_forces()
    
    def _clear_forces(self):
        """Clear accumulated forces"""
        self.force_accum.fill(0)
        self.torque_accum = 0.0
    
    def wake_up(self):
        """Wake up from sleep"""
        self.is_sleeping = False
        self.sleep_timer = 0.0
    
    def get_velocity_at_point(self, point: np.ndarray) -> np.ndarray:
        """Get velocity at a specific point on the body"""
        r = point - self.position
        tangential = np.array([-r[1] * self.angular_velocity, 
                              r[0] * self.angular_velocity])
        return self.velocity + tangential

class RigidBody3D:
    """3D Rigid body with full rotation dynamics"""
    
    def __init__(self, mass: float = 1.0, position: np.ndarray = None):
        self.mass = mass
        self.inv_mass = 1.0 / mass if mass > 0 else 0.0
        
        # Position and orientation (quaternion)
        self.position = position if position is not None else np.zeros(3)
        self.orientation = np.array([1.0, 0.0, 0.0, 0.0])  # w, x, y, z
        
        # Linear motion
        self.velocity = np.zeros(3)
        self.acceleration = np.zeros(3)
        
        # Angular motion
        self.angular_velocity = np.zeros(3)
        self.angular_acceleration = np.zeros(3)
        
        # Inertia tensor (simplified as scalar)
        self.inertia = mass
        self.inv_inertia = 1.0 / self.inertia if self.inertia > 0 else 0.0
        
        # Forces
        self.force_accum = np.zeros(3)
        self.torque_accum = np.zeros(3)
        
        # State
        self.is_static = mass <= 0
        self.use_gravity = True
        self.linear_damping = 0.01
        self.angular_damping = 0.01
        
    def add_force(self, force: np.ndarray, point: np.ndarray = None):
        """Add force to 3D body"""
        self.force_accum += force
        
        if point is not None:
            r = point - self.position
            self.torque_accum += np.cross(r, force)
    
    def integrate(self, dt: float):
        """Integrate 3D physics"""
        if self.is_static:
            return
        
        # Linear motion
        self.acceleration = self.force_accum * self.inv_mass
        
        if self.use_gravity:
            self.acceleration += np.array([0.0, -9.81, 0.0])
        
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
        
        # Angular motion
        self.angular_acceleration = self.torque_accum * self.inv_inertia
        self.angular_velocity += self.angular_acceleration * dt
        
        # Update orientation using quaternion
        omega = self.angular_velocity * dt
        theta = np.linalg.norm(omega)
        
        if theta > 1e-10:
            axis = omega / theta
            half_theta = theta * 0.5
            q_rot = np.array([
                math.cos(half_theta),
                axis[0] * math.sin(half_theta),
                axis[1] * math.sin(half_theta),
                axis[2] * math.sin(half_theta)
            ])
            self.orientation = self._quaternion_multiply(q_rot, self.orientation)
            self.orientation /= np.linalg.norm(self.orientation)
        
        # Damping
        self.velocity *= (1 - self.linear_damping * dt)
        self.angular_velocity *= (1 - self.angular_damping * dt)
        
        # Clear forces
        self.force_accum.fill(0)
        self.torque_accum.fill(0)
    
    def _quaternion_multiply(self, q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
        """Multiply two quaternions"""
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        
        return np.array([
            w1*w2 - x1*x2 - y1*y2 - z1*z2,
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2
        ])