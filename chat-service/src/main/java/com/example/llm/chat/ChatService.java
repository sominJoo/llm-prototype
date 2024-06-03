package com.example.llm.chat;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChatService {

    private final RestTemplate restTemplate;

    public Object postChat(String chat, String threadId, MultipartFile file) throws RuntimeException {

        LinkedMultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("chat", chat);
        body.add("thread_id", threadId);
        if (file != null) {
            try {
                body.add("file", file.getBytes());
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        } else {
            body.add("file", "");
        }

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        RequestEntity<Object> request = RequestEntity
                .post("http://127.0.0.1:8000/api/llm/chat/")
                .header(MediaType.MULTIPART_FORM_DATA.toString())
                .body(body);

        ResponseEntity<String> responseEntity = restTemplate.exchange(request, String.class);
        Map result = new HashMap();
        try {
            if (responseEntity.getStatusCode().is2xxSuccessful()) {
                log.info(responseEntity.getBody());
                result.put("result", 1);
                result.put("data", responseEntity.getBody());
            } else {
                result.put("result", 0);
                result.put("errorMessage", responseEntity.getBody());
            }
        } catch (Exception e) {
            log.error(e.getMessage());
            result.put("result", 0);
            result.put("errorMessage", responseEntity.getBody());
        }
        return result;
    }
}
