"""
Employment system - manages automatic work behavior for employed humans
"""
import random
import math
from constants import *
from utils.geometry import distance


class EmploymentSystem:
    """Handles automatic work behavior for employed humans"""
    
    def __init__(self, resource_system):
        self.resource_system = resource_system
    
    def update(self, dt, game_state):
        """Update all employed humans"""
        for human in game_state.human_list:
            if human.state == "employed" and human.job:
                self._update_employed_human(human, dt, game_state)
    
    def _update_employed_human(self, human, dt, game_state):
        """Update a single employed human"""
        if human.job == "lumberjack":
            self._update_lumberjack(human, dt, game_state)
        elif human.job == "miner":
            self._update_miner(human, dt, game_state)
        elif human.job == "stoneworker":
            self._update_stoneworker(human, dt, game_state)
        elif human.job == "saltworker":
            self._update_saltworker(human, dt, game_state)
        # Future jobs: elif human.job == "farmer": ...
    
    def _update_lumberjack(self, human, dt, game_state):
        """Update a lumberjack - automatically harvests trees"""
        # If carrying resource, return to lumber yard
        if human.carrying_resource:
            self._return_to_lumber_yard(human, game_state)
            return
        
        # If has a target and it's still valid, continue harvesting
        if human.work_target and not human.work_target.is_depleted():
            self._harvest_tree(human, dt, game_state)
            return
        
        # Need to find a new target - check immediately first, then use interval
        if human.work_timer == 0.0:
            # First check - try to find target immediately
            self._find_tree_target(human, game_state)
            if human.work_target:
                # Found target, start working
                return
        
        # If no target found, wait and try again
        human.work_timer += dt
        if human.work_timer >= AUTO_WORK_INTERVAL:
            human.work_timer = 0.0
            self._find_tree_target(human, game_state)
    
    def _find_tree_target(self, human, game_state):
        """Find nearest tree to harvest"""
        nearest_tree = None
        nearest_dist = float('inf')
        
        human_x = human.x + human.size/2
        human_y = human.y + human.size/2
        
        for tree in game_state.tree_list:
            if tree.is_depleted():
                continue
            
            dist = distance(human_x, human_y, tree.x, tree.y)
            if dist < AUTO_WORK_SEARCH_RADIUS and dist < nearest_dist:
                # Check if there's a lumber yard with space
                has_space = any(ly.can_accept_resource() for ly in game_state.lumber_yard_list)
                if has_space:
                    nearest_tree = tree
                    nearest_dist = dist
        
        if nearest_tree:
            # Assign the tree
            human.work_target = nearest_tree
            human.harvest_target = nearest_tree
            human.harvest_timer = 0.0
            
            # Calculate harvest position around tree
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            human.harvest_position = (
                nearest_tree.x + radius * math.cos(angle),
                nearest_tree.y + radius * math.sin(angle)
            )
            
            # Find lumber yard
            from systems.resource_system import ResourceType
            for lumber_yard in game_state.lumber_yard_list:
                if lumber_yard.can_accept_resource():
                    human.target_building = lumber_yard
                    human.resource_type = ResourceType.LOG
                    break
    
    def _harvest_tree(self, human, dt, game_state):
        """Harvest the assigned tree"""
        # Use harvest_target if available, otherwise fall back to work_target
        tree = human.harvest_target if human.harvest_target else human.work_target
        
        if not tree:
            # No tree assigned - reset and find new one
            self._reset_worker(human)
            return
        
        # Restore harvest_target if it was cleared but work_target exists
        if not human.harvest_target and human.work_target:
            human.harvest_target = human.work_target
        
        # Calculate harvest position if not set
        if not human.harvest_position:
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            human.harvest_position = (
                tree.x + radius * math.cos(angle),
                tree.y + radius * math.sin(angle)
            )
        
        # Move to harvest position
        target_x = human.harvest_position[0] if human.harvest_position else tree.x
        target_y = human.harvest_position[1] if human.harvest_position else tree.y
        
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            target_x,
            target_y
        )
        
        if dist > 5:  # Not at harvest position yet
            # Move towards harvest position
            from utils.geometry import clamp
            
            dx = target_x - (human.x + human.size/2)
            dy = target_y - (human.y + human.size/2)
            dx = (dx / dist) * human.speed
            dy = (dy / dist) * human.speed
            
            old_x, old_y = human.x, human.y
            human.x += dx
            human.y += dy
            
            # Keep within playable area bounds
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
            human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
            
            # Simple collision check
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
        else:
            # At harvest position, harvest the tree
            tree.being_harvested = True
            human.harvest_timer += dt
            
            if human.harvest_timer >= HARVEST_TIME:
                # Finished harvesting
                tree.harvest()
                tree.being_harvested = False
                human.harvest_timer = 0.0
                human.carrying_resource = True
    
    def _return_to_lumber_yard(self, human, game_state):
        """Return to lumber yard to deposit log"""
        from entities.lumberyard import LumberYard
        
        building = human.target_building
        
        # Validate that building is actually a lumber yard
        if not building or not isinstance(building, LumberYard):
            # Find a valid lumber yard
            for lumber_yard in game_state.lumber_yard_list:
                if lumber_yard.can_accept_resource():
                    building = lumber_yard
                    human.target_building = lumber_yard
                    break
            
            if not building or not isinstance(building, LumberYard):
                # No valid lumber yard - reset worker
                self._reset_worker(human)
                return
        
        # Move to building
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            building.x + building.width/2,
            building.y + building.height/2
        )
        
        if dist > 20:  # Not at building yet
            from utils.geometry import clamp
            
            dx = (building.x + building.width/2) - (human.x + human.size/2)
            dy = (building.y + building.height/2) - (human.y + human.size/2)
            dx = (dx / dist) * human.speed
            dy = (dy / dist) * human.speed
            
            old_x, old_y = human.x, human.y
            human.x += dx
            human.y += dy
            
            # Keep within playable area bounds
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
            human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
            
            # Simple collision check
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
        else:
            # At building, deposit resource
            from systems.resource_system import ResourceType
            if building.add_log():
                self.resource_system.add_resource(ResourceType.LOG, 1)
                human.carrying_resource = False
                human.harvest_timer = 0.0
                
                # Continue working if tree still has health
                if human.work_target and not human.work_target.is_depleted():
                    # Go back to tree
                    pass
                else:
                    # Tree depleted, find new one
                    human.work_target = None
                    human.harvest_target = None
                    human.harvest_position = None
            else:
                    # Building full - stop working
                    self._reset_worker(human)
    
    def _update_miner(self, human, dt, game_state):
        """Update a miner - automatically harvests iron mines"""
        # If carrying resource, return to iron yard
        if human.carrying_resource:
            self._return_to_iron_yard(human, game_state)
            return
        
        # If has a target and it's still valid, continue harvesting
        if human.work_target and not human.work_target.is_depleted():
            self._harvest_iron_mine(human, dt, game_state)
            return
        
        # Need to find a new target - check immediately first, then use interval
        if human.work_timer == 0.0:
            # First check - try to find target immediately
            self._find_iron_mine_target(human, game_state)
            if human.work_target:
                # Found target, start working
                return
        
        # If no target found, wait and try again
        human.work_timer += dt
        if human.work_timer >= AUTO_WORK_INTERVAL:
            human.work_timer = 0.0
            self._find_iron_mine_target(human, game_state)
    
    def _find_iron_mine_target(self, human, game_state):
        """Find nearest iron mine to harvest"""
        nearest_mine = None
        nearest_dist = float('inf')
        
        human_x = human.x + human.size/2
        human_y = human.y + human.size/2
        
        for iron_mine in game_state.iron_mine_list:
            if iron_mine.is_depleted():
                continue
            
            dist = distance(human_x, human_y, iron_mine.x, iron_mine.y)
            if dist < AUTO_WORK_SEARCH_RADIUS and dist < nearest_dist:
                # Check if there's an iron yard with space
                has_space = any(iy.can_accept_resource() for iy in game_state.iron_yard_list)
                if has_space:
                    nearest_mine = iron_mine
                    nearest_dist = dist
        
        if nearest_mine:
            # Assign the mine
            human.work_target = nearest_mine
            human.harvest_target = nearest_mine
            human.harvest_timer = 0.0
            
            # Calculate harvest position around mine
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            human.harvest_position = (
                nearest_mine.x + radius * math.cos(angle),
                nearest_mine.y + radius * math.sin(angle)
            )
            
            # Find iron yard
            from systems.resource_system import ResourceType
            for iron_yard in game_state.iron_yard_list:
                if iron_yard.can_accept_resource():
                    human.target_building = iron_yard
                    human.resource_type = ResourceType.IRON
                    break
    
    def _harvest_iron_mine(self, human, dt, game_state):
        """Harvest the assigned iron mine"""
        # Use harvest_target if available, otherwise fall back to work_target
        mine = human.harvest_target if human.harvest_target else human.work_target
        
        if not mine:
            # No mine assigned - reset and find new one
            self._reset_worker(human)
            return
        
        # Restore harvest_target if it was cleared but work_target exists
        if not human.harvest_target and human.work_target:
            human.harvest_target = human.work_target
        
        # Calculate harvest position if not set
        if not human.harvest_position:
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            human.harvest_position = (
                mine.x + radius * math.cos(angle),
                mine.y + radius * math.sin(angle)
            )
        
        # Move to harvest position
        target_x = human.harvest_position[0] if human.harvest_position else mine.x
        target_y = human.harvest_position[1] if human.harvest_position else mine.y
        
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            target_x,
            target_y
        )
        
        if dist > 5:  # Not at harvest position yet
            # Move towards harvest position
            from utils.geometry import clamp
            
            dx = target_x - (human.x + human.size/2)
            dy = target_y - (human.y + human.size/2)
            dx = (dx / dist) * human.speed
            dy = (dy / dist) * human.speed
            
            old_x, old_y = human.x, human.y
            human.x += dx
            human.y += dy
            
            # Keep within playable area bounds
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
            human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
            
            # Simple collision check
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
        else:
            # At harvest position, harvest the mine
            mine.being_harvested = True
            human.harvest_timer += dt
            
            if human.harvest_timer >= HARVEST_TIME:
                # Finished harvesting
                mine.harvest()
                mine.being_harvested = False
                human.harvest_timer = 0.0
                human.carrying_resource = True
    
    def _return_to_iron_yard(self, human, game_state):
        """Return to iron yard to deposit iron"""
        from entities.ironyard import IronYard
        
        building = human.target_building
        
        # Validate that building is actually an iron yard
        if not building or not isinstance(building, IronYard):
            # Find a valid iron yard
            for iron_yard in game_state.iron_yard_list:
                if iron_yard.can_accept_resource():
                    building = iron_yard
                    human.target_building = iron_yard
                    break
            
            if not building or not isinstance(building, IronYard):
                # No valid iron yard - reset worker
                self._reset_worker(human)
                return
        
        # Move to building
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            building.x + building.width/2,
            building.y + building.height/2
        )
        
        if dist > 20:  # Not at building yet
            from utils.geometry import clamp
            
            dx = (building.x + building.width/2) - (human.x + human.size/2)
            dy = (building.y + building.height/2) - (human.y + human.size/2)
            dx = (dx / dist) * human.speed
            dy = (dy / dist) * human.speed
            
            old_x, old_y = human.x, human.y
            human.x += dx
            human.y += dy
            
            # Keep within playable area bounds
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
            human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
            
            # Simple collision check
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
        else:
            # At building, deposit resource
            from systems.resource_system import ResourceType
            if building.add_iron():
                self.resource_system.add_resource(ResourceType.IRON, 1)
                human.carrying_resource = False
                human.harvest_timer = 0.0
                
                # Continue working if mine still has health
                if human.work_target and not human.work_target.is_depleted():
                    # Go back to mine
                    pass
                else:
                    # Mine depleted, find new one
                    human.work_target = None
                    human.harvest_target = None
                    human.harvest_position = None
            else:
                # Building full - stop working
                self._reset_worker(human)
    
    def _update_stoneworker(self, human, dt, game_state):
        """Update a stoneworker - automatically harvests rocks"""
        # If carrying resource, return to stone yard
        if human.carrying_resource:
            self._return_to_stone_yard(human, game_state)
            return
        
        # If has a target and it's still valid, continue harvesting
        if human.work_target and not human.work_target.is_depleted():
            self._harvest_rock(human, dt, game_state)
            return
        
        # Need to find a new target - check immediately first, then use interval
        if human.work_timer == 0.0:
            # First check - try to find target immediately
            self._find_rock_target(human, game_state)
            if human.work_target:
                # Found target, start working
                return
        
        # If no target found, wait and try again
        human.work_timer += dt
        if human.work_timer >= AUTO_WORK_INTERVAL:
            human.work_timer = 0.0
            self._find_rock_target(human, game_state)
    
    def _find_rock_target(self, human, game_state):
        """Find nearest rock to harvest"""
        nearest_rock = None
        nearest_dist = float('inf')
        
        human_x = human.x + human.size/2
        human_y = human.y + human.size/2
        
        for rock in game_state.rock_list:
            if rock.is_depleted():
                continue
            
            dist = distance(human_x, human_y, rock.x, rock.y)
            if dist < AUTO_WORK_SEARCH_RADIUS and dist < nearest_dist:
                # Check if there's a stone yard with space
                has_space = any(sy.can_accept_resource() for sy in game_state.stone_yard_list)
                if has_space:
                    nearest_rock = rock
                    nearest_dist = dist
        
        if nearest_rock:
            # Assign the rock
            human.work_target = nearest_rock
            human.harvest_target = nearest_rock
            human.harvest_timer = 0.0
            
            # Calculate harvest position around rock
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            human.harvest_position = (
                nearest_rock.x + radius * math.cos(angle),
                nearest_rock.y + radius * math.sin(angle)
            )
            
            # Find stone yard
            from systems.resource_system import ResourceType
            for stone_yard in game_state.stone_yard_list:
                if stone_yard.can_accept_resource():
                    human.target_building = stone_yard
                    human.resource_type = ResourceType.STONE
                    break
    
    def _harvest_rock(self, human, dt, game_state):
        """Harvest the assigned rock"""
        # Use harvest_target if available, otherwise fall back to work_target
        rock = human.harvest_target if human.harvest_target else human.work_target
        
        if not rock:
            # No rock assigned - reset and find new one
            self._reset_worker(human)
            return
        
        # Restore harvest_target if it was cleared but work_target exists
        if not human.harvest_target and human.work_target:
            human.harvest_target = human.work_target
        
        # Calculate harvest position if not set
        if not human.harvest_position:
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            human.harvest_position = (
                rock.x + radius * math.cos(angle),
                rock.y + radius * math.sin(angle)
            )
        
        # Move to harvest position
        target_x = human.harvest_position[0] if human.harvest_position else rock.x
        target_y = human.harvest_position[1] if human.harvest_position else rock.y
        
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            target_x,
            target_y
        )
        
        if dist > 5:  # Not at harvest position yet
            # Move towards harvest position
            from utils.geometry import clamp
            
            dx = target_x - (human.x + human.size/2)
            dy = target_y - (human.y + human.size/2)
            dx = (dx / dist) * human.speed
            dy = (dy / dist) * human.speed
            
            old_x, old_y = human.x, human.y
            human.x += dx
            human.y += dy
            
            # Keep within playable area bounds
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
            human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
            
            # Simple collision check
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
        else:
            # At harvest position, harvest the rock
            rock.being_harvested = True
            human.harvest_timer += dt
            
            if human.harvest_timer >= HARVEST_TIME:
                # Finished harvesting
                rock.harvest()
                rock.being_harvested = False
                human.harvest_timer = 0.0
                human.carrying_resource = True
    
    def _return_to_stone_yard(self, human, game_state):
        """Return to stone yard to deposit stone"""
        from entities.stoneyard import StoneYard
        
        building = human.target_building
        
        # Validate that building is actually a stone yard
        if not building or not isinstance(building, StoneYard):
            # Find a valid stone yard
            for stone_yard in game_state.stone_yard_list:
                if stone_yard.can_accept_resource():
                    building = stone_yard
                    human.target_building = stone_yard
                    break
            
            if not building or not isinstance(building, StoneYard):
                # No valid stone yard - reset worker
                self._reset_worker(human)
                return
        
        # Move to building
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            building.x + building.width/2,
            building.y + building.height/2
        )
        
        if dist > 20:  # Not at building yet
            from utils.geometry import clamp
            
            dx = (building.x + building.width/2) - (human.x + human.size/2)
            dy = (building.y + building.height/2) - (human.y + human.size/2)
            dx = (dx / dist) * human.speed
            dy = (dy / dist) * human.speed
            
            old_x, old_y = human.x, human.y
            human.x += dx
            human.y += dy
            
            # Keep within playable area bounds
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
            human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
            
            # Simple collision check
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
        else:
            # At building, deposit resource
            from systems.resource_system import ResourceType
            if building.add_stone():
                self.resource_system.add_resource(ResourceType.STONE, 1)
                human.carrying_resource = False
                human.harvest_timer = 0.0
                
                # Continue working if rock still has health
                if human.work_target and not human.work_target.is_depleted():
                    # Go back to rock
                    pass
                else:
                    # Rock depleted, find new one
                    human.work_target = None
                    human.harvest_target = None
                    human.harvest_position = None
            else:
                # Building full - stop working
                self._reset_worker(human)
    
    def _update_saltworker(self, human, dt, game_state):
        """Update a saltworker - automatically harvests salt deposits"""
        # If carrying resource, return to salt yard
        if human.carrying_resource:
            self._return_to_salt_yard(human, game_state)
            return
        
        # If has a target and it's still valid, continue harvesting
        if human.work_target and not human.work_target.is_depleted():
            self._harvest_salt(human, dt, game_state)
            return
        
        # Need to find a new target - check immediately first, then use interval
        if human.work_timer == 0.0:
            # First check - try to find target immediately
            self._find_salt_target(human, game_state)
            if human.work_target:
                # Found target, start working
                return
        
        # If no target found, wait and try again
        human.work_timer += dt
        if human.work_timer >= AUTO_WORK_INTERVAL:
            human.work_timer = 0.0
            self._find_salt_target(human, game_state)
    
    def _find_salt_target(self, human, game_state):
        """Find nearest salt deposit to harvest"""
        nearest_salt = None
        nearest_dist = float('inf')
        
        human_x = human.x + human.size/2
        human_y = human.y + human.size/2
        
        for salt in game_state.salt_list:
            if salt.is_depleted():
                continue
            
            dist = distance(human_x, human_y, salt.x, salt.y)
            if dist < AUTO_WORK_SEARCH_RADIUS and dist < nearest_dist:
                # Check if there's a salt yard with space
                has_space = any(sy.can_accept_resource() for sy in game_state.salt_yard_list)
                if has_space:
                    nearest_salt = salt
                    nearest_dist = dist
        
        if nearest_salt:
            # Assign the salt
            human.work_target = nearest_salt
            human.harvest_target = nearest_salt
            human.harvest_timer = 0.0
            
            # Calculate harvest position around salt
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            human.harvest_position = (
                nearest_salt.x + radius * math.cos(angle),
                nearest_salt.y + radius * math.sin(angle)
            )
            
            # Find salt yard
            from systems.resource_system import ResourceType
            for salt_yard in game_state.salt_yard_list:
                if salt_yard.can_accept_resource():
                    human.target_building = salt_yard
                    human.resource_type = ResourceType.SALT
                    break
    
    def _harvest_salt(self, human, dt, game_state):
        """Harvest the assigned salt deposit"""
        # Use harvest_target if available, otherwise fall back to work_target
        salt = human.harvest_target if human.harvest_target else human.work_target
        
        if not salt:
            # No salt assigned - reset and find new one
            self._reset_worker(human)
            return
        
        # Restore harvest_target if it was cleared but work_target exists
        if not human.harvest_target and human.work_target:
            human.harvest_target = human.work_target
        
        # Calculate harvest position if not set
        if not human.harvest_position:
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            human.harvest_position = (
                salt.x + radius * math.cos(angle),
                salt.y + radius * math.sin(angle)
            )
        
        # Move to harvest position
        target_x = human.harvest_position[0] if human.harvest_position else salt.x
        target_y = human.harvest_position[1] if human.harvest_position else salt.y
        
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            target_x,
            target_y
        )
        
        if dist > 5:  # Not at harvest position yet
            # Move towards harvest position
            from utils.geometry import clamp
            
            dx = target_x - (human.x + human.size/2)
            dy = target_y - (human.y + human.size/2)
            dx = (dx / dist) * human.speed
            dy = (dy / dist) * human.speed
            
            old_x, old_y = human.x, human.y
            human.x += dx
            human.y += dy
            
            # Keep within playable area bounds
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
            human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
            
            # Simple collision check
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
        else:
            # At harvest position, harvest the salt
            salt.being_harvested = True
            human.harvest_timer += dt
            
            if human.harvest_timer >= HARVEST_TIME:
                # Finished harvesting
                salt.harvest()
                salt.being_harvested = False
                human.harvest_timer = 0.0
                human.carrying_resource = True
    
    def _return_to_salt_yard(self, human, game_state):
        """Return to salt yard to deposit salt"""
        from entities.saltyard import SaltYard
        
        building = human.target_building
        
        # Validate that building is actually a salt yard
        if not building or not isinstance(building, SaltYard):
            # Find a valid salt yard
            for salt_yard in game_state.salt_yard_list:
                if salt_yard.can_accept_resource():
                    building = salt_yard
                    human.target_building = salt_yard
                    break
            
            if not building or not isinstance(building, SaltYard):
                # No valid salt yard - reset worker
                self._reset_worker(human)
                return
        
        # Move to building
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            building.x + building.width/2,
            building.y + building.height/2
        )
        
        if dist > 20:  # Not at building yet
            from utils.geometry import clamp
            
            dx = (building.x + building.width/2) - (human.x + human.size/2)
            dy = (building.y + building.height/2) - (human.y + human.size/2)
            dx = (dx / dist) * human.speed
            dy = (dy / dist) * human.speed
            
            old_x, old_y = human.x, human.y
            human.x += dx
            human.y += dy
            
            # Keep within playable area bounds
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
            human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
            
            # Simple collision check
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
        else:
            # At building, deposit resource
            from systems.resource_system import ResourceType
            if building.add_salt():
                self.resource_system.add_resource(ResourceType.SALT, 1)
                human.carrying_resource = False
                human.harvest_timer = 0.0
                
                # Continue working if salt still has health
                if human.work_target and not human.work_target.is_depleted():
                    # Go back to salt
                    pass
                else:
                    # Salt depleted, find new one
                    human.work_target = None
                    human.harvest_target = None
                    human.harvest_position = None
            else:
                # Building full - stop working
                self._reset_worker(human)
    
    def _reset_worker(self, human):
        """Reset worker state"""
        human.work_target = None
        human.harvest_target = None
        human.carrying_resource = False
        human.target_building = None
        human.resource_type = None
        human.harvest_position = None
        human.harvest_timer = 0.0
    
    def _check_collisions(self, human, game_state):
        """Simple collision check for employed workers"""
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
        # Salt yards are passable - no collision check needed
        return False
