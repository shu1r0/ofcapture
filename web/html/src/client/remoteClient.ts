
abstract class RemoteClientBase{

  abstract onNewMessage(callback: Function): void
  abstract onNewDevice(callback: Function): void
}

const nodes = []
const messages = []
const local_ports = []

const ws_socket = new WebSocket("ws://localhost:8080/ws")

ws_socket.onopen = (event) => {
  console.log("ws open connection")
  console.log(event)
}
ws_socket.onmessage = (event) => {
  console.log("ws get message")
  console.log(event)
}