#!/usr/bin/env python3
"""
Validation script to check code structure without running the game
"""
import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} MISSING!")
        return False

def main():
    print("Validating refactored game structure...\n")
    
    all_good = True
    
    # Check main files
    print("Core Files:")
    all_good &= check_file_exists("main.py", "main.py")
    all_good &= check_file_exists("constants.py", "constants.py")
    all_good &= check_file_exists("README.md", "README.md")
    all_good &= check_file_exists("COMPARISON.md", "COMPARISON.md")
    
    # Check entities
    print("\nEntity Files:")
    all_good &= check_file_exists("entities/__init__.py", "entities/__init__.py")
    all_good &= check_file_exists("entities/pen.py", "entities/pen.py")
    all_good &= check_file_exists("entities/townhall.py", "entities/townhall.py")
    all_good &= check_file_exists("entities/tree.py", "entities/tree.py")
    all_good &= check_file_exists("entities/sheep.py", "entities/sheep.py")
    all_good &= check_file_exists("entities/human.py", "entities/human.py")
    
    # Check systems
    print("\nSystem Files:")
    all_good &= check_file_exists("systems/__init__.py", "systems/__init__.py")
    all_good &= check_file_exists("systems/collision_system.py", "systems/collision_system.py")
    all_good &= check_file_exists("systems/day_cycle_system.py", "systems/day_cycle_system.py")
    all_good &= check_file_exists("systems/reproduction_system.py", "systems/reproduction_system.py")
    all_good &= check_file_exists("systems/input_system.py", "systems/input_system.py")
    
    # Check UI
    print("\nUI Files:")
    all_good &= check_file_exists("ui/__init__.py", "ui/__init__.py")
    all_good &= check_file_exists("ui/context_menu.py", "ui/context_menu.py")
    all_good &= check_file_exists("ui/build_mode.py", "ui/build_mode.py")
    all_good &= check_file_exists("ui/hud.py", "ui/hud.py")
    
    # Check managers
    print("\nManager Files:")
    all_good &= check_file_exists("managers/__init__.py", "managers/__init__.py")
    all_good &= check_file_exists("managers/game_state.py", "managers/game_state.py")
    
    # Check utils
    print("\nUtility Files:")
    all_good &= check_file_exists("utils/__init__.py", "utils/__init__.py")
    all_good &= check_file_exists("utils/geometry.py", "utils/geometry.py")
    all_good &= check_file_exists("utils/world_generator.py", "utils/world_generator.py")
    
    # Summary
    print("\n" + "="*50)
    if all_good:
        print("✓ All files present!")
        print("\nTo run the game:")
        print("  1. Make sure pygame is installed: pip install pygame")
        print("  2. Run: python main.py")
    else:
        print("✗ Some files are missing!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
