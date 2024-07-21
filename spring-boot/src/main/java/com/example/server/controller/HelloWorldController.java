package com.example.server.controller;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.view.RedirectView;

@RestController
public class HelloWorldController {

    @RequestMapping("/")
    public RedirectView helloWorld() {
        return new RedirectView("index.html");
    }
}
