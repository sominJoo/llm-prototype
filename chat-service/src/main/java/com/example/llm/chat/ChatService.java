package com.example.llm.chat;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.tomcat.util.http.fileupload.IOUtils;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChatService {

    private final RestTemplate restTemplate;

    public Object postChat(String chat, String threadId, MultipartFile file) throws RuntimeException, IOException {
        
        HttpHeaders headers = new HttpHeaders();
        LinkedMultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("chat", chat);
        body.add("thread_id", threadId);
        if (file != null) {
            String fileName = file.getOriginalFilename();
            try (
                    InputStream inputStream = file.getInputStream();
                    ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            ) {
                byte[] buffer = new byte[1024];
                int length;
                while ((length = inputStream.read(buffer)) != -1) {
                    outputStream.write(buffer, 0, length);
                }
                
                ByteArrayResource resource = new ByteArrayResource(outputStream.toByteArray()){
                    @Override
                    public String getFilename(){
                        return fileName; // 파일 이름 설정
                    }
                };
                headers.set("Content-Disposition", "form-data; name=\"file\"; filename="+file.getOriginalFilename());
                body.add("file", resource);
            } catch (IOException e) {
                log.info("file error");
                throw new RuntimeException(e);
            }
        } else {
            log.info("file 없음");
            body.add("file", "");
        }

        headers.setContentType(MediaType.MULTIPART_FORM_DATA);
        headers.setContentLength(800);
        
        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
        ResponseEntity<Map> responseEntity = restTemplate.exchange(
               "http://127.0.0.1:8000/api/llm/chat/",
                HttpMethod.POST,
                requestEntity,
                Map.class);

//        ResponseEntity<Map> responseEntity = restTemplate.exchange(request, Map.class);
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
