package com.example.llm.chat;

import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/llm")
@RequiredArgsConstructor
public class ChatController {

    private final ChatService chatService;

    @PostMapping(value = "/chat", consumes = "multipart/form-data")
    public Object handleChat(@RequestParam String chat, @RequestParam String threadId, @RequestParam(required = false) MultipartFile file) {
        return chatService.postChat(chat, threadId, file);
    }
}
