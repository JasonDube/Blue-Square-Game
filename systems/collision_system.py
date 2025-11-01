"""
Collision detection system
"""


class CollisionSystem:
    """Handles collision detection between entities and structures"""
    
    @staticmethod
    def check_player_collision(px, py, pen_list, townhall_list):
        """Check if player collides with any structure"""
        for pen in pen_list:
            if pen.check_collision_player(px, py):
                return True
        for townhall in townhall_list:
            if townhall.check_collision_player(px, py):
                return True
        return False
    
    @staticmethod
    def check_sheep_collision(sx, sy, sw, sh, pen_list, townhall_list):
        """Check if sheep collides with any structure"""
        for pen in pen_list:
            if pen.check_collision_sheep(sx, sy, sw, sh):
                return True
        for townhall in townhall_list:
            if townhall.check_collision_sheep(sx, sy, sw, sh):
                return True
        return False
