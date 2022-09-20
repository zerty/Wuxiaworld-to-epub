#Initial code from sonora https://github.com/public/sonora but i need to understand how this works

import undetected_chromedriver as uc
import base64
import functools
import struct
import io

from time import sleep
from urllib.parse import urljoin

_HEADER_FORMAT = ">BI"
_HEADER_LENGTH = struct.calcsize(_HEADER_FORMAT)


def insecure_web_channel(url):
    return WebChannel(url)


class WebChannel:
    def __init__(self, url):
        if not url.startswith("http") and "://" not in url:
            url = f"http://{url}"
        self._url = url
        self._session = uc.Chrome()
        self._session.get(url)
        self._metadata = [
            ("content-type", "application/grpc-web+proto")
        ]
        sleep(5.5)
    def __enter__(self):
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        pass
    def unary_unary(self,path, request_serializer, response_deserializer):
        return UnaryUnaryMulticallable(self._session, self._url,self._metadata,  path, request_serializer, response_deserializer)
    def unary_stream(self, path, request_serializer, response_deserializer):
        pass
    def stream_unary(self, path, request_serializer, response_deserializer):
        pass
    def stream_stream(self, path, request_serializer, response_deserializer):
        pass



class UnaryUnaryMulticallable:
    def __init__(self, session, url,metadata, path, request_serializer, response_deserializer):
        self._session=session
        self._serializer = request_serializer
        self._deserializer = response_deserializer
        self._url = url
        self._path = path
        self._rpc_url = urljoin(url, path)
        self._metadata=metadata

    def __call__(self, request, timeout=None, metadata=None):
        self._request=request
        self.call_metadata = self._metadata.copy()
        if metadata is not None:
            self.call_metadata.extend(self.encode_headers(metadata))
        if timeout is not None:
            self.call_metadata.append(("grpc-timeout", protocol.serialize_timeout(timeout)))
        self._response=self._session.execute_script("""
            var payload=new Uint8Array(%s);
            var resp = await fetch ('%s',{ method: 'POST',  redirect: 'follow',  headers: { 'content-type': 'application/grpc-web+proto'}, body:payload});
            var data= await resp.arrayBuffer();
            var datauint = new Uint8Array(data);
            return datauint;
        """%(list(self.wrap_message(False, False, self._serializer(self._request))),self._rpc_url))
        buffer = io.BytesIO(bytes(list(self._response)))
        messages = self.unwrap_message_stream(buffer)
        trailers, _, message = next(messages)
        result = self._deserializer(message)
        return result
          




    def  _unpack_header_flags(self,flags):
        trailers = 1 << 7
        compressed = 1

        return bool(trailers & flags), bool(compressed & flags)


    def encode_headers(self,metadata):
        for header, value in metadata:
            if isinstance(value, bytes):
                if not header.endswith("-bin"):
                    raise ValueError("binary headers must have the '-bin' suffix")
                value = base64.b64encode(value).decode("ascii")

            if isinstance(header, bytes):
                header = header.decode("ascii")

            yield header, value

    def wrap_message(self,trailers, compressed, message):
        return (
            struct.pack(
                _HEADER_FORMAT, self._pack_header_flags(trailers, compressed), len(message)
            )
            + message
        )
    def _pack_header_flags(self,trailers, compressed):
        return (trailers << 7) | (compressed)

    def unwrap_message_stream(self,stream):
        data = stream.read(_HEADER_LENGTH)

        while data:
            flags, length = struct.unpack(_HEADER_FORMAT, data)
            trailers, compressed = self._unpack_header_flags(flags)

            yield trailers, compressed, stream.read(length)

            if trailers:
                break

            data = stream.read(_HEADER_LENGTH)
