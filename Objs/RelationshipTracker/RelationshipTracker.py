from collections import defaultdict
from typing import Any, List

# A simple class that keeps track of a single type of relationship between characters, enforcing symmetry and clean
# deletion. Assumes sparse relationships. Note that it can be used to store the original objects; so make sure to Disconnect
# if you really want such an object to disappear.
class RelationshipTracker:
    def __init__(self):
        # Relationships are assumed to be sparse, so a sparse table makes sense.
        self.grid = defaultdict(list)
        self.id_member_lookup = {}
 
    @staticmethod
    def ProcessObjectOrIdIntoId(object_or_id):
        if hasattr(object_or_id, "id"):
            return object_or_id.id
        else:
            return object_or_id
            
    @staticmethod
    def ProcessObjectOrIdIntoObject(object_or_id):
        if hasattr(object_or_id, "id"):
            return object_or_id
        else:
            return self.ReturnMemberById[object_or_id]
    
    @staticmethod
    def EnforceFullObject(potential_object):
        assert hasattr(potential_object, "id")
 
    def ReturnMemberById(self, id: int):
        return self.id_member_lookup[id] 
 
    # We need the original objects for this. We can be lax about using Ids elsewhere.
    def Connect(self, first: Any, second: Any):
        self.EnforceFullObject(first)
        self.EnforceFullObject(second)
        self.grid[first.id].append(second)
        self.grid[second.id].append(first)
        self.id_member_lookup[first.id] = first
        self.id_member_lookup[second.id] = second
    
    def Disconnect(self, first: Any, second: Any):
        self.grid[self.ProcessObjectOrIdIntoId(first)].remove(self.ProcessObjectOrIdIntoObject(second))
        self.grid[self.ProcessObjectOrIdIntoId(second)].remove(self.ProcessObjectOrIdIntoObject(first))
        
    def Get(self, member: Any):
        return self.grid[self.ProcessObjectOrIdIntoId(member)]
        
    def RemoveMember(self, member: Any):
        id = self.ProcessObjectOrIdIntoId(member)
        for second in self.grid[id]:
            self.grid[second.id].remove(self.ProcessObjectOrIdIntoObject(member))
        del self.grid[id]
    
    # We need the original objects for this. We can be lax about using Ids elsewhere.
    def AddMultiple(self, first:Any, second: List[Any]):
        self.EnforceFullObject(first)
        [self.EnforceFullObject(x) for x in second]
        self.grid[first.id].extend(second)
        for member in second:
            self.grid[member.id].append(first)