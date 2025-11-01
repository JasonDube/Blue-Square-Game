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
                
                if WorldGenerator._is_valid_tree_position(tree_x, tree_y, tree_list, pen_list):
                    tree_list.append(Tree(tree_x, tree_y))
                    break
                
                attempts += 1
        
        return tree_list
    
    @staticmethod
    def _is_valid_tree_position(tree_x, tree_y, existing_trees, pen_list):
        """Check if tree position is valid"""
        # Check distance from other trees
        for existing_tree in existing_trees:
            dist = math.sqrt((tree_x - existing_tree.x)**2 + (tree_y - existing_tree.y)**2)
            if dist < MIN_TREE_DISTANCE:
                return False
        
        # Check distance from pens
        if pen_list:
            for pen in pen_list:
                pen_center_x = pen.x + pen.size // 2
                pen_center_y = pen.y + pen.size // 2
                dist = math.sqrt((tree_x - pen_center_x)**2 + (tree_y - pen_center_y)**2)
                if dist < MIN_TREE_PEN_DISTANCE:
                    return False
        
        return True
    
    @staticmethod
    def generate_initial_entities():
        """Generate initial sheep, humans, and pens"""
        # Create initial pen
        pen_list = [Pen(400, 250, PEN_SIZE)]
        
        # Create initial sheep
        sheep_list = [
            Sheep(300, 300, "male"),
            Sheep(350, 320, "female")
        ]
        
        # Create initial humans
        human_list = [
            Human(200, 200, "male"),
            Human(250, 200, "female")
        ]
        
        return sheep_list, human_list, pen_list
