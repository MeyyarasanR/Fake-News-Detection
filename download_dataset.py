import os
import sys
import urllib.request
import csv

# Target files
DATASET_DIR = "dataset"
FAKE_CSV_PATH = os.path.join(DATASET_DIR, "Fake.csv")
TRUE_CSV_PATH = os.path.join(DATASET_DIR, "True.csv")

# Mirror URLs for fallback download
FAKE_URLS = [
    "https://raw.githubusercontent.com/hosseindamavandi/Fake-News-Detection/main/Fake.csv",
    "https://raw.githubusercontent.com/taeefnajib/Fake-News-Detection-Using-Naive-Bayes/master/Fake.csv",
    "https://raw.githubusercontent.com/Reinforz/Fake-News-detection-with-ISOT-Dataset/main/Fake.csv",
    "https://raw.githubusercontent.com/adefemiadeh/Fake-News-Detection/main/fake.csv"
]

TRUE_URLS = [
    "https://raw.githubusercontent.com/hosseindamavandi/Fake-News-Detection/main/True.csv",
    "https://raw.githubusercontent.com/taeefnajib/Fake-News-Detection-Using-Naive-Bayes/master/True.csv",
    "https://raw.githubusercontent.com/Reinforz/Fake-News-detection-with-ISOT-Dataset/main/True.csv",
    "https://raw.githubusercontent.com/adefemiadeh/Fake-News-Detection/main/true.csv"
]

def download_file(urls, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000000:
        print(f"[OK] {dest_path} already exists and is not empty. Skipping download.")
        return True
        
    print(f"Downloading to {dest_path}...")
    for url in urls:
        try:
            print(f"Trying URL: {url}")
            # Use a User-Agent to avoid getting blocked by GitHub raw endpoint if needed
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response, open(dest_path, 'wb') as out_file:
                # Read in chunks and show progress
                meta = response.info()
                content_length = meta.get("Content-Length")
                total_size = int(content_length) if content_length else None
                
                downloaded = 0
                chunk_size = 1024 * 256  # 256KB
                
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    downloaded += len(chunk)
                    out_file.write(chunk)
                    
                    if total_size:
                        percent = (downloaded / total_size) * 100
                        sys.stdout.write(f"\rProgress: {percent:.1f}% ({downloaded}/{total_size} bytes)")
                        sys.stdout.flush()
                    else:
                        sys.stdout.write(f"\rProgress: {downloaded} bytes downloaded")
                        sys.stdout.flush()
                print()
            print(f"[SUCCESS] Downloaded to {dest_path}")
            return True
        except Exception as e:
            print(f"\n[ERROR] Failed to download from {url}: {e}")
            if os.path.exists(dest_path):
                os.remove(dest_path)
            continue
            
    print(f"[CRITICAL] All URLs failed for {dest_path}")
    return False

def validate_csv(file_path):
    print(f"Validating {file_path}...")
    if not os.path.exists(file_path):
        print(f"[FAIL] File {file_path} does not exist.")
        return False
        
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"File size: {size_mb:.2f} MB")
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            header = next(reader)
            print(f"Header: {header}")
            
            # Count rows
            row_count = 0
            for _ in reader:
                row_count += 1
                
            print(f"Row count (excluding header): {row_count}")
            
            # Simple validation on expected columns for ISOT dataset
            expected_columns = {"title", "text", "subject", "date"}
            header_lower = [h.strip().lower() for h in header]
            if not expected_columns.issubset(set(header_lower)):
                print(f"[WARNING] Header columns {header_lower} do not contain all expected columns {expected_columns}")
            else:
                print(f"[OK] Header structure matches expected columns.")
                
            if row_count < 10000:
                print(f"[FAIL] Row count ({row_count}) is unusually small for this dataset (expected >10,000 rows).")
                return False
                
            print(f"[OK] Validation passed for {file_path}")
            return True
    except Exception as e:
        print(f"[FAIL] Error validating CSV file {file_path}: {e}")
        return False

def main():
    print("Starting Fake News Dataset setup...")
    fake_success = download_file(FAKE_URLS, FAKE_CSV_PATH)
    true_success = download_file(TRUE_URLS, TRUE_CSV_PATH)
    
    if not (fake_success and true_success):
        print("\n[CRITICAL] Setup failed. One or more files could not be downloaded.")
        sys.exit(1)
        
    print("\nValidating downloaded files...")
    fake_valid = validate_csv(FAKE_CSV_PATH)
    true_valid = validate_csv(TRUE_CSV_PATH)
    
    if fake_valid and true_valid:
        print("\n[SUCCESS] Dataset successfully set up and validated!")
    else:
        print("\n[WARNING] Dataset validation failed. Please check the logs.")
        sys.exit(1)

if __name__ == "__main__":
    main()
