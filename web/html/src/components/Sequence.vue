<template>
  <div>
    <button>draw</button>
    <svg id="chart"></svg>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive } from 'vue'
// eslint-disable-next-line
//@ts-ignore
import * as d3 from 'd3'
import { Datapath, OpenFlowMessage } from '../api/api_pb'

export default defineComponent({
  setup() {
    const svg = d3.select('#chart')
    // graph margin
    const margin = {top: 20, right: 50, bottom: 100, left: 80}
    // graph width
    const width = svg.attr('width') - margin.left - margin.right
    // graph height
    const height = svg.attr('height') - margin.top - margin.bottom
    // graph
    const g = svg.append('g').attr('transform', 'translate(' + margin.left, + ', ' + margin.top + ')')

    // graph padding
    const XPAD = 100
    const YPAD = 30
    // vertical line space and padding
    const VERT_SPACE = 50
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
    const verticalLines = {}
    const nodes = {}
    const nodeNames = []
    const messages = []

    /**
     * draw vertical line
     * @param {string} name : node name
     * @param {number} index : node index number
     * @param {number} msgLength : number of messages
     */
    const drawVerticalLine = (name: string, index: number, msgLength: number) => {
      const line = svg.append("line")
                      .style('stroke', '#888')
                      .attr('x1', XPAD + index * VERT_SPACE)
                      .attr('y1', YPAD)
                      .attr('x2', XPAD + index * VERT_SPACE)
                      .attr('y2', YPAD + VERT_PAD + msgLength * (MESSAGE_SPACE + 5))
      verticalLines[name] = line
    }

    /**
     * draw node rectangle
     * @param {string} name : node name
     * @param {number} index : node index number
     */
    const drawNode = (name: string, index: number) => {
      const x = XPAD + index * VERT_SPACE
      const nodeRect = svg.append('g')
                          .attr("transform", "translate")
                          .attr('class', 'class-rect')
                          .append("rect")
                          .attr({x: -NODE_WIDTH/2, y: 0, width: NODE_WIDTH, height: NODE_HEIGHT})
      const nodeLabel = svg.append("g")
                            .attr("transform", "translate(" + x + "," + YPAD + ")")
                            .append("text")
                            .attr("class", "class-label")
                            .attr("text-anchor", "middle")
                            .text((d: any) => { return name })
                            .attr("dy", "16px")
      nodes[name] = [nodeRect, nodeLabel]
      nodeNames.push(name)
    }

    /**
     * draw message arrow
     * @param {string} message : message
     * @param {number} index : message index
     * @param {number} senderIndex : message sender index
     * @param {number} receiverIndex : message receiver index
     */
    const drawMessageArrow = (message: string, index: number, senderIndex: number, receiverIndex: number) => {
      const y = MESSAGE_ARROW_Y_OFFSET + index * MESSAGE_SPACE
      const line = svg.append("line")
                      .style("stroke", "black")
                      .attr("x1", XPAD + senderIndex * VERT_SPACE)
                      .attr("y1", y)
                      .attr("x2", XPAD + receiverIndex * VERT_SPACE)

      const xPos = XPAD + MESSAGE_LABEL_X_OFFSET + (receiverIndex - senderIndex) * VERT_SPACE / 2 + senderIndex * VERT_SPACE + senderIndex * VERT_SPACE
      const yPos = MESSAGE_LABEL_Y_OFFSET + index * MESSAGE_SPACE
      const label = svg.append("g")
                        .attr("transform", "translate(" + xPos + ", " + yPos + ")")
                        .append("text")
                        .attr("dx", "5px")
                        .attr("dy", "-2px")
                        .attr("text-anchor", "begin")
                        .style("font-size", "8px")
                        .text((d: any) => {return message})
      messages.push(line)
    }

    /**
     * draw message timestamp
     * @param {number} timestamp : timestamp
     * @param {index} index : message index
     */
    const drawMessageTimestamp = (timestamp: number, index: number) => {
      const xPos = XPAD + MESSAGE_LABEL_X_OFFSET
      const yPos = MESSAGE_LABEL_Y_OFFSET + index * MESSAGE_SPACE

      const label = svg.append("g")
                        .attr("transform", "translate(" + xPos + ", " + yPos + ")")
                        .attr("class", "first")
                        .attr("text-anchor", "middle")
                        .append("text")
                        .style("font-size", "8px")
                        .text((d: any) => {return timestamp})
    }

    /**
     * ノードを描く
     */
    const drawNodes = (nodes: Datapath[]) => {
      const nodeLength = nodes.length
      nodes.forEach((node, index) => {
        if(nodeNames.indexOf(node.getLocalPort()) === -1){
          drawNode(node.getLocalPort(), index)
          drawVerticalLine(node.getLocalPort(), index, nodeLength)
        }
      })
    }

    const drawMessages = (messages: OpenFlowMessage[], local_ports: string[]) => {
      const messageLength = messages.length
      messages.forEach((message, index) => {
        // switch to controller
        // drawMessageArrow(message.getMessageType(), index, local_ports.indexOf(message.getDatapath().getLocalPort()), 0)
      })
    }

  },
})
</script>


