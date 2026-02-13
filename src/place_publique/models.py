from ultralytics import YOLO
from ultralytics import RTDETR

def load_model(model_name="yolo11x.pt"):
    """Load the specified model based on the model name.
     Args:
         model_name: Name of the model file to load
     Returns:
         Loaded model object
     """
    print("Chargement du modèle...")
    if model_name.startswith("yolo") or model_name.endswith(".pt"):
        model = YOLO(model_name)
    elif model_name.startswith("rtdetr"):
        model = RTDETR(model_name)
    else:
        raise ValueError(f"Unsupported model identifier: {model_name}")

    return model
 
