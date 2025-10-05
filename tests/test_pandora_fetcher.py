# test_pandora_fetcher.py

import sys
import os


import pytest
import shutil
from datetime import datetime, timedelta
# Now this import will work because the project root has been added to sys.path
from pandora_fetcher import PandoraFetcher, PGN_COLLECTION_SHORTNAME, EXAMPLE_INSTRUMENT_ID

# --- Configuration for the Functional Test ---
TEST_DOWNLOAD_DIR = "pandora_test_download"
TEST_SITE_ID = "athens"
TEST_PRODUCT = "NO2" 
# ... (rest of the file remains the same) ...

# -------------------------------------------------------------------
# The rest of the content is the functional test you previously received.
# You only need to add the three lines above.
# -------------------------------------------------------------------

def skip_if_no_credentials():
    """Skips the test if the required environment variables are not set."""
    # ... (content remains the same) ...
    username = os.getenv("EARTHDATA_USERNAME")
    password = os.getenv("EARTHDATA_PASSWORD")
    if not username or not password:
        pytest.skip(
            "Skipping functional test: EARTHDATA_USERNAME and/or EARTHDATA_PASSWORD "
            "environment variables are not set. Set them to run this test."
        )

@pytest.fixture(scope="module")
def fetcher_instance():
    """
    Fixture to initialize the PandoraFetcher and handle cleanup of the test directory.
    This runs authentication once per test module.
    """
    end_dt = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
    start_dt = end_dt - timedelta(hours=3)
    
    skip_if_no_credentials()
    
    fetcher = None
    try:
        # The __init__ will attempt to log in using environment variables
        fetcher = PandoraFetcher()
    except Exception as e:
        pytest.fail(f"Failed to initialize PandoraFetcher (Authentication error): {e}")

    fetcher.test_download_path = TEST_DOWNLOAD_DIR
    if os.path.exists(fetcher.test_download_path):
        shutil.rmtree(fetcher.test_download_path)

    yield fetcher

    # 2. Teardown: Clean up the downloaded files and directory
    print(f"\n--- Starting Teardown: Cleaning up {TEST_DOWNLOAD_DIR} ---")
    if os.path.exists(fetcher.test_download_path):
        shutil.rmtree(fetcher.test_download_path)
        print("Cleanup successful.")

# --- Functional Test Cases ---

def test_01_authentication_success(fetcher_instance):
    """
    Ensures the fixture successfully authenticated (checked in the fixture itself)
    """
    assert isinstance(fetcher_instance, PandoraFetcher)
    print("Test 01: Authentication successful.")


def test_02_fetch_site_data_real_download(fetcher_instance):
    """
    Tests the core data fetching functionality, including search and download.
    """
    
    # Use a fixed, recent date range to maximize the chance of finding a single granule
    end_date = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0) - timedelta(days=1)
    start_date = end_date - timedelta(hours=3) # Search a 3-hour window from yesterday

    print(f"Searching for Pandora data from {start_date.isoformat()} to {end_date.isoformat()}")

    # Act: Call the method that executes the earthaccess search and download
    result = fetcher_instance.fetch_site_data(
        site_id=TEST_SITE_ID,
        product=TEST_PRODUCT,
        start_date=start_date,
        end_date=end_date,
        instrument_id=EXAMPLE_INSTRUMENT_ID # Critical for targeted PGN search
    )
    
    # Assert 1: Check the overall status
    assert result['status'].startswith('SUCCESS'), f"Expected SUCCESS, but got {result['status']}: {result.get('message', 'No message')}"
    
    # Assert 2: Check if files were downloaded and if the count is reasonable
    downloaded_files = result.get('files_downloaded', [])
    file_count = result.get('files_count', 0)
    
    assert file_count >= 0, "File count should be zero or greater."
    
    if file_count == 0:
        assert result['status'] == 'SUCCESS_NO_DATA_FOUND'
        print("Test 02: Search successful, but no data found in the narrow time window.")
        return 
        
    # Assert 3: If files were found, check the physical download
    assert file_count == len(downloaded_files), "Count mismatch between reported count and downloaded list."
    
    # Assert 4: Check that the downloaded file exists and is not zero-size
    first_file_path = downloaded_files[0]
    
    assert os.path.exists(first_file_path), f"Downloaded file does not exist at expected path: {first_file_path}"
    
    file_size_bytes = os.path.getsize(first_file_path)
    MIN_EXPECTED_SIZE_KB = 50 
    assert file_size_bytes > MIN_EXPECTED_SIZE_KB * 1024, f"Downloaded file is too small ({file_size_bytes} bytes). Expected > {MIN_EXPECTED_SIZE_KB} KB, suggesting a failed transfer or empty file."
    
    print(f"Test 02: Successfully downloaded {file_count} file(s) with size {file_size_bytes / 1024:.2f} KB.")