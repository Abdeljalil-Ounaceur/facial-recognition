package com.example.server.controller;

import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.example.server.component.KafkaProducer;


@RestController
public class MessageController {

    private final KafkaProducer kafkaProducer;

    public MessageController(KafkaProducer kafkaProducer) {
        this.kafkaProducer = kafkaProducer;
    }

    @PostMapping("/send-text")
    public void sendMessageToKafka(@RequestBody String message) {
        kafkaProducer.sendMessage(message);
    }

    @PostMapping("/send-image")
    public void sendMessageToKafka(@RequestBody MultipartFile image) {
        kafkaProducer.sendImage(image);
    }

    @MessageMapping("/send")
    public void sendMessageToKafkaFromWebSocket(@Header("session-id") String sessionId, String base64Image) {
        kafkaProducer.sendEncodedImageWithSessionId(sessionId,base64Image);
    }
}
