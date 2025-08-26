#!/usr/bin/env python3
"""
Script to add a new gameweek to the prediction system
Usage: python add_gameweek.py 4 "fixtures.txt"
"""

import sys
import re
from typing import List, Tuple

def parse_fixtures_file(filename: str) -> List[Tuple[str, str]]:
    """Parse a fixtures file and return list of (home, away) tuples"""
    fixtures = []
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Support multiple formats:
            # "Arsenal vs Liverpool"
            # "Arsenal - Liverpool"
            # "Arsenal,Liverpool"
            
            if ' vs ' in line:
                home, away = line.split(' vs ', 1)
            elif ' - ' in line:
                home, away = line.split(' - ', 1)
            elif ',' in line:
                home, away = line.split(',', 1)
            else:
                print(f"Warning: Couldn't parse line: {line}")
                continue
                
            fixtures.append((home.strip(), away.strip()))
    
    return fixtures

def update_main_py(gameweek: int, fixtures: List[Tuple[str, str]]):
    """Update main.py with new gameweek fixtures"""
    
    # Read current main.py
    with open('backend/main.py', 'r') as f:
        content = f.read()
    
    # Find the GAMEWEEK_FIXTURES section
    pattern = r'(GAMEWEEK_FIXTURES = \{.*?\})'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("Error: Could not find GAMEWEEK_FIXTURES in main.py")
        return False
    
    # Build new fixtures string
    fixtures_str = "[\n"
    for home, away in fixtures:
        fixtures_str += f'        ("{home}", "{away}"),\n'
    fixtures_str += "    ],"
    
    # Insert new gameweek before the closing brace
    old_fixtures = match.group(1)
    new_gameweek_entry = f"    {gameweek}: {fixtures_str}\n    # Add future gameweeks here\n}}"
    
    # Replace the closing part
    new_fixtures = old_fixtures.replace(
        "    # Add future gameweeks here\n}",
        new_gameweek_entry
    )
    
    # Update CURRENT_GAMEWEEK
    new_fixtures = re.sub(
        r'CURRENT_GAMEWEEK = \d+',
        f'CURRENT_GAMEWEEK = {gameweek}',
        new_fixtures
    )
    
    # Replace in content
    new_content = content.replace(old_fixtures, new_fixtures)
    
    # Write back
    with open('backend/main.py', 'w') as f:
        f.write(new_content)
    
    print(f"✅ Added gameweek {gameweek} with {len(fixtures)} fixtures")
    return True

def main():
    if len(sys.argv) != 3:
        print("Usage: python add_gameweek.py <gameweek_number> <fixtures_file>")
        print("\nExample fixtures file format:")
        print("Arsenal vs Liverpool")
        print("Chelsea - Manchester City")
        print("Tottenham,Newcastle")
        sys.exit(1)
    
    try:
        gameweek = int(sys.argv[1])
        fixtures_file = sys.argv[2]
        
        print(f"Adding gameweek {gameweek} from {fixtures_file}...")
        
        fixtures = parse_fixtures_file(fixtures_file)
        if not fixtures:
            print("Error: No fixtures found in file")
            sys.exit(1)
        
        print(f"Found {len(fixtures)} fixtures:")
        for home, away in fixtures:
            print(f"  {home} vs {away}")
        
        if update_main_py(gameweek, fixtures):
            print(f"\n🎉 Successfully added gameweek {gameweek}!")
            print("Remember to:")
            print("1. Update team ratings if needed")
            print("2. Test the API endpoints")
            print("3. Deploy the changes")
        
    except ValueError:
        print("Error: Gameweek must be a number")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Fixtures file '{sys.argv[2]}' not found")
        sys.exit(1)

if __name__ == "__main__":
    main()
