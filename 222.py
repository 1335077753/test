# **********---------global---------****************#
# 网页请求
import requests
# 对变量进行深拷贝
import copy
# 时间、正则
import time, re
# 网页解析
from bs4 import BeautifulSoup as bs
import random

# 请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 Edg/91.0.864.59",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "tieba.baidu.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Microsoft Edge";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}
# 拷贝一个请求头用于评论，等下会补充一个字段
headers_send = copy.copy(headers)
# 获取tbs的接口，tbs用于验证用户身份的有效性
TBS_URL = "http://tieba.baidu.com/dc/common/tbs"
# 贴吧的评论接口
ADD_URL = "https://tieba.baidu.com/f/commit/post/add"

# **********---------get_page---------****************#
"""
url为当前页的地址，tid是帖子唯一标识符，是url中的一串数字
get_page字段默认为False，此时会输出帖子已有的评论
指定为True时，会补齐headers并中断函数
"""


def get_comment(url, tid, get_page=False):
    # 请求帖子的第一页，不需要带cookie
    req = requests.get(url=url, headers=headers)
    # 正则匹配，获取帖子总页数，会匹配到两个字段，都是一样的
    pattern = re.compile('<span class="red">(.*?)</span>')
    page_num = int(re.findall(pattern, req.text)[0])
    # 如果get_page为True，则为headers添加Referer字段
    # 缺少此字段的话，评论发送成功但无法显示
    if get_page:
        headers['Referer'] = 'https://tieba.baidu.com/p/{}?pn={}'.format(tid, page_num)
        print(headers)
        return
    else:
        # 更改编码格式
        req.encoding = 'utf-8'
        # 利用bs4解析网页，抓取评论
        html = bs(req.text, 'lxml')
        comments = html.find_all('div', class_='d_post_content j_d_post_content')
        # 逐条输出，调用strip方法删除开头的空格
        # 注意，无法输出滑稽等泡泡表情（图片什么的更不要想了）
        for comment in comments:
            print(comment.text.strip())
        # 返回帖子总页数，用于抓取余下的评论
        return page_num


# **********---------comment---------****************#
"""
tid为帖子唯一标识符，content为灌水内容
Cookie仅需要BDUSS，tbs用于验证用户身份的合法性
"""


def send_comment(tid, content, Cookie, tbs):
    # 构造post请求所需参数
    data = {
        'tid': tid,
        "tbs": tbs,
        'content': content,
    }
    # 带上参数发起post请求
    req = requests.post(url=ADD_URL, data=data, cookies=Cookie, headers=headers)
    print("1:",req)
    # 获取post请求的response信息，并转换为json字典
    post_status = req.json()
    # 如果发送成功的话，err_code是0
    if post_status['err_code'] == 0:
        print('{}发布成功'.format(content))
    else:
        # 输出错误信息
        print(post_status)


# **********---------control_function---------****************#

# 这里预定义了一个参数，默认为False
# 此时不会发起灌水，而只是获取已有楼层信息
def run(send: bool = False):
    # 要灌水的帖子地址，后面一串星号就是帖子的tid
    url = "https://tieba.baidu.com/p/7260897736"
    # 用split方法将tid分离出来
    tid = url.split('/')[-1]
    # 如果send为False，则输出已有楼层
    if not send:
        # 获取第一页的同时获取总页数
        page_num = get_comment(url=url, tid=tid)
        # 总页数超过一页才有继续执行的必要
        if page_num >= 2:
            for i in range(2, page_num + 1):
                # 拼接当前页的url
                url = "https://tieba.baidu.com/p/{}?pn={}".format(tid, i)
                # 获取当前页的评论
                get_comment(url=url, tid=tid)
                # 身为爬虫一定要有基本的节操....
                time.sleep(3)
    # 如果send为True
    else:
        # 调用get_comment函数补充headers_post
        get_comment(url=url, get_page=True, tid=tid)
        # 在这里写你的BDUSS，至于如何获取，百度一下嘛！
        # Cookie = {'BIDUPSID=9D4EA8C4C3A43F309315FF936E231B3D; PSTM=1608207264; BAIDUID=9D4EA8C4C3A43F30FAD42B5628E7FB5F:FG=1; COOKIE_SESSION=1803643_6_8_1_23_6_0_0_6_5_83_2_1803574_0_3_43_1624418231_1622614628_1624418228%7C9%23228688_6_1622614585%7C3; BDRCVFR[-HoWM-pHJEc]=mk3SLVN4HKm; BD_HOME=1; BD_UPN=12314753; H_PS_PSSID=34099_31660_34004_33607_34107_34135_26350_34213; BDORZ=FAE1F8CFA4E8841CC28A015FEAEE495D; BDUSS=lwYUpKNW5LREExWEFPVkd0R3d-bDRLT1B3MVVnbzJOck5LT3FxekFqREJTUUZoRVFBQUFBJCQAAAAAAAAAAAEAAAAy7lyrdGltZc7ew8XT0NS12LwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMG82WDBvNlgaG; BDUSS_BFESS=lwYUpKNW5LREExWEFPVkd0R3d-bDRLT1B3MVVnbzJOck5LT3FxekFqREJTUUZoRVFBQUFBJCQAAAAAAAAAAAEAAAAy7lyrdGltZc7ew8XT0NS12LwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMG82WDBvNlgaG; BA_HECTOR=05840k0h25258k2hou1gdjf610q'}
        Cookie = {
            'BIDUPSID':'40981D175DB514D5E7A968CD32FEB24D',
            'PSTM':'1605058828',
            'BAIDUID':'40981D175DB514D5044C589EC6FBE295',
            'FG':'1',
            'bdshare_firstime':'1606618918930',
            '__yjs_duid':'1_0a0608bba8f80317ee15f204e85967dc1619618696206',
            'MCITY':'-104%3A',
            'BDORZ':'FFFB88E999055A3F8A630C64834BD6D0',
            'H_PS_PSSID':'',
            'BDSFRCVID':'D5tOJeC62mJQEU6ediIReZD1JmzQytnTH6aoqmtVrD_E9gRYSijCEG0P-M8g0KAMEfHsogKKX2OTHIIF_2uxOjjg8UtVJeC6EG0Ptf8g0f5',
            'H_BDCLCKID_SF':'tRk8oI85JDvDqTrP-trf5DCShUFsKUrrB2Q-XPoO3KJZKJ5PbtOE5l_8W48DBtriW5Ff-UbgylRp8P3y0bb2DUA1y4vpKMnCBeTxoUJ2fP8VJlKzqtnWbJ_ebPRiXTj9QgbAalQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0hD0wD5-bj6PVKgTa54cbb4o2WbCQyJ6N8pcN2b5oQT84qfoaK430ber-hq-hWJ6vOPL63hOUWfAkXpJvQnJjt2JxaqRC5hvN8l5jDh3MebJD24_Le4RO566y0hvcyIocShnVyfjrDRLbXU6BK5vPbNcZ0l8K3l02V-bIe-t2XjQhDHAtq68ttRKs3bRObR-_fb5k-Po_5KCShUFs56FOB2Q-5KL-LqrlMpQkbtOE0-08W48DBqTebg7QafbdJJjob-Jc0pjRKlJ0K-vQXJFJMeTxoUJO5DnJhhvq-4PbMT8ebPRiXTj9QgbAalQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0hD0wD5thj6PVKgTa54cbb4o2WbCQ0C5U8pcN2b5oQT84jJ5aK430LIn-hq-hWJ6vOPQKDpOUWfA3XpJvQnJjt2JxaqRC5M38hp5jDh3MhP_1bhode4ROfgTy0hvcyIocShnVyfjrDRLbXU6BK5vPbNcZ0l8K3l02V-bIe-t2XjQhDN-tt5LefRksQn-8KRrtHJT42DT_bJ3MQaoJWMT-0bFHWlcl3xK-eJbYyq5qWx3LyxcEQRcJaHn7_JjO-R6MS4oeBU_BbpD40UrB3MQxtN4L2CnjtpvN8q5IybbobUPUWa59LUvAWmcdot5yBbc8eIna5hjkbfJBQttjQn3hfIkj0DKLK-oj-D_xD6--3e',
            'BDSFRCVID_BFESS':'D5tOJeC62mJQEU6ediIReZD1JmzQytnTH6aoqmtVrD_E9gRYSijCEG0P-M8g0KAMEfHsogKKX2OTHIIF_2uxOjjg8UtVJeC6EG0Ptf8g0f5',
            'H_BDCLCKID_SF_BFESS': 'tRk8oI85JDvDqTrP-trf5DCShUFsKUrrB2Q-XPoO3KJZKJ5PbtOE5l_8W48DBtriW5Ff-UbgylRp8P3y0bb2DUA1y4vpKMnCBeTxoUJ2fP8VJlKzqtnWbJ_ebPRiXTj9QgbAalQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0hD0wD5-bj6PVKgTa54cbb4o2WbCQyJ6N8pcN2b5oQT84qfoaK430ber-hq-hWJ6vOPL63hOUWfAkXpJvQnJjt2JxaqRC5hvN8l5jDh3MebJD24_Le4RO566y0hvcyIocShnVyfjrDRLbXU6BK5vPbNcZ0l8K3l02V-bIe-t2XjQhDHAtq68ttRKs3bRObR-_fb5k-Po_5KCShUFs56FOB2Q-5KL-LqrlMpQkbtOE0-08W48DBqTebg7QafbdJJjob-Jc0pjRKlJ0K-vQXJFJMeTxoUJO5DnJhhvq-4PbMT8ebPRiXTj9QgbAalQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0hD0wD5thj6PVKgTa54cbb4o2WbCQ0C5U8pcN2b5oQT84jJ5aK430LIn-hq-hWJ6vOPQKDpOUWfA3XpJvQnJjt2JxaqRC5M38hp5jDh3MhP_1bhode4ROfgTy0hvcyIocShnVyfjrDRLbXU6BK5vPbNcZ0l8K3l02V-bIe-t2XjQhDN-tt5LefRksQn-8KRrtHJT42DT_bJ3MQaoJWMT-0bFHWlcl3xK-eJbYyq5qWx3LyxcEQRcJaHn7_JjO-R6MS4oeBU_BbpD40UrB3MQxtN4L2CnjtpvN8q5IybbobUPUWa59LUvAWmcdot5yBbc8eIna5hjkbfJBQttjQn3hfIkj0DKLK-oj-D_xD6--3e',
            'Hm_lvt_98b9d8c2fd6608d564bf2ac2ae642948': '1624885625,1624885821,1624930104,1624943317',
            'USER_JUMP': '1',
            'st_key_id': '17',
            'BDUSS':'WZuUDVnTURMQmhnQ2NvdFlNVVFkSk1ORlVVajk3WUFhUVB-UElqaTRsRWJTUUZoRUFBQUFBJCQAAAAAAAAAAAEAAAAy7lyrdGltZc7ew8XT0NS12LwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABu82WAbvNlge',
            'BDUSS_BFESS':'I1MmJMcFAyTktaVFU2OTZJcUZDV3pYcXJFN3pNVS1WbFlnOEE4aHZvdmdOd0poRUFBQUFBJCQAAAAAAAAAAAEAAAB9KmgrMTIzNDU2cXExNzEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOCq2mDgqtpgZT',
            'STOKEN':'903c4788f89039f6547e4389271f21d65fbfa8786306f79bf08d64e6640517ac',
            'wise_device':'0',
            'delPer':'0',
            'PSINO': '1',
            'BAIDUID_BFESS': 'DFA5E7992237395E1025FC9B356413D3:FG=1',
            'BA_HECTOR':'ak8h8h21ah85a185h21gdlcqk0q',
            'BAIDU_WISE_UID': 'wapp_1624945537642_282',
            'Hm_lpvt_98b9d8c2fd6608d564bf2ac2ae642948':'1624945544',
            'st_data':'e02d4ab85f4b171b49165d2d9ec228bbf1e333bab42739b92361ad27c482fa3cce3b1500961fd78ee77baf7bfa5fdc79836ba8f4f58734bbf0118327720fd9b71ea521ea4fe060c6eff5b38c7a6fb293e8c281181d53afa23f9e5f110854e76d844efa1ded1bcd04cf4a27bc9e52c8d28e090cbc883508a67c0376bb94db4c39',
            'st_sign':'ae975995',
            'ab_sr':'1.0.1_Y2UzYmIxZDI1MDg4YzQzNDU0MDZjZGQwZmU2MTg4ZWIzNzRlNWIyOTI1ZDJlM2M4MzA1Yjg1N2ExMzVkOTVjNGFmNTY1ZTBkNTYyMzdmNDE5MDcxMjVjYzNmNGI4NWEzNTE1YTU1NGI0MThjZmY3MTU0NGYyYjI0MjQ0ODQ1ZDA0OGNhNDM4NmQwNjRlOGJiMWI5MTNkOTRiZmQ0NjZiMg==',}

        # 经验加3，岂不美哉？
        content = '牛逼clas'
        # 获取tbs，获取一次就够了，这里必须带上cookie
        tbs = requests.post(url=TBS_URL, headers=headers, cookies=Cookie).json()['tbs']
        print("2:", tbs)
        """
        开始灌水吧！！！10次不够改成100次
        当然，你肯定不想一直对同一个帖子灌水
        可以写个函数批量获取帖子链接
        本篇博客里面当然没有这种函数
        """
        for i in range(100):
            send_comment(tid=tid, content=content, Cookie=Cookie, tbs=tbs)
            # 暂停10秒，否则百度会化身大禹来治你！
            stop = random.randint(100,180)
            time.sleep(stop)


# 入口函数
if __name__ == '__main__':
    # 要灌水的话把参数改成True
    run(send=True)



