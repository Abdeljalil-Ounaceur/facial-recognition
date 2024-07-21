import os
import numpy as np
from PIL import Image
from mtcnn.mtcnn import MTCNN

from keras_vggface.vggface import VGGFace
from sklearn.preprocessing import normalize
from keras_vggface.utils import preprocess_input
from sklearn.random_projection import GaussianRandomProjection


# Define global variables
output_file = r'output.txt'
folder_path = r'C:\people'

#define the model
model = VGGFace(model='senet50', include_top=False, input_shape=(224, 224, 3), pooling='max')

detector = MTCNN()

def extract_coordinates(image):
    faces_data = detector.detect_faces(image)
    if len(faces_data) == 0:
        raise ValueError("No face detected in image")
    coordinates = []
    for face in faces_data:
        x, y, width, height = face['box']
        coordinates.append((int(x), int(y), int(width), int(height)))
    return coordinates

def extract_faces(pixels, coordinates, required_size=(224, 224)):    
    faces = []
    for (x, y, width, height) in coordinates:
        x2, y2 = x + width, y + height
        face = pixels[y:y2, x:x2]
        image = Image.fromarray(face)
        image = image.resize(required_size)
        face_array = np.asarray(image)
        faces.append(face_array)
    return faces

def get_embeddings(face_arrays):
    samples = np.asarray(face_arrays, 'float32')
    samples = preprocess_input(samples, version=2)
    embeddings = model.predict(samples)
    return embeddings
    


def HashCode(feature_vector, n_bits=64, random_state=42):
    # Normalize the feature vector
    feature_vector = normalize(feature_vector[:, np.newaxis], axis=0).ravel()

    transformer = GaussianRandomProjection(n_components=n_bits, random_state=random_state)
    hyperplanes = transformer.fit_transform(feature_vector.reshape(1, -1))
    # Generate the hash
    binary_hash = (hyperplanes > 0).astype(int).flatten()
    return binary_hash


def convert_to_hash_string(int_list):
    return ''.join(str(bit) for bit in int_list)



def process_images_in_folder(folder_path, output_file):
    # Get the list of all folders in the directory
    all_folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]

    # Sort the folders alphanumerically
    all_folders.sort()

    # Open the output file
    with open(output_file, 'w') as file:
        # Process each folder
        for folder in all_folders:
            # List to store all embeddings
            all_embeddings = []

            # Full path to the current folder
            current_folder_path = os.path.join(folder_path, folder)

            # Process each image in the folder
            for filename in os.listdir(current_folder_path):
                if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
                    # Load the image
                    image_path = os.path.join(current_folder_path, filename)
                    image = np.array(Image.open(image_path))

                    # Extract faces from the image
                    coordinates = extract_coordinates(image)
                    faces = extract_faces(image, coordinates)

                    # Compute the embeddings for the faces
                    embeddings = get_embeddings(faces)

                    # Add the embeddings to the list
                    all_embeddings.extend(embeddings)

            # Average the embeddings
            average_embedding = np.mean(all_embeddings, axis=0)

            # Compute the hash of the average embedding
            hash_code = HashCode(average_embedding, 128)
            hash_string = convert_to_hash_string(hash_code)

            # Write the hash and folder name to the output file
            file.write(f"({hash_string}, {folder})\n")

            print(f"Hash of average embedding for folder {folder}: {hash_string}")

# Call the function with the path to your folder and the output file
process_images_in_folder(folder_path, output_file)