import os
import tifffile
import numpy as np
import javabridge as jv
import bioformats as bf

from collections import namedtuple

ShapeTXCYX = namedtuple("Shape", ["T", "Z", "C", "Y", "X"])


class JVM(object):
    # log_config = os.path.join(os.path.split(__file__)[0], "res/log4j.properties")
    started = False

    def start(self):
        if not self.started:
            jv.start_vm(class_path=bf.JARS, max_heap_size="8G")  # ,
            # args=["-Dlog4j.configuration=file:{}".format(self.log_config),],
            # run_headless=True)
            JVM.started = True

    def shutdown(self):
        if self.started:
            jv.kill_vm()


def get_numpy_pixel_type(pixel_type_int):

    if pixel_type_int == 0:
        dype = np.int8
    elif pixel_type_int == 1:
        dtype = np.uint8
    elif pixel_type_int == 2:
        dtype = np.int16
    elif pixel_type_int == 3:
        dtype = np.uint16
    elif pixel_type_int == 4:
        dtype = np.int32
    elif pixel_type_int == 5:
        dtype = np.uint32
    elif pixel_type_int == 6:
        dtype = np.float32
    elif pixel_type_int == 7:
        dtype = np.float64
    else:
        raise RuntimeError(
            f"Error: Pixel-type '{pixel_type_int}' not understood. Must be integer in range(8)"
        )
    return dtype


def metadata(file_name):
    """Read the meta data and return the metadata object.
    """
    meta = bf.get_omexml_metadata(file_name)
    metadata = bf.omexml.OMEXML(meta)
    return metadata


# def get_channel(metadata, channel):
#     """Return the channel name from the metadata object"""
#     try:
#         channel_name = metadata.image().Pixels.Channel(channel).Name
#     except:
#         return

#     if channel_name is None:
#         return
#     return channel_name.replace("/", "_")


def file_info(file_name):
    JVM().start()

    meta_data = metadata(file_name)

    with bf.ImageReader(file_name) as reader:
        n_series = reader.rdr.getSeriesCount()
        for s in range(n_series):
            reader.rdr.setSeries(0)
            shape = _get_TXCYX_shape(reader)
            name = meta_data.image(s).get_Name()

            print(f"Series {0}: {name}, {shape}")


def _get_TXCYX_shape(reader):
    z_size = reader.rdr.getSizeZ()
    y_size = reader.rdr.getSizeY()
    x_size = reader.rdr.getSizeX()
    c_size = reader.rdr.getSizeC()
    t_size = reader.rdr.getSizeT()

    return ShapeTXCYX(t_size, z_size, c_size, y_size, x_size)


def image_5d(file_name, series=0, rescale=False):
    JVM().start()

    with bf.ImageReader(file_name) as reader:
        reader.rdr.setSeries(series)

        dtype = get_numpy_pixel_type(reader.rdr.getPixelType())

        t_size, z_size, c_size, y_size, x_size = _get_TXCYX_shape(reader)

        img_5d = np.zeros((t_size, z_size, c_size, y_size, x_size), dtype=dtype)

        for t in range(t_size):
            for z in range(z_size):
                for c in range(c_size):
                    img_5d[t, z, c, :, :] = reader.read(
                        series=series, z=z, t=t, c=c, rescale=False
                    )
    return img_5d

