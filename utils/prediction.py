import joblib
import tensorflow as tf


# Load models
leaf_classifier = joblib.load("models/leaf_classifier.pkl")
disease_model = joblib.load("models/coffee_disease_model.pkl")
nutrition_model = tf.keras.models.load_model("models/trained_nutrition_model.keras")

from utils.preprocessing import preprocess_image, extract_features_for_leaf_classifier, prepare_for_nn, extract_features_for_disease_model


DISEASE_LABELS = {
    0: "Healthy",
    1: "Rust Leaves",
    2: "Phoma"
}

NUTRIENT_LABELS = {
    0: "Boron Deficiency",
    1: "Calcium Deficiency",
    2: "Healthy",
    3: "Iron Deficiency",
    4: "Magnesium Deficiency",
    5: "Manganese Deficiency",
    6: "Nitrogen Deficiency",
    7: "Phosphoras Deficiency",
    8: 'Potassium'
}

def is_leaf(image):
    features = extract_features_for_leaf_classifier(image)
    return leaf_classifier.predict([features])[0]

def get_disease(image):
    features = extract_features_for_disease_model(image)
    prediction = disease_model.predict([features])[0]
    return DISEASE_LABELS.get(prediction, "Unknown")

def get_nutrient_deficiency(image):
    img_array = prepare_for_nn(image)
    img_array = img_array.reshape(1, 128, 128, 3)  # Match model input
    prediction = nutrition_model.predict(img_array).argmax()
    return NUTRIENT_LABELS.get(prediction, "Unknown")

