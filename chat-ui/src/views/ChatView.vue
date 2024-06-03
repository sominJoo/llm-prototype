<template>
  <div>
    <vue-advanced-chat
        :current-user-id="'USER'"
        :rooms="JSON.stringify(rooms)"
        :rooms-list-opened="false"
        :loading-rooms="false"
        :messages-loaded="true"
        :rooms-loaded="false"
        :show-audio="false"
        :messages="JSON.stringify(messages)"
        @send-message="sendMessage($event.detail[0])"
        @fetch-message="addMessageToChat"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { register } from 'vue-advanced-chat'
import axios, {type AxiosResponse} from "axios";
register();
const currentUserId = "USER";

const rooms = ref([
  {
    roomId: Math.random().toString(),
    roomName: 'Chat AI',
    avatar: 'https://66.media.tumblr.com/avatar_c6a8eae4303e_512.pnj',
    users: [
      { _id: 'Chat AI', username: 'Chat AI' },
      { _id: 'USER', username: 'USER' }
    ]
  }
]);

interface Message {
  _id: number,
  content: string,
  senderId: string,
  timestamp?: string,
  date: string
}
const messages = ref<Message[]>([]);

const sendMessage = (message: { content: string, files: any[] }) => {
  messages.value = [
    ...messages.value,
    {
      _id: messages.value.length,
      content: message.content,
      senderId: currentUserId,
      timestamp: new Date().toString().substring(16, 21),
      date: new Date().toDateString()
    }
  ]
  receiveMessage(message);
};

const receiveMessage = async (message: { content: string, files: any[] }) => {
  const formData = new FormData();
  formData.append('chat', message.content);
  formData.append('threadId', rooms.value[0].roomId)

  if(message.files && message.files.length > 0) {
    message.files.forEach(file => {
      formData.append('file', file, file.name)
    })
  }

  try {
    const response: AxiosResponse = await axios.post("/api/llm/chat", formData);
    addMessageToChat(response);
  } catch (err) {
    console.error('err,,,,,', err)
  }
}

const addMessageToChat = (response: AxiosResponse) => {
  setTimeout(() => {
    messages.value = [
      ...messages.value,
      {
        _id: messages.value.length,
        content: response.data.data,
        senderId: "Chat AI",
        timestamp: new Date().toString().substring(16, 21),
        date: new Date().toDateString()
      }
    ]
  }, 1500)
}
</script>
