
import math
import random
from typing import Callable, List, Optional, Tuple

# 1. Pure-Python vector operations (no numpy)
class Vector:
    """Minimal immutable vector for convenience and clarity."""
    __slots__ = ('_data',)

    def __init__(self, data: List[float]):
        self._data = tuple(data)          # store as tuple for immutability

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, i: int) -> float:
        return self._data[i]

    def __iter__(self):
        return iter(self._data)

    def __add__(self, other: 'Vector') -> 'Vector':
        return Vector([a + b for a, b in zip(self._data, other._data)])

    def __sub__(self, other: 'Vector') -> 'Vector':
        return Vector([a - b for a, b in zip(self._data, other._data)])

    def __mul__(self, scalar: float) -> 'Vector':
        return Vector([a * scalar for a in self._data])

    def __rmul__(self, scalar: float) -> 'Vector':
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> 'Vector':
        return Vector([a / scalar for a in self._data])

    def __neg__(self) -> 'Vector':
        return Vector([-a for a in self._data])

    def dot(self, other: 'Vector') -> float:
        return sum(a * b for a, b in zip(self._data, other._data))

    def norm(self) -> float:
        return math.sqrt(sum(a * a for a in self._data))

    def to_list(self) -> List[float]:
        return list(self._data)

    def __repr__(self) -> str:
        return f"Vector({list(self._data)})"

# 2. Numerical gradient (if no analytic gradient provided)

def numerical_gradient(f: Callable[[Vector], float],
                       x: Vector,
                       h: float = 1e-6) -> Vector:
    """Central finite difference for each dimension."""
    n = len(x)
    grad = [0.0] * n
    for i in range(n):
        x_plus  = Vector([x[j] + (h if j == i else 0.0) for j in range(n)])
        x_minus = Vector([x[j] - (h if j == i else 0.0) for j in range(n)])
        grad[i] = (f(x_plus) - f(x_minus)) / (2.0 * h)
    return Vector(grad)


# 3. The Meta optimizer class
class Meta:
    def __init__(self,
                 dim: int,
                 objective: Callable[[Vector], float],
                 grad: Optional[Callable[[Vector], Vector]] = None,
                 mass: float = 1.0,
                 damping: float = 0.9,
                 temperature: float = 1.0,
                 cooling_rate: float = 0.999,
                 dt: float = 1.0):
        self.dim = dim
        self.objective = objective
        self.grad = grad
        self.mass = mass
        self.damping = damping
        self.temperature = temperature
        self.cooling_rate = cooling_rate
        self.dt = dt

        # State variables (position and velocity)
        self.position = Vector([0.0] * dim)
        self.velocity = Vector([0.0] * dim)

        # History for analysis
        self.trajectory: List[Tuple[Vector, float]] = []

    def set_position(self, x: List[float]):
        """Initialize the particle position."""
        self.position = Vector(x)
        self.velocity = Vector([0.0] * len(x))

    def step(self) -> float:
        """
        Perform one update step.  Returns the objective value at the new position.
        """
        # ------------------- Gradient calculation -------------------
        if self.grad is not None:
            g = self.grad(self.position)
        else:
            g = numerical_gradient(self.objective, self.position)

        # Force = -gradient (steepest descent direction)
        force = -g

        # ------------------- Newton's second law -------------------
        # a = F / m
        acceleration = force / self.mass

        # Update velocity: v' = damping * v + a * dt  + thermal noise
        noise_scale = math.sqrt(2.0 * self.temperature * (1.0 - self.damping))  # heuristic
        noise = Vector([random.gauss(0.0, noise_scale) for _ in range(self.dim)])

        new_velocity = self.velocity * self.damping + acceleration * self.dt + noise

        # Update position: x' = x + v' * dt
        new_position = self.position + new_velocity * self.dt

        # Accept new state
        self.position = new_position
        self.velocity = new_velocity

        # Anneal temperature
        self.temperature *= self.cooling_rate

        # Record
        obj_val = self.objective(self.position)
        self.trajectory.append((self.position, obj_val))

        return obj_val

    def run(self, steps: int, verbose: bool = True) -> Vector:
        """Run for a given number of steps."""
        for i in range(steps):
            val = self.step()
            if verbose and i % max(1, steps // 10) == 0:
                print(f"Step {i:5d}: temp={self.temperature:.4f}, "
                      f"f={val:.6f}, x={self.position.to_list()}")
        return self.position

    def best_solution(self) -> Tuple[Vector, float]:
        """Return the best (position, value) seen so far."""
        if not self.trajectory:
            raise RuntimeError("No steps taken yet.")
        return min(self.trajectory, key=lambda tup: tup[1])


# ----------------------------------------------------------------------
# 4. Example: minimize a multimodal 2D function (Himmelblau)
# ----------------------------------------------------------------------
def himmelblau(x: Vector) -> float:
    """Himmelblau's function: four identical global minima."""
    a, b = x[0], x[1]
    return (a**2 + b - 11)**2 + (a + b**2 - 7)**2

def himmelblau_grad(x: Vector) -> Vector:
    """Analytic gradient of Himmelblau's function."""
    a, b = x[0], x[1]
    df_da = 4*a*(a**2 + b - 11) + 2*(a + b**2 - 7)
    df_db = 2*(a**2 + b - 11) + 4*b*(a + b**2 - 7)
    return Vector([df_da, df_db])

if __name__ == "__main__":
  
    random.seed(42)
    print("=== Meta optimizer on Himmelblau's function ===")
    optimizer = Meta(dim=2,
                     objective=himmelblau,
                     grad=himmelblau_grad,   # we provide analytic gradient
                     mass=1.0,
                     damping=0.85,           # moderate friction
                     temperature=2.0,        # enough thermal energy to hop
                     cooling_rate=0.995,     # slow annealing
                     dt=0.1)                 # small time step for smoothness
    # Start far from known minima
    optimizer.set_position([5.0, 5.0])

    final_pos = optimizer.run(steps=500)
    best_pos, best_val = optimizer.best_solution()
    print(f"\nBest found: x = {best_pos.to_list()}, f = {best_val:.8f}")
    print("(Global minima are ~ [3.0, 2.0], [-2.805, 3.131], "
          "[-3.779, -3.283], [3.584, -1.848])")