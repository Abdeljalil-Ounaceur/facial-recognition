package com.example.server.component;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.HashMap;
import java.util.Map;


@Component
public class KafkaProducer {

    private final KafkaTemplate<String, String> kafkaTemplate;
    private final String TOPIC_NAME= "first-topic";
    
    private final ObjectMapper mapper = new ObjectMapper();
    private final Map<String, String> data = new HashMap<>();

    public KafkaProducer(KafkaTemplate<String, String> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void sendMessage(String message) {
        return;
    }

    public void sendImage(MultipartFile image) {
        return;
    }

    public void sendEncodedImageWithSessionId(String sessionId, String base64Image) {
        data.put("sessionId", sessionId);
        data.put("base64Image", base64Image);

        try {
            String json = mapper.writeValueAsString(data);
            kafkaTemplate.send(TOPIC_NAME, json);
        } catch (Exception e) {
            e.printStackTrace();
        }
        System.out.println("Encoded Image with session id has been successfully sent to the topic: " + TOPIC_NAME);
    }

}