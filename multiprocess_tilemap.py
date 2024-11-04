## 多进程爬取切片地图
import time

from urllib import request
import os
from multiprocessing import Pool, Queue
import mercantile


# def create_zoom_path(rootpath, level):
#     path = './%s/%d'%(rootpath, level)
#     if not os.path.exists(path):
#         os.makedirs(path)
#     return path


def create_image_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def create_image_url(minlon, minlat, maxlon, maxlat, minzoom, maxzoom, basetileurl, rootpath):
    imagelists = Queue()
    for zoom in range(minzoom, maxzoom + 1):
        # tiles = mercantile.tiles(minlon,minlat,maxlon, maxlat,zoom)
        mintile = mercantile.tile(minlon, maxlat, zoom, truncate=True)
        maxtile = mercantile.tile(maxlon, minlat, zoom, truncate=True)

        print('mintile', 'X:', mintile.x, 'Y:', mintile.y, 'zoom:', mintile.z)
        print('maxtile', 'X:', maxtile.x, 'Y:', maxtile.y, 'zoom:', maxtile.z)

        mintms_x, mintms_y = mintile.x, mintile.y
        maxtms_x, maxtms_y = maxtile.x, maxtile.y

        # create_zoom_path(rootpath, zoom)

        for x in range(mintms_x, maxtms_x + 1):
            create_image_path('./%s/%d/%d' % (rootpath, zoom, x))
            for y in range(mintms_y, maxtms_y + 1):
                savepath = './%s/%d/%d/%d.png' % (rootpath, zoom, x, y)
                if os.path.exists(savepath):
                    continue
                # tileurl = basetileurl + '&x=%d&y=%d&z=%d' % (x, y, zoom)
                tileurl = basetileurl + '/%d/%d/%d' % (zoom, y, x)+'.png'
                imagelists.put((tileurl, savepath))

    return imagelists


def save_image(image):
    try:
        tileurl, savepath = image[0], image[1]
        # 如果文件存在，则不保存
        if os.path.exists(savepath):
            return
        request.urlretrieve(tileurl, savepath)
        print('---- PID:', os.getpid(), tileurl)
    except Exception as e:
        print('---- {}. Error: {}'.format(tileurl, e))
        with open('./multiprocess_error.log', 'a') as f:
            f.write('---- {} Error: {}'.format(tileurl, e))


if __name__ == '__main__':
    # minlon, minlat = -66.10748291, -84  # 矩形区域左下角坐标
    minlon, minlat = 118.019907,24.440990 # 矩形区域左下角坐标
    maxlon, maxlat = 118.034305,24.453179 # 矩形区域右上角坐标
    # maxlon, maxlat =  -64.508972167, 84  # 矩形区域右上角坐标
    minzoom, maxzoom = 19, 19

    # basetileurl = 'http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8'
    # basetileurl = 'https://tiles.arcgis.com/tiles/C8EMgrsFcRFL6LrL/arcgis/rest/services/GEBCO_basemap_NCEI/MapServer/tile'
    # basetileurl = 'https://tiles.arcgis.com/tiles/C8EMgrsFcRFL6LrL/arcgis/rest/services/multibeam_mosaic_hillshade/MapServer/tile'
    # basetileurl = 'http://mt2.google.cn/vt/lyrs=m&hl=zh-CN&gl=cn&x=%d&y=%d&z=%d'%(x, y, zoom)
    # basetileurl = 'http://wprd04.is.autonavi.com/appmaptile?lang=zh_cn&size=1&style=7&x=%d&y=%d&z=%d&scl=1&ltype=11'
    basetileurl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile'
    # basetileurl = 'http://g3.ships66.com/maps/gpi'
    rootpath = './arcgis'
    start_time = time.time()
    imagelists = create_image_url(minlon, minlat, maxlon, maxlat, minzoom, maxzoom, basetileurl, rootpath)
    print('---- Init size', imagelists.qsize())
    p = Pool(processes=8)
    while True:
        print('---- Length', imagelists.qsize())
        if imagelists.empty():  # 为空退出循环结束线程
            print("Done!")
            break
        image = imagelists.get()
        p.apply_async(save_image, args=(image,))

    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    used_time = time.time() - start_time
    print('---- Used time: ', used_time)
