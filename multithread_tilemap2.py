# coding: utf-8
from pygeotile.tile import Tile
from urllib import request
import os
import time
from multiprocessing import Pool, TimeoutError, Queue
import threading
import inspect
import ctypes
import socket
import random

socket.setdefaulttimeout(15)

global start_time
start_time = time.time()


def create_image_path(path):
    # path = '%s/%d'%(rootpath, level)
    parent_path = os.path.abspath(os.path.dirname(path))
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)
    return path


def create_image_url(minlon, minlat, maxlon, maxlat, minzoom, maxzoom, basetileurl, rootpath):
    for zoom in range(minzoom, maxzoom + 1):
        mintile = Tile.for_meters(meter_y=minlat, meter_x=minlon, zoom=zoom)
        maxtile = Tile.for_meters(meter_y=maxlat, meter_x=maxlon, zoom=zoom)
        gg = maxtile.google[1]

        print('mintile', 'X:', mintile.tms_x, 'Y:', mintile.tms_y, 'zoom:', mintile.zoom)
        print('maxtile', 'X:', maxtile.tms_x, 'Y:', maxtile.tms_y, 'zoom:', maxtile.zoom)

        mintms_x, mintms_y = mintile.tms_x, mintile.tms_y
        maxtms_x, maxtms_y = maxtile.tms_x, gg

        # create_image_path(rootpath, zoom)

        global imagelists
        imagelists = Queue()
        for x in range(mintms_x, maxtms_x + 1):
            for y in range( maxtms_y,mintms_y, + 1):
                # index = random.randint(0,7)
                savepath = '%s/%d/%d/%d.png' % (rootpath, zoom, x + 1, y)
                create_image_path(savepath)
                # tileurl = basetileurl + '&x=%d&y=%d&l=%d'%(x+1, y, zoom)
                tileurl = basetileurl.replace("{x}", str(x + 1)).replace("{y}", str(y)).replace("{z}", str(zoom))
                # tileurl = tileurl.replace('index', str(index))
                # tileurl = basetileurl + '/%d/%d/%d' % (zoom, x+1, y)
                print(tileurl)
                if not os.path.exists(savepath):
                    imagelists.put((tileurl, savepath))

    return imagelists


def save_image(imagelists):
    while True:
        try:
            print('---- Length', imagelists.qsize())
            if imagelists.empty():
                print("Done!")
                global used_time
                used_time = time.time() - start_time
                print('---- Used time: ', used_time)
                break
            image = imagelists.get()
            tileurl, savepath = image[0], image[1]
            opener = request.build_opener()
            opener.addheaders = [('user-agent',
                                  ' Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36')]
            request.install_opener(opener)
            request.urlretrieve(tileurl, savepath)
            print('---- PID:', os.getpid(), tileurl)
        except Exception as e:
            print('---- Error: {}'.format(e))
            with open('./error.log', 'a') as f:
                f.write('---- Error: {}'.format(e))


def main():
    # 11678927, 329642.6, 14814009.8, 5074968.45
    minlon, minlat = 11678927, 329642  # 矩形区域左下角坐标
    maxlon, maxlat = 14814009, 5074968  # 矩形区域右上角坐标
    minzoom, maxzoom = 1, 8

    # minlon, minlat = 118.02303, - 27.0164 # 矩形区域左下角坐标
    # maxlon, maxlat = 122.9880, - 31.1808 # 矩形区域右上角坐标
    # minzoom, maxzoom = 14, 14

    # 湖州市下载到15级
    # minlon, minlat = 119.23179, - 30.37555  # 矩形区域左下角坐标
    # maxlon, maxlat = 120.48603, - 31.18085  # 矩形区域右上角坐标
    # minzoom, maxzoom = 15, 15

    # 安吉县下载到18级
    # minlon, minlat = 119.231808, - 30.375565  # 矩形区域左下角坐标
    # maxlon, maxlat = 119.885773, - 30.874609  # 矩形区域右上角坐标
    # minzoom, maxzoom = 17, 17

    # basetileurl = 'http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8'
    # basetileurl = 'http://mt2.google.cn/vt/lyrs=s&hl=zh-CN&gl=cn'

    # basetileurl = 'https://elevation3d.arcgis.com/arcgis/rest/services/WorldElevation3D/Terrain3D/ImageServer/tile'
    basetileurl = 'http://139.196.39.225:8081/service/rest/services/cf8cb8de21ad4acbad82699732eae3fc/wmts/tile/1.0.0/default/default028mm/{z}/{y}/{x}.png?token=1eae3679661c450ea94466bfc3ba8328'
    # basetileurl = 'http://wprd04.is.autonavi.com/appmaptile?lang=zh_cn&size=1&style=7&x=%d&y=%d&z=%d&scl=1&ltype=11'%(x, y, zoom)
    # index = random.randint(0, 7)
    # basetileurl = basetileurl.replace('index', str(index))
    # rootpath = 'G:/work/data/tilefile'
    rootpath = 'E:/data/tile/s100_python'

    global threadNum
    threadNum = 10

    imagelists = create_image_url(minlon, minlat, maxlon, maxlat, minzoom, maxzoom, basetileurl, rootpath)
    print('---- Init size', imagelists.qsize())
    if imagelists.qsize() < 8:
        threadNum = 1
    for i in range(threadNum):
        td = threading.Thread(target=save_image, args=(imagelists,))
        td.start()

    # td.stop()
    stop_thread(td)


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


if __name__ == '__main__':
    main()
    # path = 'G:\work\data/tilefile/2/3/3.png'
    # parent_path = os.path.abspath(os.path.dirname(path))
    # print(parent_path)
