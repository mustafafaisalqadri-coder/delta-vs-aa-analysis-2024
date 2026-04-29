import zipfile
from pathlib import Path

import pandas as pd


def main() -> None:
    project_dir = Path(__file__).parent
    zip_path = project_dir / "flight_data.zip"
    extract_dir = project_dir / "flight_data_unzipped"

    if not zip_path.exists():
        raise FileNotFoundError(f"Could not find zip file at: {zip_path}")

    extract_dir.mkdir(exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
        csv_files = [name for name in zip_ref.namelist() if name.lower().endswith(".csv")]

    if not csv_files:
        raise FileNotFoundError("No CSV file found inside flight_data.zip")

    csv_path = extract_dir / csv_files[0]
    df = pd.read_csv(csv_path)

    print("First 5 rows:")
    print(df.head(5))
    print("\nColumn names:")
    print(list(df.columns))
    print(f"\nTotal rows: {len(df)}")


if __name__ == "__main__":
    main()
