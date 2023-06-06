import os
import librosa
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping

class Trainer:
    def __init__(self, axel_dir, noise_dir, unknown_dir):
        self.axel_dir = axel_dir
        self.noise_dir = noise_dir
        self.unknown_dir = unknown_dir

    def load_audio_files(self, directory, label):
        file_paths = [os.path.join(directory, f) for f in os.listdir(directory)]
        np.random.shuffle(file_paths)
        audio_data = []
        for file_path in file_paths[:1000]:
            y, sr = librosa.load(file_path, sr=16000, duration=2)
            y = librosa.util.fix_length(y, 2 * sr)  # Ensure all files have the same length
            mfcc = librosa.feature.mfcc(y, sr=sr, n_mfcc=128)
            mfcc = mfcc.astype(np.float32)
            mfcc = np.stack((mfcc, mfcc, mfcc), axis=-1)  # Create 3 channels
            audio_data.append((mfcc, label))
        return audio_data

    def train(self):
        # Load audio files
        axel_data = self.load_audio_files(self.axel_dir, 0)
        noise_data = self.load_audio_files(self.noise_dir, 1)
        unknown_data = self.load_audio_files(self.unknown_dir, 2)

        # Combine and shuffle data
        all_data = axel_data + noise_data + unknown_data
        np.random.shuffle(all_data)

        # Split data into training and validation sets
        split_index = int(0.8 * len(all_data))
        train_data = all_data[:split_index]
        val_data = all_data[split_index:]

        # Prepare data generators
        train_datagen = ImageDataGenerator(rescale=1./255, zoom_range=0.1, width_shift_range=0.1, height_shift_range=0.1)
        val_datagen = ImageDataGenerator(rescale=1./255)

        # Create MobileNetV2 model for transfer learning in tensorflow
        base_model = tf.keras.applications.MobileNetV2(input_shape=(128, 63, 3), include_top=False, weights='imagenet')
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(128, activation="relu")(x)
        predictions = Dense(3, activation='softmax')(x)
        model = Model(inputs=base_model.input, outputs=predictions)

        # Freeze layers for transfer learning
        for layer in base_model.layers:
            layer.trainable = False

        model.compile(optimizer=Adam(lr=1e-3), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        # Train the model
        train_generator = train_datagen.flow(np.array([x[0] for x in train_data]), np.array([x[1] for x in train_data]), batch_size=32)
        val_generator = val_datagen.flow(np.array([x[0] for x in val_data]), np.array([x[1] for x in val_data]), batch_size=32)

        model.fit(train_generator, epochs=10, validation_data=val_generator)

        # Unfreeze layers for fine-tuning
        for layer in model.layers[-15:]:
            layer.trainable = True

        # Fine-tuning the model
        model.compile(optimizer=Adam(lr=1e-5), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        # Set up early stopping callback
        early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

        history = model.fit(train_generator, epochs=15, validation_data=val_generator, callbacks=[early_stopping])

        # Save the model
        model.save('../user_data/model.h5')

        # Model evaluation
        evaluation = model.evaluate(val_generator)
        print(f"Validation Loss: {evaluation[0]}, Validation Accuracy: {evaluation[1]}")
