<template>
  <div>
    <!-- <button>draw</button> -->
    <svg id="chart" width="1000" height="800"></svg>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted } from 'vue'

import { WSClient } from '../client/remoteClient'

import {Sequence} from '../scripts/sequence'

export default defineComponent({
  setup() {
    onMounted(() => {
      const client = new WSClient("10.0.0.109", "8889")

      const seq = new Sequence('#chart')

      /**
       * update
       */
      const update = (args: any[]) => {
        const datapathes = client.getDatapathes()
        const messages = client.getMessages()

        seq.setDrawnDatapathes([])

        seq.drawController(0, messages.length)
        seq.drawDatapathes(datapathes, messages.length)
        seq.drawMessages(messages)
      }

      /**
       * setup
       */
      client.onGetOpenFlowMessage(update)
      client.connect()
      setInterval(client.emitGetOpenFlowMessageRequest.bind(client), 5000)

    })
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
</style>

