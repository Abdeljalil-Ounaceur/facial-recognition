import ast
import numpy as np
from PIL import Image
from mtcnn.mtcnn import MTCNN

from keras_vggface.vggface import VGGFace
from sklearn.preprocessing import normalize
from keras_vggface.utils import preprocess_input
from sklearn.random_projection import GaussianRandomProjection

# Define global variables
data_list = []
data_file = r'data_file.txt'
folder_path = r'C:\Users\Ounaceur\Documents\VS Code\Playground\Anas\gt_db'

#define the model
model = VGGFace(model='senet50', include_top=False, input_shape=(224, 224, 3), pooling='max')


def load_data_to_list(filename="data_file.txt"):
    """Load group hashes from a file into a list."""
    data_list = []
    with open(filename, 'r') as file:
        group_hashes = file.readlines()

    for line in group_hashes:
        group_tuple = ast.literal_eval(line.strip())
        # Ensure group_hash is a string
        group_hash = str(group_tuple[0])
        data_list.append((group_hash, group_tuple[1]))
    
    print(f"Loaded {len(group_hashes)} people's hashes with their informations from the file.")
    
    return data_list

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

# Function to calculate hamming distance
def hamming_distance(hash1, hash2):
    return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))



min_distance = 35
def match_face_info(new_embedding):
    new_hash = HashCode(new_embedding, 128)
    new_hash = convert_to_hash_string(new_hash)
    print(f"New face hash: {new_hash}")
    min_dist = np.inf  # initialize minimum distance to infinity
    matched_info = []
    for Hash, info in data_list:
        distance = hamming_distance(new_hash, Hash)
        # print(f"Comparing with hash {Hash}, distance: {distance}")
        if distance <= min_distance:
            if distance < min_dist:  # update minimum distance and matched group if necessary
                min_dist = distance
                matched_info = info
    if min_dist > min_distance:
        print("Unknown face.")
        matched_info = ['','Unknown','person']
    print(f"Similar person: {matched_info}")
    print(f"Minimum distance: {min_dist}")
    return matched_info

data_list = load_data_to_list(data_file)

def predict_faces_info_from_image(image):
    try:
        coordinates = extract_coordinates(image)
        actual_faces = extract_faces(image, coordinates)
        embeddings = get_embeddings(actual_faces)

        faces_info = []
        for (face_coordinates,embedding) in zip(coordinates,embeddings):
            matched_info = face_coordinates,match_face_info(embedding)
            faces_info.append(matched_info)   
        return faces_info
    
    except ValueError as e:
        print(e)
        return []



# Load the group list on script start
# print(data_list[0])
