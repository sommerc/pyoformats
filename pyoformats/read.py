import os
import numpy as np
import javabridge as jv
import bioformats as bf
from collections import namedtuple

ShapeTZCYX = namedtuple("Shape", ["T", "Z", "C", "Y", "X"])
"""5D shape object"""


class JVM(object):
    """Java Virtual Machine pseudo-singleton
    """

    started = False

    def start(self):
        """Starts the JVM
        """
        if not JVM.started:
            jv.start_vm(class_path=bf.JARS, max_heap_size="8G")
            JVM.started = True

    def shutdown(self):
        if JVM.started:
            jv.kill_vm()


def get_numpy_pixel_type(pixel_type_int):
    """Returns the correct numpy dtype from bioformats.FormatTools integers

    Args:
        pixel_type_int (int): pixel type integer from bioformats.FormatTools

    Raises:
        RuntimeError: if pixel type not understood

    Returns:
        numpy.dtype: the pixel type
    """

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
    """Read the meta data and return the OME metadata object.
    """
    meta = bf.get_omexml_metadata(file_name)
    return bf.omexml.OMEXML(meta)


def file_info(file_name):
    """Displays the name and shape of all available series in file_name

    Args:
        file_name (str): path to file
    """
    JVM().start()

    meta_data = metadata(file_name)

    with bf.ImageReader(file_name) as reader:
        n_series = reader.rdr.getSeriesCount()
        for s in range(n_series):
            reader.rdr.setSeries(s)
            shape = _get_TXCYX_shape(reader)
            name = meta_data.image(s).get_Name()

            print(f"Series {s}: {name}, {shape}")


def _get_TXCYX_shape(reader):
    z_size = reader.rdr.getSizeZ()
    y_size = reader.rdr.getSizeY()
    x_size = reader.rdr.getSizeX()
    c_size = reader.rdr.getSizeC()
    t_size = reader.rdr.getSizeT()

    return ShapeTZCYX(t_size, z_size, c_size, y_size, x_size)


def image_5d(file_name, series=0, rescale=False):
    """Read a single series as 5d numpy array

    Args:
        file_name (str): path to file
        series (int, optional): series to open. Defaults to 0.
        rescale (bool, optional): rescale to min/max. Defaults to False.

    Returns:
        numpy.array: 5d numpy array
    """
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

