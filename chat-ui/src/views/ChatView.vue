<template>
  <div>
    <vue-advanced-chat
        :current-user-id="'USER'"
        :rooms="JSON.stringify(rooms)"
        :rooms-loaded="true"
        :show-audio="false"
        :messages="JSON.stringify(messages)"
        :messages-loaded="messagesLoaded"
        @send-message="sendMessage($event.detail[0])"
        @fetch-messages="fetchMessages($event.detail[0])"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { register } from 'vue-advanced-chat'
register();

const rooms = ref([
  {
    roomId: '1',
    roomName: 'Room 1',
    avatar: 'https://66.media.tumblr.com/avatar_c6a8eae4303e_512.pnj',
    users: [
      { _id: '1234', username: 'John Doe' },
      { _id: '4321', username: 'John Snow' }
    ]
  }
]);
const messages = ref([]);
const messagesLoaded = ref(false);

const fetchMessages = ({ options = {} }) => {
  setTimeout(() => {
    if (options.reset) {
      messages.value = addMessages(true)
    } else {
      messages.value = [...addMessages(), ...messages.value]
      messagesLoaded.value = true
    }
  })
};

const addMessages = (reset: boolean) => {
  const newMessages = []

  for (let i = 0; i < 30; i++) {
    newMessages.push({
      _id: reset ? i : messages.value.length + i,
      content: `${reset ? '' : 'paginated'} message ${i + 1}`,
      senderId: '4321',
      username: 'John Doe',
      date: '13 November',
      timestamp: '10:20'
    })
  }

  return newMessages
};

const sendMessage = (message: { content: string }) => {
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
};

const addNewMessage = () => {
  setTimeout(() => {
    messages.value = [
      ...messages.value,
      {
        _id: messages.value.length,
        content: 'NEW MESSAGE',
        senderId: '1234',
        timestamp: new Date().toString().substring(16, 21),
        date: new Date().toDateString()
      }
    ]
  }, 2000)
};
</script>
