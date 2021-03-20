import os
import time

sizes = [100000000, 200000000, 300000000, 400000000,500000000]
print("********** Creating test input files ***********")
for size in sizes:
    file_name = f'random_file_{size}.txt'
    os.system(f'base64 /dev/urandom 2>/dev/null | head -c {size} > {file_name}')

print('*********** Generating GZIP software benchmark ************')
avg_th = 0
for size in sizes:
    file_name = f'random_file_{size}.txt'
    start = time.time()
    os.system(f'gzip -1 -c {file_name} > compressed.gz')
    duration = time.time() - start
    throughput = round((size/(1024*1024))/duration, 2)
    print("File size (MB): ", round(size/(1024*1024),2))
    print("Compression time (s): ", duration)
    avg_th += throughput
avg_th /= len(sizes)
print(f"\n\nAVERAGE GZIP THROUGHPUT: {avg_th} MBps")


print('*********** Generating PIGZ software benchmarks ************')
avg_th = 0
for size in sizes:
    file_name = f'random_file_{size}.txt'
    start = time.time()
    os.system(f'pigz -c {file_name} > compressed.gz')
    duration = time.time() - start
    throughput = round((size/(1024*1024))/duration, 2)
    print("File size (MB): ", round(size/(1024*1024),2))
    print("Compression time (s): ", duration)
    avg_th += throughput
avg_th /= len(sizes)
print(f"\n\nAVERAGE PIGZ THROUGHPUT: {avg_th} MBps")

os.system('rm random_file_*')
os.system('rm compressed.gz')
