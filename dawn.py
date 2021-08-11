"""
Python Wechaty - https://github.com/wechaty/python-wechaty
Authors:    Huan LI (李卓桓) <https://github.com/huan>
            Jingjing WU (吴京京) <https://github.com/wj-Mcat>
2020 @ Copyright Wechaty Contributors <https://github.com/wechaty>
Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import datetime
import os
import asyncio
import random
from typing import List

import requests
import json
import numpy as np
import base64
import cv2
from wechaty_puppet import get_logger
log = get_logger('RoomMemberBot')
from typing import List, Optional
from wechaty import Wechaty, Room, RoomQueryFilter

from PIL import Image
from wechaty import (
    Contact,
    FileBox,
    Message,
    Wechaty,
    ScanStatus,
    Friendship,
    Room,
    RoomInvitation,
)
from wechaty_grpc.wechaty.puppet import MessageType
from wechaty_puppet import EventReadyPayload

os.environ["WECHATY_PUPPET"] = 'wechaty-puppet-service'
os.environ["WECHATY_PUPPET_SERVICE_TOKEN"] = 'puppet_padlocal_6c909d60a7444eeaa106e044de0a6026'

names = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
        'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
        'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
        'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
        'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
        'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
        'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
        'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
        'hair drier', 'toothbrush']
names_CN = {'person':'人', 'bicycle':'自行车', 'car':'汽车', 'motorcycle':'摩托车', 'airplane':'飞机', 'bus':'公共汽车', 'train':'火车', 'truck':'卡车', 'boat':'船', 'traffic light':'红绿灯',
        'fire hydrant':'消防栓', 'stop sign':'停车标志', 'parking meter':'停车计时器', 'bench':'长凳', 'bird':'鸟', 'cat':'猫', 'dog':'狗', 'horse':'马', 'sheep':'羊', 'cow':'牛',
        'elephant':'大象', 'bear':'熊', 'zebra':'斑马', 'giraffe':'长颈鹿', 'backpack':'背包', 'umbrella':'伞', 'handbag':'手提包', 'tie':'领带', 'suitcase':'手提箱', 'frisbee':'飞盘',
        'skis':'滑雪', 'snowboard':'滑雪板', 'sports ball':'运动球', 'kite':'风筝', 'baseball bat':'棒球棒', 'baseball glove':'棒球手套', 'skateboard':'滑板', 'surfboard':'冲浪板',
        'tennis racket':'网球拍', 'bottle':'瓶子', 'wine glass':'酒杯', 'cup':'杯子', 'fork':'叉子', 'knife':'刀', 'spoon':'勺', 'bowl':'碗', 'banana':'香蕉', 'apple':'苹果',
        'sandwich':'三明治', 'orange':'橘子', 'broccoli':'西兰花', 'carrot':'胡萝卜', 'hot dog':'热狗', 'pizza':'比萨', 'donut':'甜甜圈', 'cake':'蛋糕', 'chair':'椅子', 'couch':'沙发',
        'potted plant':'盆栽', 'bed':'床', 'dining table':'餐桌', 'toilet':'厕所', 'tv':'电视', 'laptop':'笔记本', 'mouse':'鼠标', 'remote':'遥控器', 'keyboard':'键盘', 'cell phone':'手机',
        'microwave':'微波炉', 'oven':'烤箱', 'toaster':'烤面包机', 'sink':'水槽', 'refrigerator':'冰箱', 'book':'书', 'clock':'时钟', 'vase':'花瓶', 'scissors':'剪刀', 'teddy bear':'泰迪熊',
        'hair drier':'吹风机', 'toothbrush':'牙刷'}

#功能逻辑记录数组,初始化一个3*10的数组，代表3个功能，10代表每一个功能中的某个子功能模块
LogicArray = [[[0]*10]*3]
# 记录当前发送来的图片名
imagesList = []
# 记录检测后的图片和json文件
outImagesList = []

class pictureSign:
    #生成唯一图片标识符
    def create_uuid(self):
        nowTime = datetime.datetime().strftime("%Y%m%d%H%M%S")
        randomNum = random.randint(0,100)
        if randomNum <10:
            randomNum = str(0)+str(randomNum)
        uniqueNum = str(nowTime)+str(randomNum)
        return  uniqueNum

# 接收发来的图片，存储到images
# def imgSave():
#     img_path = r'./images/'

#在图片上绘制一个框，返回问题答案
def plot_one_box(x, img, color=None, label=None, line_thickness=None):
    # Plots one bounding box on image img
    tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]-x[2]/2), int(x[1]-x[3]/2)), (int(x[0]+x[2]/2), int(x[1]+x[3]/2))
    cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)


async def on_room_topic(self, room: Room, new_topic: str, old_topic: str, changer: Contact, date: datetime):
    print(f'receive room topic changed event <from<{new_topic}> to <{old_topic}>> from room<{room}> ')


async def on_friendship(self, friendship: Friendship):
    print(f'receive friendship<{friendship}> event')


async def on_room_invite(self, room_invitation: RoomInvitation):
    print(f'receive room invitation<{room_invitation}> event')


async def on_room_join(self, room: Room, invitees: List[Contact], inviter: Contact, date: datetime):
    print(f'receive room join event from Room<{room}>')

async def on_room_leave(self, room: Room, leavers: List[Contact], remover: Contact, date: datetime):
    print(f'receive room leave event from Room<{room}>')

async def on_ready(self, payload: EventReadyPayload):
    """Any initialization work can be put in here
    Args:
        payload (EventReadyPayload): ready data
    """
    # 当曙光被@时：
    contacts: List[Contact] = await self.Contact.find_all()
    for contact in contacts:
        print(f'id<{contact.contact_id}>, name<{contact.name}>, type<{contact.type()}>')
    print(f'receive ready event<{payload}>')

    """all of initialization jobs shoule be done here.
     """
    log.info('ready event<%s>', payload)
    # search contact and add them to the specific room
    room: Optional[Room] = await self.Room.find(query=RoomQueryFilter(topic='ef9c032666fdf335b81bd7b192e8e31177642c72b9e244eac9d158d2c87ef2b3'))
    if not room:
        return
    contacts: List[Contact] = await self.Contact.find_all()

    for contact in contacts:
        await contact.ready()
        if contact.name == '骑鱼赶海':
            await room.add(contact)


async def on_message(msg: Message):
    """
    Message Handler for the Bot
    """

    #监听房间所有人员消息

    #启动机器人

    # 接受一张图片
    print("接收数据类型", msg.type())
    if msg.type() == MessageType.MESSAGE_TYPE_IMAGE :

        image_file_box = await msg.to_file_box()
        print(f'saving file<{image_file_box.name}>')
        await image_file_box.to_file(f'./images/{image_file_box.name}')
        imagesList.append(image_file_box.name)
        print("imagesList",imagesList)
        await  msg.say(f"编号82769号星球已成功接受基地发送数据,编号为{str(image_file_box.name)[:-4]}")
    #答题模式
    if len(imagesList)>0 and msg.text()[:4]=='检测图片':
        print("{str(imagesList[-1])[:-4]}",str(imagesList[-1])[:-4])
        print(msg.text())
        if msg.text() == f'检测图片{str(imagesList[-1])[:-4]}':
            # await  msg.say(f"编号{str(imagesList[-1])[:-4]}图片正在飞速发往图片星球，请稍后...")

            image_path = f'./images/{imagesList[-1]}'
            ##当图片存在时，以二进制形式打开图片
            if os.path.exists(image_path):
                print("打开文件！")
                file = open(image_path, mode='rb')
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                    "Connection": "keep-alive",
                    "Host": "36kr.com/newsflashes",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0"
                }

                files = {'file': (f'{str(imagesList[-1])[:-4]}', file, 'image/jpg')}
                print('向服务器发送请求！')
                url = 'http://124.114.22.149:20051/api'
                # url = 'http://127.0.0.1:5000/api'
                re = requests.post(url,headers,files=files)
                if re.status_code == 200:
                    # data = json.loads(re.content)
                    # image = base64.b64encode(bytes(str(data['ImageList']), encoding='utf-8'))
                    # # image = Image.fromarray(np.uint8(np.array(data['ImageList'])))
                    # # 当前图片通道RGB
                    # # r, g, b = image.split()
                    # # img = Image.merge("RGB", [b, g, r])
                    # label = data['message']
                    # # image = base64.decodebytes(data['ImageBytes'])
                    # # img.show()
                    # outImagesList.append(label)
                    # file_box = FileBox.from_base64(image,'label.jpg')
                    # # await  msg.say(f"图片星球分析出",label)
                    # await  msg.say(file_box)

                    data = json.loads(re.content)
                    imgName = data['imageName']
                    boxList = data['resJson']
                    clsList = data['resCls']

                    img = Image.open(f'./images/{imgName}.jpg')
                    imgArray = np.array(img)
                    txt_path = f'./DataBase/boxList/{imgName}'
                    # 收到boxList，绘制
                    for eachbox in boxList:
                        label2 = f"{names_CN[f'{eachbox[-2]}']} {eachbox[-1]*100}"
                        label = '%s %.2f%%' % (eachbox[-2], eachbox[-1]*100)
                        print(label2)
                        plot_one_box(eachbox, imgArray, label=label, color=None, line_thickness=3)
                    img = Image.fromarray(imgArray)
                    # img.show()

                    img.save(f'./DataBase/image/{imgName}.jpg')

                    num = random.randrange(len(clsList))
                    question = f"图片中{names_CN[f'{clsList[num][1]}']}数量是多少呢?"
                    with open(txt_path + '.txt', 'a') as f:
                        for cls in clsList:
                            f.write(('%g %s %g' + '\n') % (num,cls[1], cls[2]))  # label for
                    await msg.say(question)

                else:
                    await  msg.say(f"编号{str(imagesList[-1])[:-4]}图片正在飞速发往图片星球路上被加勒比星球拦截，请重新发送！...")

    if msg.text().split('+')[0][:2] == f'回答' and len(imagesList)>0:
        anserName = str(imagesList[-1])[:-4]
        if msg.text().split('+')[0][2:]==f'{anserName}':
            anserJson = open(f'./DataBase/boxList/{anserName}.txt', mode='r').readlines()
            if len(anserJson)>0:
                #找到出题类别下标
                questionNumIndex = int(anserJson[0].split(' ')[0])
                userAnserNum =  int(msg.text().split('+')[-1])                    #默认用户输入数字
                quesAnser = int(anserJson[questionNumIndex].split(' ')[-1])
                if userAnserNum == quesAnser:
                    await msg.say(f"恭喜你回答正确！答案为{userAnserNum}")
                else:
                    await msg.say("回答错误！可以继续回答或者提示答案！")

            else:
                await msg.say("未检测处类别")

    if msg.text()[:4] == f'图片答案' and len(imagesList)>0 :
        anserName = str(imagesList[-1])[:-4]
        if msg.text()[4:]== anserName:
            img_file_box = FileBox.from_file(f'./DataBase/image/{anserName}.jpg')
            await msg.say(img_file_box)

    if msg.text()[:4] == f'文字答案' and len(imagesList)>0 :
        anserName = str(imagesList[-1])[:-4]
        if msg.text()[4:]== anserName:
            anserJson = open(f'./DataBase/boxList/{anserName}.txt', mode='r').readlines()
            questionNumIndex = int(anserJson[0].split(' ')[0])
            question = anserJson[questionNumIndex].split(' ')[1]
            quesAnser = int(anserJson[questionNumIndex].split(' ')[2])
            await msg.say(f"图片中{names_CN[f'{question}']}数量为{quesAnser}")





    if msg.text() == 'ding':
        # await msg.say('dong')

        file_box = FileBox.from_url(
            'https://ss3.bdstatic.com/70cFv8Sh_Q1YnxGkpoWK1HF6hhy/it/'
            'u=1116676390,2305043183&fm=26&gp=0.jpg',
            name='ding-dong.jpg'
        )
        await msg.say(file_box)


async def on_scan(
        qrcode: str,
        status: ScanStatus,
        _data,
):
    """
    Scan Handler for the Bot
    """
    print('Status: ' + str(status))
    print('View QR Code Online: https://wechaty.js.org/qrcode/' + qrcode)


async def on_login(user: Contact):
    """
    Login Handler for the Bot
    print(f'User {Contact} logged in\n')
    # TODO: To be written
"""


async def main():
    """
    Async Main Entry
    """
    #
    # Make sure we have set WECHATY_PUPPET_SERVICE_TOKEN in the environment variables.
    # Learn more about services (and TOKEN) from https://wechaty.js.org/docs/puppet-services/
    #
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
    bot.on('friendship', on_friendship)
    bot.on('room-topic', on_room_topic)
    bot.on('room-leave', on_room_leave)
    bot.on('room-invite', on_room_invite)
    bot.on('room-join', on_room_join)
    bot.on('ready', on_ready)
    await bot.start()

    print('[Python Wechaty] Ding Dong Bot started.')


asyncio.run(main())
