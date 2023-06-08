import json
import io
import soundfile as sf
from channels.generic.websocket import AsyncWebsocketConsumer
import librosa
import numpy as np
import tensorflow as tf
from asgiref.sync import sync_to_async
from tensorflow.keras import backend as K

def f1_score(y_true, y_pred): 
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    recall = true_positives / (possible_positives + K.epsilon())
    f1_val = 2*(precision*recall)/(precision+recall+K.epsilon())
    return f1_val

labels = ["Keyword", 'Noise', 'Unknown']

# Function to process the audio and make predictions
async def process_audio(audio_data, sr):
    model = tf.keras.models.load_model('C:\\Users\\nardi\\keyword_spotting_model.h5', custom_objects={'f1_score': f1_score})
    y = librosa.util.fix_length(data=audio_data, size=2*sr)  # Ensure all files have the same length
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc = mfcc.astype(np.float32)
    input_array = np.stack((mfcc,)*3, axis=-1)  # convert to 3 channels
    input_array = np.expand_dims(input_array, axis=0)  # add an extra dimension for batch size
    input_array = tf.image.resize(input_array, [128, 128])  # resize to model's expected input size
    preprocessed_input = tf.keras.applications.mobilenet_v2.preprocess_input(input_array)
    return model.predict(preprocessed_input, verbose=0)


class AudioProcessingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            result = await self.receive_text(text_data)
        elif bytes_data is not None:
            audio_buffer = io.BytesIO(bytes_data)
            audio_data, samplerate = sf.read(audio_buffer)
            prediction = await process_audio(audio_data, 16000)
            predicted_label = labels[np.argmax(prediction)]

        await self.send(text_data=json.dumps({
            'prediction': predicted_label
        }))

    async def receive_text(self, text_data):
        # Handle text data.
        return "Text result"

    async def receive_bytes(self, bytes_data):
        return "Audio result"
