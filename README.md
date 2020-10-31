# Octoray

In this repo, we demonstrate 2 examples of using Dask (https://github.com/dask/dask) to parallelise data analytics using multiple U50 FPGAs.

General architecture:


![Overview](images/architecture-1.png)

1. GZIP accleration using Vitis Data Compression Library
2. CNV accelration using FINN (`cnv_w1a1_u50/`)
