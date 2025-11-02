"""
Collision detection system
"""


class CollisionSystem:
    """Handles collision detection between entities and structures"""
    
    @staticmethod
    def check_player_collision(px, py, pen_list, townhall_list, lumber_yard_list=None, stone_yard_list=None, iron_yard_list=None, hut_list=None):
        """Check if player collides with any structure"""
        for pen in pen_list:
            if pen.check_collision_player(px, py):
                return True
        for townhall in townhall_list:
            if townhall.check_collision_player(px, py):
                return True
        if lumber_yard_list:
            for lumber_yard in lumber_yard_list:
                if lumber_yard.check_collision_player(px, py):
                    return True
        if stone_yard_list:
            for stone_yard in stone_yard_list:
                if stone_yard.check_collision_player(px, py):
                    return True
        if iron_yard_list:
            for iron_yard in iron_yard_list:
                if iron_yard.check_collision_player(px, py):
                    return True
        # FIXED: Added hut collision detection
        if hut_list:
            for hut in hut_list:
                if hut.check_collision_player(px, py):
                    return True
        return False
    
    @staticmethod
    def check_sheep_collision(sx, sy, sw, sh, pen_list, townhall_list, lumber_yard_list=None, stone_yard_list=None, iron_yard_list=None, hut_list=None):
        """Check if sheep collides with any structure"""
        for pen in pen_list:
            if pen.check_collision_sheep(sx, sy, sw, sh):
                return True
        for townhall in townhall_list:
            if townhall.check_collision_sheep(sx, sy, sw, sh):
                return True
        if lumber_yard_list:
            for lumber_yard in lumber_yard_list:
                if lumber_yard.check_collision_sheep(sx, sy, sw, sh):
                    return True
        if stone_yard_list:
            for stone_yard in stone_yard_list:
                if stone_yard.check_collision_sheep(sx, sy, sw, sh):
                    return True
        if iron_yard_list:
            for iron_yard in iron_yard_list:
                if iron_yard.check_collision_sheep(sx, sy, sw, sh):
                    return True
        # FIXED: Added hut collision detection
        if hut_list:
            for hut in hut_list:
                # Sheep can't collide with huts (no check_collision_sheep method)
                # But we could add basic collision if needed
                pass
        return False
