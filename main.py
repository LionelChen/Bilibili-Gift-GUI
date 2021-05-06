import asyncio
from tkinter import *
import tkinter as tk
import threading
import queue
from blivedm import blivedm

gui_queue = queue.Queue()
ROOM_ID = 22605466
TEST_ROOM_KURI = 22918711
TEST_ROOM_JINGGEGE = 704808
TEST_ROOM_AZA = 21696950
TEST_ROOM_MIELI = 8792912
REVERT_LIST = []  # 撤销礼物删除
GIFT_STAT = 0.0  # 追踪流水信息
RECENT_GIFT = []



def revert_delete(frame):
    last_text = REVERT_LIST.pop()
    b = Button(frame, text=last_text, command=lambda: remove_gift(b))
    b.pack()


def remove_gift(button):
    REVERT_LIST.append(button.cget('text'))
    # print(REVERT_LIST[-1])
    button.pack_forget()


class MyBLiveClient(blivedm.BLiveClient):
    _COMMAND_HANDLERS = blivedm.BLiveClient._COMMAND_HANDLERS.copy()

    async def _on_receive_danmaku(self, danmaku: blivedm.DanmakuMessage):
        print(f'{danmaku.uname}：{danmaku.msg}')
        #global var
        #new_danmu_text = tk.Label(text=danmaku.msg)
        #new_danmu_text.pack()

        #b = Button(bottomframe, text=f'弹幕test信息：\n>>>{danmaku.msg}<<<', command=lambda: remove_gift(b))
        #gift_list.insert(END, b)
        #b.pack(fill = X, pady=5)
        #var.set(danmaku.msg)

        
    async def _on_receive_gift(self, gift: blivedm.GiftMessage):
        global GIFT_STAT
        if gift.coin_type == 'gold':
            price = gift.total_coin * 0.001
            if price >= 0.1:
                b = Button(bottomframe, text=f'{gift.uname} 赠送{gift.gift_name}x{gift.num} （{price}元）', command=lambda: remove_gift(b))
                GIFT_STAT += price
                stat_label_text.set("流水: "+str(GIFT_STAT))
                b.pack(fill=X, pady=5)
            # print(f'>>>>>>{gift.uname} 赠送{gift.gift_name}x{gift.num} （{price}元）<<<<<<')

    async def _on_buy_guard(self, message: blivedm.GuardBuyMessage):
        global GIFT_STAT
        price = round(message.price * 0.001, 3)
        b = Button(bottomframe, text=f'>>>购买舰长:{message.username} {message.gift_name} ¥{price}<<<', command=lambda: remove_gift(b))
        GIFT_STAT += price
        stat_label_text.set("流水: "+str(GIFT_STAT))
        b.pack(fill=X, pady=5)
        # print(f'舰长>>>>>>{message.username} 购买{message.gift_name}<<<<<<')

    async def _on_super_chat(self, message: blivedm.SuperChatMessage):
        global GIFT_STAT
        b = Button(bottomframe, highlightbackground=message.background_price_color,
                   text=f'SC ¥{message.price}{message.uname}：\n>>>{message.message}<<<', command=lambda: remove_gift(b))
        GIFT_STAT += message.price
        stat_label_text.set("流水: "+str(GIFT_STAT))
        b.pack(fill=X, pady=5)
        # print(f'SuperChat>>>>>> ¥{message.price} {message.uname}：{message.message}<<<<<<')


async def danmu_print():
    # 参数1是直播间ID
    # 如果SSL验证失败就把ssl设为False

    #22605466
    client = MyBLiveClient(TEST_ROOM_MIELI, ssl=True)
    future = client.start()
    try:
        await future
    finally:
        await client.close()


def periodicGuiUpdate():
    while True:
        try:
            fn = gui_queue.get_nowait()
        except queue.Empty:
            break
        fn()
    root.after(100, periodicGuiUpdate)


# Run the asyncio event loop in a worker thread.
def start_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(danmu_print())
    loop.run_forever()


threading.Thread(target=start_loop).start()

# Run the GUI main loop in the main thread.
root = tk.Tk()
root.winfo_toplevel().title("礼物记录")
root.geometry("500x800")

# frame = Frame(root)
# frame.pack()
topframe = Frame(root)
topframe.pack(side=TOP, fill=X)
bottomframe = Frame(root)
bottomframe.pack(side=BOTTOM, fill=X)
b = Button(topframe, text="撤销删除", fg="red", command=lambda: revert_delete(bottomframe))
b.pack(side=tk.LEFT, fill=BOTH, padx=10)


stat_label_text = StringVar()
stat_label_text.set("流水: "+str(GIFT_STAT))
stat_label = Label(topframe, textvariable=stat_label_text, relief=RAISED)
stat_label.pack(side=tk.RIGHT, fill=BOTH, padx=10)


#gift_scrollbar = Scrollbar(bottomframe, orient='vertical')

#canvas = tk.Canvas(bottomframe)
#gift_scrollbar.config(bottomframe, orient="vertical", command=canvas.yview)

#scrollable_frame = tk.ttk.Frame(canvas)

"""
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)
"""

# periodicGuiUpdate()
root.mainloop()
