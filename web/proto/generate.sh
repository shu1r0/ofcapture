#! /bin/bash

PLUGIN_TS=./node_modules/.bin/protoc-gen-ts
PLUGIN_GRPC=./node_modules/.bin/grpc_tools_node_protoc_plugin
DIST_DIR=./
DIST_DIR_TS=../html/src/api

protoc \
--js_out=import_style=commonjs,binary:"${DIST_DIR_TS}"/ \
--ts_out=import_style=commonjs,binary:"${DIST_DIR_TS}"/ \
--python_out="${DIST_DIR}"/ \
--grpc_out="${DIST_DIR}"/ \
--plugin=protoc-gen-grpc="${PLUGIN_GRPC}" \
--plugin=protoc-gen-ts="${PLUGIN_TS}" \
--proto_path=./ \
-I $DIST_DIR \
./api.proto