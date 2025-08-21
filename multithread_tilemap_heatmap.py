# coding: utf-8
from pygeotile.tile import Tile
from urllib import request
import os
import time
import threading
import inspect
import ctypes
import socket
import random
import queue
import requests
from functools import partial

socket.setdefaulttimeout(15)

start_time = time.time()
threadNum = 8
download_retries = 1  # 设置下载重试次数
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'


def create_image_path(path):
    parent_path = os.path.abspath(os.path.dirname(path))
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)
    return path


def generate_tile_tasks(minlon, minlat, maxlon, maxlat, minzoom, maxzoom, basetileurl, rootpath):
    """生成瓦片下载任务的生成器，按需生成任务，避免一次性加载所有任务到内存中"""
    for zoom in range(minzoom, maxzoom + 1):
        mintile = Tile.for_latitude_longitude(minlat, minlon, zoom=zoom).google
        maxtile = Tile.for_latitude_longitude(maxlat, maxlon, zoom=zoom).google

        mintms_x = min(mintile[0], maxtile[0])
        mintms_y = min(mintile[1], maxtile[1])
        maxtms_x = max(mintile[0], maxtile[0])
        maxtms_y = max(mintile[1], maxtile[1])

        for x in range(mintms_x, maxtms_x + 1):
            for y in range(mintms_y, maxtms_y + 1):
                savepath = f'{rootpath}/{zoom}/{x + 1}/{y}.png'
                create_image_path(savepath)

                if os.path.exists(savepath):
                    continue  # 如果文件已存在，跳过

                tileurl = basetileurl.replace("{x}", str(x + 1)).replace("{y}", str(y)).replace("{z}", str(zoom))
                yield (tileurl, savepath)


def download_tile(tileurl, savepath, retries=download_retries):
    """下载单个瓦片的函数，支持重试"""
    headers = {'User-Agent': user_agent}
    try:
        response = requests.get(tileurl, headers=headers, timeout=600)
        if response.status_code == 200:
            with open(savepath, 'wb') as f:
                f.write(response.content)
            print(f'Downloaded: {tileurl}')
            return True
        else:
            print(f'Failed to download: {tileurl} (Status code: {response.status_code})')
            return False
    except Exception as e:
        print(f'Error downloading {tileurl}: {e}')
        if retries > 0:
            print(f'Retrying ({retries} left)...')
            return download_tile(tileurl, savepath, retries - 1)
        else:
            with open('./error.log', 'a') as f:
                f.write(f'Error: {e} - URL: {tileurl}\n')
            return False


def worker(task_queue):
    """线程工作函数，从队列中获取任务并执行"""
    while True:
        try:
            task = task_queue.get(timeout=1)  # 设置超时避免阻塞
            if task is None:
                break  # 如果收到None，表示任务结束
            url, path = task
            download_tile(url, path)
            #time.sleep(0.5)  # 下载完成后添加0.5秒的延迟，避免被服务器限制
        except queue.Empty:
            break
        except Exception as e:
            print(f'Worker error: {e}')
        finally:
            task_queue.task_done()


def main():
    # 设置瓦片范围和下载路径
    minlon, minlat = -179.99999, -85 # 矩形区域左下角坐标
    maxlon, maxlat = 179.99999, 85 # 矩形区域右上角坐标
    minzoom, maxzoom = 8, 9
    # basetileurl = 'http://10.10.99.12:8866/maps/one/{z}/{x}/{y}.png'
    basetileurl = 'http://10.10.66.38:8888/tile/green?x={x}&y={y}&z={z}'
    rootpath = 'C:/data/tile/heatmap'

    # 创建任务队列
    task_queue = queue.Queue()

    # 生成任务
    task_generator = generate_tile_tasks(minlon, minlat, maxlon, maxlat, minzoom, maxzoom, basetileurl, rootpath)
    for task in task_generator:
        task_queue.put(task)

    print(f'Total tasks: {task_queue.qsize()}')

    # 动态调整线程数量
    global threadNum
    if task_queue.qsize() < 2:
        threadNum = 1

    # 启动线程
    threads = []
    for _ in range(threadNum):
        t = threading.Thread(target=worker, args=(task_queue,))
        t.start()
        threads.append(t)

    # 等待所有任务完成
    task_queue.join()

    # 停止线程
    for _ in range(threadNum):
        task_queue.put(None)
    for t in threads:
        t.join()

    # 打印总用时
    used_time = time.time() - start_time
    print(f'All tasks completed in {used_time:.2f} seconds')


def _async_raise(tid, exctype):
    """强制终止线程"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Main error: {e}')