import os
import gdown

FOLDER_URL = "https://drive.google.com/drive/folders/1TGEc66YKbD443nslRi1bWgVd238gJCnb"
OUTPUT_DIR = r"C:\Users\rattu\Downloads\Target SQL\data"

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Downloading all files from:\n  {FOLDER_URL}")
    print(f"Saving into:\n  {OUTPUT_DIR}\n")

    # Download every file from the Drive folder
    gdown.download_folder(
        url=FOLDER_URL,
        output=OUTPUT_DIR,
        quiet=False,
        use_cookies=False,
    )

    # Keep only CSVs
    kept, removed = [], []
    for fname in os.listdir(OUTPUT_DIR):
        full_path = os.path.join(OUTPUT_DIR, fname)
        if os.path.isfile(full_path):
            if fname.lower().endswith(".csv"):
                kept.append(fname)
            else:
                os.remove(full_path)
                removed.append(fname)

    print("\nCSV files downloaded:")
    for k in kept:
        print("  -", k)

    if removed:
        print("\nNon-CSV files removed:")
        for r in removed:
            print("  -", r)

if __name__ == "__main__":
    main()