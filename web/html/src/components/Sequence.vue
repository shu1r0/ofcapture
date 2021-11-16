<template>
  <div>
    <!-- <button>draw</button> -->
    <svg id="chart" width="1000" height="800"></svg>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted } from 'vue'
// eslint-disable-next-line
//@ts-ignore
import * as d3 from 'd3'
import { Datapath, OpenFlowMessage } from '../api/api_pb'
import { WSClient } from '../client/remoteClient'

export default defineComponent({
  setup() {
    onMounted(() => {
      const client = new WSClient("10.0.0.109", "8889")

      const svg = d3.select('#chart')
      // graph margin
      const margin = {top: 20, right: 50, bottom: 100, left: 80}
      // graph width
      const width = svg.attr('width') - margin.left - margin.right
      // graph height
      const height = svg.attr('height') - margin.top - margin.bottom
      // graph
      const g = svg.append('g').attr('transform', 'translate(' + margin.left + ', ' + margin.top + ')')

      // graph padding
      const XPAD = 100
      const YPAD = 30
      // vertical line space and padding
      const VERT_SPACE = 80
      const VERT_PAD = 20
      // message space
      const MESSAGE_SPACE = 30

      // message label offset
      const MESSAGE_LABEL_X_OFFSET = -40
      const MESSAGE_LABEL_Y_OFFSET = 75
      const MESSAGE_ARROW_Y_OFFSET = 80
      // node offset
      const NODE_WIDTH = VERT_SPACE - 10
      const NODE_HEIGHT = 25
      const NODE_LABEL_X_OFFSET = -30
      const NODE_LABEL_Y_OFFSET = 25

      // drawn obj
      const nodes = {}
      // const nodeNames = []
      // const messages = []

        
      /**
       * draw vertical line
       * @param {string} name : node name
       * @param {number} index : node index number
       * @param {number} msgLength : number of messages
       */
      const drawVerticalLine = (index: number, msgLength: number) => {
        const line = svg.append("line")
                        .style('stroke', '#888')
                        .attr('x1', XPAD + index * VERT_SPACE)
                        .attr('y1', YPAD + NODE_LABEL_Y_OFFSET)
                        .attr('x2', XPAD + index * VERT_SPACE)
                        .attr('y2', YPAD + VERT_PAD + msgLength * (MESSAGE_SPACE + 5))
        
        svg.attr("height", YPAD*2 + VERT_PAD + msgLength * (MESSAGE_SPACE + 5))
      }

      /**
       * draw node rectangle
       * @param {string} name : node name
       * @param {number} index : node index number
       */
      const drawNode = (name: string, index: number) => {
        const x = XPAD + index * VERT_SPACE
        const nodeRect = svg.append('g')
                            .attr("transform", "translate(" + x + "," + YPAD + ")")
                            .attr('class', 'class-rect')
                            .append("rect")
                            .style("background-color", "white")
                            .attr({x: -NODE_WIDTH/2, y: 0, width: NODE_WIDTH, height: NODE_HEIGHT})

        const nodeLabel = svg.append("g")
                              .attr("transform", "translate(" + x + "," + YPAD + ")")
                              .append("text")
                              .attr("class", "class-label")
                              .attr("text-anchor", "middle")
                              .text((d: any) => { return name })
                              .attr("dy", "16px")
      }

      const drawController = (index: number, messageLength: number) => {
        drawNode("controller", index)
        drawVerticalLine(index, messageLength)
      }

      /**
       * draw message arrow
       * @param {string} message : message  (label)
       * @param {number} index : message index
       * @param {number} senderIndex : message sender index
       * @param {number} receiverIndex : message receiver index
       */
      const drawMessageArrow = (message: string, index: number, senderIndex: number, receiverIndex: number) => {
        // Arrow
        svg.append("svg:defs").append("svg:marker")
            .attr("id", "arrow")
            .attr("refX", 6)
            .attr("refY", 6)
            .attr("markerWidth", 30)
            .attr("markerHeight", 30)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M 0 0 12 6 0 12 3 6")
            .style("fill", "black")

        const y = MESSAGE_ARROW_Y_OFFSET + index * MESSAGE_SPACE
        const line = svg.append("line")
                        .style("stroke", "black")
                        .attr("x1", XPAD + senderIndex * VERT_SPACE)
                        .attr("y1", y)
                        .attr("x2", XPAD + receiverIndex * VERT_SPACE)
                        .attr("y2", y)
                        .attr("marker-end", "url(#arrow)")

        const xPos = XPAD + MESSAGE_LABEL_X_OFFSET + Math.abs(receiverIndex - senderIndex) * VERT_SPACE / 2
        const yPos = MESSAGE_LABEL_Y_OFFSET + index * MESSAGE_SPACE
        const label = svg.append("g")
                          .attr("transform", "translate(" + xPos + ", " + yPos + ")")
                          .append("text")
                          .attr("dx", "5px")
                          .attr("dy", "-2px")
                          .attr("text-anchor", "begin")
                          .style("font-size", "8px")
                          .text((d: any) => {return message})
      }

      /**
       * draw message timestamp
       * @param {number} timestamp : timestamp
       * @param {index} index : message index
       */
      const drawMessageTimestamp = (timestamp: number, index: number) => {
        const xPos = XPAD + MESSAGE_LABEL_X_OFFSET
        const yPos = MESSAGE_LABEL_Y_OFFSET + index * MESSAGE_SPACE
        const date = new Date(timestamp)

        const label = svg.append("g")
                          .attr("transform", "translate(" + xPos + ", " + yPos + ")")
                          .attr("class", "first")
                          .attr("text-anchor", "middle")
                          .append("text")
                          .style("font-size", "8px")
                          .text((d: any) => {return date.toLocaleTimeString()})
      }


      let drawnDatapathes: string[] = []

      /**
       * ノードを描く
       * 
       * TODO: controller
       */
      const drawDatapathes = (datapathes: Datapath[], msgLength: number) => {
        datapathes.forEach((datapath, index) => {
          let name = datapath.getLocalPort()
          if(datapath.getId()){
            name = "dpid=" + datapath.getId().toString()
          }
          index++// controller分足す

          drawNode(name, index)  
          drawVerticalLine(index, msgLength)

          drawnDatapathes.push(datapath.getLocalPort())
        })
      }

      /**
       * draw OpenFlow Message
       */
      const drawMessages = (messages: OpenFlowMessage[]) => {
        const messageLength = messages.length
        messages.forEach((message, index) => {
          // switch to controller
          const datapath_index = drawnDatapathes.indexOf((message.getDatapath() as Datapath).getLocalPort()) + 1
          const controller_index = 0
          if(message.getSwitch2controller()){
            drawMessageArrow(message.getMessageType(), index, datapath_index, controller_index)
          }else{
            drawMessageArrow(message.getMessageType(), index, controller_index, datapath_index)
          }
          drawMessageTimestamp(message.getTimestamp(), index)
        })
      }

      /**
       * update
       */
      const update = (args: any[]) => {
        const datapathes = client.getDatapathes()
        const messages = client.getMessages()

        svg.selectAll("*").remove()
        drawnDatapathes = []

        drawController(0, messages.length)
        drawDatapathes(datapathes, messages.length)
        drawMessages(messages)
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

