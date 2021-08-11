#from asyncio.windows_events import NULL
import os
import asyncio
import json
#import paddlehub as hub
#import cv2
import time
#from PIL import Image
from operator import methodcaller

from typing import Union
from wechaty.plugin import WechatyPlugin
from wechaty import (
    Contact,
    Room,
    FileBox,
    Message,
    Wechaty,
    ScanStatus,
)

with open('data.json', 'r') as f:
    processes = json.load(f)
with open('pair.json', 'r') as f:
    pair = json.load(f)

curProcess = ''

#model = hub.Module(name="humanseg_lite")
os.environ['WECHATY_PUPPET']="wechaty-puppet-service"
os.environ['WECHATY_PUPPET_SERVICE_TOKEN']="puppet_padlocal_192b712c11a8495fa46317d9b90d8292"
os.environ['WECHATY_PUPPET_SERVICE_ENDPOINT']="182.61.61.97:8090"


class Action(object):
    def __init__(self, msg):
        self.msg = msg

    def Switch(self, cur_Process):
        path = r''
        text: str = self.msg.text()
        if text in cur_Process :
            cur_Process = processes[cur_Process[text]['next']]
            send = cur_Process['question']
        else :
            send = ''
        return send, cur_Process

    def SendMsg(self, cur_Process):
        send = cur_Process['question']
        cur_Process = processes[cur_Process['A00']['next']]
        return send, cur_Process

    def RivcePic(self, cur_Process):
        #img_path = ''
        if 'imgpath' in curProcess :
            img_path  = curProcess['imgpath']
            send = cur_Process['question']
            cur_Process = processes[cur_Process['A00']['next']]
        else :
            send = ''
        return send, cur_Process

    def SendPic(self, cur_Process):
       
        if 'imgpath' in curProcess :
            img_path  = curProcess['imgpath']
            send = FileBox.from_url(img_path)
            #send = cur_Process['question']
            cur_Process = processes[cur_Process['A00']['next']]
        else :
            send = ''
        return send, cur_Process
    

def img_koutu():
    img_path = r'dongman/dongman.jpg'
    # 图片转换后存放的路径
    img_new_path = os.path.join('humanseg_output', 'dongman' + '.png')
    print(img_new_path)
    """   
        res = model.segment(
        paths=[os.path.join(img_path)],
        visualization=True,
        output_dir='humanseg_output')
    # 返回新图片的路径
    while not os.path.exists(img_new_path):
        time.sleep(1)
        """
    return img_new_path


def merge(back_img_path, img_path):
    # import cv2
    # cv2.namedWindow("logo")  # 定义一个窗口
    new_img_path = r'merge/result.png'
    """
    frame = cv2.imread('3.jpg', cv2.IMREAD_COLOR)  # 捕获图像1
    # IMREAD_UNCHANGED  If set, return the loaded image as is (with alpha channel, otherwise it gets cropped).
    # 因此Png必须是4通道的IMREAD_UNCHANGED
    logo = cv2.imread('humanseg_output/dongmantime=1626272659.png', cv2.IMREAD_UNCHANGED)
    rows, cols, channels = logo.shape
    dx, dy = 120, 150
    roi = frame[dx:dx + rows, dy:dy + cols]
    for i in range(rows):
        for j in range(cols):
            if not (logo[i, j][3] == 0):  # 透明的意思
                roi[i, j][0] = logo[i, j][0]
                roi[i, j][1] = logo[i, j][1]
                roi[i, j][2] = logo[i, j][2]
    frame[dx:dx + rows, dy:dy + cols] = roi
    cv2.imwrite(new_img_path, frame)
    """
    return new_img_path


def dongman(img_path, img_name):
    # 图片转换后存放的路径
    img_new_path = r'dongman/dongman.jpg'
    print(img_new_path)
    """
    model = hub.Module(name='animegan_v2_shinkai_33')
    result = model.style_transfer(images=[cv2.imread(img_path)], visualization=True,
                                  output_dir='dongman')
    cv2.imwrite(img_new_path, result[0])
    # 返回新图片的路径
    # while not os.path.exists(img_new_path):
    #     time.sleep(1)
    """
    return img_new_path


class DoProcess(object):
    global curProcess
    def __init__(self, msg):
        self.msg = msg

    def P01(self, cur_Process):
        a = Action(self.msg)
        method = cur_Process['action']
        send = methodcaller(method, cur_Process)(a)   
        return send

    def S01(self, cur_Process):
        cur_Process = processes[processes['start']]
        send = cur_Process['question']
        return send, cur_Process

    def P02(self, cur_Process):

        a = Action(self.msg)
        method = cur_Process['action']
        send = methodcaller(method, cur_Process)(a)   
       # send = self["A00"]
        return send, cur_Process

    def P03(self, cur_Process):
        a = Action(self.msg)
        method = cur_Process['action']
        send = methodcaller(method, cur_Process)(a)
        return send, cur_Process

    def P04(self, cur_Process):
        a = Action(self.msg)
        method = cur_Process['action']
        send = methodcaller(method, cur_Process)(a)
        return send, cur_Process

    def P05(self, cur_Process):
        a = Action(self.msg)
        method = cur_Process['action']
        send = methodcaller(method, cur_Process)(a)
        return send, cur_Process

    def P06(self, cur_Process):
        a = Action(self.msg)
        method = cur_Process['action']
        send = methodcaller(method, cur_Process)(a)  
        return send, cur_Process

def doGame(msg: Message, img_path: str):
    global curProcess
    send = ''
    #if msg.text() == 'show the game': 
    if msg.text() == 's': 
        dp =  DoProcess(msg)
        send = methodcaller('S01', curProcess)(dp) 
    elif curProcess:
        dp =  DoProcess(msg)
        if 'imgpath' in curProcess :
            curProcess['imgpath'] = img_path
        send = methodcaller(curProcess['state'], curProcess)(dp)

    if len(send) > 1 :
        curProcess = send[1]
        return send[0]
    else :
        return ''

async def save_img(msg: Message):
    # 将Message转换为FileBox
    file_box_2 = await msg.to_file_box()
    # 获取图片名
    img_name = file_box_2.name
    # 图片保存的路径
    img_path = './image/' + img_name
    # 将图片保存为本地文件
    await file_box_2.to_file(file_path=img_path)
    return img_path

async def on_message(msg: Message):
    from_contact = msg.talker()
   # if from_contact.is_self :  return
    text = msg.text()
#     room = msg.room()
#     conversation: Union[Room, Contact] = from_contact if room is None else room
#     await conversation.ready()
    #await conversation.say('dong')
    img_path = ''
    # 如果收到的message是一张图片
    if msg.type() == Message.Type.MESSAGE_TYPE_IMAGE:
       # '''
        # 将Message转换为FileBox
        file_box_2 = await msg.to_file_box()
        # 获取图片名
        img_name = file_box_2.name
        # 图片保存的路径
        img_path = './image/' + img_name
        print('img_path=',img_path)
        # 将图片保存为本地文件
        await file_box_2.to_file(file_path=img_path)
     #   '''
        img_path = r'/img/3300177014,1795749502.jpg'
    '''
        # 调用图片风格转换的函数
        img_new_path = dongman(img_path, img_name)
        print(img_new_path)
        img_new_path = img_koutu()
        print(img_new_path)
        img_new_path = merge('3.jpg', img_new_path)
        print(img_new_path)
        # 从新的路径获取图片
        file_box_3 = FileBox.from_file(img_new_path)
        await msg.say(file_box_3)
'''

    send = doGame(msg, img_path = img_path) 
    if len(send) > 0 :
        await conversation.say(send) 

    if msg.text() == 'ding': 
        await msg.say('这是自动回复: dong dong dong')
    if msg.text() == '图片':
        url = 'https://ai.bdstatic.com/file/403BC03612CC4AF1B05FB26A19D99BAF'
        # 构建一个FileBox
        file_box_1 = FileBox.from_url(url=url, name='xx.jpg')
        await conversation.say(file_box_1)
  


async def on_scan(
        qrcode: str,
        status: ScanStatus,
        _data,
):
    print('Status: ' + str(status))
    print('View QR Code Online: https://wechaty.js.org/qrcode/' + qrcode)


async def on_login(user: Contact):
    print(user)


async def main():
    # 确保我们在环境变量中设置了WECHATY_PUPPET_SERVICE_TOKEN
    if 'WECHATY_PUPPET_SERVICE_TOKEN' not in os.environ:
        print('''
            Error: WECHATY_PUPPET_SERVICE_TOKEN is not found in the environment variables
            You need a TOKEN to run the Python Wechaty. Please goto our README for details
            https://github.com/wechaty/python-wechaty-getting-started/#wechaty_puppet_service_token
        ''')

    bot = Wechaty()

    bot.on('scan', on_scan)
    bot.on('login', on_login)
    bot.on('message', on_message)

    await bot.start()

    print('[Python Wechaty] Ding Dong Bot started.')


#asyncio.run(main())

asyncio.run(main())
