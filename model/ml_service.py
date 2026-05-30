import json
import os
import time

import numpy as np
import redis
import settings
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import decode_predictions, preprocess_input
from tensorflow.keras.preprocessing import image

db = redis.Redis(
    host=settings.REDIS_IP, port=settings.REDIS_PORT, db=settings.REDIS_DB_ID
)

model = ResNet50(include_top=True, weights="imagenet")


def predict(image_name):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.

    Returns
    -------
    class_name, pred_probability : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
    class_name = None
    pred_probability = None
    # Load image
    image_path = os.path.join(settings.UPLOAD_FOLDER, image_name)
    # Apply preprocessing (convert to numpy array, match model input dimensions (including batch) and use the resnet50 preprocessing)
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    # Get predictions using model methods and decode predictions using resnet50 decode_predictions
    predictions = model.predict(img_array)
    _, class_name, pred_probability = decode_predictions(predictions, top=1)[0][0]

    # Convert probabilities to float and round it
    pred_probability = round(float(pred_probability), 4)

    return class_name, pred_probability


def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """
    while True:
        # Take a new job from Redis
        new_job = db.brpop(settings.REDIS_QUEUE)[1]
        # Decode the JSON data for the given job
        job = json.loads(
            new_job
        )  # Cargamos un archivo json como un objeto (diccionario/lista)
        image_name = job["image_name"]
        job_id = job["id"]
        # Run the loaded ml model (use the predict() function)
        predicted_class, score = predict(image_name)
        # Prepare a new JSON with the results
        output = {"prediction": predicted_class, "score": score}

        # Store the job results on Redis using the original
        # job ID as the key
        db.set(job_id, json.dumps(output))
        # Sleep for a bit
        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()
