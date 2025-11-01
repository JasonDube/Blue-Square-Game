"""
Resource management system
"""
from constants import *


class ResourceType:
    """Resource type definitions"""
    LOG = "log"
    STONE = "stone"
    WOOL = "wool"
    MEAT = "meat"


class ResourceSystem:
    """Manages all resources and storage"""
    
    def __init__(self):
        # Global resource counts (across all town halls)
        self.resources = {
            ResourceType.LOG: 0,
            ResourceType.STONE: 0,
            ResourceType.WOOL: 0,
            ResourceType.MEAT: 0
        }
    
    def add_resource(self, resource_type, amount=1):
        """Add resource to global storage"""
        if resource_type in self.resources:
            self.resources[resource_type] += amount
            return True
        return False
    
    def remove_resource(self, resource_type, amount=1):
        """Remove resource from global storage"""
        if resource_type in self.resources and self.resources[resource_type] >= amount:
            self.resources[resource_type] -= amount
            return True
        return False
    
    def get_resource_count(self, resource_type):
        """Get count of a specific resource"""
        return self.resources.get(resource_type, 0)
    
    def get_all_resources(self):
        """Get all resource counts"""
        return self.resources.copy()
    
    def get_total_storage_used(self):
        """Get total number of items stored"""
        return sum(self.resources.values())


class ResourceVisualizer:
    """Handles visual representation of resources"""
    
    # Resource visual properties (width, height, color, shape)
    RESOURCE_VISUALS = {
        ResourceType.LOG: {
            'width': 3,
            'height': 15,
            'color': BROWN,
            'shape': 'rect'
        },
        ResourceType.STONE: {
            'width': 8,
            'height': 8,
            'color': GRAY,
            'shape': 'rect'
        },
        ResourceType.WOOL: {
            'width': 6,
            'height': 6,
            'color': WHITE,
            'shape': 'circle'
        },
        ResourceType.MEAT: {
            'width': 10,
            'height': 6,
            'color': (220, 100, 100),  # Pinkish red
            'shape': 'rect'
        }
    }
    
    @staticmethod
    def get_resource_visual(resource_type):
        """Get visual properties for a resource type"""
        return ResourceVisualizer.RESOURCE_VISUALS.get(resource_type, {
            'width': 5,
            'height': 5,
            'color': WHITE,
            'shape': 'rect'
        })
    
    @staticmethod
    def calculate_storage_positions(townhall, resources):
        """
        Calculate optimal positions for resources in town hall
        Returns list of (resource_type, x, y, visual_data) tuples
        """
        positions = []
        
        # Storage area inside town hall (leave margins)
        margin = 5
        storage_x = townhall.x + margin
        storage_y = townhall.y + margin
        storage_width = townhall.width - (margin * 2)
        storage_height = townhall.height - (margin * 2)
        
        # Current position tracker
        current_x = storage_x
        current_y = storage_y
        row_height = 0
        
        # Place each resource type
        for resource_type, count in resources.items():
            if count == 0:
                continue
            
            visual = ResourceVisualizer.get_resource_visual(resource_type)
            
            # Calculate how many items can fit
            items_to_show = min(count, 50)  # Cap visual display at 50 items
            
            # Stack items
            for i in range(items_to_show):
                # Check if we need to move to next row
                if current_x + visual['width'] > storage_x + storage_width:
                    current_x = storage_x
                    current_y += row_height + 2  # 2px spacing between rows
                    row_height = 0
                
                # Check if we're out of vertical space
                if current_y + visual['height'] > storage_y + storage_height:
                    break  # Town hall is full (visually)
                
                positions.append((
                    resource_type,
                    current_x,
                    current_y,
                    visual
                ))
                
                current_x += visual['width'] + 1  # 1px spacing
                row_height = max(row_height, visual['height'])
        
        return positions