package com.example.chat.chat;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChatService {

    public Object postChat(String chat, String threadId, MultipartFile file) {
        /**
         * TODO : llm 연동
         */
        if(file != null) {
            log.info(file.getOriginalFilename());
            try {
                byte[] bytes = file.getBytes();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }
        Map map = new HashMap();
        map.put("data", "채팅중,,");
        return map;
    }
}
