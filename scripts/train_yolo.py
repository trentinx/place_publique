import os
import sys
import zipfile
import requests
from pathlib import Path
from dotenv import load_dotenv
from ultralytics import YOLO, settings
import mlflow

# chargement des variables d'environnement
load_dotenv()

#mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
#mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME"))

def main(trial_name, model_name, dataset_name):        
    dest_dir = Path(f"datasets/{dataset_name}")
    # récupération des variables
    host = os.getenv("ROBOFLOW_HOST")
    ds_id = os.getenv("ROBOFLOW_DATASET")
    api_key = os.getenv("ROBOFLOW_API_KEY")
    url = f"https://{host}/ds/{ds_id}?key={api_key}"
    # vérification du répertoire
    if dest_dir.exists():
        print(f"{dest_dir} already created")
    else:
        dest_dir.mkdir(parents=True, exist_ok=True)            
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
    
    if "26" in model_name:
        model = YOLO()
        model.load(model_name)
    else:
        model = YOLO(model_name)
    mlflow.set_tracking_uri("file://" + str(Path.cwd() / "mlruns"))
    mlflow.set_experiment("yolo_training")  
    with mlflow.start_run(run_name=trial_name):
        mlflow.autolog()
        mlflow.set_tag("model", model_name)
        mlflow.log_param("dataset", url)
        model.train(
            data=str(yaml_path),
            task="detect",
            epochs=100,
            name=trial_name,
            device=0,
            batch=8
        )


if __name__ == "__main__": 
        
    if len(sys.argv) < 3:
        print("usage: python train.py <trial_name> <dataset_name>")
        sys.exit(1)

    trial_name = sys.argv[1]
    dataset_name = sys.argv[2]
    model_name = "yolov8n.pt"
    model_name = "yolo11l.pt"
    #model_name = "weights/yolo26x.pt"
    
    # Update a setting
    settings.update({"mlflow": True})
    main(trial_name, model_name, dataset_name)