from model.chat.channel import Channel, Lines
from model.chat.chatter import Chatter
from model.chat.channelchatter import ChannelChatter
from enum import Enum


class ChatController:
    def __init__(self, connection, model, autojoin_channels):
        self._connection = connection
        self._model = model
        self._autojoin_channels = autojoin_channels

        c = connection
        c.new_line.connect(self._at_new_line)
        c.new_channel_chatters.connect(self._at_new_channel_chatters)
        c.channel_chatters_left.connect(self._at_channel_chatters_left)
        c.chatters_quit.connect(self._at_chatters_quit)
        c.quit_channel.connect(self._at_quit_channel)
        c.chatter_renamed.connect(self._at_chatter_renamed)
        c.new_chatter_elevation.connect(self._at_new_chatter_elevation)
        c.new_channel_topic.connect(self._at_new_channel_topic)
        c.connected.connect(self._at_connected)
        c.disconnected.connect(self._at_disconnected)
        c.new_server_message.connect(self._at_new_server_message)

    @property
    def _channels(self):
        return self._model.channels

    @property
    def _chatters(self):
        return self._model.chatters

    @property
    def _ccs(self):
        return self._model.channelchatters

    def _check_add_new_channel(self, cid):
        if cid not in self._channels:
            channel = Channel(cid, Lines(), "")
            self._channels[cid] = channel
        return self._channels[cid]

    def _check_add_new_chatter(self, cinfo):
        if cinfo.name not in self._chatters:
            chatter = Chatter(cinfo.name, cinfo.hostname)
            self._chatters[chatter.name] = chatter
        return self._chatters[cinfo.name]

    def _add_or_update_cc(self, cid, cinfo):
        channel = self._check_add_new_channel(cid)
        chatter = self._check_add_new_chatter(cinfo)
        key = (channel.id_key, chatter.id_key)
        if key not in self._ccs:
            cc = ChannelChatter(channel, chatter, cinfo.elevation)
            self._ccs[key] = cc
        else:
            self._ccs[key].update(elevation=cinfo.elevation)

    def _remove_cc(self, cid, cinfo):
        key = (cid, cinfo.name)
        del self._ccs[key]

    def _at_new_line(self, line, cid):
        if cid not in self._channels:
            return
        self._channels[cid].lines.add_line(line)

    def _at_new_channel_chatters(self, cid, chatters):
        for c in chatters:
            self._add_or_update_cc(cid, c)

    def _at_channel_chatters_left(self, cid, chatters):
        for c in chatters:
            self._remove_cc(cid, c)

    def _at_chatters_quit(self, chatters):
        for c in chatters:
            del self._chatters[c.name]

    def _at_quit_channel(self, cid):
        del self._channels[cid]

    def _at_chatter_renamed(self, old, new):
        if old not in self._chatters:
            return
        self._chatters[old].update(name=new)

    def _at_new_chatter_elevation(self, cid, chatter, added, removed):
        key = (cid, chatter.name)
        if key not in self._ccs:
            return
        cc = self._ccs[key]
        old = cc.elevation
        new = ''.join(c for c in old + added if c not in removed)
        cc.update(elevation=new)

    def _at_new_channel_topic(self, cid, topic):
        channel = self._channels.get(cid)
        if channel is None:
            return
        channel.update(topic=topic)

    def _at_connected(self):
        for channel in self._autojoin_channels:
            self._connection.join(channel)

    def _at_disconnected(self):
        self._channels.clear()
        self._chatters.clear()
        self._ccs.clear()

    def _at_new_server_message(self, msg):
        self._model.add_server_message(msg)

    # User actions start here.
    def send_message(self, cid, message):
        action, msg = MessageAction.parse_message(message)
        if action == MessageAction.MSG:
            self._connection.send_message(cid.name, msg)
        elif action == MessageAction.PRIVMSG:
            chatter_name, msg = msg.split(" ", 1)
            self._connection.send_message(chatter_name, msg)
        elif action == MessageAction.ME:
            self._connection.send_action(cid.name, msg)
        elif action == MessageAction.SEEN:
            self._connection.send_action("nickserv", "info {}".format(msg))
        elif action == MessageAction.TOPIC:
            self._connection.set_topic(cid.name, msg)
        elif action == MessageAction.JOIN:
            self._connection.join(msg)
        else:
            pass    # TODO - raise 'Sending failed' error back to the view?


class MessageAction(Enum):
    MSG = "message"
    UNKNOWN = "unknown"
    PRIVMSG = "/msg "
    ME = "/me "
    SEEN = "/seen "
    TOPIC = "/topic "
    JOIN = "/join "

    @classmethod
    def parse_message(cls, msg):
        if not msg.startswith("/"):
            return cls.MSG, msg

        for cmd in cls:
            if cmd in [cls.MSG, cls.UNKNOWN]:
                continue
            if msg.startswith(cmd.value):
                return cmd, msg[len(cmd.value):]

        return cls.UNKNOWN, msg