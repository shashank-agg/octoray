## Build instructions

1. Install the required python libraries:

```pip3 install numpy bitstring cffi ```

```pip3 install pynq jupyter "dask[complete]" bokeh matplotlib```

2. Run the Dask scheduler using:

```$ dask-scheduler```

3. Run the Dask worker (using the IP from above) in this directory.

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

### Calculate software baseline
Install brevitas:
```
pip install git+https://github.com/Xilinx/brevitas.git
```

To run the evaluation script on CPU:
```
PYTORCH_JIT=1 brevitas_bnn_pynq_train --evaluate --network CNV_1W1A --pretrained --gpus None
```

The output should look like:
```
2021-03-20 15:02:20,712 Test: [0/100]	Model Time 0.476 (0.476)	Loss Time 0.000 (0.000)	Loss 0.1048 (0.1048)	Prec@1 84.000 (84.000)	Prec@5 99.000 (99.000)	
2021-03-20 15:02:21,145 Test: [1/100]	Model Time 0.432 (0.454)	Loss Time 0.000 (0.000)	Loss 0.0806 (0.0927)	Prec@1 89.000 (86.500)	Prec@5 97.000 (98.000)	
2021-03-20 15:02:21,568 Test: [2/100]	Model Time 0.420 (0.443)	Loss Time 0.000 (0.000)	Loss 0.0958 (0.0937)	Prec@1 86.000 (86.333)	Prec@5 100.000 (98.667)	
2021-03-20 15:02:21,988 Test: [3/100]	Model Time 0.419 (0.437)	Loss Time 0.000 (0.000)	Loss 0.0884 (0.0924)	Prec@1 85.000 (86.000)	Prec@5 100.000 (99.000)	
```

Each line corresponds to a batch of 100 images.
```
Avg. throughput (in images/second) = 100/(Average 'Model Time' from logs above)
```
For example, for the logs above, 
```
Avg. throughput = 100/((0.476 + 0.454 + 0.443 + 0.437)/4) = 221 Images/second
```

