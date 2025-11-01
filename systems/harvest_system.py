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
        # Check if target tree is still valid
        if human.harvest_target and human.harvest_target.is_depleted():
            # Tree depleted, stop harvesting
            human.state = "stay"
            human.harvest_target = None
            human.harvest_timer = 0.0
            human.carrying_log = False
            return
        
        if human.carrying_log:
            # Human is carrying a log, go to town hall
            self._return_to_townhall(human, game_state)
        elif human.harvest_target:
            # Human is at tree, harvest it
            self._harvest_tree(human, dt, game_state)
    
    def _harvest_tree(self, human, dt, game_state):
        """Human harvests the tree"""
        tree = human.harvest_target
        
        # Move to tree
        dist = distance(
            human.x + human.size/2, 
            human.y + human.size/2,
            tree.x,
            tree.y
        )
        
        if dist > 25:  # Not at tree yet
            # Move towards tree
            dx = tree.x - (human.x + human.size/2)
            dy = tree.y - (human.y + human.size/2)
            dx = (dx / dist) * human.speed
            dy = (dy / dist) * human.speed
            
            old_x, old_y = human.x, human.y
            human.x += dx
            human.y += dy
            
            # Simple collision check (revert if needed)
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
        else:
            # At tree, harvest it
            tree.being_harvested = True
            human.harvest_timer += dt
            
            if human.harvest_timer >= HARVEST_TIME:
                # Finished harvesting
                tree.harvest()
                tree.being_harvested = False
                human.harvest_timer = 0.0
                human.carrying_log = True
    
    def _return_to_townhall(self, human, game_state):
        """Human returns to town hall to deposit log"""
        # Find nearest town hall
        townhall = self._find_nearest_townhall(human, game_state.townhall_list)
        
        if not townhall:
            # No town hall available - shouldn't happen as we check before starting
            human.state = "stay"
            human.harvest_target = None
            human.carrying_log = False
            return
        
        # Move to town hall
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            townhall.x + townhall.width/2,
            townhall.y + townhall.height/2
        )
        
        if dist > 20:  # Not at town hall yet
            dx = (townhall.x + townhall.width/2) - (human.x + human.size/2)
            dy = (townhall.y + townhall.height/2) - (human.y + human.size/2)
            dx = (dx / dist) * human.speed
            dy = (dy / dist) * human.speed
            
            old_x, old_y = human.x, human.y
            human.x += dx
            human.y += dy
            
            # Simple collision check
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
        else:
            # At town hall, deposit log
            from systems.resource_system import ResourceType
            self.resource_system.add_resource(ResourceType.LOG, 1)
            
            human.carrying_log = False
            human.harvest_timer = 0.0
            # Continue harvesting if tree still has health
            if human.harvest_target and not human.harvest_target.is_depleted():
                # Go back to tree
                pass
            else:
                # Tree depleted, stop harvesting
                human.state = "stay"
                human.harvest_target = None
    
    def _check_collisions(self, human, game_state):
        """Simple collision check for harvesting humans"""
        for pen in game_state.pen_list:
            if pen.check_collision_player(human.x, human.y):
                return True
        for townhall in game_state.townhall_list:
            if townhall.check_collision_player(human.x, human.y):
                return True
        return False
    
    def _find_nearest_townhall(self, human, townhall_list):
        """Find the nearest town hall"""
        if not townhall_list:
            return None
        
        nearest = None
        min_dist = float('inf')
        
        for townhall in townhall_list:
            dist = distance(
                human.x + human.size/2,
                human.y + human.size/2,
                townhall.x + townhall.width/2,
                townhall.y + townhall.height/2
            )
            if dist < min_dist:
                min_dist = dist
                nearest = townhall
        
        return nearest
    
    def assign_harvest_target(self, human, tree, game_state):
        """Assign a tree as harvest target for a human"""
        # Check if town hall exists
        if not game_state.townhall_list:
            self.show_error("No town hall available")
            return False
        
        # Check if human is male
        if human.gender != "male":
            return False
        
        # Assign target
        human.state = "harvest"
        human.harvest_target = tree
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
        
        tree = human.harvest_target
        
        # Only draw tool if at tree and not carrying log
        if not human.carrying_log:
            dist = distance(
                human.x + human.size/2,
                human.y + human.size/2,
                tree.x,
                tree.y
            )
            
            if dist <= 25:  # At tree
                # Draw small tool hitting tree
                tool_x = int(human.x + human.size/2 + (tree.x - human.x) * 0.5)
                tool_y = int(human.y + human.size/2 + (tree.y - human.y) * 0.5)
                pygame.draw.circle(screen, GRAY, (tool_x, tool_y), HARVEST_TOOL_SIZE // 2)