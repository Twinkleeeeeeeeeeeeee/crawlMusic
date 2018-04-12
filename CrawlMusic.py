import requests
import json
from urllib.parse import urlencode
from multiprocessing import Pool
import os
def get_top_list(num):
    url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?tpl=3&page=detail&date=2018_05&topid=26&type=top&song_begin={num}&song_num=30&g_tk=5381&jsonpCallback=MusicJsonCallbacktoplist&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'
    headers={
                'accept':'*/*',
                'accept-encoding':'gzip, deflate, br',
                'accept-language':'zh-CN,zh;q=0.9',
                'referer':'https://y.qq.com/n/yqq/toplist/26.html',
                'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.3'}
    response = requests.get(url.format(num=num),headers=headers)
    if response.status_code == 200:
        return response.text
    return None
def parse_index(html):
    jsl = json.loads(html)
    if 'songlist' in jsl.keys():
        for songlist in jsl.get('songlist'):
            file_name = songlist['data']['strMediaMid']
            songmid = songlist['data'].get('songmid')
            album_id = songlist['data'].get('albumname')
            yield  songmid,file_name,album_id
def get_sec_page(songmid,filename):
    data ={
        'g_tk':' 5381',

        'loginUin':'0',
        'hostUin':'0',
        'format':'json',
        'inCharset':'utf8',
        'outCharset':'utf - 8',
        'notice':'0',
        'platform':'yqq',
        'needNewCode':'0',
        'cid':'205361747',

        'uin':'0',
        'songmid':songmid,
        'filename':'C400'+filename+'.m4a',
        'guid':'402165968'
    }
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.3'}
    url = 'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?'+urlencode(data)
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
       return response.text
    return None
def parse_sec_page(sec_music):
    if sec_music is not  None:
        modify = sec_music.replace('MusicJsonCallback050867258393514136(','')
        map_content = modify.replace(')','')
        js = json.loads(map_content)
        for list in js['data']['items']:
            filename = list['filename']
            vkey = list['vkey']
            yield filename,vkey
def get_last_page(filename,vkey,album_id):
    headers = {
        'Accept':'*/*',
        'Accept-Encoding':'identity;q=1, *;q=0',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Connection':'keep-alive',
        'Host':'dl.stream.qqmusic.qq.com',
        'If-Range':'Wed, 20 Dec 2017 05:47:38 GMT',
        'Range':'bytes=611950-611950',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
    }
    cookie = {'Cookie':'pgv_pvi=7922192384; ptui_loginuin=727884283; pt2gguin=o0727884283; RK=AJ4gf1QFf0; ptcz=28b119670917397df1f6d5a6ccb0d4164bc560225141c1aa31cafca90f8194c4; pgv_pvid=402165968; pgv_info=ssid=s8422556996; pgv_si=s3842669568; qqmusic_fromtag=66'}
    url = 'http://dl.stream.qqmusic.qq.com/'+filename+'?vkey='+vkey+'&guid=402165968&uin=0&fromtag=66'
    response = requests.get(url,headers=headers,cookies=cookie)
    if response.status_code == 200:
         download_file(response.content,album_id)
    return None
def download_file(music,album_id):
    file_path ='{0}/{1}.{2}'.format('E:\music',str(album_id),'m4a')
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            print('正在写入:'+str(album_id))
            f.write(music)
            f.flush()
            print('写入'+album_id+'成功')
def main(num):
    modify = get_top_list(num).replace('MusicJsonCallbacktoplist(','')
    map_content = modify.replace(')','')
    for msinf in parse_index(map_content):
        sec_music = get_sec_page(msinf[0],msinf[1])
        for third_music in parse_sec_page(sec_music):
            get_last_page(third_music[0],third_music[1],msinf[2])
if __name__ == '__main__':
    pool = Pool()
    pool.map(main,[num for num in range(0,270,30)])