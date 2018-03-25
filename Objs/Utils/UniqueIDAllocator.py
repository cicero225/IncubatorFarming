from typing import Any, List
from threading import RLock


class UniqueIDAllocator:
    def __init__(self):
        self.last_active = -1
        self.recycled_ids = []
        self.id_lock = RLock()
        
    @classmethod
    def RestoreFromSaved(cls, last_active: int, recycled_ids: List[int]):
        allocator = cls()
        allocator.last_active = last_active
        allocator.recycled_ids = recycled_ids
        return allocator
        
    def GetNewID(self) -> int:
        with self.id_lock:
            if self.recycled_ids:
                return self.recycled_ids.pop()
            self.last_active += 1
            return self.last_active
    
    def ReturnID(self, id: int) -> None:
        with self.id_lock:
            self.recycled_ids.append(id)