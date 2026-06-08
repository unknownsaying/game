"""
Serialization System
Save/Load game states, JSON and binary formats
"""

import json
import pickle
import gzip
import base64
from typing import Any, Dict
from pathlib import Path
from datetime import datetime

class SaveManager:
    """Manages game save files"""
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, data: Dict[str, Any], slot_name: str = "autosave", 
             format: str = "json") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{slot_name}_{timestamp}"
        
        if format == "json":
            filepath = self.save_dir / f"{filename}.json"
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        elif format == "json_gz":
            filepath = self.save_dir / f"{filename}.json.gz"
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                json.dump(data, f, default=str)
        elif format == "binary":
            filepath = self.save_dir / f"{filename}.pkl"
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
        elif format == "binary_gz":
            filepath = self.save_dir / f"{filename}.pkl.gz"
            with gzip.open(filepath, 'wb') as f:
                pickle.dump(data, f)
        else:
            raise ValueError("Unknown format")
        
        return str(filepath)
    
    def load(self, filepath: str) -> Dict[str, Any]:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Save file not found: {filepath}")
        
        if path.suffix == '.json':
            with open(path, 'r') as f:
                return json.load(f)
        elif path.suffix == '.gz':
            with gzip.open(path, 'rt' if path.stem.endswith('.json') else 'rb') as f:
                if path.stem.endswith('.json'):
                    return json.load(f)
                else:
                    return pickle.load(f)
        elif path.suffix == '.pkl':
            with open(path, 'rb') as f:
                return pickle.load(f)
        else:
            raise ValueError("Unsupported file type")
    
    def list_saves(self) -> list:
        saves = []
        for file in self.save_dir.iterdir():
            if file.is_file():
                saves.append({
                    'name': file.stem,
                    'path': str(file),
                    'size': file.stat().st_size,
                    'modified': datetime.fromtimestamp(file.stat().st_mtime)
                })
        return sorted(saves, key=lambda x: x['modified'], reverse=True)

class JSONSerializer:
    """Helper to serialize/deserialize complex objects to JSON-compatible dicts"""
    @staticmethod
    def encode(obj: Any) -> Any:
        if hasattr(obj, '__dict__'):
            data = {'__class__': obj.__class__.__name__, '__module__': obj.__class__.__module__}
            data.update({k: JSONSerializer.encode(v) for k, v in obj.__dict__.items()})
            return data
        elif isinstance(obj, (list, tuple)):
            return [JSONSerializer.encode(x) for x in obj]
        elif isinstance(obj, dict):
            return {k: JSONSerializer.encode(v) for k, v in obj.items()}
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)
    
    @staticmethod
    def decode(data: Any):
        if isinstance(data, dict) and '__class__' in data:
            # Reconstruct object (requires import)
            module = __import__(data['__module__'], fromlist=[data['__class__']])
            cls = getattr(module, data['__class__'])
            obj = cls.__new__(cls)
            for k, v in data.items():
                if k not in ('__class__', '__module__'):
                    setattr(obj, k, JSONSerializer.decode(v))
            return obj
        elif isinstance(data, list):
            return [JSONSerializer.decode(x) for x in data]
        elif isinstance(data, dict):
            return {k: JSONSerializer.decode(v) for k, v in data.items()}
        return data

class BinarySerializer:
    """High-performance binary serialization with optional compression"""
    @staticmethod
    def serialize(obj: Any, compress: bool = True) -> bytes:
        data = pickle.dumps(obj)
        if compress:
            data = gzip.compress(data)
        return data
    
    @staticmethod
    def deserialize(data: bytes, compressed: bool = True) -> Any:
        if compressed:
            data = gzip.decompress(data)
        return pickle.loads(data)
    
    @staticmethod
    def to_base64(obj: Any) -> str:
        return base64.b64encode(BinarySerializer.serialize(obj)).decode('ascii')
    
    @staticmethod
    def from_base64(encoded: str) -> Any:
        return BinarySerializer.deserialize(base64.b64decode(encoded.encode('ascii')))