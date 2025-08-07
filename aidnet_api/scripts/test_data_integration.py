import os
import sys
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aidnet_api.utils import fetch_acled_data, fetch_reliefweb_data

# Load environment variables
load_dotenv()

def test_acled_integration():
    # Get credentials from environment variables
    email = os.getenv('ACLED_EMAIL')
    api_key = os.getenv('ACLED_API_KEY')
    
    if not email or not api_key:
        print("Error: ACLED credentials not found in environment variables")
        print("Please set ACLED_EMAIL and ACLED_API_KEY in .env file")
        return
    
    # Set date range for last 30 days
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Test countries
    countries = ['Syria', 'Yemen', 'South Sudan']
    
    print("\nFetching ACLED conflict data...")
    df = fetch_acled_data(email, api_key, start_date, end_date, countries)
    
    if not df.empty:
        print(f"Successfully retrieved {len(df)} conflict events")
        print("\nSample data:")
        print(df.head())
    else:
        print("No data retrieved from ACLED")

def test_reliefweb_integration():
    # Test country
    country = 'Syria'
    
    print("\nFetching ReliefWeb reports...")
    reports = fetch_reliefweb_data(country)
    
    if reports:
        print(f"Successfully retrieved {len(reports)} reports")
        print("\nRecent reports:")
        for report in reports[:3]:  # Show first 3 reports
            print(f"- {report['fields']['title']}")
    else:
        print("No reports retrieved from ReliefWeb")

def main():
    print("Testing data integration functions...")
    
    test_acled_integration()
    test_reliefweb_integration()

if __name__ == '__main__':
    main()