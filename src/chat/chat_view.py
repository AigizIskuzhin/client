from chat.chat_widget import ChatWidget
from chat.channel_view import ChannelView


class ChatView:
    def __init__(self, chat, controller):
        self._chat = chat
        self._controller = controller
        self._channels = {}
        self.widget = ChatWidget()
        self._chat.channels.added.connect(self._add_channel)
        self._chat.channels.removed.connect(self._remove_channel)
        self._chat.new_server_message.connect(self._new_server_message)
        self._add_channels()

    def _add_channels(self):
        for channel in self._chat.channels.values():
            self._add_channel(channel)

    def _add_channel(self, channel):
        if channel.id_key in self._channels:
            return
        view = ChannelView(channel, self._controller)
        self._channels[channel.id_key] = view
        self.widget.add_channel(view.widget, channel.id_key.name)

    def _remove_channel(self, channel):
        if channel.id_key in self._channels:
            return
        view = self._channels[channel.id_key]
        self.widget.remove_channel(view.widget)
        del self._channels[channel.id_key]

    def _new_server_message(self, msg):
        self.widget.write_server_message(msg)