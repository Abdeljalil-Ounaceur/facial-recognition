package com.example.server.component;


import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Map;

@Component
public class KafkaConsumer {

    private final SimpMessagingTemplate template;
    private final ObjectMapper mapper = new ObjectMapper();
    private final 
    TypeReference<Map<String, Object>> typeRef = new TypeReference<Map<String, Object>>() {};

    public KafkaConsumer(SimpMessagingTemplate template) {
        this.template = template;
    }

    @KafkaListener(topics = "second-topic", groupId = "whatever-group-id")
    public void consumeMessage(String data) {
        try {
            Map<String, Object> map = mapper.readValue(data, typeRef);

            String sessionId = ((String)map.get("sessionId")).replaceAll("\"", "");

            System.out.println(data);
            // Publish the results on the dynamic topic
            String topic = "/topic/messages/" + sessionId;
            template.convertAndSend(topic, data);

            System.out.println("Consumed message with sessionId: " + sessionId);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}