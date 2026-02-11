import os
import sys
import zipfile
import requests
from pathlib import Path
from dotenv import load_dotenv
from ultralytics import YOLO

# chargement des variables d'environnement
load_dotenv()

def main():
    if len(sys.argv) < 2:
        print("usage: python setup_and_train.py <dataset_name>")
        sys.exit(1)

    dataset_name = sys.argv[1]
    model_name = "yolov8n.pt"
    dest_dir = Path(f"datasets/{dataset_name}")

    # vérification du répertoire
    if dest_dir.exists():
        print(f"{dest_dir} already created")
        return

    dest_dir.mkdir(parents=True, exist_ok=True)

    # récupération des variables
    host = os.getenv("ROBOFLOW_HOST")
    ds_id = os.getenv("ROBOFLOW_DATASET")
    api_key = os.getenv("ROBOFLOW_API_KEY")
    url = f"https://{host}/ds/{ds_id}?key={api_key}"
    print(url)

    # téléchargement du dataset
    zip_path = Path("roboflow.zip")
    print(f"downloading dataset from {host}...")
    response = requests.get(url, stream=True)
    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # extraction
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(dest_dir)
    zip_path.unlink()

    # modification du fichier data.yaml (équivalent sed)
    yaml_path = dest_dir / "data.yaml"
    if yaml_path.exists():
        content = yaml_path.read_text()
        content = content.replace("train: ..", "train: .")
        content = content.replace("val: ..", "val: .")
        content = content.replace("test: ..", "test: .")
        yaml_path.write_text(content)

    # entraînement avec yolo
    model = YOLO(model_name)
    model.train(
        data=str(yaml_path),
        task="detect",
        epochs=3
    )

if __name__ == "__main__":
    main()