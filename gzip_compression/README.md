## Build instructions
Note: For this demo, we are using the branch `2019.2` of https://github.com/Xilinx/Vitis_Libraries

1. Clone the Vitis_Libraries repo:

```$ git clone --single-branch --branch 2019.2 https://github.com/Xilinx/Vitis_Libraries``` 

```$ export VITIS_LIBRARIES_PATH=/path/to/vitis_libraries```

2. For this example, we use the `libz.so` shared library object. First, append a thin C wrapper to the source file `zlib.cpp`:

```$ cat wrapper.c >> $VITIS_LIBRARIES_PATH/data_compression/L3/src/zlib.cpp```

3. Generate the `xclbin` and `libz.so` file

```$ cd $VITIS_LIBRARIES_PATH/data_compression/L3/demos/gzip_hbm && make lib xclbin TARGET=hw DEVICE=xilinx_u50_gen3x16_xdma_201920_3```

Copy them into this directory:

```$ cp -r $VITIS_LIBRARIES_PATH/data_compression/L3/demos/gzip_hbm/build .```

4. This assumes a Python version > 3.6. Install dependencies using:

```$ pip3 install jupyter "dask[complete]" bokeh```

5. Run the Dask scheduler using:

```$ dask-scheduler```

Note the IP address of the scheduler (of the form tcp://x.x.x.x:8786)

6. Run the Dask worker (using the IP above).

```$ dask-worker tcp://x.x.x.x:8786 --nthreads 1 --memory-limit 0 --no-nanny```

7. Run the `dask.ipynb` notebook using jupyter (```$ jupyter notebook```). This notebook contains a Dask client to compress a file using multiple FPGAs, and validates the output using Linux's builtin gzip tool.


### Calculate software baseline
```
    python3 softwarebaseline.py 
```
