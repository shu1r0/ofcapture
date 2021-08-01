// package: 
// file: api.proto

/* tslint:disable */
/* eslint-disable */

import * as jspb from "google-protobuf";

export class Datapath extends jspb.Message { 
    getId(): string;
    setId(value: string): Datapath;
    getLocalPort(): string;
    setLocalPort(value: string): Datapath;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): Datapath.AsObject;
    static toObject(includeInstance: boolean, msg: Datapath): Datapath.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: Datapath, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): Datapath;
    static deserializeBinaryFromReader(message: Datapath, reader: jspb.BinaryReader): Datapath;
}

export namespace Datapath {
    export type AsObject = {
        id: string,
        localPort: string,
    }
}

export class OpenFlowMessage extends jspb.Message { 

    hasDatapath(): boolean;
    clearDatapath(): void;
    getDatapath(): Datapath | undefined;
    setDatapath(value?: Datapath): OpenFlowMessage;
    getXid(): number;
    setXid(value: number): OpenFlowMessage;
    getMessageType(): string;
    setMessageType(value: string): OpenFlowMessage;
    getTimestamp(): number;
    setTimestamp(value: number): OpenFlowMessage;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): OpenFlowMessage.AsObject;
    static toObject(includeInstance: boolean, msg: OpenFlowMessage): OpenFlowMessage.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: OpenFlowMessage, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): OpenFlowMessage;
    static deserializeBinaryFromReader(message: OpenFlowMessage, reader: jspb.BinaryReader): OpenFlowMessage;
}

export namespace OpenFlowMessage {
    export type AsObject = {
        datapath?: Datapath.AsObject,
        xid: number,
        messageType: string,
        timestamp: number,
    }
}
