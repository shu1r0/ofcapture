//@ts-ignore
import * as d3 from 'd3'


import { Datapath, OpenFlowMessage } from '../api/api_pb'


export class Sequence {

  private svg: any

  private margin  = {top: 20, right: 50, bottom: 100, left: 80}

  // graph padding
  private XPAD = 100
  private YPAD = 30

  // vertical line space and padding
  private VERT_SPACE = 80
  private VERT_PAD = 20

  // message space
  private MESSAGE_SPACE = 30

  // message label offset
  private MESSAGE_LABEL_X_OFFSET = -40
  private MESSAGE_LABEL_Y_OFFSET = 75
  private MESSAGE_ARROW_Y_OFFSET = 80

  // node offset
  private NODE_WIDTH = this.VERT_SPACE - 10
  private NODE_HEIGHT = 25
  private NODE_LABEL_X_OFFSET = -30
  private NODE_LABEL_Y_OFFSET = 25

  private drawnDatapathes: string[] = []

  constructor(id: string){
    this.svg = d3.select(id)
  }

  reset(){
    this.svg.selectAll("*").remove()
  }

  /**
   * draw vertical line
   * @param {string} name : node name
   * @param {number} index : node index number
   * @param {number} msgLength : number of messages
   */
  private drawVerticalLine(index: number, msgLength: number){
    const line = this.svg.append("line")
                    .style('stroke', '#888')
                    .attr('x1', this.XPAD + index * this.VERT_SPACE)
                    .attr('y1', this.YPAD + this.NODE_LABEL_Y_OFFSET)
                    .attr('x2', this.XPAD + index * this.VERT_SPACE)
                    .attr('y2', this.YPAD + this.VERT_PAD + msgLength * (this.MESSAGE_SPACE + 5))
    
    this.svg.attr("height", this.YPAD*2 + this.VERT_PAD + msgLength * (this.MESSAGE_SPACE + 5))
  }

  /**
   * draw node rectangle
   * @param {string} name : node name
   * @param {number} index : node index number
   */
  private drawNode(name: string, index: number){
    const x = this.XPAD + index * this.VERT_SPACE
    const nodeRect = this.svg.append('g')
                        .attr("transform", "translate(" + x + "," + this.YPAD + ")")
                        .attr('class', 'class-rect')
                        .append("rect")
                        .style("background-color", "white")
                        .attr({x: - this.NODE_WIDTH/2, y: 0, width: this.NODE_WIDTH, height: this.NODE_HEIGHT})

    const nodeLabel = this.svg.append("g")
                          .attr("transform", "translate(" + x + "," + this.YPAD + ")")
                          .append("text")
                          .attr("class", "class-label")
                          .attr("text-anchor", "middle")
                          .text((d: any) => { return name })
                          .attr("dy", "16px")
  }

  drawController(index: number, messageLength: number){
    this.drawNode("controller", index)
    this.drawVerticalLine(index, messageLength)
  }

  /**
   * draw message arrow
   * @param {string} message : message  (label)
   * @param {number} index : message index
   * @param {number} senderIndex : message sender index
   * @param {number} receiverIndex : message receiver index
   */
  private drawMessageArrow(message: string, index: number, senderIndex: number, receiverIndex: number){
    // Arrow
    this.svg.append("svg:defs").append("svg:marker")
      .attr("id", "arrow")
      .attr("refX", 6)
      .attr("refY", 6)
      .attr("markerWidth", 30)
      .attr("markerHeight", 30)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M 0 0 12 6 0 12 3 6")
      .style("fill", "black")

    const y = this.MESSAGE_ARROW_Y_OFFSET + index * this.MESSAGE_SPACE
    const line = this.svg.append("line")
                    .style("stroke", "black")
                    .attr("x1", this.XPAD + senderIndex * this.VERT_SPACE)
                    .attr("y1", y)
                    .attr("x2", this.XPAD + receiverIndex * this.VERT_SPACE)
                    .attr("y2", y)
                    .attr("marker-end", "url(#arrow)")

    const xPos = this.XPAD + this.MESSAGE_LABEL_X_OFFSET + Math.abs(receiverIndex - senderIndex) * this.VERT_SPACE / 2
    const yPos = this.MESSAGE_LABEL_Y_OFFSET + index * this.MESSAGE_SPACE
    const label = this.svg.append("g")
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
  private drawMessageTimestamp(timestamp: number, index: number){
    const xPos = this.XPAD + this.MESSAGE_LABEL_X_OFFSET
    const yPos = this.MESSAGE_LABEL_Y_OFFSET + index * this.MESSAGE_SPACE
    const date = new Date(timestamp * 1000)
    const time = date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds() + "." + date.getMilliseconds()

    const label = this.svg.append("g")
                      .attr("transform", "translate(" + xPos + ", " + yPos + ")")
                      .attr("class", "first")
                      .attr("text-anchor", "middle")
                      .append("text")
                      .style("font-size", "8px")
                      .text((d: any) => {return time})
  }

  /**
   * ノードを描く
   * 
   * TODO: controller
   */
  drawDatapathes(datapathes: Datapath[], msgLength: number){
    datapathes.forEach((datapath, index) => {
      let name = datapath.getLocalPort()
      if(datapath.getId()){
        name = "dpid=" + datapath.getId().toString()
      }
      index++// controller分足す

      this.drawNode(name, index)  
      this.drawVerticalLine(index, msgLength)

      this.drawnDatapathes.push(datapath.getLocalPort())
    })
  }

  /**
   * draw OpenFlow Message
   */
  drawMessages(messages: OpenFlowMessage[]){
    const messageLength = messages.length
    messages.forEach((message, index) => {
      // switch to controller
      const datapath_index = this.drawnDatapathes.indexOf((message.getDatapath() as Datapath).getLocalPort()) + 1
      const controller_index = 0
      if(message.getSwitch2controller()){
        this.drawMessageArrow(message.getMessageType(), index, datapath_index, controller_index)
      }else{
        this.drawMessageArrow(message.getMessageType(), index, controller_index, datapath_index)
      }
      this.drawMessageTimestamp(message.getTimestamp(), index)
    })
  }

  getDrawnDatapathes(){
    return this.drawnDatapathes
  }

  setDrawnDatapathes(datapathes: string[]){
    this.drawnDatapathes = datapathes
  }

  getWidth(){
    return this.svg.attr('width') - this.margin.left - this.margin.right
  }
}