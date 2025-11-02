"""
World generation utilities
"""
import random
import math
from constants import *
from entities.tree import Tree
from entities.pen import Pen
from entities.sheep import Sheep
from entities.human import Human
from entities.lumberyard import LumberYard
from entities.stoneyard import StoneYard
from entities.ironyard import IronYard
from entities.rock import Rock
from entities.ironmine import IronMine


class WorldGenerator:
    """Generates initial game world"""
    
    @staticmethod
    def generate_trees(num_trees=NUM_TREES, pen_list=None):
        """Generate trees randomly across the map"""
        tree_list = []
        
        for _ in range(num_trees):
            attempts = 0
            while attempts < 50:
                tree_x = random.randint(20, SCREEN_WIDTH - 20)
                tree_y = random.randint(50, SCREEN_HEIGHT - 50)
                
                if WorldGenerator._is_valid_resource_position(tree_x, tree_y, tree_list, pen_list):
                    tree_list.append(Tree(tree_x, tree_y))
                    break
                
                attempts += 1
        
        return tree_list
    
    @staticmethod
    def generate_rocks(num_rocks=15, pen_list=None, tree_list=None):
        """Generate rocks randomly across the map"""
        rock_list = []
        
        for _ in range(num_rocks):
            attempts = 0
            while attempts < 50:
                rock_x = random.randint(20, SCREEN_WIDTH - 20)
                rock_y = random.randint(50, SCREEN_HEIGHT - 50)
                
                # Check distance from trees and other rocks
                valid = True
                if tree_list:
                    for tree in tree_list:
                        dist = math.sqrt((rock_x - tree.x)**2 + (rock_y - tree.y)**2)
                        if dist < 60:
                            valid = False
                            break
                
                if valid:
                    for rock in rock_list:
                        dist = math.sqrt((rock_x - rock.x)**2 + (rock_y - rock.y)**2)
                        if dist < 60:
                            valid = False
                            break
                
                if valid and pen_list:
                    for pen in pen_list:
                        pen_center_x = pen.x + pen.size // 2
                        pen_center_y = pen.y + pen.size // 2
                        dist = math.sqrt((rock_x - pen_center_x)**2 + (rock_y - pen_center_y)**2)
                        if dist < 80:
                            valid = False
                            break
                
                if valid:
                    rock_list.append(Rock(rock_x, rock_y, health=200))
                    break
                
                attempts += 1
        
        return rock_list
    
    @staticmethod
    def generate_iron_mine(pen_list=None, tree_list=None, rock_list=None):
        """Generate a single iron mine on the map"""
        for attempt in range(100):
            mine_x = random.randint(50, SCREEN_WIDTH - 50)
            mine_y = random.randint(100, SCREEN_HEIGHT - 100)
            
            # Check distance from other resources
            valid = True
            
            if tree_list:
                for tree in tree_list:
                    dist = math.sqrt((mine_x - tree.x)**2 + (mine_y - tree.y)**2)
                    if dist < 100:
                        valid = False
                        break
            
            if valid and rock_list:
                for rock in rock_list:
                    dist = math.sqrt((mine_x - rock.x)**2 + (mine_y - rock.y)**2)
                    if dist < 100:
                        valid = False
                        break
            
            if valid and pen_list:
                for pen in pen_list:
                    pen_center_x = pen.x + pen.size // 2
                    pen_center_y = pen.y + pen.size // 2
                    dist = math.sqrt((mine_x - pen_center_x)**2 + (mine_y - pen_center_y)**2)
                    if dist < 120:
                        valid = False
                        break
            
            if valid:
                return IronMine(mine_x, mine_y, health=1000)
        
        return None  # Couldn't find valid position
    
    @staticmethod
    def _is_valid_resource_position(x, y, existing_resources, pen_list):
        """Check if resource position is valid"""
        # Check distance from other resources
        for existing_resource in existing_resources:
            dist = math.sqrt((x - existing_resource.x)**2 + (y - existing_resource.y)**2)
            if dist < 60:
                return False
        
        # Check distance from pens
        if pen_list:
            for pen in pen_list:
                pen_center_x = pen.x + pen.size // 2
                pen_center_y = pen.y + pen.size // 2
                dist = math.sqrt((x - pen_center_x)**2 + (y - pen_center_y)**2)
                if dist < 100:
                    return False
        
        return True
    
    @staticmethod
    def generate_initial_entities():
        """Generate initial sheep, humans, pens, and buildings"""
        # Create initial pen
        pen_list = [Pen(400, 250, PEN_SIZE)]
        
        # Create initial lumber yard
        lumber_yard_list = [LumberYard(50, 300)]
        
        # Create stone yard
        stone_yard_list = [StoneYard(50, 100)]
        
        # Create iron yard
        iron_yard_list = [IronYard(900, 400)]
        
        # Create initial sheep
        sheep_list = [
            Sheep(300, 300, "male"),
            Sheep(350, 320, "female")
        ]
        
        # Create initial humans - more of them for testing!
        human_list = [
            Human(200, 200, "male"),
            Human(250, 200, "female"),
            Human(200, 250, "male"),    # Second male worker
            Human(250, 250, "female"),  # Second female worker
            Human(200, 100, "male")     # Third male worker for testing
        ]
        
        return sheep_list, human_list, pen_list, lumber_yard_list, stone_yard_list, iron_yard_list