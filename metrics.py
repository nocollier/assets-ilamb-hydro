import xarray as xr


def metrics(da: xr.Dataset | xr.DataArray, varname: str | None = None) -> xr.Dataset:
    """
    Return a dataset containing Deeksha's metrics request for the ILAMB Hydro project.

    Parameters
    ----------
    da : xr.Dataset or xr.DataArray
        The dataset containing the variable
    varname: str, optional
        The name of the variable if a xr.Dataset is passed.

    Returns
    -------
    xr.Dataset
        The metrics derived from the input dataset.

    """
    if isinstance(da, xr.Dataset):
        assert varname is not None
        da = da[varname]
    out = {}
    out["annual_mean"] = da.mean(dim="time")  # already in ILAMB
    out["annual_std"] = da.std(dim="time")
    grp = da.groupby("time.year")
    out["seasonal_mean"] = grp.mean().mean(dim="year")
    out["seasonal_std"] = grp.std().mean(dim="year")
    grp = da.groupby("time.year")
    amp = grp.max() - grp.min()
    out["amplitude_mean"] = amp.mean(dim="year")
    out["amplitude_std"] = amp.std(dim="year")
    cycle = da.groupby("time.month").mean()
    out["peak_timing"] = cycle.argmax(dim="month")
    return xr.Dataset(out)


if __name__ == "__main__":
    ds = xr.open_dataset(
        "/lustre/orion/cli137/world-shared/ESGF-data/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Amon/pr/gn/v20181126/pr_Amon_BCC-CSM2-MR_historical_r1i1p1f1_gn_185001-201412.nc"
    ).sel(time=slice("1980-01-01", "2020-01-01"))
    out = metrics(ds, "pr")
    print(out)
