package com.example.llm.chat;

import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
@AllArgsConstructor
public class ChatService {
    private final ChatClient chatClient;
    
    
    public Object postChat(String chat, String threadId, MultipartFile file) throws RuntimeException {
        if (file != null) {
            return fileChat(chat, threadId, file);
        }
        
        return chatClient.getChat(chat, threadId, null);
    }
    
    
    public Object fileChat(String chat, String threadId, MultipartFile file) throws RuntimeException {
        return chatClient.getChat(chat, threadId, file);
    }
    
    
    private Map getResult(ResponseEntity<Map> responseEntity) {
        Map result = new HashMap();
        Map responseEntityBody = responseEntity.getBody();
        try {
            if (responseEntity.getStatusCode().is2xxSuccessful()) {
                log.info(responseEntityBody.toString());
                result.put("result", responseEntityBody.get("result"));
                result.put("data", responseEntityBody.get("data"));
                result.put("errorMessage", responseEntityBody.get("errorMessage"));
            } else {
                result.put("result", responseEntityBody.get("result"));
                result.put("errorMessage", responseEntityBody.get("errorMessage"));
            }
        } catch (Exception e) {
            log.error(e.getMessage());
            result.put("result", responseEntityBody.get("result"));
            result.put("errorMessage", responseEntityBody.get("errorMessage"));
        }
        return result;
    }
}
