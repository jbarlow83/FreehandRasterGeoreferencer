import numpy as np
from osgeo import gdal, ogr


def format(filepath):
    with ogr.ExceptionMgr(useExceptions=True):
        dataset = gdal.Open(filepath, gdal.GA_ReadOnly)
        cols = dataset.RasterXSize
        rows = dataset.RasterYSize
        bands = dataset.RasterCount
        if bands == 0:
            return None
        band = dataset.GetRasterBand(1)
        bandtype = gdal.GetDataTypeName(band.DataType)

        return bands, bandtype, cols, rows


def pixels(filepath):
    with ogr.ExceptionMgr(useExceptions=True):
        dataset = gdal.Open(filepath, gdal.GA_ReadOnly)
        cols = dataset.RasterXSize
        rows = dataset.RasterYSize
        data = dataset.ReadAsArray(0, 0, cols, rows)
        if len(data.shape) == 2:
            # monoband
            data = data.reshape((1, *data.shape))
        return data


def to_byte(data):
    min_ = np.min(data)
    max_ = np.max(data)
    data = 255.0 * (data - min_) / (max_ - min_)
    data = data.astype(np.uint8)
    return data


def save_with_gdal(tmp_filepath, filepath, srs, gt):
    # GDAL requires us to open the temporary file in update mode, even though it will
    # be discarded. It does not allow changing SetGeoTransform unless in this mode.
    with ogr.ExceptionMgr(useExceptions=True):
        dataset = gdal.OpenEx(tmp_filepath, gdal.OF_RASTER | gdal.OF_UPDATE)
        dataset.SetProjection(srs)
        dataset.SetGeoTransform(gt)

        fileformat = "GTiff"
        driver = gdal.GetDriverByName(fileformat)
        dataset_copy = driver.CreateCopy(
            filepath, dataset, strict=0, options=["TILED=YES", "COMPRESS=JPEG"]
        )
        del dataset, driver, dataset_copy
