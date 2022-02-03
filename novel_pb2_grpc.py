# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import novel_pb2 as novel__pb2


class NovelsStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetNovel = channel.unary_unary(
                '/wuxiaworld.api.v2.Novels/GetNovel',
                request_serializer=novel__pb2.GetNovelRequest.SerializeToString,
                response_deserializer=novel__pb2.GetNovelResponse.FromString,
                )


class NovelsServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetNovel(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_NovelsServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetNovel': grpc.unary_unary_rpc_method_handler(
                    servicer.GetNovel,
                    request_deserializer=novel__pb2.GetNovelRequest.FromString,
                    response_serializer=novel__pb2.GetNovelResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'wuxiaworld.api.v2.Novels', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Novels(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetNovel(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/wuxiaworld.api.v2.Novels/GetNovel',
            novel__pb2.GetNovelRequest.SerializeToString,
            novel__pb2.GetNovelResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
