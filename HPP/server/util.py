import pickle
import json
import pandas as pd
from typing import List
import os

__model = None
__scaler = None
__categorical_columns = None
__columns = None

def load_saved_artifacts() -> None:
    """Load all saved model artifacts with proper error handling."""
    print("Loading saved artifacts...start")
    global __model, __scaler, __categorical_columns, __columns
    
    try:
        # Define file paths
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        model_path = os.path.join(BASE_DIR, "artifacts", "housing_price_model.pickle")
        scaler_path = os.path.join(BASE_DIR, "artifacts", "scaler.pickle")
        columns_path = os.path.join(BASE_DIR, "artifacts", "columns.json")
        categorical_path = os.path.join(BASE_DIR, "artifacts", "categorical_columns.json")

        
        # Check if all files exist
        for name, path in [("model", model_path), ("scaler", scaler_path), 
                          ("columns", columns_path), ("categorical columns", categorical_path)]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"{name} file not found: {path}")

        # Load pickle files
        with open(model_path, "rb") as f:
            __model = pickle.load(f)
        with open(scaler_path, "rb") as f:
            __scaler = pickle.load(f)

        # Load JSON files
        with open(columns_path, "r", encoding="utf-8") as f:
            __columns = json.load(f)
        with open(categorical_path, "r", encoding="utf-8") as f:
            __categorical_columns = json.load(f)

        print("Loading saved artifacts...done")
        print(f"Loaded {len(__columns)} total columns, {len(__categorical_columns)} categorical")
        
    except Exception as e:
        print(f"Error loading artifacts: {e}")
        raise

def get_estimated_price(input_features: List) -> float:
    """
    Predict housing price from input features.
    
    Args:
        input_features: List of feature values in the same order as training columns
        
    Returns:
        Estimated price as float
        
    Raises:
        RuntimeError: If artifacts not loaded
        ValueError: If input features don't match expected format
    """
    global __model, __scaler, __columns, __categorical_columns

    # Check if artifacts are loaded
    if any(artifact is None for artifact in [__model, __scaler, __columns, __categorical_columns]):
        raise RuntimeError("Artifacts not loaded. Call load_saved_artifacts() first.")
    
    # Validate input
    if not isinstance(input_features, list):
        raise ValueError("input_features must be a list")
    
    if len(input_features) != len(__columns):
        raise ValueError(f"Expected {len(__columns)} features, got {len(input_features)}. "
                        f"Expected columns: {__columns}")
    
    try:
        # Create DataFrame with single row
        input_df = pd.DataFrame([input_features], columns=__columns)
        
        # Debug: print original data
        print(f"Input DataFrame shape: {input_df.shape}")
        print(f"Categorical columns to encode: {__categorical_columns}")
        
        # One-hot encode categorical features
        one_hot_encoded = pd.get_dummies(input_df, columns=__categorical_columns)
        print(f"After one-hot encoding shape: {one_hot_encoded.shape}")
        
        # Get expected feature names from scaler
        expected_features = __scaler.feature_names_in_
        print(f"Expected features by scaler: {len(expected_features)} features")
        
        # Reindex to match model's expected features (add missing columns as 0)
        one_hot_encoded = one_hot_encoded.reindex(columns=expected_features, fill_value=0)
        print(f"After reindexing shape: {one_hot_encoded.shape}")
        
        # Scale features
        scaled_features = __scaler.transform(one_hot_encoded)
        
        # Make prediction
        estimated_price = __model.predict(scaled_features)[0]
        
        return float(estimated_price)
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        print(f"Input features: {input_features}")
        raise

def validate_input_format(input_features: List) -> bool:
    """
    Validate that input features are in the correct format.
    
    Args:
        input_features: List of feature values
        
    Returns:
        True if valid format
    """
    if not __columns:
        print("Warning: Columns not loaded, cannot validate format")
        return False
        
    if len(input_features) != len(__columns):
        print(f"Error: Expected {len(__columns)} features, got {len(input_features)}")
        print(f"Expected columns: {__columns}")
        return False
        
    return True

def main():
    """Main function to test the prediction pipeline."""
    try:
        # Load artifacts first
        load_saved_artifacts()
        
        # Test data - make sure this matches your actual column order
        input_data = [
            [7420, 4, 2, 3, "yes", "no", "no", "no", "yes", 2, "yes", "furnished"],
            [8960, 4, 4, 4, "yes", "no", "no", "no", "yes", 3, "no", "furnished"],
            [9960, 3, 2, 2, "yes", "no", "yes", "no", "no", 2, "yes", "semi-furnished"],
            [7500, 4, 2, 2, "yes", "no", "yes", "no", "yes", 3, "yes", "furnished"],
            [7420, 4, 1, 2, "yes", "yes", "yes", "no", "yes", 2, "no", "furnished"]
        ]
        
        print("\nStarting predictions...")
        print("=" * 60)
        
        for i, data in enumerate(input_data, 1):
            try:
                print(f"\nProcessing row {i}:")
                print(f"Input: {data}")
                
                # Validate input format
                if not validate_input_format(data):
                    print(f"Skipping row {i} due to format error")
                    continue
                
                estimated_price = get_estimated_price(data)
                print(f"✓ Estimated Price: ${estimated_price:,.2f}")
                
            except Exception as e:
                print(f"✗ Error predicting row {i}: {e}")
                continue
                
        print("\n" + "=" * 60)
        print("Prediction testing completed")
        
    except Exception as e:
        print(f"Critical error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)