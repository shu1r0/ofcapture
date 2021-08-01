<template>
  <!-- <img alt="Vue logo" src="./assets/logo.png"> -->
  <Sequence />
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import Sequence from './components/Sequence.vue';

export default defineComponent({
  name: 'App',
  components: {
    Sequence
  }
});
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
