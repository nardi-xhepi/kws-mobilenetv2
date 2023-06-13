import os
import librosa
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.regularizers import l2
from librosa.effects import pitch_shift
from tensorflow.keras import backend as K



def fix_length(data, size):
    if len(data) < size:
        # Pad the input data with zeros
        return np.pad(data, (0, size - len(data)))
    else:
        # Truncate the input data to the target size
        return data[:size]

def f1_score(y_true, y_pred): 
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    recall = true_positives / (possible_positives + K.epsilon())
    f1_val = 2*(precision*recall)/(precision+recall+K.epsilon())
    return f1_val


def augment_pitch(y, sr):
    tones = range(-1, 2)
    tuned_sound = pitch_shift(y=y, sr=sr, n_steps = np.random.choice(tones))
    return tuned_sound

class DataLoader:
    def __init__(self, axel_dir, noise_dir, unknown_dir):
        self.axel_dir = axel_dir
        self.noise_dir = noise_dir
        self.unknown_dir = unknown_dir
        self.all_data = []

    def load_random_noise(self, sr):
        noise_files = [os.path.join(self.noise_dir, f) for f in os.listdir(self.noise_dir)]
        random_noise_file = np.random.choice(noise_files)
        noise, _ = librosa.load(random_noise_file, sr=sr, duration=2)
        noise = librosa.util.fix_length(data=noise, size = 2*sr)
        return noise

    def add_noise_to_sound(self, y, sr):
        noise = self.load_random_noise(sr)
        scale = np.random.uniform(0.01, 0.1)  # scale factor between 1% to 10%
        return y + scale * noise


    def get_mfcc(self, y, sr):
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc = mfcc.astype(np.float32)
        input_array = np.stack((mfcc,)*3, axis=-1)
        input_array = tf.image.resize(input_array, [128, 128])
        preprocessed_input = tf.keras.applications.mobilenet_v2.preprocess_input(input_array)
        return preprocessed_input

    def load_audio_files(self, directory, label):
        file_paths = [os.path.join(directory, f) for f in os.listdir(directory)]
        np.random.shuffle(file_paths)
        audio_data = []
        for file_path in file_paths[:340]:
            y, sr = librosa.load(file_path, sr=16000, duration=2)
            y = librosa.util.fix_length(data=y, size=2*sr)  # Ensure all files have the same length
             # If "Axel" class, augment data
            if label == 0:
                for i in range(10):  # Generate 10 new samples for each original sample
                    y_aug = augment_pitch(y, sr)
                    mfcc = self.get_mfcc(y_aug, sr)
                    audio_data.append((mfcc, label))
                for i in range(10):
                    y = self.add_noise_to_sound(y, sr)
                    mfcc = self.get_mfcc(y, sr)
                    audio_data.append((mfcc, label))
            else:
                mfcc = self.get_mfcc(y, sr)
                audio_data.append((mfcc, label))
        return audio_data


    def load_data(self):
        # Load audio files
        print("Loading audio files ...", end="\r")
        axel_data = self.load_audio_files(self.axel_dir, 0)
        print("Keyword data length: ", len(axel_data))
        noise_data = self.load_audio_files(self.noise_dir, 1)
        print("Noise data length: ", len(noise_data))
        unknown_data = self.load_audio_files(self.unknown_dir, 2)
        print("Unknown data length: ", len(unknown_data))

        # Combine and shuffle data
        all_data = axel_data + noise_data + unknown_data
        np.random.shuffle(all_data)
        self.all_data = all_data


class Trainer:
    def __init__(self, data):
        self.all_data = data

    def generator(self, data):
        for item in data:
            yield item[0], item[1]

    def train(self):
        # Split data into training and validation sets
        split_index = int(0.8 * len(self.all_data))
        train_data = self.all_data[:split_index]
        val_data = self.all_data[split_index:]

        # Create datasets from the train and validation data
        train_dataset = tf.data.Dataset.from_generator(lambda: self.generator(train_data), output_signature=(
            tf.TensorSpec(shape=(128, 128, 3), dtype=tf.float32),
            tf.TensorSpec(shape=(), dtype=tf.int32)))

        val_dataset = tf.data.Dataset.from_generator(lambda: self.generator(val_data), output_signature=(
            tf.TensorSpec(shape=(128, 128, 3), dtype=tf.float32),
            tf.TensorSpec(shape=(), dtype=tf.int32)))

        # Create batched datasets
        train_dataset = train_dataset.batch(16)
        val_dataset = val_dataset.batch(16)

        # He initializer
        he_init = tf.keras.initializers.HeNormal()

        # Glorot initializer
        glorot_init = tf.keras.initializers.GlorotNormal()

        # Create MobileNetV2 model for transfer learning
        base_model = tf.keras.applications.MobileNetV2(input_shape=(128, 128, 3), include_top=False, weights='imagenet')
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        #Good performance for 128 and 64 neurons
        # Now use the specified initializers in the layers you add
        x = Dense(128, activation="relu", kernel_initializer=he_init)(x)  # or glorot_init
        x = Dropout(0.3)(x)
        x = Dense(64, activation="relu", kernel_initializer=he_init)(x)
        predictions = Dense(3, activation='softmax', kernel_initializer=glorot_init)(x)  # or glorot_init
        model = Model(inputs=base_model.input, outputs=predictions)




        # Freeze layers for transfer learning
        for layer in base_model.layers:
            layer.trainable = False

        model.compile(optimizer=Adam(learning_rate=1e-3), loss='sparse_categorical_crossentropy', metrics=[f1_score], run_eagerly=True)

        print("Training ... ", end="\r")

        model.fit(
            train_dataset, 
            epochs=1, 
            validation_data=val_dataset)
        """
        # Unfreeze layers for fine-tuning
        for layer in model.layers[-100:]:
            layer.trainable = True
       # Fine-tuning the model
        model.compile(optimizer=Adam(learning_rate=1e-5), 
              loss='sparse_categorical_crossentropy', 
              metrics=[f1_score])
        # Set up early stopping callback
        early_stopping = EarlyStopping(monitor='val_loss', patience=3)
        
        
        history = model.fit(
            train_dataset, 
            epochs=8, 
            validation_data=val_dataset, 
            callbacks=[early_stopping])  
        # Save the model
        
        """
        model.save('C:\\Users\\nardi\\website\\kws\\ia\\user_data\\model.h5')

         # Model evaluation
        evaluation = model.evaluate(val_dataset)
        print(f"Validation Loss: {evaluation[0]}, Validation Accuracy: {evaluation[1]}")