from __important.PluginInterface import PluginInterface



    
class Tlg_msg(PluginInterface):
    load = False
    types = {"source":3, "target":4}
    type_types = "tlg send msg"

    callname = "tlgmsg"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        self.api_id = 12789983
        self.api_hash = "80f5379824352149929686c0c0795e38"
        return True

   

    async def main(self, source, target) -> bool:
        client = TelegramClient('session_name', self.api_id, self.api_hash)
        msg = source
        target_arr = target.split("||") #NotiBot Testing||574288384||chat
        channel_name = target_arr[0]
        chat_id = int(target_arr[1])
        chat_type = target_arr[2]

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        await client.start()
        await client.send_message(chat_id, msg)
        self.logger.success(f"send msg {msg} to {channel_name}")
        await client.disconnect()


    async def getres(self) -> bool:
        client = TelegramClient('session_name', self.api_id, self.api_hash)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        await client.start()
        request = await client(functions.messages.GetDialogFiltersRequest())
        dict_grps = {}
        for dialog_filter in request:
            dict_grps[dialog_filter.title] = []
            for peer in dialog_filter.include_peers:
                #check if item in an InputPeerUser object
                if isinstance(peer, tl.types.InputPeerChat):
                    chat = await client.get_entity(PeerChat(peer.chat_id))
                    #[chat.title, chat.id, "chat"]
                    dict_grps[dialog_filter.title].append([chat.title, chat.id, "chat"])
                elif isinstance(peer, tl.types.InputPeerChannel):
                    channel = await client.get_entity(PeerChannel(peer.channel_id))
                    #[channel.title, peer.channel_id, "channel"]
                    dict_grps[dialog_filter.title].append([channel.title, channel.id, "channel"])
        await client.disconnect()
        return dict_grps
    
    def load_types(self):
        return {"target":["selection_layered", ["Select folder", "select grp/chnl"], asyncio.run(self.getres()) ], "source":["text", "Enter Message"],  "__Name":"tlg send msg"}

        
            
