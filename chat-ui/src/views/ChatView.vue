<template>
  <div>
    <vue-advanced-chat
        :current-user-id="'USER'"
        :rooms="JSON.stringify(rooms)"
        :messages-loaded="true"
        :rooms-loaded="true"
        :show-audio="false"
        :multiple-files="false"
        :messages="JSON.stringify(allMessages[threadId])"
        @send-message="sendMessage($event.detail[0])"
        @fetch-messages="fetchMessage"
        @room-info="enterRoom"
        @add-room="addRoom"
        @room-action-handler="console.log(v)"
        @menu-action-handler="logger"
    />
  </div>
  {{ allMessages }}
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { register } from 'vue-advanced-chat'
import axios, {type AxiosResponse} from "axios";
register();
const currentUserId = "USER";
const threadId = ref(Math.random().toString());
const rooms = ref([
  {
    roomId: threadId.value,
    roomName: 'Chat AI' + threadId.value,
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
  files?: object[]
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
    };

    if (message.files) {
      newMessage.files = [message.files[0]];
    }
    console.log(threadId.value)
    console.log(allMessages.value[threadId.value])
    allMessages.value[threadId.value] = [
      ...allMessages.value[threadId.value],
      newMessage
    ];
  receiveMessage(message);
};

const receiveMessage = async (message: { content: string, files: any[] }) => {
  const formData = new FormData();
  formData.append('chat', message.content);
  formData.append('threadId', threadId.value)

  if(message.files) {
    formData.append("file", message.files[0].blob, message.files[0].name)
  }
  formData.forEach(function(value, key){
    console.log(key + ': ' + value);
  });

  try {
    const response: AxiosResponse = await axios.post("/api/llm/chat", formData);
    addMessageToChat(response);
  } catch (err) {
    console.error(err)
  }
}

const addMessageToChat = (response: AxiosResponse) => {
  allMessages.value[threadId.value] = [
    ...allMessages.value[threadId.value],
    {
      _id: messages.value.length,
      content: response.data.data,
      senderId: threadId.value,
      timestamp: new Date().toString().substring(16, 21),
      date: new Date().toDateString()
    }
  ];
}

const addRoom = () => {
  threadId.value = Math.random().toString();
  rooms.value = [
      ...rooms.value,
    {
      roomId: threadId.value,
      roomName: 'Chat AI' + threadId.value,
      avatar: 'https://66.media.tumblr.com/avatar_c6a8eae4303e_512.pnj',
      users: [
        { _id: threadId.value, username: 'Chat AI' },
        { _id: 'USER', username: 'USER' }
      ]
    }
  ]
  allMessages.value[threadId.value] = [];
}
const logger = ({v1, v2}) => {
  console.log(v2)
}
const enterRoom = (room) => {
  const roomId = room.detail[0].roomId;
  console.log(roomId)
  threadId.value = roomId
}

const fetchMessage = ({ room, options }) => {
  console.log(room, options)
}
</script>
