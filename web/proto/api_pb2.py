# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: api.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='api.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\tapi.proto\"*\n\x08\x44\x61tapath\x12\n\n\x02id\x18\x01 \x01(\t\x12\x12\n\nlocal_port\x18\x02 \x01(\t\"d\n\x0fOpenFlowMessage\x12\x1b\n\x08\x64\x61tapath\x18\x01 \x01(\x0b\x32\t.Datapath\x12\x0b\n\x03xid\x18\x02 \x01(\x03\x12\x14\n\x0cmessage_type\x18\x03 \x01(\t\x12\x11\n\ttimestamp\x18\x04 \x01(\x02\x62\x06proto3'
)




_DATAPATH = _descriptor.Descriptor(
  name='Datapath',
  full_name='Datapath',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Datapath.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='local_port', full_name='Datapath.local_port', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=13,
  serialized_end=55,
)


_OPENFLOWMESSAGE = _descriptor.Descriptor(
  name='OpenFlowMessage',
  full_name='OpenFlowMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='datapath', full_name='OpenFlowMessage.datapath', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='xid', full_name='OpenFlowMessage.xid', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='message_type', full_name='OpenFlowMessage.message_type', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='OpenFlowMessage.timestamp', index=3,
      number=4, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=57,
  serialized_end=157,
)

_OPENFLOWMESSAGE.fields_by_name['datapath'].message_type = _DATAPATH
DESCRIPTOR.message_types_by_name['Datapath'] = _DATAPATH
DESCRIPTOR.message_types_by_name['OpenFlowMessage'] = _OPENFLOWMESSAGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Datapath = _reflection.GeneratedProtocolMessageType('Datapath', (_message.Message,), {
  'DESCRIPTOR' : _DATAPATH,
  '__module__' : 'api_pb2'
  # @@protoc_insertion_point(class_scope:Datapath)
  })
_sym_db.RegisterMessage(Datapath)

OpenFlowMessage = _reflection.GeneratedProtocolMessageType('OpenFlowMessage', (_message.Message,), {
  'DESCRIPTOR' : _OPENFLOWMESSAGE,
  '__module__' : 'api_pb2'
  # @@protoc_insertion_point(class_scope:OpenFlowMessage)
  })
_sym_db.RegisterMessage(OpenFlowMessage)


# @@protoc_insertion_point(module_scope)
