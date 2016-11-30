import argparse
import io
import random
import time
import urllib.request

import PIL.Image


# This is the zoom level. Given an image of size 2500px x 1667px we
# usually use a viewer size of 525px x 350px. This results in each pixel
# of the viewer to represent 4.7619047619px x 4.7628571429px. The zoom level
# can now be used to decrease the ratio up to 1/8 resulting in a representation
# of 0.5952380952px x 0.5953571429px.
# The parameters x0 and y0 start at the top left of the image and
# represent the top left of the viewer. They can also be negative.
# The image returned by the API still contains a watermark. But we
# crop the returned viewer and only take the part below the watermark.
# The stepsize is not perfectly correct now but could be computed
# given the information presented above.
Z = 8


def open_fragment(prefix, id, x, y, width, height):
    """
    :type prefix: str
    :type id: int
    :type x: int
    :type y: int
    :type width: int
    :type height: int
    :rtype: Image
    """
    url = "{}?id={}&x1=0&x0={}&y1=0&y0={}&z={}&width={}&height={}".format(prefix, id, x, y, Z, width, height)
    req = urllib.request.urlopen(url)
    data = req.read()

    print(url)

    return PIL.Image.open(io.BytesIO(data))


def download_loop(prefix, id, width, height, x0_delta, y0_delta, zoom_level):
    full_image = PIL.Image.new("RGB", (width * (zoom_level + 1), height * (zoom_level + 1)))

    crop_x = x0_delta * zoom_level
    crop_y = y0_delta * zoom_level

    # x0 = 0
    # y0 = 0
    # full_x = 0
    # full_y = 0
    x0 = width
    y0 = height
    full_x = width * zoom_level
    full_y = height * zoom_level

    # while y0 < height:
    while y0 > 0:
        x0 = width
        y0 -= y0_delta
        full_x = width * zoom_level
        full_y -= crop_y
        # x0 = 0
        # full_x = 0

        # while x0 < width:
        while x0 > 0:
            x0 -= x0_delta
            full_x -= crop_x
            with open_fragment(prefix, id, x0, y0, width, height) as img:
                full_image.paste(
                    img.crop((0, 0, crop_x, crop_y)),
                    (full_x, full_y))
                full_image.paste(
                    img.crop((width - crop_x, height - crop_y, width, height)),
                    (full_x + width - crop_x, full_y + height - crop_y))
                img.close()

            # x0 += x0_delta
            # full_x += crop_x

            time.sleep(.5 + random.uniform(0, .5))

        # y0 += y0_delta
        # full_y += crop_y

        full_image.save("{}.jpg".format(id))

    return full_image.crop((0, 0, width * zoom_level, height * zoom_level))


def download_portrait(prefix, id):
    width = 266
    height = 400
    x0_delta = 32  # = 266 / 8
    y0_delta = 15  # = 400 / 8 / 3
    zoom_level = 8

    return download_loop(prefix, id, width, height, x0_delta, y0_delta, zoom_level)


def download_landscape(prefix, id):
    width = 400
    height = 266
    x0_delta = 50  # = 400 / 8
    y0_delta = 11  # = 266 / 8 / 3
    zoom_level = 8

    return download_loop(prefix, id, width, height, x0_delta, y0_delta, zoom_level)


def download_id(prefix, id):
    if id < 0:
        id = -id
        img = download_landscape(prefix, id)
    else:
        img = download_portrait(prefix, id)

    print("=== SAVING {} ===".format(id))
    img.save("{}.jpg".format(id))
    img.close()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--url", dest="url_base", type=str, required=True)
    parser.add_argument("ids", metavar='N', type=int, nargs='+',
                        help='list of image integers, prepend "-" for landscape')

    args = parser.parse_args()

    for id in args.ids:
        download_id(args.url_base, id)


if __name__ == '__main__':
    main()
