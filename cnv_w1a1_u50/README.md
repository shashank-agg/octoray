## Build instructions

1. Install the required python libraries:

```pip3 install numpy bitstring cffi ```

```pip3 install pynq jupyter "dask[complete]" bokeh matplotlib```

2. Run the dask scheduler using:

```$ dask-scheduler```

3. Run the dask worker (using the IP from above) in this directory.

```$ XCLBIN_PATH=<path-to-xclbin-file> DEVICE_NAME=<name-of-device> dask-worker tcp://x.x.x.x:8786 --nthreads 1 --memory-limit 0 --no-nanny```

<name-of-device> can be obtained by running the following in a python3 shell:
```python
from pynq import Device
for i in Device.devices:
    print(i.name)
```
Default values:
```
XCLBIN_PATH = a.xclbin
DEVICE_NAME = xilinx_u50_gen3x16_xdma_201920_3
```

4. Run the `dask.ipynb` notebook using jupyter (```$ jupyter notebook```). This notebook will download the CIFAR-10 dataset, and classify the images using the accelerator.
