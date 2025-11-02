"""
Harvest system - handles human harvesting of resources
"""
import pygame
from constants import *
from utils.geometry import distance


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
        import pygame
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
            human.carrying_log = False
            human.target_building = None
            return
        
        if human.carrying_log:
            # Human is carrying a resource, go to building
            self._return_to_building(human, game_state)
        elif human.harvest_target:
            # Human is at resource, harvest it
            self._harvest_resource(human, dt, game_state)
    
    def _harvest_resource(self, human, dt, game_state):
        """Human harvests the resource"""
        resource = human.harvest_target
        
        # Move to resource
        dist = distance(
            human.x + human.size/2, 
            human.y + human.size/2,
            resource.x,
            resource.y
        )
        
        if dist > 25:  # Not at resource yet
            # Move towards resource
            dx = resource.x - (human.x + human.size/2)
            dy = resource.y - (human.y + human.size/2)
            dx = (dx / dist) * human.speed
            dy = (dy / dist) * human.speed
            
            old_x, old_y = human.x, human.y
            human.x += dx
            human.y += dy
            
            # Simple collision check (revert if needed)
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
        else:
            # At resource, harvest it
            resource.being_harvested = True
            human.harvest_timer += dt
            
            if human.harvest_timer >= HARVEST_TIME:
                # Finished harvesting
                resource.harvest()
                resource.being_harvested = False
                human.harvest_timer = 0.0
                human.carrying_log = True
    
    def _return_to_building(self, human, game_state):
        """Human returns to building to deposit resource"""
        # Use the building we stored when assignment was made
        building = human.target_building
        
        if not building:
            # No building available - shouldn't happen
            human.state = "stay"
            human.harvest_target = None
            human.carrying_log = False
            human.target_building = None
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
            building.add_log()
            
            human.carrying_log = False
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
        return False
    
    def assign_harvest_target(self, human, tree, game_state):
        """Assign a tree as harvest target for a human"""
        # Check if any lumber yard has space
        available_lumber_yard = None
        for lumber_yard in game_state.lumber_yard_list:
            if lumber_yard.can_accept_resource():
                available_lumber_yard = lumber_yard
                break
        
        if not available_lumber_yard:
            self.show_error("No lumber yard with space")
            return False
        
        # Check if human is male
        if human.gender != "male":
            return False
        
        # Assign target
        human.state = "harvest"
        human.harvest_target = tree
        human.target_building = available_lumber_yard  # Store which building to deliver to
        human.harvest_timer = 0.0
        human.carrying_log = False
        
        return True
    
    def get_hovered_tree(self, mouse_x, mouse_y, tree_list):
        """Get tree under mouse cursor"""
        for tree in tree_list:
            if not tree.is_depleted() and tree.contains_point(mouse_x, mouse_y):
                return tree
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
        if not human.carrying_log:
            dist = distance(
                human.x + human.size/2,
                human.y + human.size/2,
                resource.x,
                resource.y
            )
            
            if dist <= 25:  # At resource
                # Draw small tool hitting resource
                tool_x = int(human.x + human.size/2 + (resource.x - human.x) * 0.5)
                tool_y = int(human.y + human.size/2 + (resource.y - human.y) * 0.5)
                pygame.draw.circle(screen, GRAY, (tool_x, tool_y), HARVEST_TOOL_SIZE // 2)