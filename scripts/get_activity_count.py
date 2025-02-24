#!/usr/bin/env python3
"""
Uses garminconnect library to efficiently count activities
"""

import argparse
import sys
import json
from garminconnect import Garmin

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--activity", default="running", help="Activity type")
    parser.add_argument("--email", required=True, help="Garmin Connect email")
    parser.add_argument("--password", required=True, help="Garmin Connect password")
    
    args = parser.parse_args()

    try:
        # Initialize the Garmin Connect client
        client = Garmin(args.email, args.password)
        client.login()

        # Get activities for the date range
        activities = client.get_activities_by_date(args.start, args.end, args.activity)
        
        # Simply return the count
        print(json.dumps({"count": len(activities)}))
        
    except Exception as e:
        print(f"Error getting activity count: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 