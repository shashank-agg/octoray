## Build instructions

1. Install the required python libraries:

```pip3 install numpy bitstring cffi ```

```pip3 install pynq jupyter "dask[complete]" bokeh```

2. Run the dask scheduler using:

```$ dask-scheduler```

3. Run the dask worker (using the IP above).

```$ dask-worker tcp://x.x.x.x:8786 --nthreads 1 --memory-limit 0 --no-nanny```


4. Run the `dask.ipynb` notebook using jupyter (```$ jupyter notebook```). This notebook will download the CIFAR-10 dataset, and classify the images using the accelerator. Note: You have to provide the path to a precompiled `.xclbin` file in the notebook.
