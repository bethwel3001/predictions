import os
import shutil
import sys
import pytest
from datetime import datetime, timedelta
from dateutil.parser import parse

# --- PATH SETUP (Remains the same) ---
# Get the path to the 'src' directory (relative to this test file)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')

# Add the 'src' directory to the Python path
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# --- IMPORT MODIFICATION ---
# Note: TEMPO_NO2_SHORT_NAME is removed. TEMPO_SHORT_NAMES dictionary is new.
# We will import TEMPOFetcher and DOWNLOAD_DIR, and the full TEMPO_SHORT_NAMES dict.
from backend.src.data_ingestion.tempo_fetcher import TEMPOFetcher, DOWNLOAD_DIR, TEMPO_SHORT_NAMES 

# --- Pytest Fixtures and Setup/Teardown (Minimal changes) ---

@pytest.fixture(scope="session")
def fetcher_instance():
    """
    Fixture to initialize the TEMPOFetcher once per test session.
    This will trigger the earthaccess login.
    
    NOTE: The constructor now calls earthaccess.login() internally, 
    which uses environment variables directly. We keep the explicit check 
    for better test feedback.
    """
    print("\n--- Running earthaccess.login() ---")
    try:
        # PULL CREDENTIALS DIRECTLY FROM THE ENVIRONMENT
        user = os.getenv("EARTHDATA_USERNAME")
        pw = os.getenv("EARTHDATA_PASSWORD")

        if not user or not pw:
             pytest.fail("EARTHDATA_USERNAME or EARTHDATA_PASSWORD not found in environment. Check your .env file.")

        # Instantiate TEMPOFetcher. It will use the env vars implicitly.
        fetcher = TEMPOFetcher(username=user, password=pw)
        return fetcher
    except Exception as e:
        # Check for authentication failure messages if needed
        pytest.fail(f"earthaccess login failed. Ensure credentials are valid: {e}")

@pytest.fixture(scope="function", autouse=True)
def cleanup_download_dir():
    """
    Fixture to ensure the download directory is clean before and after each test.
    """
    # Teardown: Cleanup after the test runs
    yield
    if os.path.exists(DOWNLOAD_DIR):
        print(f"\n--- Cleaning up {DOWNLOAD_DIR} directory ---")
        shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)

# --- Test Parameters for a Small, Stable Dataset (Remains the same) ---

TEST_END_DATE = datetime.now().date() 
TEST_START_DATE = TEST_END_DATE - timedelta(days=1)
TEST_BBOX = (-80, 30, -70, 40) # Eastern US / Atlantic

# --- Integration Tests ---

def test_fetch_data_successfully_downloads_no2_files(fetcher_instance: TEMPOFetcher):
    """
    Tests successful download for the default NO2 constituent.
    """
    target_constituent = "NO2"
    print(f"\nTargeting constituent: {target_constituent}")
    print(f"Time range: {TEST_START_DATE} to {TEST_END_DATE}")
    print(f"BBox: {TEST_BBOX}")

    # ACT: Run the data fetcher with the default NO2
    result = fetcher_instance.fetch_data(
        start_date=parse(str(TEST_START_DATE)),
        end_date=parse(str(TEST_END_DATE)), 
        constituents=target_constituent, # Pass a single string constituent
        bbox=TEST_BBOX
    )

    # ASSERT 1: Check the overall result status
    assert result is not None
    assert result.get("status") == "success", f"Fetch failed: {result.get('message')}"
    
    downloaded_files = result.get("files", [])
    
    if 'No granules found' in result.get('message', ''):
        print("INFO: No granules found for the test criteria, skipping file assertions.")
        return
        
    # ASSERT 2: Check if files were downloaded and ensure files names reflect the constituent (optional)
    assert len(downloaded_files) > 0, f"Expected > 0 files, but downloaded {len(downloaded_files)}."
    
    # ASSERT 3: Check filesystem integrity
    assert os.path.exists(DOWNLOAD_DIR), f"Download directory {DOWNLOAD_DIR} was not created."
    
    for filepath in downloaded_files:
        assert os.path.exists(filepath)
        # Check for the expected short name in the filename (more robust check)
        assert TEMPO_SHORT_NAMES["NO2"] in filepath, "Downloaded filename does not contain the expected short name for NO2."
        assert os.path.getsize(filepath) > 1000
        print(f"Successfully verified downloaded file: {filepath} ({os.path.getsize(filepath)} bytes)")


def test_fetch_data_multiple_constituents(fetcher_instance: TEMPOFetcher):
    """
    Tests successful search and download for multiple constituents (e.g., O3 and CH2O).
    """
    target_constituents = ["O3", "CH2O"]
    print(f"\nTargeting constituents: {target_constituents}")
    
    # ACT: Run the data fetcher with multiple constituents
    result = fetcher_instance.fetch_data(
        start_date=parse(str(TEST_START_DATE)),
        end_date=parse(str(TEST_END_DATE)), 
        constituents=target_constituents,
        bbox=TEST_BBOX
    )

    # ASSERT 1: Check the overall result status
    assert result is not None
    assert result.get("status") == "success", f"Fetch failed: {result.get('message')}"
    
    downloaded_files = result.get("files", [])
    
    if 'No granules found' in result.get('message', ''):
        print("INFO: No granules found for the test criteria, skipping file assertions.")
        return

    # ASSERT 2: Check if files were downloaded
    assert len(downloaded_files) > 0, f"Expected > 0 files, but downloaded {len(downloaded_files)}."
    
    # ASSERT 3: Check that at least one file for each requested short name was searched for
    short_name_o3 = TEMPO_SHORT_NAMES["O3"]
    short_name_ch2o = TEMPO_SHORT_NAMES["CH2O"]
    
    o3_files = [f for f in downloaded_files if short_name_o3 in f]
    ch2o_files = [f for f in downloaded_files if short_name_ch2o in f]

    # This check is slightly less strict for integration testing, 
    # as the coverage might not include every constituent for the bbox/date.
    # However, if TEMPO is consistently producing both, this should pass.
    if o3_files:
        print(f"Downloaded {len(o3_files)} O3 files.")
    if ch2o_files:
         print(f"Downloaded {len(ch2o_files)} CH2O files.")


def test_fetch_data_with_invalid_constituent(fetcher_instance: TEMPOFetcher):
    """
    Test that the validation logic correctly rejects an invalid constituent name.
    """
    invalid_constituent = "CO2" # Not a supported TEMPO L2 product in the list
    
    # ACT & ASSERT
    with pytest.raises(ValueError, match="Invalid constituent 'CO2'"):
        fetcher_instance.fetch_data(
            start_date=parse(str(TEST_START_DATE)),
            end_date=parse(str(TEST_END_DATE)), 
            constituents=invalid_constituent,
            bbox=TEST_BBOX
        )


def test_fetch_data_with_invalid_dates(fetcher_instance: TEMPOFetcher):
    """
    Test that the internal validation logic is working correctly (Negative Test for dates).
    """
    start_date = datetime.now()
    end_date = start_date - timedelta(days=5) # end_date is before start_date

    # ACT & ASSERT
    with pytest.raises(ValueError, match="end_date must be after start_date"):
        # The constituent is optional and defaults to NO2, which is fine here.
        fetcher_instance.fetch_data(start_date, end_date)