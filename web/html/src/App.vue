<template>
  <header id="header">
    <h1>Sequence Diagram</h1>
  </header>


  <!-- <img alt="Vue logo" src="./assets/logo.png"> -->
  <div id="sequence-container">
    <Sequence
      @showinfo="showInfo" />
  </div>

  <div id="message-information">
    <div>MessageType: {{ data.messageType }}</div>
    <div>order: {{ data.order }}</div>
    <div>timestamp: {{ data.timestamp }}</div>
    <div>content: </div>
    <div>{{ data.content }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive } from 'vue';
import Sequence from './components/Sequence.vue';
import { MessageInformation } from './scripts/information';

export default defineComponent({
  name: 'App',
  components: {
    Sequence
  },
  setup(){
    const data = reactive({
      messageType: "",
      order: "",
      timestamp: 0,
      content: ""
    })
    const showinfo = (information: MessageInformation) => {
      data.messageType = information.messageType
      data.order = information.order
      data.timestamp = information.timestamp
      data.content = information.content
    }

    return {
      showinfo,
      data
    }
  }
});

</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  
  
  display: grid;
  grid-template-areas: 
    " header header"
    " sequence information";
  grid-auto-rows: 
    5rem
    minmax(50rem, auto);
  grid-auto-columns: 
    3fr
    1fr;
  grid-gap: 1rem;
}

#header{
    grid-area: header;
    /* // background-color: #f0f0f9; */
    border-bottom: 0.5rem solid #2c3e50;
    /* // padding: 1.5rem; */
}

#header.h1{
  margin: 1rem 2rem;
  font-size: 2.5rem;
}

#sequence{
  grid-area: sequence;
  height: auto;
  width: auto;
}

#information{
  grid-area: information;
}
</style>
