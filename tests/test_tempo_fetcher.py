import os
import shutil
import sys
import pytest
from datetime import datetime, timedelta
from dateutil.parser import parse

# Get the path to the 'src' directory (relative to this test file)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')

# Add the 'src' directory to the Python path
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Now, the import should work because 'src' is on the path.
# Note: Since 'src' is on the path, we import 'tempo_fetcher' directly.
from backend.src.data_ingestion.tempo_fetcher import TEMPOFetcher, DOWNLOAD_DIR, TEMPO_NO2_SHORT_NAME

# --- Pytest Fixtures and Setup/Teardown ---

@pytest.fixture(scope="session")
def fetcher_instance():
    """
    Fixture to initialize the TEMPOFetcher once per test session.
    This will trigger the earthaccess login, which is often slow.
    """
    print("\n--- Running earthaccess.login() ---")
    try:
        # PULL CREDENTIALS DIRECTLY FROM THE ENVIRONMENT
        user = os.getenv("EARTHDATA_USERNAME")
        pw = os.getenv("EARTHDATA_PASSWORD")

        if not user or not pw:
             pytest.fail("EARTHDATA_USERNAME or EARTHDATA_PASSWORD not found in environment. Check your .env file.")

        # PASS CREDENTIALS TO THE MODIFIED TEMPOFETCHER
        fetcher = TEMPOFetcher(username=user, password=pw)
        return fetcher
    except Exception as e:
        # Check for authentication failure messages if needed
        pytest.fail(f"earthaccess login failed. Ensure credentials are valid: {e}")

@pytest.fixture(scope="function", autouse=True)
def cleanup_download_dir():
    """
    Fixture to ensure the download directory is clean before and after each test.
    This is crucial for integration tests that write to the filesystem.
    """
    # Teardown: Cleanup after the test runs
    yield
    if os.path.exists(DOWNLOAD_DIR):
        print(f"\n--- Cleaning up {DOWNLOAD_DIR} directory ---")
        shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)

# --- Test Parameters for a Small, Stable Dataset ---

# TEMPO is a new, geostationary mission. 
# We need to find the smallest, most stable time/space slice for testing.
# A small time slice over a small, stable area is best.

# Using a recent, very small time range to limit the number of granules
TEST_END_DATE = datetime.now().date() 
TEST_START_DATE = TEST_END_DATE - timedelta(days=1)

# A small bounding box over a stable land area (e.g., eastern USA)
# The bounding box is (min_lon, min_lat, max_lon, max_lat)
TEST_BBOX = (-80, 30, -70, 40) # A small box over the Atlantic/Eastern US

# --- Integration Tests ---

def test_fetch_data_successfully_downloads_files(fetcher_instance: TEMPOFetcher):
    """
    End-to-end test to ensure data is searched, found, and actually downloaded.
    
    This is the core functional test.
    """
    print(f"\nTargeting short_name: {TEMPO_NO2_SHORT_NAME}")
    print(f"Time range: {TEST_START_DATE} to {TEST_END_DATE}")
    print(f"BBox: {TEST_BBOX}")

    # ACT: Run the data fetcher
    result = fetcher_instance.fetch_data(
        start_date=parse(str(TEST_START_DATE)), # Convert to datetime
        end_date=parse(str(TEST_END_DATE)), 
        bbox=TEST_BBOX
    )

    # ASSERT 1: Check the overall result status
    assert result is not None
    assert result.get("status") == "success", f"Fetch failed: {result.get('message')}"
    
    # ASSERT 2: Check if files were downloaded
    downloaded_files = result.get("files", [])
    
    # We expect to download at least one file, but zero is acceptable if the 
    # specific test time/bbox is empty. A failure here is 
    # 'Did not find the files' or 'Download failed'.
    if 'No granules found' in result.get('message', ''):
        print("INFO: No granules found for the test criteria, skipping file assertions.")
        return # Skip remaining file checks if search was legitimately empty
        
    assert downloaded_files, "Expected to find and download at least one file, but found none."
    assert len(downloaded_files) > 0, f"Expected > 0 files, but downloaded {len(downloaded_files)}."
    
    # ASSERT 3: Check filesystem integrity
    assert os.path.exists(DOWNLOAD_DIR), f"Download directory {DOWNLOAD_DIR} was not created."
    
    # Check that the files are in the expected directory and are not zero-byte files
    for filepath in downloaded_files:
        assert os.path.exists(filepath), f"Downloaded file does not exist on disk: {filepath}"
        assert os.path.getsize(filepath) > 1000, f"Downloaded file is too small (possibly empty/corrupt): {filepath}"
        print(f"Successfully verified downloaded file: {filepath} ({os.path.getsize(filepath)} bytes)")


def test_fetch_data_with_invalid_dates(fetcher_instance: TEMPOFetcher):
    """
    Test that the internal validation logic is working correctly (Negative Test).
    """
    start_date = datetime.now()
    end_date = start_date - timedelta(days=5) # end_date is before start_date

    # ACT & ASSERT
    with pytest.raises(ValueError, match="end_date must be after start_date"):
        fetcher_instance.fetch_data(start_date, end_date)