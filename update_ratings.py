#!/usr/bin/env python3
"""
Script to update team ratings after gameweek results
Usage: python update_ratings.py results.json
"""

import sys
import json
from backend.main import update_ratings_after_gameweek, CURRENT_RATINGS

def main():
    if len(sys.argv) != 2:
        print("Usage: python update_ratings.py <results_file.json>")
        print("\nExample results file format:")
        print('{')
        print('  "Arsenal vs Leeds United": {"Arsenal": 2, "Leeds United": 1},')
        print('  "Chelsea vs Manchester City": {"Chelsea": 1, "Manchester City": 3}')
        print('}')
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r') as f:
            results = json.load(f)
        
        print("Current ratings (before update):")
        for team, rating in sorted(CURRENT_RATINGS.items(), key=lambda x: x[1], reverse=True):
            print(f"  {team}: {rating:.2f}")
        
        print(f"\nUpdating ratings based on {len(results)} matches...")
        update_ratings_after_gameweek(results)
        
        print("\nNew ratings (after update):")
        for team, rating in sorted(CURRENT_RATINGS.items(), key=lambda x: x[1], reverse=True):
            print(f"  {team}: {rating:.2f}")
        
        print("\n✅ Ratings updated successfully!")
        print("Remember to update the CURRENT_RATINGS in main.py with these new values")
        
    except FileNotFoundError:
        print(f"Error: Results file '{sys.argv[1]}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in results file")
        sys.exit(1)

if __name__ == "__main__":
    main()
