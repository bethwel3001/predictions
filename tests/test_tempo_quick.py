#!/usr/bin/env python3
"""
Quick test script for TEMPO fetcher
This will test  NASA Earthdata credentials and fetch a small amount of TEMPO data
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path (go up one level from tests/ to root, then to backend/src)
sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / "src"))

from data_ingestion.tempo_fetcher import TEMPOFetcher

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_credentials():
    """Test if NASA Earthdata credentials are set"""
    print("\n" + "="*60)
    print("STEP 1: Checking NASA Earthdata Credentials")
    print("="*60)
    
    username = os.getenv("NASA_EARTHDATA_USERNAME") or os.getenv("EARTHDATA_USERNAME")
    password = os.getenv("NASA_EARTHDATA_PASSWORD") or os.getenv("EARTHDATA_PASSWORD")
    
    if not username or not password:
        print("❌ ERROR: NASA Earthdata credentials not found!")
        print("\nPlease set your credentials in .env file:")
        print("  NASA_EARTHDATA_USERNAME=your_username")
        print("  NASA_EARTHDATA_PASSWORD=your_password")
        print("\nOr export them as environment variables:")
        print("  export EARTHDATA_USERNAME=your_username")
        print("  export EARTHDATA_PASSWORD=your_password")
        return False
    
    print(f"✅ Username found: {username}")
    print(f"✅ Password found: {'*' * len(password)}")
    return True

def test_tempo_fetcher():
    """Test TEMPO fetcher with small dataset"""
    print("\n" + "="*60)
    print("STEP 2: Initializing TEMPO Fetcher")
    print("="*60)
    
    try:
        # Initialize fetcher (this will attempt login)
        fetcher = TEMPOFetcher()
        print("✅ TEMPO Fetcher initialized successfully!")
        print("✅ NASA Earthdata authentication successful!")
        
    except Exception as e:
        print(f"❌ Failed to initialize TEMPO fetcher: {e}")
        print("\nPossible issues:")
        print("  1. Invalid credentials")
        print("  2. Network connection issue")
        print("  3. NASA Earthdata service unavailable")
        return None
    
    print("\n" + "="*60)
    print("STEP 3: Fetching TEMPO Data (Small Test)")
    print("="*60)
    
    # Use recent dates for testing
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=1)
    
    # Small bounding box for Los Angeles area
    la_bbox = (-118.5, 33.5, -117.5, 34.5)
    
    print(f"\nTest Parameters:")
    print(f"  Date Range: {start_date} to {end_date}")
    print(f"  Location: Los Angeles area")
    print(f"  Bounding Box: {la_bbox}")
    print(f"  Constituent: NO2 (Nitrogen Dioxide)")
    print("\nThis will search for and download TEMPO satellite data...")
    print("(This may take 30-60 seconds depending on data availability)\n")
    
    try:
        result = fetcher.fetch_data(
            start_date=datetime.combine(start_date, datetime.min.time()),
            end_date=datetime.combine(end_date, datetime.min.time()),
            constituents="NO2",
            bbox=la_bbox
        )
        
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        
        files = result.get('files', [])
        if files:
            print(f"\n✅ Downloaded {len(files)} file(s):")
            for i, filepath in enumerate(files, 1):
                file_size = os.path.getsize(filepath) / (1024 * 1024)  # Convert to MB
                print(f"  {i}. {os.path.basename(filepath)} ({file_size:.2f} MB)")
            print(f"\nFiles saved to: tempo_data_downloads/")
        else:
            print("\nℹ️  No files downloaded (may be no data available for this date/location)")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error fetching TEMPO data: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_multiple_constituents():
    """Test fetching multiple air quality constituents"""
    print("\n" + "="*60)
    print("STEP 4: Testing Multiple Constituents (OPTIONAL)")
    print("="*60)
    
    response = input("\nWould you like to test fetching multiple constituents? (y/n): ")
    if response.lower() != 'y':
        print("Skipping multiple constituent test.")
        return
    
    try:
        fetcher = TEMPOFetcher()
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=1)
        la_bbox = (-118.5, 33.5, -117.5, 34.5)
        
        print("\nFetching NO2, O3 (Ozone), and CH2O (Formaldehyde)...")
        
        result = fetcher.fetch_data(
            start_date=datetime.combine(start_date, datetime.min.time()),
            end_date=datetime.combine(end_date, datetime.min.time()),
            constituents=["NO2", "O3", "CH2O"],
            bbox=la_bbox
        )
        
        print(f"\n✅ Result: {result.get('message')}")
        files = result.get('files', [])
        if files:
            print(f"Downloaded {len(files)} total file(s)")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main test function"""
    print("\n" + "🛰️ "*15)
    print(" "*10 + "NASA TEMPO SATELLITE DATA FETCHER TEST")
    print("🛰️ "*15 + "\n")
    
    # Step 1: Check credentials
    if not test_credentials():
        sys.exit(1)
    
    # Step 2 & 3: Test fetcher
    result = test_tempo_fetcher()
    
    if result and result.get('status') == 'success':
        # Step 4: Optional multiple constituent test
        test_multiple_constituents()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\n✅ If you see data downloaded above, your TEMPO integration is working!")
    print("✅ You can now use this in your FastAPI endpoints.\n")

if __name__ == "__main__":
    main()
