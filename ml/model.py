"""
Neural Collaborative Filtering (NCF) Model Implementation for RetailRec India.
Uses Customer and Item embeddings combined through a Multi-Layer Perceptron (MLP)
to predict customer-item interaction probability.
"""
import os
import sys
import logging
from typing import List, Tuple, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model, callbacks, optimizers

from app.core.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def create_ncf_model(
    num_customers: int,
    num_items: int,
    embedding_dim: int = 32,
    dense_layers: List[int] = [64, 32],
    dropout_rate: float = 0.20,
    learning_rate: float = 0.001,
) -> Model:
    """
    Constructs the Neural Collaborative Filtering architecture:
    Customer ID -> Embedding -> Customer Vector
    Item ID     -> Embedding -> Item Vector
    Concat -> Dense 64 (ReLU) -> Dropout -> Dense 32 (ReLU) -> Dropout -> Dense 1 (Sigmoid)
    """
    # Customer Branch
    customer_input = layers.Input(shape=(1,), name="customer_id", dtype=tf.int32)
    customer_embedding = layers.Embedding(
        input_dim=num_customers,
        output_dim=embedding_dim,
        embeddings_initializer="he_normal",
        name="customer_embedding",
    )(customer_input)
    customer_vector = layers.Flatten(name="flatten_customer")(customer_embedding)

    # Item Branch
    item_input = layers.Input(shape=(1,), name="item_id", dtype=tf.int32)
    item_embedding = layers.Embedding(
        input_dim=num_items,
        output_dim=embedding_dim,
        embeddings_initializer="he_normal",
        name="item_embedding",
    )(item_input)
    item_vector = layers.Flatten(name="flatten_item")(item_embedding)

    # Collaborative Interaction Representation (Concatenation)
    concat = layers.Concatenate(name="concat_vectors")([customer_vector, item_vector])

    # Multi-Layer Perceptron (MLP)
    x = concat
    for idx, units in enumerate(dense_layers):
        x = layers.Dense(units, activation="relu", name=f"dense_{units}_{idx+1}")(x)
        if dropout_rate > 0.0:
            x = layers.Dropout(dropout_rate, name=f"dropout_{idx+1}")(x)

    # Final Prediction Layer (Sigmoid output for probability [0, 1])
    output = layers.Dense(1, activation="sigmoid", name="interaction_probability")(x)

    model = Model(inputs=[customer_input, item_input], outputs=output, name="RetailRec_NCF")

    optimizer = optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="binary_crossentropy",
        metrics=["binary_accuracy"],
    )

    return model


class RetailRecNCF:
    """
    Wrapper class managing NCF model lifecycle:
    creation, compilation, training, evaluation, saving, and inference.
    """

    def __init__(
        self,
        num_customers: int,
        num_items: int,
        embedding_dim: int = settings.EMBEDDING_DIM,
        dense_layers: List[int] = [settings.DENSE_UNITS_1, settings.DENSE_UNITS_2],
        dropout_rate: float = settings.DROPOUT_RATE,
        learning_rate: float = 0.001,
        model: Optional[Model] = None,
    ):
        self.num_customers = num_customers
        self.num_items = num_items
        self.embedding_dim = embedding_dim
        self.dense_layers = dense_layers
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate

        if model is not None:
            self.model = model
        else:
            self.model = create_ncf_model(
                num_customers=num_customers,
                num_items=num_items,
                embedding_dim=embedding_dim,
                dense_layers=dense_layers,
                dropout_rate=dropout_rate,
                learning_rate=learning_rate,
            )

    def train(
        self,
        train_cust: np.ndarray,
        train_item: np.ndarray,
        train_labels: np.ndarray,
        val_cust: np.ndarray,
        val_item: np.ndarray,
        val_labels: np.ndarray,
        epochs: int = settings.MAX_EPOCHS,
        batch_size: int = settings.BATCH_SIZE,
        model_save_path: Optional[str] = None,
    ) -> tf.keras.callbacks.History:
        """Trains the NCF model with EarlyStopping and ModelCheckpoint."""
        cb_list = [
            callbacks.EarlyStopping(
                monitor="val_loss",
                patience=8,
                restore_best_weights=True,
                verbose=1,
            )
        ]

        if model_save_path:
            os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
            cb_list.append(
                callbacks.ModelCheckpoint(
                    filepath=model_save_path,
                    monitor="val_loss",
                    save_best_only=True,
                    verbose=1,
                )
            )

        history = self.model.fit(
            x=[train_cust, train_item],
            y=train_labels,
            validation_data=([val_cust, val_item], val_labels),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=cb_list,
            verbose=1,
        )

        return history

    def evaluate(self, test_cust: np.ndarray, test_item: np.ndarray, test_labels: np.ndarray) -> Dict[str, float]:
        """Evaluates model loss and accuracy on holdout test samples."""
        results = self.model.evaluate(x=[test_cust, test_item], y=test_labels, verbose=0)
        return {
            "loss": float(results[0]),
            "binary_accuracy": float(results[1]),
        }

    def predict_score(self, customer_idx: int, item_idx: int) -> float:
        """Predicts interaction score for a single customer-item pair."""
        c = np.array([customer_idx], dtype=np.int32)
        i = np.array([item_idx], dtype=np.int32)
        pred = self.model.predict([c, i], verbose=0)
        return float(pred[0][0])

    def predict_batch(self, customer_indices: np.ndarray, item_indices: np.ndarray) -> np.ndarray:
        """Vectorized prediction for multiple customer-item pairs."""
        preds = self.model.predict([customer_indices, item_indices], verbose=0)
        return preds.flatten()

    def save(self, filepath: str) -> None:
        """Saves model in Keras 3 format (.keras)."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.model.save(filepath)
        logger.info(f"Model saved to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> "RetailRecNCF":
        """Loads a saved Keras model."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file {filepath} does not exist.")
        loaded_model = tf.keras.models.load_model(filepath)
        
        # Extract shapes from embedding layer if possible
        cust_emb = loaded_model.get_layer("customer_embedding")
        item_emb = loaded_model.get_layer("item_embedding")
        num_customers = cust_emb.input_dim
        num_items = item_emb.input_dim
        embedding_dim = cust_emb.output_dim

        instance = cls(
            num_customers=num_customers,
            num_items=num_items,
            embedding_dim=embedding_dim,
            model=loaded_model,
        )
        return instance
