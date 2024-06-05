package com.example.llm.chat;

import com.example.llm.framework.AutoRegisterApi;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.service.annotation.HttpExchange;
import org.springframework.web.service.annotation.PostExchange;

import java.util.Map;

@AutoRegisterApi
@HttpExchange("http://127.0.0.1:8000//api")
public interface ChatClient {
	
	@PostExchange(url = "/llm/chat/", contentType= MediaType.MULTIPART_FORM_DATA_VALUE)
	Map getChat(@RequestPart String chat, @RequestPart String thread_id, @RequestPart(required = false) MultipartFile file);
}
