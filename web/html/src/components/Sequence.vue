<template>
  <div>
    <button @click="update()">update</button>
    <div>
    <svg id="chart" width="1000" height="800"></svg>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from 'vue'

import { WSClient } from '../client/remoteClient'

import {Sequence} from '../scripts/sequence'

export default defineComponent({
  setup() {
    let update = ref<any>()

    onMounted(() => {
      const client = new WSClient("10.0.0.109", "8889")

      const seq = new Sequence('#chart')

      /**
       * update
       */
      const updateDiagram = (args: any[]) => {
        const datapathes = client.getDatapathes()
        const messages = client.getMessages()

        seq.setDrawnDatapathes([])

        seq.drawController(0, messages.length)
        seq.drawDatapathes(datapathes, messages.length)
        seq.drawMessages(messages)
      }

      client.onGetOpenFlowMessage(updateDiagram)
      client.connect()

      /**
       * setup
       */
      update.value = () => {
        client.emitGetOpenFlowMessageRequest()
      }
    })

    return {
      update
    }
  }
})
</script>


<style>
.class-rect {
  border: 1;
  fill: white;
  stroke-width: 1px;
  stroke: black;
}

button {
  background: #2c3e50;
  color: white;
}
</style>

