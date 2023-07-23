from dataclasses import dataclass, field
from typing import List, Optional

from marshmallow import EXCLUDE
import marshmallow_dataclass


@dataclass
class Chat:
    id: int
    type: str
    title: Optional[str]
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]

    class Meta:
        unknown = EXCLUDE


ChatSchema = marshmallow_dataclass.class_schema(Chat)


@dataclass
class MessageFrom:
    id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]
    is_bot: bool = False

    class Meta:
        unknown = EXCLUDE


MessageFromSchema = marshmallow_dataclass.class_schema(MessageFrom)


@dataclass
class Message:
    message_id: int
    message_from: MessageFrom = field(metadata={'data_key': 'from'})
    chat: Chat
    text: Optional[str] = None

    class Meta:
        unknown = EXCLUDE


MessageSchema = marshmallow_dataclass.class_schema(Message)


@dataclass
class UpdateObj:
    update_id: int
    message: Message

    class Meta:
        unknown = EXCLUDE


UpdateObjSchema = marshmallow_dataclass.class_schema(UpdateObj)


@dataclass
class GetUpdatesResponse:
    ok: bool
    result: List[UpdateObj]

    class Meta:
        unknown = EXCLUDE


GetUpdatesResponseSchema = marshmallow_dataclass.class_schema(GetUpdatesResponse)


@dataclass
class SendMessageResponse:
    ok: bool
    result: Message

    class Meta:
        unknown = EXCLUDE


SendMessageResponseSchema = marshmallow_dataclass.class_schema(SendMessageResponse)
