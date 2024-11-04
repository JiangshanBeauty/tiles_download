# -*- coding:utf-8 -*-
"""
@author: Allen-bWFv
@contact: allen95bwfv@gmail.com
@time: 2024/11/01 17:05
@desc:
"""

import os
import shutil

import mercantile


def create_zoom_path(rootpath, level):
    path = '%s/%d'%(rootpath, level)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def create_image_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path
def create_image_url(minlon, minlat, maxlon, maxlat, minzoom, maxzoom, rootpath):
    for zoom in range(minzoom, maxzoom + 1):
        mintile = mercantile.tile(minlon, maxlat, zoom, truncate=True)
        maxtile = mercantile.tile(maxlon, minlat, zoom, truncate=True)

        print('mintile', 'X:', mintile.x, 'Y:', mintile.y, 'zoom:', mintile.z)
        print('maxtile', 'X:', maxtile.x, 'Y:', maxtile.y, 'zoom:', maxtile.z)

        mintms_x, mintms_y = mintile.x, mintile.y
        maxtms_x, maxtms_y = maxtile.x, maxtile.y

        create_zoom_path(rootpath, zoom)

        for x in range(mintms_x, maxtms_x + 1):
            create_image_path('./%s/%d/%d' % (rootpath, zoom, x))
            for y in range(mintms_y, maxtms_y + 1):
                destination_path = '%s/%d/%d/%d.png' % (rootpath, zoom, x, y)
                if os.path.exists(destination_path):
                    continue
                # 确保目标路径的目录存在
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                source_path = "/data/tile/gyp" + '/%d/%d/%d' % (zoom, x, y)+'.png'
                if os.path.exists(source_path):
                    shutil.copy2(source_path, destination_path)
                    print(f"文件已从 {source_path} 拷贝到 {destination_path}")




if __name__ == '__main__':
    # minlon, minlat = -66.10748291, -84  # 矩形区域左下角坐标
    # minlon, minlat = 118.019907,24.440990 # 矩形区域左下角坐标
    minlon, minlat = 117.918818,24.287999 # 矩形区域左下角坐标
    # maxlon, maxlat = 118.034305,24.629263 # 矩形区域右上角坐标
    maxlon, maxlat = 118.518946,24.629263 # 矩形区域右上角坐标
    # maxlon, maxlat =  -64.508972167, 84  # 矩形区域右上角坐标
    minzoom, maxzoom = 1, 19

    rootpath = '/home/arcgiscopy'
    create_image_url(minlon, minlat, maxlon, maxlat, minzoom, maxzoom, rootpath)