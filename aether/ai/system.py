"""
AetherEngine Core Systems
Central system management, entity processing, physics integration,
event orchestration, and engine-wide coordination
"""

import numpy as np
import pygame
import time
import threading
import queue
from typing import Dict, List, Any, Optional, Type, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict, OrderedDict
import weakref
import uuid
import json
import hashlib
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AetherEngine.Systems")

class SystemPriority(Enum):
    """Execution priority for systems"""
    CRITICAL = 0    # Input, core updates
    HIGH = 100      # Physics, AI
    NORMAL = 200    # Rendering, particles
    LOW = 300       # UI, audio
    BACKGROUND = 400 # Profiling, logging

class SystemState(Enum):
    """System lifecycle states"""
    UNINITIALIZED = auto()
    INITIALIZING = auto()
    ACTIVE = auto()
    PAUSED = auto()
    SHUTTING_DOWN = auto()
    ERROR = auto()

@dataclass
class SystemConfig:
    """Configuration for individual systems"""
    name: str
    priority: SystemPriority = SystemPriority.NORMAL
    enabled: bool = True
    update_interval: float = 0.0  # 0 = every frame
    parallel: bool = False  # Can run in parallel with other systems
    dependencies: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)

class System:
    """
    Base system class for all engine systems
    Systems are the core processing units of the engine
    """
    
    def __init__(self, engine: 'SystemManager', config: SystemConfig):
        self.engine = engine
        self.config = config
        self.state = SystemState.UNINITIALIZED
        self.id = str(uuid.uuid4())
        self.last_update_time = 0.0
        self.update_count = 0
        self.total_update_time = 0.0
        self._error = None
        self._dependencies_met = False
        
    def initialize(self) -> bool:
        """Initialize the system. Return True on success."""
        try:
            self.state = SystemState.INITIALIZING
            self._on_initialize()
            self.state = SystemState.ACTIVE
            self._dependencies_met = self._check_dependencies()
            return True
        except Exception as e:
            self._error = str(e)
            self.state = SystemState.ERROR
            logger.error(f"Failed to initialize system {self.config.name}: {e}")
            return False
    
    def update(self, dt: float) -> bool:
        """Update the system. Return True if update was successful."""
        if self.state != SystemState.ACTIVE:
            return False
        
        if not self.config.enabled:
            return True
        
        try:
            start_time = time.perf_counter()
            self._on_update(dt)
            elapsed = time.perf_counter() - start_time
            
            self.last_update_time = elapsed
            self.update_count += 1
            self.total_update_time += elapsed
            
            return True
        except Exception as e:
            self._error = str(e)
            self.state = SystemState.ERROR
            logger.error(f"Error updating system {self.config.name}: {e}")
            return False
    
    def shutdown(self):
        """Shutdown the system gracefully"""
        self.state = SystemState.SHUTTING_DOWN
        try:
            self._on_shutdown()
        except Exception as e:
            logger.error(f"Error shutting down system {self.config.name}: {e}")
    
    def _on_initialize(self):
        """Override for custom initialization logic"""
        pass
    
    def _on_update(self, dt: float):
        """Override for custom update logic"""
        pass
    
    def _on_shutdown(self):
        """Override for custom shutdown logic"""
        pass
    
    def _check_dependencies(self) -> bool:
        """Check if all dependencies are met"""
        for dep_name in self.config.dependencies:
            dep_system = self.engine.get_system(dep_name)
            if dep_system is None or dep_system.state != SystemState.ACTIVE:
                return False
        return True
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get system performance statistics"""
        return {
            'name': self.config.name,
            'state': self.state.name,
            'updates': self.update_count,
            'avg_update_time': self.total_update_time / max(1, self.update_count),
            'last_update_time': self.last_update_time,
            'total_time': self.total_update_time
        }
    
    def __repr__(self):
        return f"System({self.config.name}, state={self.state.name})"

class EntityQuery:
    """Query entities based on component types and filters"""
    
    def __init__(self):
        self.required_components: Set[Type] = set()
        self.optional_components: Set[Type] = set()
        self.excluded_components: Set[Type] = set()
        self.tag_filter: Optional[str] = None
        self.layer_filter: Optional[int] = None
        
    def has_required(self, required: Type):
        """Add required component"""
        self.required_components.add(required)
        return self
    
    def has_optional(self, optional: Type):
        """Add optional component"""
        self.optional_components.add(optional)
        return self
    
    def excludes(self, excluded: Type):
        """Exclude entities with this component"""
        self.excluded_components.add(excluded)
        return self
    
    def with_tag(self, tag: str):
        """Filter by tag"""
        self.tag_filter = tag
        return self
    
    def with_layer(self, layer: int):
        """Filter by layer"""
        self.layer_filter = layer
        return self

class Entity:
    """
    Entity - composition of components
    Each entity has a unique ID and can hold multiple components
    """
    
    def __init__(self, name: str = "Entity", entity_id: str = None):
        self.id = entity_id or str(uuid.uuid4())
        self.name = name
        self.tag = ""
        self.layer = 0
        self.active = True
        self.components: Dict[Type, Any] = {}
        self._component_order: List[Type] = []
        
    def add_component(self, component: Any) -> Any:
        """Add a component to the entity"""
        component_type = type(component)
        component._entity = self
        self.components[component_type] = component
        if component_type not in self._component_order:
            self._component_order.append(component_type)
        return component
    
    def get_component(self, component_type: Type) -> Optional[Any]:
        """Get component by type"""
        return self.components.get(component_type)
    
    def has_component(self, component_type: Type) -> bool:
        """Check if entity has component"""
        return component_type in self.components
    
    def remove_component(self, component_type: Type):
        """Remove component from entity"""
        if component_type in self.components:
            component = self.components[component_type]
            if hasattr(component, '_entity'):
                component._entity = None
            del self.components[component_type]
            if component_type in self._component_order:
                self._component_order.remove(component_type)
    
    def get_components(self) -> List[Any]:
        """Get all components in order they were added"""
        return [self.components[t] for t in self._component_order if t in self.components]
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize entity to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'tag': self.tag,
            'layer': self.layer,
            'active': self.active,
            'components': {}
        }
        for comp_type, component in self.components.items():
            comp_data = {}
            if hasattr(component, '__dict__'):
                for key, value in component.__dict__.items():
                    if key != '_entity':
                        try:
                            json.dumps(value)  # Test serializability
                            comp_data[key] = value
                        except:
                            comp_data[key] = str(value)
            data['components'][comp_type.__name__] = comp_data
        return data
    
    def __repr__(self):
        return f"Entity({self.name}, id={self.id[:8]}, components={list(self.components.keys())})"

@dataclass
class EntityArchetype:
    """Defines a specific combination of components"""
    component_types: Tuple[Type, ...]
    
    def __hash__(self):
        return hash(self.component_types)
    
    def matches(self, entity: Entity) -> bool:
        """Check if entity matches this archetype"""
        for comp_type in self.component_types:
            if not entity.has_component(comp_type):
                return False
        return True

class EntityManager:
    """
    Entity Manager - maintains entity registry and queries
    Uses archetype-based storage for efficient iteration
    """
    
    def __init__(self):
        self.entities: Dict[str, Entity] = OrderedDict()
        self.entities_by_tag: Dict[str, List[str]] = defaultdict(list)
        self.entities_by_layer: Dict[int, List[str]] = defaultdict(list)
        self.entities_to_destroy: List[str] = []
        self.archetype_cache: Dict[EntityArchetype, List[str]] = {}
        self.entity_count = 0
        
        # Event callbacks
        self.on_entity_created: List[Callable] = []
        self.on_entity_destroyed: List[Callable] = []
        self.on_component_added: List[Callable] = []
        self.on_component_removed: List[Callable] = []
    
    def create_entity(self, name: str = "Entity", tag: str = "", 
                     layer: int = 0) -> Entity:
        """Create a new entity"""
        entity = Entity(name=name)
        entity.tag = tag
        entity.layer = layer
        
        self.entities[entity.id] = entity
        self.entity_count += 1
        
        if tag:
            self.entities_by_tag[tag].append(entity.id)
        self.entities_by_layer[layer].append(entity.id)
        
        # Invalidate archetype cache
        self.archetype_cache.clear()
        
        for callback in self.on_entity_created:
            callback(entity)
        
        return entity
    
    def destroy_entity(self, entity_id: str):
        """Mark entity for destruction"""
        if entity_id in self.entities:
            self.entities_to_destroy.append(entity_id)
    
    def destroy_entities(self):
        """Process destruction queue"""
        for entity_id in self.entities_to_destroy:
            if entity_id in self.entities:
                entity = self.entities[entity_id]
                
                entity.active = False
                
                # Notify observers
                for callback in self.on_entity_destroyed:
                    callback(entity)
                
                # Remove from indices
                if entity.tag and entity.id in self.entities_by_tag[entity.tag]:
                    self.entities_by_tag[entity.tag].remove(entity.id)
                if entity.id in self.entities_by_layer[entity.layer]:
                    self.entities_by_layer[entity.layer].remove(entity.id)
                
                # Clear component references
                for component in entity.get_components():
                    if hasattr(component, '_entity'):
                        component._entity = None
                
                del self.entities[entity_id]
                self.entity_count -= 1
        
        self.entities_to_destroy.clear()
        
        # Clear archetype cache after batch destruction
        if self.entities_to_destroy:
            self.archetype_cache.clear()
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID"""
        return self.entities.get(entity_id)
    
    def get_entities_by_tag(self, tag: str) -> List[Entity]:
        """Get all entities with specific tag"""
        return [self.entities[eid] for eid in self.entities_by_tag[tag] 
                if eid in self.entities]
    
    def get_entities_by_layer(self, layer: int) -> List[Entity]:
        """Get all entities on specific layer"""
        return [self.entities[eid] for eid in self.entities_by_layer[layer]
                if eid in self.entities]
    
    def query(self, query: EntityQuery) -> List[Entity]:
        """Query entities based on components and filters"""
        # Build archetype for caching
        archetype = EntityArchetype(tuple(sorted(query.required_components, key=lambda x: x.__name__)))
        
        if archetype in self.archetype_cache:
            # Use cached entity list
            candidate_ids = self.archetype_cache[archetype]
            candidates = [self.entities[eid] for eid in candidate_ids 
                         if eid in self.entities and self.entities[eid].active]
        else:
            # Find matching entities
            candidates = []
            for entity in self.entities.values():
                if not entity.active:
                    continue
                if all(entity.has_component(c) for c in query.required_components):
                    candidates.append(entity)
            
            # Cache for future queries
            self.archetype_cache[archetype] = [e.id for e in candidates]
        
        # Apply additional filters
        results = []
        for entity in candidates:
            if query.excluded_components:
                if any(entity.has_component(c) for c in query.excluded_components):
                    continue
            
            if query.optional_components:
                if not any(entity.has_component(c) for c in query.optional_components):
                    continue
            
            if query.tag_filter and entity.tag != query.tag_filter:
                continue
            
            if query.layer_filter is not None and entity.layer != query.layer_filter:
                continue
            
            results.append(entity)
        
        return results
    
    def get_all_entities(self) -> List[Entity]:
        """Get all active entities"""
        return [e for e in self.entities.values() if e.active]
    
    def clear(self):
        """Destroy all entities"""
        for entity_id in list(self.entities.keys()):
            self.destroy_entity(entity_id)
        self.destroy_entities()

class EventBus:
    """
    Event Bus - publish/subscribe event system
    Supports synchronous and asynchronous event handling
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[Tuple[int, Callable]]] = defaultdict(list)
        self.global_subscribers: List[Tuple[int, Callable]] = []
        self.event_queue: List[Tuple[str, Any]] = []
        self.async_queue = queue.Queue()
        self._processing = False
        
    def subscribe(self, event_type: str, callback: Callable, priority: int = 0):
        """Subscribe to a specific event type"""
        self.subscribers[event_type].append((priority, callback))
        self.subscribers[event_type].sort(key=lambda x: x[0], reverse=True)
    
    def subscribe_all(self, callback: Callable, priority: int = 0):
        """Subscribe to all events"""
        self.global_subscribers.append((priority, callback))
        self.global_subscribers.sort(key=lambda x: x[0], reverse=True)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event type"""
        if event_type in self.subscribers:
            self.subscribers[event_type] = [
                (p, cb) for p, cb in self.subscribers[event_type] 
                if cb != callback
            ]
    
    def emit(self, event_type: str, data: Any = None, immediate: bool = True):
        """Emit an event"""
        if immediate and not self._processing:
            self._dispatch(event_type, data)
        else:
            self.event_queue.append((event_type, data))
    
    def emit_async(self, event_type: str, data: Any = None):
        """Emit event asynchronously"""
        self.async_queue.put((event_type, data))
    
    def _dispatch(self, event_type: str, data: Any):
        """Dispatch event to subscribers"""
        # Specific subscribers
        if event_type in self.subscribers:
            for _, callback in self.subscribers[event_type]:
                try:
                    callback(event_type, data)
                except Exception as e:
                    logger.error(f"Error in event subscriber: {e}")
        
        # Global subscribers
        for _, callback in self.global_subscribers:
            try:
                callback(event_type, data)
            except Exception as e:
                logger.error(f"Error in global event subscriber: {e}")
    
    def process_events(self):
        """Process all queued events"""
        self._processing = True
        
        # Process synchronous queue
        while self.event_queue:
            event_type, data = self.event_queue.pop(0)
            self._dispatch(event_type, data)
        
        # Process async queue
        while not self.async_queue.empty():
            try:
                event_type, data = self.async_queue.get_nowait()
                self._dispatch(event_type, data)
            except queue.Empty:
                break
        
        self._processing = False

class JobSystem:
    """
    Job System - parallel task execution
    Manages worker threads for parallel processing
    """
    
    def __init__(self, num_workers: int = None):
        self.num_workers = num_workers or max(1, threading.cpu_count() - 1)
        self.job_queue = queue.Queue()
        self.results: Dict[str, Any] = {}
        self.workers: List[threading.Thread] = []
        self.running = False
        self._job_counter = 0
        self._lock = threading.Lock()
        
    def start(self):
        """Start worker threads"""
        self.running = True
        for i in range(self.num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"JobWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        logger.info(f"Job System started with {self.num_workers} workers")
    
    def stop(self):
        """Stop all workers"""
        self.running = False
        for _ in self.workers:
            self.job_queue.put(None)  # Poison pill
        for worker in self.workers:
            worker.join(timeout=2.0)
        self.workers.clear()
        logger.info("Job System stopped")
    
    def submit(self, job_func: Callable, *args, callback: Callable = None, **kwargs) -> str:
        """Submit a job for execution"""
        with self._lock:
            job_id = f"job_{self._job_counter}"
            self._job_counter += 1
        
        self.job_queue.put((job_id, job_func, args, kwargs, callback))
        return job_id
    
    def _worker_loop(self):
        """Main worker loop"""
        while self.running:
            try:
                item = self.job_queue.get(timeout=0.1)
                if item is None:  # Poison pill
                    break
                
                job_id, job_func, args, kwargs, callback = item
                
                try:
                    result = job_func(*args, **kwargs)
                    
                    with self._lock:
                        self.results[job_id] = result
                    
                    if callback:
                        callback(result)
                        
                except Exception as e:
                    logger.error(f"Error in job {job_id}: {e}")
                    with self._lock:
                        self.results[job_id] = None
                
            except queue.Empty:
                continue
    
    def get_result(self, job_id: str) -> Any:
        """Get result of a completed job"""
        with self._lock:
            return self.results.get(job_id)
    
    def wait_for_job(self, job_id: str, timeout: float = None) -> Any:
        """Wait for a job to complete and return its result"""
        start_time = time.time()
        while True:
            result = self.get_result(job_id)
            if result is not None:
                return result
            if timeout and time.time() - start_time > timeout:
                return None
            time.sleep(0.001)

class ResourceRegistry:
    """
    Resource Registry - centralized resource management
    Handles loading, caching, and hot-reloading of game assets
    """
    
    def __init__(self, base_path: str = "assets/"):
        self.base_path = Path(base_path)
        self.resources: Dict[str, Any] = {}
        self.resource_types: Dict[str, str] = {}
        self.resource_timestamps: Dict[str, float] = {}
        self.loaders: Dict[str, Callable] = {}
        self.unload_callbacks: Dict[str, Callable] = {}
        self.dependencies: Dict[str, List[str]] = defaultdict(list)
        self._loading_lock = threading.Lock()
        
        # Register default loaders
        self._register_default_loaders()
    
    def _register_default_loaders(self):
        """Register default resource loaders"""
        self.register_loader('texture', self._load_texture)
        self.register_loader('audio', self._load_audio)
        self.register_loader('json', self._load_json)
        self.register_loader('font', self._load_font)
        self.register_loader('shader', self._load_shader)
    
    def register_loader(self, resource_type: str, loader: Callable):
        """Register a custom resource loader"""
        self.loaders[resource_type] = loader
    
    def load(self, resource_type: str, name: str, path: str, 
             async_load: bool = False) -> Optional[Any]:
        """Load a resource"""
        if resource_type not in self.loaders:
            logger.error(f"No loader registered for type: {resource_type}")
            return None
        
        full_path = self.base_path / path
        
        # Check if already loaded and up to date
        if name in self.resources:
            current_mtime = full_path.stat().st_mtime if full_path.exists() else 0
            if current_mtime <= self.resource_timestamps.get(name, 0):
                return self.resources[name]
        
        # Load or reload
        try:
            resource = self.loaders[resource_type](full_path)
            if resource is not None:
                with self._loading_lock:
                    self.resources[name] = resource
                    self.resource_types[name] = resource_type
                    self.resource_timestamps[name] = full_path.stat().st_mtime if full_path.exists() else time.time()
                return resource
        except Exception as e:
            logger.error(f"Failed to load resource {name}: {e}")
        
        return None
    
    def unload(self, name: str):
        """Unload a resource"""
        if name in self.resources:
            if name in self.unload_callbacks:
                self.unload_callbacks[name](self.resources[name])
            del self.resources[name]
            if name in self.resource_types:
                del self.resource_types[name]
    
    def get(self, name: str) -> Optional[Any]:
        """Get a loaded resource"""
        return self.resources.get(name)
    
    def check_hot_reload(self) -> List[str]:
        """Check for modified resources and reload them"""
        reloaded = []
        for name, path in list(self.resource_types.items()):
            # Implementation would check file timestamps
            pass
        return reloaded
    
    def _load_texture(self, path: Path) -> Optional[pygame.Surface]:
        """Load texture/image resource"""
        try:
            if path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tga']:
                return pygame.image.load(str(path)).convert_alpha()
        except Exception as e:
            logger.error(f"Failed to load texture {path}: {e}")
        return None
    
    def _load_audio(self, path: Path) -> Optional[pygame.mixer.Sound]:
        """Load audio resource"""
        try:
            return pygame.mixer.Sound(str(path))
        except Exception as e:
            logger.error(f"Failed to load audio {path}: {e}")
        return None
    
    def _load_json(self, path: Path) -> Optional[Dict]:
        """Load JSON resource"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON {path}: {e}")
        return None
    
    def _load_font(self, path: Path) -> Optional[pygame.font.Font]:
        """Load font resource"""
        try:
            return pygame.font.Font(str(path), 32)
        except Exception as e:
            logger.error(f"Failed to load font {path}: {e}")
        return None
    
    def _load_shader(self, path: Path) -> Optional[str]:
        """Load shader resource"""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load shader {path}: {e}")
        return None

class SystemManager:
    """
    System Manager - orchestrates all engine systems
    Central coordination point for the entire engine
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.systems: Dict[str, System] = OrderedDict()
        self.entity_manager = EntityManager()
        self.event_bus = EventBus()
        self.job_system = JobSystem()
        self.resources = ResourceRegistry()
        
        # Engine state
        self.state = SystemState.UNINITIALIZED
        self.running = False
        self.delta_time = 0.0
        self.frame_count = 0
        self.total_time = 0.0
        self.time_scale = 1.0
        
        # Performance tracking
        self.frame_times: List[float] = []
        self.max_frame_history = 120
        self.target_fps = 60
        self.fixed_timestep = 1.0 / 60.0
        self.accumulator = 0.0
        
        # Debug
        self.debug_mode = False
        self.profiling_enabled = False
        
        # Window/screen (to be set by engine)
        self.screen = None
        self.clock = None
        
        logger.info("System Manager created")
    
    def initialize(self) -> bool:
        """Initialize all systems"""
        self.state = SystemState.INITIALIZING
        
        # Start job system
        self.job_system.start()
        
        # Initialize systems in dependency order
        for system in self._get_ordered_systems():
            if not system.initialize():
                logger.error(f"Failed to initialize system: {system.config.name}")
                self.state = SystemState.ERROR
                return False
        
        self.state = SystemState.ACTIVE
        self.running = True
        logger.info(f"All systems initialized ({len(self.systems)} systems)")
        return True
    
    def register_system(self, system: System):
        """Register a system with the manager"""
        self.systems[system.config.name] = system
        logger.debug(f"Registered system: {system.config.name}")
    
    def get_system(self, name: str) -> Optional[System]:
        """Get a system by name"""
        return self.systems.get(name)
    
    def _get_ordered_systems(self) -> List[System]:
        """Sort systems by priority and dependencies"""
        def get_priority_and_deps(sys):
            deps = sys.config.dependencies
            return (sys.config.priority.value, len(deps))
        
        ordered = sorted(self.systems.values(), key=get_priority_and_deps)
        return ordered
    
    def update(self, dt: float):
        """Update all systems"""
        if self.state != SystemState.ACTIVE:
            return
        
        # Apply time scale
        scaled_dt = dt * self.time_scale
        
        # Track frame time
        self.frame_times.append(dt)
        if len(self.frame_times) > self.max_frame_history:
            self.frame_times.pop(0)
        
        # Update each system
        for system in self._get_ordered_systems():
            if system.config.enabled and system.state == SystemState.ACTIVE:
                if system.update(scaled_dt):
                    if self.profiling_enabled:
                        logger.debug(f"System {system.config.name}: {system.last_update_time*1000:.2f}ms")
                else:
                    logger.warning(f"System {system.config.name} update failed")
        
        # Destroy queued entities
        self.entity_manager.destroy_entities()
        
        # Process events
        self.event_bus.process_events()
        
        # Update counters
        self.frame_count += 1
        self.total_time += dt
    
    def render(self):
        """Render all systems"""
        if self.state != SystemState.ACTIVE or not self.screen:
            return
        
        self.screen.fill((20, 20, 30))
        
        # Render systems in order
        for system in self._get_ordered_systems():
            if hasattr(system, 'render') and system.config.enabled:
                try:
                    system.render(self.screen)
                except Exception as e:
                    logger.error(f"Error rendering system {system.config.name}: {e}")
    
    def run(self):
        """Main engine loop"""
        if not self.initialize():
            logger.error("Engine initialization failed")
            return
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        logger.info("Engine main loop started")
        
        while self.running:
            # Calculate frame time
            frame_time = self.clock.tick(self.target_fps) / 1000.0
            self.accumulator += frame_time
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                self.event_bus.emit('input', event)
            
            # Fixed timestep updates
            while self.accumulator >= self.fixed_timestep:
                self.update(self.fixed_timestep)
                self.accumulator -= self.fixed_timestep
            
            # Render
            self.render()
            pygame.display.flip()
        
        self.shutdown()
    
    def quit(self):
        """Request engine shutdown"""
        logger.info("Quit requested")
        self.running = False
    
    def shutdown(self):
        """Shutdown all systems gracefully"""
        logger.info("Shutting down engine...")
        self.state = SystemState.SHUTTING_DOWN
        
        # Shutdown systems in reverse order
        for system in reversed(list(self.systems.values())):
            system.shutdown()
        
        # Stop job system
        self.job_system.stop()
        
        # Clear entities
        self.entity_manager.clear()
        
        logger.info("Engine shutdown complete")
    
    def get_fps(self) -> float:
        """Get current FPS"""
        if len(self.frame_times) > 0:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            return 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        return 0.0
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance report"""
        return {
            'fps': self.get_fps(),
            'frame_count': self.frame_count,
            'total_time': self.total_time,
            'active_systems': len([s for s in self.systems.values() if s.state == SystemState.ACTIVE]),
            'active_entities': self.entity_manager.entity_count,
            'system_performance': {
                name: system.get_performance_stats()
                for name, system in self.systems.items()
            }
        }

class InputSystem(System):
    """Input handling system"""
    
    def __init__(self, engine: SystemManager):
        super().__init__(engine, SystemConfig(
            name="InputSystem",
            priority=SystemPriority.CRITICAL
        ))
        self.keys_pressed = set()
        self.keys_held = set()
        self.keys_released = set()
        self.mouse_position = (0, 0)
        self.mouse_buttons = [False, False, False]
        self.mouse_wheel = 0
        self.controllers = []
        
    def _on_initialize(self):
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            self.controllers.append(joy)
    
    def _on_update(self, dt: float):
        self.keys_pressed.clear()
        self.keys_released.clear()
        self.mouse_wheel = 0
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                self.keys_held.add(event.key)
            elif event.type == pygame.KEYUP:
                self.keys_released.add(event.key)
                self.keys_held.discard(event.key)
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_position = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button < 4:
                    self.mouse_buttons[event.button - 1] = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button < 4:
                    self.mouse_buttons[event.button - 1] = False
            elif event.type == pygame.MOUSEWHEEL:
                self.mouse_wheel = event.y
    
    def is_key_pressed(self, key: int) -> bool:
        return key in self.keys_pressed
    
    def is_key_held(self, key: int) -> bool:
        return key in self.keys_held
    
    def is_key_released(self, key: int) -> bool:
        return key in self.keys_released