# Setting Up Python and Spring Boot Environments
Tb3o ghir hadchi maghaykheskom walo inchaalah.
Bach ikhdem lik hadchi khass tkon 3ndek: 
K=JAVA_17 blast JAVA_1.8
W khass tkon 3ndek Maven m instalia. 
lba9i khlih 3lia.

## Configuration

### Kafka Topics
RUN ZOOKEEPER AND KAFKA FIRST
Then create two topics 'first-topic' and 'second-topic', these kafka commands are perfect in my case (they work in my computer):

cd c:\kafka\bin\windows
.\kafka-topics localhost:9092 --create --topic first-topic
.\kafka-topics localhost:9092 --create --topic second-topic 



### Python Model Setup

Open the terminal on project location.

Create a new virtual environnement just to avoid prblems:

cd model
py -m venv vgg-face
vgg-face\Scripts\activate
pip install -r requirements.txt


Run the server:

cd best_model
py server.py

(Optional) you can go to _model_tester to test the model:
cd ../_model_tester
py image_sender.py

And try to send an image and see the result appear in the window.



### Spring Boot Setup

Open another terminal and head to the project location again.

cd spring-boot
mvn dependency:resolve
./mvnw spring-boot:run

### Testing

open the brower and go to localhost:9092
ENJOY!


