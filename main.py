"""
Main game class and entry point
"""
import pygame
import sys
from constants import *
from managers.game_state import GameState
from systems import CollisionSystem, DayCycleSystem, InputSystem, HarvestSystem, ResourceSystem
from ui import ContextMenuRenderer, BuildModeRenderer, HUD
from utils.world_generator import WorldGenerator
from utils.geometry import clamp


class Game:
    """Main game class"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Blue Square Game")
        self.clock = pygame.time.Clock()
        
        # Initialize game state
        self.game_state = GameState()
        
        # Initialize systems
        self.collision_system = CollisionSystem()
        self.day_cycle = DayCycleSystem()
        self.resource_system = ResourceSystem()
        self.harvest_system = HarvestSystem(self.resource_system)
        self.input_system = InputSystem(self.game_state, self.harvest_system)
        
        # Initialize UI renderers
        self.context_menu_renderer = ContextMenuRenderer()
        self.build_mode_renderer = BuildModeRenderer()
        self.hud = HUD()
        
        # Initialize world
        self._initialize_world()
    
    def _initialize_world(self):
        """Initialize game world with entities"""
        # Generate entities
        sheep_list, human_list, pen_list = WorldGenerator.generate_initial_entities()
        
        self.game_state.sheep_list = sheep_list
        self.game_state.human_list = human_list
        self.game_state.pen_list = pen_list
        
        # Generate trees
        self.game_state.tree_list = WorldGenerator.generate_trees(pen_list=pen_list)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            dt = self.clock.get_time() / 1000.0
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    result = self.input_system.handle_event(event)
                    if result is True:  # Escape pressed outside build mode
                        running = False
            
            # Update game state
            self._update(dt)
            
            # Render
            self._render()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        self._cleanup()
    
    def _update(self, dt):
        """Update all game systems"""
        # Update player movement
        self._update_player()
        
        # Update day cycle
        self.day_cycle.update(dt, self.game_state)
        
        # Update harvest system
        self.harvest_system.update(dt, self.game_state)
        
        # Update entities
        self._update_sheep(dt)
        self._update_humans()
    
    def _update_player(self):
        """Update player position based on keyboard input"""
        keys = pygame.key.get_pressed()
        
        old_x, old_y = self.game_state.player_x, self.game_state.player_y
        
        # Move player
        if keys[pygame.K_LEFT]:
            self.game_state.player_x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.game_state.player_x += PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.game_state.player_y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.game_state.player_y += PLAYER_SPEED
        
        # Keep within bounds
        self.game_state.player_x = clamp(self.game_state.player_x, 0, SCREEN_WIDTH - PLAYER_SIZE)
        self.game_state.player_y = clamp(self.game_state.player_y, 0, SCREEN_HEIGHT - PLAYER_SIZE)
        
        # Check collision
        if self.collision_system.check_player_collision(
            self.game_state.player_x, 
            self.game_state.player_y,
            self.game_state.pen_list,
            self.game_state.townhall_list
        ):
            self.game_state.player_x, self.game_state.player_y = old_x, old_y
    
    def _update_sheep(self, dt):
        """Update all sheep"""
        herd_center_x, herd_center_y = self.game_state.get_herd_center()
        
        for sheep in self.game_state.sheep_list:
            # Move towards player
            sheep.move_towards(
                self.game_state.player_x,
                self.game_state.player_y,
                self.game_state.pen_list,
                self.game_state.townhall_list,
                self.game_state.sheep_list
            )
            
            # Update grazing
            sheep.update_graze(
                dt,
                herd_center_x,
                herd_center_y,
                self.game_state.eaten_pixels,
                None,
                self.game_state.pen_list,
                self.game_state.townhall_list
            )
    
    def _update_humans(self):
        """Update all humans"""
        player_center_x = self.game_state.player_x + PLAYER_SIZE / 2
        player_center_y = self.game_state.player_y + PLAYER_SIZE / 2
        
        for i, human in enumerate(self.game_state.human_list):
            other_humans = [h for j, h in enumerate(self.game_state.human_list) if j != i]
            human.move_towards(
                player_center_x,
                player_center_y,
                other_humans,
                self.game_state.pen_list,
                self.game_state.townhall_list,
                self.game_state.sheep_list
            )
    
    def _render(self):
        """Render all game elements"""
        # Fill background
        self.screen.fill(GREEN)
        
        # Draw terrain
        self._draw_terrain()
        
        # Draw structures
        self._draw_structures()
        
        # Draw entities
        self._draw_entities()
        
        # Draw UI
        self._draw_ui()
        
        # Draw player
        self._draw_player()
    
    def _draw_terrain(self):
        """Draw terrain (eaten grass pixels)"""
        for pixel_x, pixel_y in self.game_state.eaten_pixels:
            pygame.draw.circle(self.screen, DARK_GREEN, (pixel_x, pixel_y), 2)
    
    def _draw_structures(self):
        """Draw trees, pens, and town halls"""
        # Draw trees (show health if in harvest cursor mode)
        show_health = self.harvest_system.harvest_cursor_active
        for tree in self.game_state.tree_list:
            if not tree.is_depleted():
                tree.draw(self.screen, show_health=show_health)
        
        # Draw pens
        for pen in self.game_state.pen_list:
            pen.draw(self.screen, preview=False)
        
        # Draw town halls
        for townhall in self.game_state.townhall_list:
            townhall.draw(self.screen, preview=False, resource_system=self.resource_system)
    
    def _draw_entities(self):
        """Draw sheep and humans"""
        for sheep in self.game_state.sheep_list:
            sheep.draw(self.screen, self.game_state.debug_mode)
        
        for human in self.game_state.human_list:
            human.draw(self.screen, self.game_state.debug_mode)
            # Draw harvesting tool if human is harvesting
            self.harvest_system.draw_harvesting_human(self.screen, human)
    
    def _draw_ui(self):
        """Draw all UI elements"""
        # Draw build mode preview
        self.build_mode_renderer.draw(self.screen, self.game_state)
        
        # Draw debug herd boundary
        self.hud.draw_debug_herd_boundary(self.screen, self.game_state)
        
        # Draw box selection
        self.hud.draw_box_selection(self.screen, self.game_state)
        
        # Draw context menus
        self.context_menu_renderer.draw_all(self.screen, self.game_state)
        
        # Draw harvest UI (messages and cursor)
        self.harvest_system.draw_harvest_ui(self.screen)
        self.harvest_system.draw_harvest_cursor(self.screen)
        
        # Draw HUD (must be last to be on top)
        self.hud.draw(self.screen, self.game_state, self.day_cycle, self.resource_system)
    
    def _draw_player(self):
        """Draw the player square"""
        pygame.draw.rect(
            self.screen, 
            BLUE, 
            (self.game_state.player_x, self.game_state.player_y, PLAYER_SIZE, PLAYER_SIZE)
        )
    
    def _cleanup(self):
        """Cleanup and exit"""
        pygame.quit()
        sys.exit()


def main():
    """Entry point"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()