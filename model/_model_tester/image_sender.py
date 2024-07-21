import cv2
from kafka import KafkaProducer, KafkaConsumer
import json
import base64
from PIL import Image
# import io
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk
import threading

import numpy as np

# Kafka configuration
bootstrap_servers = ['localhost:9092']
input_topic = 'first-topic'
output_topic = 'second-topic'

#the image
image = None

# Lock for thread-safe updates to the counter
lock = threading.Lock()

# Create Kafka producer
producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                         max_request_size=20971520)  # Set max request size to 20MB

# Create Kafka consumer for receiving processed images
consumer = KafkaConsumer(output_topic,
                         bootstrap_servers=bootstrap_servers,
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                         max_partition_fetch_bytes=20971520,  # Set max fetch size to 20MB
                         consumer_timeout_ms=1000)  # Set timeout to 1 second

def select_and_send_image():
    global image
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, "rb") as image_file:
            image_data = image_file.read()
            encoded_string = base64.b64encode(image_data).decode()
            #store the showble image in the global variable
            with lock:
                image = np.frombuffer(image_data, dtype=np.uint8)
        producer.send(input_topic, {'sessionId':'0','base64Image': encoded_string})
        producer.flush()
        status_label.config(text="Image sent. Waiting for processed image...")
        threading.Thread(target=receive_and_display_image, daemon=True).start()

def resize_image(image, max_width):
    # Calculate the scale factor
    scale_factor = max_width / image.shape[1]
    # Resize the image
    resized_image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
    return resized_image, scale_factor

def receive_and_display_image():
    global image
    local_image = None
    while True:
        try:
            for message in consumer:
                encoded_data = message.value
                session_id, results = encoded_data["sessionId"], encoded_data["results"]
                session_id = session_id.strip().strip('"')

                print(results)
                if(results == []):
                    status_label.config(text="No faces detected")
                    image_label.config(image="")
                    continue

                with lock:
                    local_image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                
                local_image, scale_factor = resize_image(local_image, max_width=400)
                # Draw rectangles around the detected faces
                for ((x, y, w, h),(sex,f_name,l_name)) in results:
                    x, y, w, h = int(x * scale_factor), int(y * scale_factor), int(w * scale_factor), int(h * scale_factor)
                    cv2.rectangle(local_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(local_image, f_name+" "+l_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36,255,12), 1)
                
                pil_image = Image.fromarray(local_image)  # Convert numpy array to PIL Image
                photo = ImageTk.PhotoImage(pil_image)
                image_label.config(image=photo)
                image_label.image = photo
                status_label.config(text="Received processed image")
                return
        except StopIteration:
            # No message received, continue polling
            continue

# Create GUI
root = tk.Tk()
root.title("Image Processor")

send_button = tk.Button(root, text="Select and Send Image", command=select_and_send_image)
send_button.pack()

status_label = tk.Label(root, text="")
status_label.pack()

image_label = tk.Label(root)
image_label.pack()

root.mainloop()