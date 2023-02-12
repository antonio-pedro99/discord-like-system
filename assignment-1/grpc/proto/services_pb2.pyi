from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
FAIL: Status
SUCCESS: Status

class Article(_message.Message):
    __slots__ = ["_type", "author", "content", "time"]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    _TYPE_FIELD_NUMBER: _ClassVar[int]
    _type: str
    author: str
    content: str
    time: str
    def __init__(self, _type: _Optional[str] = ..., author: _Optional[str] = ..., time: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class ArticleList(_message.Message):
    __slots__ = ["articleList"]
    ARTICLELIST_FIELD_NUMBER: _ClassVar[int]
    articleList: _containers.RepeatedCompositeFieldContainer[Article]
    def __init__(self, articleList: _Optional[_Iterable[_Union[Article, _Mapping]]] = ...) -> None: ...

class ArticleRequest(_message.Message):
    __slots__ = ["article", "client"]
    ARTICLE_FIELD_NUMBER: _ClassVar[int]
    CLIENT_FIELD_NUMBER: _ClassVar[int]
    article: Article
    client: Client
    def __init__(self, client: _Optional[_Union[Client, _Mapping]] = ..., article: _Optional[_Union[Article, _Mapping]] = ...) -> None: ...

class Client(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class Result(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: Status
    def __init__(self, status: _Optional[_Union[Status, str]] = ...) -> None: ...

class ServerList(_message.Message):
    __slots__ = ["serverList"]
    SERVERLIST_FIELD_NUMBER: _ClassVar[int]
    serverList: _containers.RepeatedCompositeFieldContainer[ServerMessage]
    def __init__(self, serverList: _Optional[_Iterable[_Union[ServerMessage, _Mapping]]] = ...) -> None: ...

class ServerMessage(_message.Message):
    __slots__ = ["address", "name"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    address: str
    name: str
    def __init__(self, name: _Optional[str] = ..., address: _Optional[str] = ...) -> None: ...

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
