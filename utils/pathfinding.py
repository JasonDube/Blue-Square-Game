"""
Pathfinding utility for AI navigation
"""
import pygame
import math
from utils.geometry import distance


def is_path_blocked(start_x, start_y, goal_x, goal_y, game_state, human_size=10, ignore_goal_building=False):
    """
    Check if direct path from start to goal is blocked by buildings.
    Samples points along the line and checks for collisions.
    
    Args:
        ignore_goal_building: If True, don't check collisions near the goal point (allows approaching buildings)
    """
    # Sample points along the path
    num_samples = 20
    human_center_size = human_size / 2
    
    for i in range(num_samples + 1):
        t = i / num_samples
        sample_x = start_x + (goal_x - start_x) * t
        sample_y = start_y + (goal_y - start_y) * t
        
        # If we're very close to goal and ignoring goal building, skip collision check
        if ignore_goal_building:
            dist_to_goal = distance(sample_x, sample_y, goal_x, goal_y)
            if dist_to_goal < 50:  # Within 50 pixels of goal, allow approaching
                continue
        
        # Check collision with all buildings
        human_rect = pygame.Rect(sample_x - human_center_size, 
                                 sample_y - human_center_size,
                                 human_size, human_size)
        
        # Check all building types
        if _check_building_collision(human_rect, game_state):
            return True
    
    return False


def _check_building_collision(human_rect, game_state):
    """Check if human rect collides with any building"""
    # Check pens
    for pen in game_state.pen_list:
        if pen.collision_enabled:
            pen_rect = pygame.Rect(pen.x, pen.y, pen.size, pen.size)
            if human_rect.colliderect(pen_rect):
                return True
    
    # Check town halls
    for townhall in game_state.townhall_list:
        if townhall.collision_enabled:
            townhall_rect = pygame.Rect(townhall.x, townhall.y, 
                                       townhall.width, townhall.height)
            if human_rect.colliderect(townhall_rect):
                return True
    
    # Check lumber yards
    for lumber_yard in game_state.lumber_yard_list:
        if lumber_yard.collision_enabled:
            lumber_rect = pygame.Rect(lumber_yard.x, lumber_yard.y,
                                      lumber_yard.width, lumber_yard.height)
            if human_rect.colliderect(lumber_rect):
                return True
    
    # Check stone yards
    for stone_yard in game_state.stone_yard_list:
        if stone_yard.collision_enabled:
            stone_rect = pygame.Rect(stone_yard.x, stone_yard.y,
                                     stone_yard.width, stone_yard.height)
            if human_rect.colliderect(stone_rect):
                return True
    
    # Check iron yards
    for iron_yard in game_state.iron_yard_list:
        if iron_yard.collision_enabled:
            iron_rect = pygame.Rect(iron_yard.x, iron_yard.y,
                                   iron_yard.width, iron_yard.height)
            if human_rect.colliderect(iron_rect):
                return True
    
    # Check salt yards
    for salt_yard in game_state.salt_yard_list:
        if salt_yard.collision_enabled:
            salt_rect = pygame.Rect(salt_yard.x, salt_yard.y,
                                    salt_yard.width, salt_yard.height)
            if human_rect.colliderect(salt_rect):
                return True
    
    # Check wool sheds
    for wool_shed in game_state.wool_shed_list:
        if wool_shed.collision_enabled:
            wool_rect = pygame.Rect(wool_shed.x, wool_shed.y,
                                    wool_shed.width, wool_shed.height)
            if human_rect.colliderect(wool_rect):
                return True
    
    # Check barley farms
    for farm in game_state.barley_farm_list:
        if farm.collision_enabled:
            farm_rect = pygame.Rect(farm.x, farm.y, farm.width, farm.height)
            if human_rect.colliderect(farm_rect):
                return True
    
    # Check silos (circular collision)
    for silo in game_state.silo_list:
        if silo.collision_enabled:
            # Circular collision check
            human_center_x = human_rect.centerx
            human_center_y = human_rect.centery
            silo_center_x = silo.x + silo.radius
            silo_center_y = silo.y + silo.radius
            dist = distance(human_center_x, human_center_y, 
                          silo_center_x, silo_center_y)
            if dist < (silo.radius + human_rect.width / 2):
                return True
    
    # Check mills
    for mill in game_state.mill_list:
        if mill.collision_enabled:
            mill_rect = pygame.Rect(mill.x, mill.y, mill.width, mill.height)
            if human_rect.colliderect(mill_rect):
                return True
    
    # Check huts (circular collision)
    for hut in game_state.hut_list:
        if hut.collision_enabled:
            human_center_x = human_rect.centerx
            human_center_y = human_rect.centery
            hut_center_x = hut.x + hut.size / 2
            hut_center_y = hut.y + hut.size / 2
            dist = distance(human_center_x, human_center_y,
                          hut_center_x, hut_center_y)
            if dist < (hut.radius + human_rect.width / 2):
                return True
    
    return False


def find_nearest_road(pos_x, pos_y, game_state):
    """Find the nearest road segment to the given position"""
    if not game_state.road_list:
        return None
    
    nearest_road = None
    min_distance = float('inf')
    
    for road in game_state.road_list:
        # Get center of road
        road_center_x = road.x + road.width / 2
        road_center_y = road.y + road.height / 2
        
        dist = distance(pos_x, pos_y, road_center_x, road_center_y)
        if dist < min_distance:
            min_distance = dist
            nearest_road = road
    
    return nearest_road


def is_on_road(pos_x, pos_y, game_state, tolerance=15, preferred_road=None):
    """
    Check if a position is on or near a road segment.
    Returns the road segment if on road, None otherwise.
    At corners/intersections, strongly prefers staying on the current road.

    Args:
        preferred_road: If provided and the position is on this road, strongly prefer it
    """
    if not game_state.road_list:
        return None

    # Strongly prefer the current road if provided - prevents oscillation at corners
    if preferred_road:
        road_rect = pygame.Rect(preferred_road.x, preferred_road.y,
                               preferred_road.width, preferred_road.height)
        # Use a larger tolerance for preferred road to maintain continuity
        expanded_rect = road_rect.inflate(tolerance * 3, tolerance * 3)
        if expanded_rect.collidepoint(pos_x, pos_y):
            return preferred_road

    # If no preferred road or not on preferred road, find the closest road
    closest_road = None
    closest_distance = float('inf')

    for road in game_state.road_list:
        road_rect = pygame.Rect(road.x, road.y, road.width, road.height)
        # Check if point is within road bounds (with tolerance)
        expanded_rect = road_rect.inflate(tolerance * 2, tolerance * 2)
        if expanded_rect.collidepoint(pos_x, pos_y):
            # Prefer roads where the point is closer to the center
            road_center_x = road_rect.centerx
            road_center_y = road_rect.centery
            dist_to_center = distance(pos_x, pos_y, road_center_x, road_center_y)
            if dist_to_center < closest_distance:
                closest_distance = dist_to_center
                closest_road = road

    return closest_road


def find_connected_roads(current_road, game_state, max_distance=80):
    """
    Find roads that are connected/adjacent to the current road.
    Roads are considered connected if their edges are within max_distance.
    """
    connected = []

    current_rect = pygame.Rect(current_road.x, current_road.y,
                                current_road.width, current_road.height)

    for road in game_state.road_list:
        if road == current_road:
            continue

        road_rect = pygame.Rect(road.x, road.y, road.width, road.height)

        # Check if roads are adjacent (touching or very close)
        # Calculate distance between nearest edges
        dx = max(current_rect.left - road_rect.right,
                 road_rect.left - current_rect.right, 0)
        dy = max(current_rect.top - road_rect.bottom,
                 road_rect.top - current_rect.bottom, 0)

        edge_distance = math.sqrt(dx * dx + dy * dy)

        if edge_distance <= max_distance:
            connected.append(road)

    return connected


def find_next_road_segment(current_pos_x, current_pos_y, current_road, goal_x, goal_y, game_state, previous_road=None):
    """
    Find the next road segment to move toward that gets closer to the goal.
    Transitions only when near the end of a road segment in the direction of travel.
    """
    # First, check if we can exit the road directly to goal
    if not is_path_blocked(current_pos_x, current_pos_y, goal_x, goal_y, game_state, ignore_goal_building=True):
        return (goal_x, goal_y)

    current_rect = pygame.Rect(current_road.x, current_road.y,
                               current_road.width, current_road.height)

    transition_dist_from_end = 20
    ready_to_transition = False

    # Determine if we are near the end of the road IN THE DIRECTION of the overall goal
    if current_road.width > current_road.height:  # Horizontal road
        dx_to_goal = goal_x - current_pos_x
        if dx_to_goal > 0 and current_pos_x > current_rect.right - transition_dist_from_end:
            ready_to_transition = True
        elif dx_to_goal < 0 and current_pos_x < current_rect.left + transition_dist_from_end:
            ready_to_transition = True
    else:  # Vertical road
        dy_to_goal = goal_y - current_pos_y
        if dy_to_goal > 0 and current_pos_y > current_rect.bottom - transition_dist_from_end:
            ready_to_transition = True
        elif dy_to_goal < 0 and current_pos_y < current_rect.top + transition_dist_from_end:
            ready_to_transition = True

    if not ready_to_transition:
        return move_along_road_toward_goal(current_pos_x, current_pos_y, current_road, goal_x, goal_y)

    # We are ready to transition, find the best next road
    connected_roads = find_connected_roads(current_road, game_state)

    # Strongly prefer roads that continue in the direction we're moving
    # Calculate movement direction based on distance from center
    center_x = current_rect.centerx
    center_y = current_rect.centery
    move_dir_x = current_pos_x - center_x  # Positive = moving right, Negative = moving left
    move_dir_y = current_pos_y - center_y  # Positive = moving down, Negative = moving up

    best_road = None
    best_score = float('inf')

    for connected_road in connected_roads:
        # Skip the previous road to prevent oscillation
        if connected_road == previous_road:
            continue

        connected_rect = pygame.Rect(connected_road.x, connected_road.y,
                                     connected_road.width, connected_road.height)

        # Score based on:
        # 1. Distance to goal (primary)
        # 2. Continuity with movement direction (secondary)
        goal_dist = distance(connected_rect.centerx, connected_rect.centery, goal_x, goal_y)

        # Calculate direction continuity bonus
        connected_center_x = connected_rect.centerx
        connected_center_y = connected_rect.centery
        dir_continuity = 0

        if abs(move_dir_x) > abs(move_dir_y):  # Moving horizontally
            if move_dir_x > 0 and connected_center_x > current_pos_x:  # Continuing right
                dir_continuity = -50  # Bonus for continuing in same direction
            elif move_dir_x < 0 and connected_center_x < current_pos_x:  # Continuing left
                dir_continuity = -50
        else:  # Moving vertically
            if move_dir_y > 0 and connected_center_y > current_pos_y:  # Continuing down
                dir_continuity = -50  # Bonus for continuing in same direction
            elif move_dir_y < 0 and connected_center_y < current_pos_y:  # Continuing up
                dir_continuity = -50

        total_score = goal_dist + dir_continuity

        if total_score < best_score:
            best_score = total_score
            best_road = connected_road

    if best_road:
        # Transition to the best connected road
        best_rect = pygame.Rect(best_road.x, best_road.y,
                                best_road.width, best_road.height)
        return (best_rect.centerx, best_rect.centery)

    # No good transition - stay on current road
    return move_along_road_toward_goal(current_pos_x, current_pos_y, current_road, goal_x, goal_y)


def move_along_road_toward_goal(current_pos_x, current_pos_y, road, goal_x, goal_y):
    """
    Move along the road's main axis toward the goal, while being pulled to the center.
    """
    road_rect = pygame.Rect(road.x, road.y, road.width, road.height)
    center_x = road_rect.centerx
    center_y = road_rect.centery

    # Calculate direction to goal
    dx = goal_x - current_pos_x
    dy = goal_y - current_pos_y

    if road.width > road.height: # Horizontal road
        # Primary movement is horizontal
        target_x = current_pos_x + (dx / abs(dx) if dx != 0 else 0) * 20
        # Gentle pull towards center Y
        target_y = current_pos_y + (center_y - current_pos_y) * 0.5
    else: # Vertical road
        # Primary movement is vertical
        target_y = current_pos_y + (dy / abs(dy) if dy != 0 else 0) * 20
        # Gentle pull towards center X
        target_x = current_pos_x + (center_x - current_pos_x) * 0.5

    # Clamp to road bounds to be safe
    target_x = max(road_rect.left + 5, min(target_x, road_rect.right - 5))
    target_y = max(road_rect.top + 5, min(target_y, road_rect.bottom - 5))

    return (target_x, target_y)




def get_road_path_target(current_x, current_y, goal_x, goal_y, game_state, previous_road=None):
    """
    Get target position for pathfinding.
    - If on a road, follow the road network.
    - If not on a road, check if the goal is closer than the nearest road.
        - If so, and if the path is clear, go directly to the goal.
        - Otherwise, pathfind to the nearest road.
    """
    human = None
    for h in game_state.human_list:
        if h.x == current_x and h.y == current_y:
            human = h
            break
    
    if human:
        previous_road = human.previous_road

    on_road = is_on_road(current_x, current_y, game_state, preferred_road=previous_road)

    if on_road:
        if human:
            human.previous_road = on_road
        return find_next_road_segment(current_x, current_y, on_road, goal_x, goal_y, game_state, previous_road)

    # --- Not on a road ---

    # 1. Find the nearest road
    nearest_road = find_nearest_road(current_x, current_y, game_state)

    if nearest_road:
        # 2. Check if the goal is closer than the nearest road
        dist_to_goal = distance(current_x, current_y, goal_x, goal_y)
        
        road_rect = pygame.Rect(nearest_road.x, nearest_road.y, nearest_road.width, nearest_road.height)
        dist_to_road = distance(current_x, current_y, road_rect.centerx, road_rect.centery)

        # 3. If goal is closer AND path is clear, go directly to goal
        if dist_to_goal < dist_to_road:
            if not is_path_blocked(current_x, current_y, goal_x, goal_y, game_state, ignore_goal_building=True):
                return (goal_x, goal_y)
            # If direct path is blocked, we must use roads, so we fall through...

    # 4. Pathfind to the nearest road (or go direct if no roads exist)
    if nearest_road:
        road_rect = pygame.Rect(nearest_road.x, nearest_road.y, nearest_road.width, nearest_road.height)
        target_road_pos = (road_rect.centerx, road_rect.centery)

        if is_path_blocked(current_x, current_y, target_road_pos[0], target_road_pos[1], game_state):
             # Path to road is blocked, stay still
            return (current_x, current_y)
        else:
            # Path to road is clear, go to it
            return target_road_pos
    else:
        # No roads on map, just try to go directly to goal (checking for blocks)
        if not is_path_blocked(current_x, current_y, goal_x, goal_y, game_state, ignore_goal_building=True):
            return (goal_x, goal_y)

    # Fallback: stay still if no other option
    return (current_x, current_y)

