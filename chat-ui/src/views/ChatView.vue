<template>
  <div>
    <vue-advanced-chat
        height="calc(100vh - 20px)"
        :current-user-id="'USER'"
        :rooms="JSON.stringify(rooms)"
        :messages-loaded="messagesLoaded"
        :rooms-loaded="true"
        :show-audio="false"
        :multiple-files="false"
        :messages="JSON.stringify(allMessages[threadId])"
        @send-message="sendMessage($event.detail[0])"
        @fetch-messages="fetchMessage($event.detail[0])"
        @room-info="enterRoom"
        @add-room="addRoom"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {register} from 'vue-advanced-chat'
import axios, {type AxiosResponse} from "axios";
register();
const currentUserId = "USER";
const threadId = ref(Math.random().toString());
const rooms = ref([
  {
    roomId: threadId.value,
    roomName: 'Chat AI 1',
    avatar: 'https://66.media.tumblr.com/avatar_c6a8eae4303e_512.pnj',
    users: [
      { _id: 'Chat AI', username: 'Chat AI' },
      { _id: 'USER', username: 'USER' }
    ]
  }
]);
interface AllMessages {
  [key:string]: [];
}
interface Message {
  _id: number,
  content: string,
  senderId: string,
  timestamp?: string,
  date: string,
  files?: object[],
  seen?: boolean
}
const allMessages = ref<AllMessages>({
  [threadId.value]: []
});
const messages = ref<Message[]>([]);

const sendMessage = (message: { content: string, files: any[] }) => {
    const newMessage = {
      _id: allMessages.value[threadId.value].length,
      content: message.content,
      senderId: currentUserId,
      timestamp: new Date().toString().substring(16, 21),
      date: new Date().toDateString(),
      seen: true
    };
    const id = threadId.value;
    if (message.files) {
      newMessage.files = [message.files[0]];
    }
    allMessages.value[id] = [
      ...allMessages.value[id],
      newMessage
    ];
  receiveMessage(message, id);
};

const receiveMessage = async (message: { content: string, files: any[] }, id: string) => {
  const formData = new FormData();
  formData.append('chat', message.content);
  formData.append('threadId', id)

  if(message.files) {
    const file = message.files[0]
    formData.append("file", message.files[0].blob, file.name+"."+file.extension)
  }
  try {
    const response: AxiosResponse = await axios.post("/api/llm/chat", formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    });
    addMessageToChat(response, id);
  } catch (err) {
    console.error(err)
  }
}

const addMessageToChat = (response: AxiosResponse, senderId: string) => {
  const isError = response.data.data === null;
  const content = isError ? response.data.errorMessage : response.data.data;
  const newMessage =       {
    _id: messages.value.length,
    content: content,
    senderId: senderId,
    timestamp: new Date().toString().substring(16, 21),
    date: new Date().toDateString(),
    seen: true
  }
  allMessages.value[threadId.value] = [
    ...allMessages.value[threadId.value],
    newMessage
  ];
}

const addRoom = () => {
  threadId.value = Math.random().toString();
  rooms.value = [
      ...rooms.value,
    {
      roomId: threadId.value,
      roomName: 'Chat AI ' + (rooms.value.length + 1).toString(),
      avatar: 'https://66.media.tumblr.com/avatar_c6a8eae4303e_512.pnj',
      users: [
        { _id: threadId.value, username: 'Chat AI' },
        { _id: 'USER', username: 'USER' }
      ]
    }
  ]
  allMessages.value[threadId.value] = [];
}

const enterRoom = (room) => {
  threadId.value = room.detail[0].roomId;
}
const messagesLoaded = ref(false)

const fetchMessage = ({ room, options }) => {
  messagesLoaded.value = false;
  threadId.value = room.roomId;
  /**
   * NOTE: spinner message loader 문제
   */
  setTimeout(() => {
    messagesLoaded.value = true
  }, 0)
}
</script>
