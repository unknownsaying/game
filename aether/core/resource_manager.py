"""
Resource Management with Caching and Async Loading
"""

import os
import json
import pickle
from typing import Any, Dict, Optional, Type, Union
from pathlib import Path
import pygame
import numpy as np
from dataclasses import dataclass
from collections import OrderedDict
import hashlib
import threading
from queue import Queue

@dataclass
class ResourceMetadata:
    """Resource metadata"""
    path: str
    type: str
    size: int
    last_modified: float
    reference_count: int = 0
    compressed: bool = False

class ResourceCache(OrderedDict):
    """LRU Cache for resources"""
    
    def __init__(self, max_size: int = 1000):
        super().__init__()
        self.max_size = max_size
    
    def __setitem__(self, key, value):
        if len(self) >= self.max_size:
            self.popitem(last=False)  # Remove oldest
        super().__setitem__(key, value)

class ResourceManager:
    """
    Advanced resource management with:
    - LRU caching
    - Asynchronous loading
    - Resource compression
    - Dependency tracking
    - Hot-reloading
    """
    
    def __init__(self, base_path: str = "assets/"):
        self.base_path = Path(base_path)
        self.cache = ResourceCache(max_size=500)
        self.metadata: Dict[str, ResourceMetadata] = {}
        self.loading_queue = Queue()
        self.loaded_resources: Dict[str, Any] = {}
        self.resource_dependencies: Dict[str, list] = {}
        
        # Create directory structure
        self._create_directories()
        
        # Start async loader
        self.loader_thread = threading.Thread(target=self._async_loader, daemon=True)
        self.loader_thread.start()
        
    def _create_directories(self):
        """Create standard resource directories"""
        directories = [
            'textures', 'sprites', 'audio', 'music', 
            'fonts', 'data', 'shaders', 'maps',
            'animations', 'particles', 'ui', 'models'
        ]
        for dir_name in directories:
            (self.base_path / dir_name).mkdir(parents=True, exist_ok=True)
    
    def load_texture(self, name: str, use_alpha: bool = True) -> Optional[pygame.Surface]:
        """Load a texture/image"""
        cache_key = f"texture_{name}"
        
        if cache_key in self.cache:
            self.metadata[cache_key].reference_count += 1
            return self.cache[cache_key]
        
        # Search in textures directory
        for ext in ['.png', '.jpg', '.jpeg', '.bmp']:
            path = self.base_path / 'textures' / (name + ext)
            if path.exists():
                try:
                    if use_alpha:
                        texture = pygame.image.load(str(path)).convert_alpha()
                    else:
                        texture = pygame.image.load(str(path)).convert()
                    
                    # Cache and create metadata
                    self.cache[cache_key] = texture
                    self.metadata[cache_key] = ResourceMetadata(
                        path=str(path),
                        type='texture',
                        size=os.path.getsize(path),
                        last_modified=os.path.getmtime(path),
                        reference_count=1
                    )
                    
                    return texture
                except Exception as e:
                    print(f"Error loading texture {name}: {e}")
                    return None
        
        print(f"Texture not found: {name}")
        return None
    
    def load_spritesheet(self, name: str, frame_width: int, 
                        frame_height: int, columns: int = None) -> list:
        """Load spritesheet and split into frames"""
        sheet = self.load_texture(name)
        if not sheet:
            return []
        
        frames = []
        sheet_width, sheet_height = sheet.get_size()
        
        if columns is None:
            columns = sheet_width // frame_width
        
        rows = sheet_height // frame_height
        
        for row in range(rows):
            for col in range(columns):
                x = col * frame_width
                y = row * frame_height
                
                frame = sheet.subsurface(
                    pygame.Rect(x, y, frame_width, frame_height)
                )
                frames.append(frame)
        
        return frames
    
    def load_audio(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Load sound effect"""
        cache_key = f"audio_{name}"
        
        if cache_key in self.cache:
            self.metadata[cache_key].reference_count += 1
            return self.cache[cache_key]
        
        for ext in ['.wav', '.ogg', '.mp3']:
            path = self.base_path / 'audio' / (name + ext)
            if path.exists():
                try:
                    sound = pygame.mixer.Sound(str(path))
                    self.cache[cache_key] = sound
                    self.metadata[cache_key] = ResourceMetadata(
                        path=str(path),
                        type='audio',
                        size=os.path.getsize(path),
                        last_modified=os.path.getmtime(path),
                        reference_count=1
                    )
                    return sound
                except Exception as e:
                    print(f"Error loading audio {name}: {e}")
                    return None
        return None
    
    def load_json(self, name: str) -> Optional[dict]:
        """Load JSON data file"""
        cache_key = f"json_{name}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        path = self.base_path / 'data' / (name + '.json')
        if path.exists():
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                
                self.cache[cache_key] = data
                self.metadata[cache_key] = ResourceMetadata(
                    path=str(path),
                    type='json',
                    size=os.path.getsize(path),
                    last_modified=os.path.getmtime(path),
                    reference_count=1
                )
                return data
            except Exception as e:
                print(f"Error loading JSON {name}: {e}")
        return None
    
    def save_json(self, name: str, data: dict, pretty: bool = True):
        """Save data to JSON file"""
        path = self.base_path / 'data' / (name + '.json')
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            if pretty:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f)
        
        # Update cache
        cache_key = f"json_{name}"
        self.cache[cache_key] = data
    
    def load_binary(self, name: str) -> Optional[Any]:
        """Load pickled binary data"""
        cache_key = f"binary_{name}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        path = self.base_path / 'data' / (name + '.pkl')
        if path.exists():
            try:
                with open(path, 'rb') as f:
                    data = pickle.load(f)
                
                self.cache[cache_key] = data
                return data
            except Exception as e:
                print(f"Error loading binary {name}: {e}")
        return None
    
    def save_binary(self, name: str, data: Any):
        """Save binary data"""
        path = self.base_path / 'data' / (name + '.pkl')
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    
    def load_shader(self, name: str) -> Optional[str]:
        """Load GLSL shader code"""
        path = self.base_path / 'shaders' / name
        if path.exists():
            with open(path, 'r') as f:
                return f.read()
        return None
    
    def async_load(self, resource_type: str, name: str):
        """Queue resource for async loading"""
        self.loading_queue.put((resource_type, name))
    
    def _async_loader(self):
        """Background thread for loading resources"""
        while True:
            try:
                resource_type, name = self.loading_queue.get()
                
                if resource_type == 'texture':
                    self.load_texture(name)
                elif resource_type == 'audio':
                    self.load_audio(name)
                elif resource_type == 'json':
                    self.load_json(name)
                
                self.loading_queue.task_done()
            except Exception as e:
                print(f"Async loading error: {e}")
    
    def unload_resource(self, cache_key: str):
        """Unload a resource and free memory"""
        if cache_key in self.cache:
            self.metadata[cache_key].reference_count -= 1
            
            if self.metadata[cache_key].reference_count <= 0:
                del self.cache[cache_key]
                del self.metadata[cache_key]
    
    def clear_cache(self):
        """Clear all cached resources"""
        self.cache.clear()
        self.metadata.clear()
    
    def get_resource_path(self, relative_path: str) -> Path:
        """Get full path for a resource"""
        return self.base_path / relative_path
    
    def resource_exists(self, path: str) -> bool:
        """Check if resource exists"""
        return (self.base_path / path).exists()
    
    def get_metadata(self, cache_key: str) -> Optional[ResourceMetadata]:
        """Get resource metadata"""
        return self.metadata.get(cache_key)
    
    def check_hot_reload(self):
        """Check for modified files and reload them"""
        for cache_key, metadata in list(self.metadata.items()):
            if os.path.exists(metadata.path):
                current_mtime = os.path.getmtime(metadata.path)
                if current_mtime > metadata.last_modified:
                    print(f"Hot-reloading: {cache_key}")
                    
                    # Force reload
                    if cache_key in self.cache:
                        del self.cache[cache_key]
                    
                    # Reload based on type
                    name = Path(metadata.path).stem
                    if metadata.type == 'texture':
                        self.load_texture(name)
                    elif metadata.type == 'audio':
                        self.load_audio(name)
                    elif metadata.type == 'json':
                        self.load_json(name)