import { io, Socket } from 'socket.io-client';
// eslint-disable-next-line
import { OpenFlowMessages, OpenFlowMessage, Datapath, OpenFlowMessageRequest } from '@/api/api_pb'

/**
 * A client connect to the server.
 */
export abstract class RemoteClient{

  /**
   * server ip address
   */
  private ip: string

  /**
   * server port number
   */
  private port: string

  constructor(ip: string, port: string){
    this.ip = ip
    this.port = port
  }

  /**
   * connect to server
   */
  abstract connect(): void

  /**
   * target ip address
   * @returns string
   */
  getIp(){
    return this.ip;
  }

  /**
   * target port number
   * @returns string
   */
  getPort(){
    return this.port
  }
}


/**
 * WebSocket Client
 */
export class WSClient extends RemoteClient {

  /**
   * Socket
   */
  private socket: Socket;

  /**
   * Web Socket Namespace
   */
  private namespace = ""

  private datapathes: Datapath[] = []
  private messages: OpenFlowMessage[] = []

  private handlers: Map<string, any> = new Map()

  constructor(ip: string, port: string, namespace?: string){
    super(ip, port)
    this.namespace = namespace || ""
    this.socket = io('http://' + this.getIp() + ":" + this.getPort() + "/" + this.namespace)
    this.setupEvent()
  }

  setupEvent(){
    this.socket.on("connect", () => {
      console.log("connect!!")
    })
    
    this.socket.on("disconnect", () => {
      console.log("disconnect!!")
    })

    this.socket.on('getOpenFlowMessage', (data) => {
      console.log("get OpenFlow Message =")
      const ofMsg = OpenFlowMessages.deserializeBinary(data)
      console.log(ofMsg)
      ofMsg.getMessagesList().forEach(m => {
        this.messages.push(m)
        const datapath: Datapath = m.getDatapath() as Datapath
        const is_new = this.setDatapath(datapath)
        if(is_new){
          const handler = this.handlers.get("NewNode")
          if(handler !== undefined){
            handler(datapath)
          }
        }
        const handler = this.handlers.get("OpenFlowMessage")
        if(handler !== undefined){
          handler(m)
        }
      })
      const handler = this.handlers.get("getOpenFlowMessage")
      if(handler !== undefined){
        handler(ofMsg.getMessagesList())
      }
    })
    this.socket.on("flowOpenFlowMessage", () => {
      console.log("got message")
    })
  }

  /**
   * connect to server
   */
  connect(){
    this.socket.connect()
  }
  
  /**
   * emit to server
   * @param event : event name
   * @param data : sent data
   */
  emit(event: string, data: any){
    console.log("try to emit event=" + event + " data=" + data)
    this.socket.emit(event, data)
  }

  emitGetOpenFlowMessageRequest(){
    const req = new OpenFlowMessageRequest()
    this.emit("getOpenFlowMessage", req.serializeBinary())
  }

  onGetOpenFlowMessage(handler: (message: OpenFlowMessage[]) => void){
    this.handlers.set("getOpenFlowMessage", handler)
  }

  onOpenFlowMessage(handler: (message: OpenFlowMessage) => void){
    this.handlers.set("OpenFlowMessage", handler)
  }

  onNewNode(handler: (node: Datapath) => void){
    this.handlers.set("NewNode", handler)
  }

  setDatapath(datapath: Datapath): boolean {
    let is_new = true
    this.datapathes.forEach(d => {
      if(d.getLocalPort() === datapath.getLocalPort()){
        d.setId(datapath.getId())
        is_new = false
      }
    })
    if(is_new){
      this.datapathes.push(datapath)
    }
    return is_new
  }

  getDatapathes(): Datapath[]{
    return this.datapathes
  }

  getMessages(): OpenFlowMessage[]{
    return this.messages
  }
}
