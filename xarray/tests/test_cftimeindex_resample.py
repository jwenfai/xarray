from __future__ import absolute_import

import itertools
import pytest
import datetime as dt

import numpy as np
import pandas as pd
import xarray as xr
from xarray.tests import assert_array_equal, assert_identical


# @pytest.mark.parametrize(('start', 'stop'), [(1, 2), (1, 3)])
# def test_nprange(start, stop):
#     assert np.all(np.arange(start, stop) == np.arange(start, stop))


# @pytest.fixture()
# def nprange():
#     return np.arange(1, 10)


# def test_nprange2(nprange):
#     # print(nprange)
#     assert np.all(nprange == nprange)


# @pytest.fixture(params=['MS', 'M'])
@pytest.fixture()
def pd_index():
    return pd.date_range('2000-01-01', periods=30, freq='MS', tz='UTC')


# @pytest.fixture(params=['MS', 'M'])
@pytest.fixture()
def xr_index():
    # return xr.cftime_range('2000', periods=30, freq='MS')
    return xr.cftime_range('2000-01-01', periods=30, freq='MS', tz='UTC')


@pytest.fixture()
def daily_pd_index():
    return pd.date_range('2000-01-01', periods=900, freq='D', tz='UTC')


@pytest.fixture()
def daily_xr_index():
    return xr.cftime_range('2000-01-01', periods=900, freq='D', tz='UTC')


@pytest.fixture()
def base_pd_index():
    return pd.date_range('2000-01-01', periods=30, freq='D', tz='UTC')


@pytest.fixture()
def base_xr_index():
    return xr.cftime_range('2000-01-01', periods=30, freq='D', tz='UTC')


# @pytest.fixture()
# def da(xr_index):
#     return xr.DataArray(np.arange(100., 100.+xr_index.size),
#                         coords=[xr_index], dims=['time'])
#
#
# @pytest.fixture()
# def series(pd_index):
#     return pd.Series(np.arange(100., 100.+pd_index.size), index=pd_index)


def da(index):
    return xr.DataArray(np.arange(100., 100.+index.size),
                        coords=[index], dims=['time'])


def series(index):
    return pd.Series(np.arange(100., 100.+index.size), index=index)


# @pytest.fixture(params=list(itertools.product(['left', 'right'],
#                                               ['left', 'right'],
#                                               ['2MS', '2M', '3MS',
#                                                '3M', '7MS', '7M'])))
# @pytest.fixture(params=list(itertools.product(['left', 'right'],
#                                               ['left', 'right'],
#                                               ['T', '3T', '7T'])))
# def da_resampler(request, da):
#     closed = request.param[0]
#     label = request.param[1]
#     freq = request.param[2]
#     return da.resample(time=freq, closed=closed, label=label).mean()


# @pytest.fixture(params=list(itertools.product(['left', 'right'],
#                                               ['left', 'right'],
#                                               ['MS', '3MS', '7MS'])))
# def series_resampler(request, series):
#     closed = request.param[0]
#     label = request.param[1]
#     freq = request.param[2]
#     return series.resample(freq, closed=closed, label=label).mean()


@ pytest.mark.parametrize(('closed', 'label', 'freq'),
                          list(itertools.product(
                              ['left', 'right'],
                              ['left', 'right'],
                              ['2MS', '2M', '3MS', '3M', '7MS', '7M'])))
def test_downsampler(closed, label, freq):
    downsamp_series = series(pd_index()).resample(
        freq, closed=closed, label=label).mean().dropna()
    downsamp_da = da(xr_index()).resample(
        time=freq, closed=closed, label=label).mean().dropna(dim='time')
    assert np.all(downsamp_series.values == downsamp_da.values)
    assert np.all(downsamp_series.index.strftime('%Y-%m-%dT%T').values ==
                  np.array([timestamp.strftime('%Y-%m-%dT%T') for
                            timestamp in downsamp_da.indexes['time']]))


@ pytest.mark.parametrize(('closed', 'label', 'freq'),
                          list(itertools.product(
                              ['left', 'right'],
                              ['left', 'right'],
                              ['2MS', '2M', '3MS', '3M', 'AS', 'A', '2AS', '2A'])))
def test_downsampler_daily(closed, label, freq):
    downsamp_series = series(daily_pd_index()).resample(
        freq, closed=closed, label=label).mean().dropna()
    downsamp_da = da(daily_xr_index()).resample(
        time=freq, closed=closed, label=label).mean().dropna(dim='time')
    assert np.all(downsamp_series.values == downsamp_da.values)
    assert np.all(downsamp_series.index.strftime('%Y-%m-%dT%T').values ==
                  np.array([timestamp.strftime('%Y-%m-%dT%T') for
                            timestamp in downsamp_da.indexes['time']]))


@ pytest.mark.parametrize(('closed', 'label', 'freq'),
                          list(itertools.product(
                              ['left', 'right'],
                              ['left', 'right'],
                              ['MS', 'M', '7D', 'D'])))
def test_upsampler(closed, label, freq):
    # the testing here covers cases of equal sampling as well
    # for pandas --not xarray--, .ffill() and .bfill() gives
    # error (mismatched length)
    upsamp_series = series(pd_index()).resample(
        freq, closed=closed, label=label).mean().fillna(0)
    upsamp_da = da(xr_index()).resample(
        time=freq, closed=closed, label=label).mean().fillna(0)
    print(upsamp_series.values)
    print(upsamp_da.values)
    print(upsamp_series.index.strftime('%Y-%m-%dT%T').values)
    print(np.array([timestamp.strftime('%Y-%m-%dT%T') for
                    timestamp in upsamp_da.indexes['time']]))
    assert np.all(upsamp_series.values == upsamp_da.values)
    assert np.all(upsamp_series.index.strftime('%Y-%m-%dT%T').values ==
                  np.array([timestamp.strftime('%Y-%m-%dT%T') for
                            timestamp in upsamp_da.indexes['time']]))


@ pytest.mark.parametrize(('closed', 'label', 'base'),
                          list(itertools.product(
                              ['left', 'right'],
                              ['left', 'right'],
                              [1, 5, 12, 17, 24])))
def test_upsampler_base(closed, label, base, freq='12H'):
    upsamp_series = series(base_pd_index()).resample(
        freq, closed=closed, label=label, base=base).mean().dropna()
    upsamp_da = da(base_xr_index()).resample(
        time=freq, closed=closed,
        label=label, base=base).mean().dropna(dim='time')
    # fix for cftime ranges that are 1 second off
    time_ix = upsamp_da.indexes['time'].values
    for ix in np.arange(len(time_ix)):
        if time_ix[ix].second == 59:
            time_ix[ix] += dt.timedelta(seconds=1)
    upsamp_da = upsamp_da.assign_coords(time=time_ix)
    # fix for cftime ranges that are 1 second off
    print(upsamp_series.values)
    print(upsamp_da.values)
    print(upsamp_series.index.strftime('%Y-%m-%dT%T').values)
    print(np.array([timestamp.strftime('%Y-%m-%dT%T') for
                    timestamp in upsamp_da.indexes['time']]))
    assert np.all(upsamp_series.values == upsamp_da.values)
    assert np.all(upsamp_series.index.strftime('%Y-%m-%dT%T').values ==
                  np.array([timestamp.strftime('%Y-%m-%dT%T') for
                            timestamp in upsamp_da.indexes['time']]))
