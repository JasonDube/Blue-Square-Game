#!/usr/bin/env python3
"""
Diagnostic script to check hut system issues
Run this AFTER starting your game to see what's wrong
"""

print("=" * 60)
print("HUT SYSTEM DIAGNOSTIC")
print("=" * 60)

# Test 1: Check if Hut can be imported
print("\n1. Testing Hut import...")
try:
    from entities.hut import Hut
    print("   ✓ Hut can be imported directly")
except ImportError as e:
    print(f"   ✗ FAILED to import Hut: {e}")

# Test 2: Check if Hut is in entities module
print("\n2. Testing entities module...")
try:
    import entities
    if hasattr(entities, 'Hut'):
        print("   ✓ Hut is in entities module")
    else:
        print("   ✗ Hut is NOT in entities module __all__")
        print(f"   Available: {entities.__all__ if hasattr(entities, '__all__') else 'No __all__ defined'}")
except ImportError as e:
    print(f"   ✗ Cannot import entities: {e}")

# Test 3: Check TownHall.hire_human method
print("\n3. Checking TownHall.hire_human method...")
try:
    from entities.townhall import TownHall
    import inspect
    source = inspect.getsource(TownHall.hire_human)
    if 'is_employed = True' in source:
        print("   ✓ hire_human sets is_employed = True")
    else:
        print("   ✗ hire_human does NOT set is_employed = True")
        print("   This is the CRITICAL BUG!")
except Exception as e:
    print(f"   ✗ Error checking method: {e}")

# Test 4: Check Hut color
print("\n4. Checking Hut color...")
try:
    from entities.hut import Hut
    import inspect
    source = inspect.getsource(Hut.draw)
    if 'TAN' in source:
        print("   ✓ Hut uses TAN color (light brown)")
    elif 'BROWN' in source:
        print("   ✗ Hut uses BROWN color (should be TAN)")
    else:
        print("   ? Cannot determine color")
except Exception as e:
    print(f"   ✗ Error checking color: {e}")

# Test 5: Check if constants has TAN
print("\n5. Checking constants...")
try:
    from constants import TAN, HUT_SIZE
    print(f"   ✓ TAN color defined: {TAN}")
    print(f"   ✓ HUT_SIZE: {HUT_SIZE}")
    print(f"   ✓ Radius should be: {HUT_SIZE // 2}")
except ImportError as e:
    print(f"   ✗ Cannot import constants: {e}")

# Test 6: Check HumanBehaviorSystem
print("\n6. Checking HumanBehaviorSystem._update_hut_claiming...")
try:
    from systems.human_behavior_system import HumanBehaviorSystem
    import inspect
    source = inspect.getsource(HumanBehaviorSystem._update_hut_claiming)
    if 'human.is_employed' in source:
        print("   ✓ Checks is_employed flag")
    else:
        print("   ✗ Does NOT check is_employed flag")
    
    if 'hut.claim' in source:
        print("   ✓ Calls hut.claim()")
    else:
        print("   ✗ Does NOT call hut.claim()")
        
    if 'print' in source or 'print(' in source:
        print("   ✓ Has debug print statements")
    else:
        print("   ⚠ No debug print statements (won't see claiming messages)")
except Exception as e:
    print(f"   ✗ Error checking system: {e}")

print("\n" + "=" * 60)
print("RECOMMENDATIONS:")
print("=" * 60)

recommendations = []

# Check each component
try:
    import entities
    if not hasattr(entities, 'Hut'):
        recommendations.append("→ UPDATE entities/__init__.py to include Hut import")
except:
    pass

try:
    from entities.townhall import TownHall
    import inspect
    source = inspect.getsource(TownHall.hire_human)
    if 'is_employed = True' not in source:
        recommendations.append("→ UPDATE entities/townhall.py - add 'human.is_employed = True' in hire_human()")
except:
    pass

try:
    from entities.hut import Hut
    import inspect
    source = inspect.getsource(Hut.draw)
    if 'TAN' not in source:
        recommendations.append("→ UPDATE entities/hut.py - change BROWN to TAN")
except:
    pass

if recommendations:
    for rec in recommendations:
        print(rec)
else:
    print("✓ All checks passed! If huts still don't work:")
    print("  1. Make sure you RESTARTED the game after updating files")
    print("  2. Check that hut_list is being passed to collision_system")
    print("  3. Enable debug mode (press 'd') and check console output")
    print("  4. Make sure you actually HIRED a worker at the town hall")

print("=" * 60)
