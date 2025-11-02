"""
Harvest system - handles human harvesting of resources
"""
import pygame
import math
from constants import *
from utils.geometry import distance
from systems.resource_system import ResourceType


class HarvestSystem:
    """Manages harvesting behavior for humans"""
    
    def __init__(self, resource_system):
        self.harvest_cursor_active = False
        self.show_select_target_msg = False
        self.select_target_timer = 0.0
        self.error_message = None
        self.error_message_timer = 0.0
        self.resource_system = resource_system
    
    def activate_harvest_cursor(self):
        """Activate harvest cursor mode"""
        self.harvest_cursor_active = True
        self.show_select_target_msg = True
        self.select_target_timer = 1.0  # Show for 1 second
    
    def deactivate_harvest_cursor(self):
        """Deactivate harvest cursor mode"""
        self.harvest_cursor_active = False
        self.show_select_target_msg = False
        self.select_target_timer = 0.0
        # Restore normal cursor
        pygame.mouse.set_visible(True)
    
    def show_error(self, message, duration=3.0):
        """Show an error message"""
        self.error_message = message
        self.error_message_timer = duration
    
    def update(self, dt, game_state):
        """Update harvest system timers"""
        # Update select target message timer
        if self.show_select_target_msg:
            self.select_target_timer -= dt
            if self.select_target_timer <= 0:
                self.show_select_target_msg = False
        
        # Update error message timer
        if self.error_message:
            self.error_message_timer -= dt
            if self.error_message_timer <= 0:
                self.error_message = None
        
        # Update all harvesting humans
        for human in game_state.human_list:
            if human.state == "harvest":
                self._update_harvesting_human(human, dt, game_state)
    
    def _update_harvesting_human(self, human, dt, game_state):
        """Update a human that is harvesting"""
        # Check if target resource is still valid
        if human.harvest_target and human.harvest_target.is_depleted():
            # Resource depleted, stop harvesting
            human.state = "stay"
            human.harvest_target = None
            human.harvest_timer = 0.0
            human.carrying_resource = False
            human.target_building = None
            human.resource_type = None
            human.harvest_position = None
            return
        
        if human.carrying_resource:
            # Human is carrying a resource, go to building
            self._return_to_building(human, game_state)
        elif human.harvest_target:
            # Human is at resource, harvest it
            self._harvest_resource(human, dt, game_state)
    
    def _harvest_resource(self, human, dt, game_state):
        """Human harvests the resource"""
        resource = human.harvest_target
        
        # Use assigned harvest position
        target_x = human.harvest_position[0] if human.harvest_position else resource.x
        target_y = human.harvest_position[1] if human.harvest_position else resource.y
        
        # Move to harvest position
        dist = distance(
            human.x + human.size/2, 
            human.y + human.size/2,
            target_x,
            target_y
        )
        
        if dist > 5:  # Not at harvest position yet (reduced from 25 for tighter positioning)
            # Move towards harvest position
            dx = target_x - (human.x + human.size/2)
            dy = target_y - (human.y + human.size/2)
            dx = (dx / dist) * human.speed
            dy = (dy / dist) * human.speed
            
            old_x, old_y = human.x, human.y
            human.x += dx
            human.y += dy
            
            # Simple collision check (revert if needed)
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
        else:
            # At harvest position, harvest the resource
            resource.being_harvested = True
            human.harvest_timer += dt
            
            if human.harvest_timer >= HARVEST_TIME:
                # Finished harvesting
                resource.harvest()
                resource.being_harvested = False
                human.harvest_timer = 0.0
                human.carrying_resource = True
    
    def _return_to_building(self, human, game_state):
        """Human returns to building to deposit resource"""
        # Use the building we stored when assignment was made
        building = human.target_building
        
        if not building:
            # No building available - shouldn't happen
            human.state = "stay"
            human.harvest_target = None
            human.carrying_resource = False
            human.target_building = None
            human.resource_type = None
            human.harvest_position = None
            return
        
        # Move to building
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            building.x + building.width/2,
            building.y + building.height/2
        )
        
        if dist > 20:  # Not at building yet
            dx = (building.x + building.width/2) - (human.x + human.size/2)
            dy = (building.y + building.height/2) - (human.y + human.size/2)
            dx = (dx / dist) * human.speed
            dy = (dy / dist) * human.speed
            
            old_x, old_y = human.x, human.y
            human.x += dx
            human.y += dy
            
            # Simple collision check
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
        else:
            # At building, deposit resource
            deposited = False
            
            # Deposit based on resource type
            if human.resource_type == ResourceType.LOG:
                if building.add_log():
                    self.resource_system.add_resource(ResourceType.LOG, 1)
                    deposited = True
            elif human.resource_type == ResourceType.STONE:
                if building.add_stone():
                    self.resource_system.add_resource(ResourceType.STONE, 1)
                    deposited = True
            elif human.resource_type == ResourceType.IRON:
                if building.add_iron():
                    self.resource_system.add_resource(ResourceType.IRON, 1)
                    deposited = True
            elif human.resource_type == ResourceType.SALT:
                if building.add_salt():
                    self.resource_system.add_resource(ResourceType.SALT, 1)
                    deposited = True
            
            if deposited:
                human.carrying_resource = False
                human.harvest_timer = 0.0
                
                # Continue harvesting if resource still has health
                if human.harvest_target and not human.harvest_target.is_depleted():
                    # Go back to resource
                    pass
                else:
                    # Resource depleted, stop harvesting
                    human.state = "stay"
                    human.harvest_target = None
                    human.target_building = None
                    human.resource_type = None
                    human.harvest_position = None
            else:
                # Building is full, stop harvesting
                human.state = "stay"
                human.harvest_target = None
                human.carrying_resource = False
                human.target_building = None
                human.resource_type = None
                human.harvest_position = None
                self.show_error("Storage building is full")
    
    def _check_collisions(self, human, game_state):
        """Simple collision check for harvesting humans"""
        for pen in game_state.pen_list:
            if pen.check_collision_player(human.x, human.y):
                return True
        for townhall in game_state.townhall_list:
            if townhall.check_collision_player(human.x, human.y):
                return True
        for lumber_yard in game_state.lumber_yard_list:
            if lumber_yard.check_collision_player(human.x, human.y):
                return True
        for stone_yard in game_state.stone_yard_list:
            if stone_yard.check_collision_player(human.x, human.y):
                return True
        for iron_yard in game_state.iron_yard_list:
            if iron_yard.check_collision_player(human.x, human.y):
                return True
        return False
    
    def _calculate_harvest_positions(self, resource, game_state):
        """Calculate positions around a resource for multiple workers"""
        # Count how many workers are already assigned to this resource
        assigned_count = 0
        for human in game_state.human_list:
            if human.harvest_target == resource:
                assigned_count += 1
        
        # Create positions in a circle around the resource
        positions = []
        radius = 30  # Distance from resource center
        
        # Calculate positions around the resource
        for i in range(assigned_count):
            angle = (2 * math.pi * i) / max(assigned_count, 1)
            pos_x = resource.x + radius * math.cos(angle)
            pos_y = resource.y + radius * math.sin(angle)
            positions.append((pos_x, pos_y))
        
        return positions
    
    def assign_harvest_target(self, human, resource, game_state):
        """Assign a resource as harvest target for a human"""
        # Determine resource type and find appropriate building
        resource_type = None
        available_building = None
        
        # Check what type of resource this is
        from entities.tree import Tree
        from entities.rock import Rock
        from entities.ironmine import IronMine
        from entities.salt import Salt
        
        if isinstance(resource, Tree):
            resource_type = ResourceType.LOG
            # Find lumber yard with space
            for lumber_yard in game_state.lumber_yard_list:
                if lumber_yard.can_accept_resource():
                    available_building = lumber_yard
                    break
            if not available_building:
                self.show_error("No lumber yard with space")
                return False
        
        elif isinstance(resource, Rock):
            resource_type = ResourceType.STONE
            # Find stone yard with space
            for stone_yard in game_state.stone_yard_list:
                if stone_yard.can_accept_resource():
                    available_building = stone_yard
                    break
            if not available_building:
                self.show_error("No stone yard with space")
                return False
        
        elif isinstance(resource, IronMine):
            resource_type = ResourceType.IRON
            # Find iron yard with space
            for iron_yard in game_state.iron_yard_list:
                if iron_yard.can_accept_resource():
                    available_building = iron_yard
                    break
            if not available_building:
                self.show_error("No iron yard with space")
                return False
        
        elif isinstance(resource, Salt):
            resource_type = ResourceType.SALT
            # Find salt yard with space
            for salt_yard in game_state.salt_yard_list:
                if salt_yard.can_accept_resource():
                    available_building = salt_yard
                    break
            if not available_building:
                self.show_error("No salt yard with space")
                return False
        
        else:
            return False
        
        # Check if human is male
        if human.gender != "male":
            return False
        
        # Calculate harvest positions for all workers on this resource
        positions = self._calculate_harvest_positions(resource, game_state)
        
        # Find which position this worker should use (next available)
        worker_index = 0
        for h in game_state.human_list:
            if h.harvest_target == resource and h != human:
                worker_index += 1
        
        # Assign position (or use resource center if calculation failed)
        if worker_index < len(positions):
            harvest_position = positions[worker_index]
        else:
            harvest_position = (resource.x, resource.y)
        
        # Assign target
        human.state = "harvest"
        human.harvest_target = resource
        human.target_building = available_building
        human.resource_type = resource_type
        human.harvest_timer = 0.0
        human.carrying_resource = False
        human.harvest_position = harvest_position
        
        return True
    
    def get_hovered_resource(self, mouse_x, mouse_y, tree_list, rock_list, iron_mine_list, salt_list=None):
        """Get any harvestable resource under mouse cursor"""
        # Check trees
        for tree in tree_list:
            if not tree.is_depleted() and tree.contains_point(mouse_x, mouse_y):
                return tree
        
        # Check rocks
        for rock in rock_list:
            if not rock.is_depleted() and rock.contains_point(mouse_x, mouse_y):
                return rock
        
        # Check iron mines
        for iron_mine in iron_mine_list:
            if not iron_mine.is_depleted() and iron_mine.contains_point(mouse_x, mouse_y):
                return iron_mine
        
        # Check salt deposits
        if salt_list:
            for salt in salt_list:
                if not salt.is_depleted() and salt.contains_point(mouse_x, mouse_y):
                    return salt
        
        return None
    
    def draw_harvest_ui(self, screen):
        """Draw harvest-related UI elements"""
        # Draw select target message
        if self.show_select_target_msg:
            font = pygame.font.Font(None, 36)
            text = "Select Target"
            text_surface = font.render(text, True, YELLOW)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
            # Black background
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(screen, BLACK, bg_rect)
            pygame.draw.rect(screen, YELLOW, bg_rect, 2)
            screen.blit(text_surface, text_rect)
        
        # Draw error message
        if self.error_message:
            font = pygame.font.Font(None, 32)
            text_surface = font.render(self.error_message, True, RED)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            # Black background
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(screen, BLACK, bg_rect)
            pygame.draw.rect(screen, RED, bg_rect, 2)
            screen.blit(text_surface, text_rect)
    
    def draw_harvest_cursor(self, screen):
        """Draw crosshair cursor"""
        if not self.harvest_cursor_active:
            return
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        crosshair_size = 15
        
        # Draw crosshair
        pygame.draw.line(screen, WHITE, 
                        (mouse_x - crosshair_size, mouse_y), 
                        (mouse_x + crosshair_size, mouse_y), 2)
        pygame.draw.line(screen, WHITE, 
                        (mouse_x, mouse_y - crosshair_size), 
                        (mouse_x, mouse_y + crosshair_size), 2)
        # Draw circle in center
        pygame.draw.circle(screen, WHITE, (mouse_x, mouse_y), 3, 1)
    
    def draw_harvesting_human(self, screen, human):
        """Draw tool when human is harvesting"""
        if human.state != "harvest" or not human.harvest_target:
            return
        
        resource = human.harvest_target
        
        # Only draw tool if at resource and not carrying
        if not human.carrying_resource:
            harvest_pos = human.harvest_position if human.harvest_position else (resource.x, resource.y)
            dist = distance(
                human.x + human.size/2,
                human.y + human.size/2,
                harvest_pos[0],
                harvest_pos[1]
            )
            
            if dist <= 10:  # At harvest position (reduced from 25)
                # Draw small tool hitting resource
                tool_x = int(human.x + human.size/2 + (resource.x - human.x) * 0.5)
                tool_y = int(human.y + human.size/2 + (resource.y - human.y) * 0.5)
                pygame.draw.circle(screen, GRAY, (tool_x, tool_y), HARVEST_TOOL_SIZE // 2)
