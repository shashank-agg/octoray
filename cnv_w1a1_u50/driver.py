
import argparse
import os
from pynq import Overlay
import numpy as np
from pynq import allocate, Device
import time
from finn.util.data_packing import (
    finnpy_to_packed_bytearray,
    packed_bytearray_to_finnpy
)
from finn.core.datatype import DataType
from pynq.ps import Clocks

class FINNAccelDriver():
    def __init__(self, N, bitfile, platform="alveo", device_name="xilinx_u50_gen3x16_xdma_201920_3"):
        """Instantiate the FINN accelerator driver.
        Gets batchsize (N) as integer and path to bitfile as string."""
        self.platform = platform
        self.N = N
        # input FINN DataType
        self.idt = DataType.UINT8
        # output FINN DataType
        self.odt = DataType.UINT8
        # input and output shapes
        self.ishape_normal = (N, 32, 32, 3)
        self.oshape_normal = (N, 1)
        self.ishape_folded = (N, 32, 32, 1, 3)
        self.oshape_folded = (N, 1, 1)
        self.ishape_packed = (N, 32, 32, 1, 3)   # datatype np.uint8
        self.oshape_packed = (N, 1, 1)  # datatype np.uint8
        # load bitfile and set up accelerator
        self.device = [i for i in Device.devices if i.name == device_name][0]
        Device.active_device = self.device
        self.ol = Overlay(bitfile)
        # neuron folding factor of output = iterations per sample
        self.itersPerSample = self.oshape_packed[-2]
        # clock frequency as specified by user
        self.fclk_mhz = 100.0
        if self.platform == "alveo":
            self.idma = self.ol.idma0
            self.odma = self.ol.odma0
        elif self.platform == "zynq-iodma":
            self.idma = self.ol.idma0
            self.odma = self.ol.odma0
            # set the clock frequency as specified by user during transformations
            if self.fclk_mhz > 0:
                Clocks.fclk0_mhz = self.fclk_mhz
        else:
            raise ValueError("Supported platforms are zynq-iodma alveo")

        # allocate a PYNQ buffer for the packed input and buffer
        if self.platform == "alveo":
            self.ibuf_packed_device = allocate(shape=self.ishape_packed, dtype=np.uint8)
            self.obuf_packed_device = allocate(shape=self.oshape_packed, dtype=np.uint8)
        else:
            self.ibuf_packed_device = allocate(shape=self.ishape_packed, dtype=np.uint8, cacheable=True)
            self.obuf_packed_device = allocate(shape=self.oshape_packed, dtype=np.uint8, cacheable=True)

    def fold_input(self, ibuf_normal):
        """Reshapes input in desired shape.
        Gets input data (ibuf_normal), checks if data is in expected normal shape.
        Returns folded input."""
        # ensure that shape is as expected
        assert ibuf_normal.shape == self.ishape_normal
        # convert to folded form
        ibuf_folded = ibuf_normal.reshape(self.ishape_folded)
        return ibuf_folded

    def pack_input(self, ibuf_folded):
        """Packs folded input and reverses both SIMD dim and endianness.
        Gets input data in folded shape and returns packed input data."""
        ibuf_packed = finnpy_to_packed_bytearray(
            ibuf_folded, self.idt, reverse_endian=True, reverse_inner=True
        )
        return ibuf_packed

    def unpack_output(self, obuf_packed):
        """Unpacks the packed output buffer from accelerator.
        Gets packed output and returns output data in folded shape."""
        obuf_folded = packed_bytearray_to_finnpy(
            obuf_packed, self.odt, self.oshape_folded, reverse_endian=True, reverse_inner=True
        )
        return obuf_folded

    def unfold_output(self, obuf_folded):
        """Unfolds output data to normal shape.
        Gets folded output data and returns output data in normal shape."""
        obuf_normal = obuf_folded.reshape(self.oshape_normal)
        return obuf_normal

    def copy_input_data_to_device(self, data):
        """Copies given input data to PYNQ buffer."""
        np.copyto(self.ibuf_packed_device, data)
        self.ibuf_packed_device.flush()

    def copy_output_data_from_device(self, data):
        """Copies PYNQ output buffer from device."""
        self.obuf_packed_device.invalidate()
        np.copyto(data, self.obuf_packed_device)

    def execute(self):
        """Executes accelerator by setting up the DMA(s) and
        waiting until all transfers/calls complete. Uses only member variables and
        returns nothing."""
        if self.platform == "zynq-iodma":
            # manually launch IODMAs since signatures are missing
            self.idma.write(0x10, self.ibuf_packed_device.device_address)
            self.idma.write(0x1c, self.N)
            self.odma.write(0x10, self.obuf_packed_device.device_address)
            self.odma.write(0x1c, self.N)
            self.idma.write(0x00, 1)
            self.odma.write(0x00, 1)
            # wait until output IODMA is finished
            status = self.odma.read(0x00)
            while status & 0x2 == 0:
                status = self.odma.read(0x00)
        elif self.platform == "alveo":
            idma_handle = self.idma.start_sw(self.ibuf_packed_device, self.N)
            odma_handle = self.odma.start_sw(self.obuf_packed_device, self.N)
            odma_handle.wait()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set exec mode, batchsize N, bitfile name, inputfile name and outputfile name')
    parser.add_argument('--exec_mode', help='Please select functional verification ("execute") or throughput test ("throughput_test")', default="execute")
    parser.add_argument('--platform', help='Target platform: zynq-iodma alveo', default="zynq")
    parser.add_argument('--batchsize', help='number of samples for inference', type=int, default=1)
    parser.add_argument('--bitfile', help='name of bitfile (i.e. "resizer.bit")', default="resizer.bit")
    parser.add_argument('--inputfile', help='name of input npy file (i.e. "input.npy")', default="input.npy")
    parser.add_argument('--outputfile', help='name of output npy file (i.e. "output.npy")', default="output.npy")
    # parse arguments
    args = parser.parse_args()
    exec_mode = args.exec_mode
    platform = args.platform
    N = args.batchsize
    bitfile = args.bitfile
    inputfile = args.inputfile
    outputfile = args.outputfile

    # instantiate FINN accelerator driver and pass batchsize and bitfile
    finnDriver = FINNAccelDriver(N, bitfile, platform)

    # for the remote execution the data from the input npy file has to be loaded,
    # packed and copied to the PYNQ buffer
    if exec_mode == "execute":
        # remove old output file to prevent reusing old output
        # in case execution fails
        try:
            os.remove(outputfile)
        except FileNotFoundError:
            pass
        # load desired input .npy file
        ibuf_normal = np.load(inputfile)
        ibuf_folded = finnDriver.fold_input(ibuf_normal)
        ibuf_packed = finnDriver.pack_input(ibuf_folded)
        finnDriver.copy_input_data_to_device(ibuf_packed)
    elif exec_mode != "throughput_test":
        raise Exception("Exec mode has to be set to remote_pynq or throughput_test")

    # for the throughput test the runtime of the network has to be measured
    if exec_mode == "throughput_test":
        # remove old metrics file
        try:
            os.remove("nw_metrics.txt")
        except FileNotFoundError:
            pass
        # dictionary for results of throughput test
        res={}
        # measure runtime of network
        start = time.time()

    # execute accelerator
    finnDriver.execute()

    # measure run time and fill dictionary with results of the throughput test
    if exec_mode == "throughput_test":
        end = time.time()
        runtime = end - start
        res["runtime[ms]"] = runtime*1000
        res["throughput[images/s]"] = N / runtime
        res["DRAM_in_bandwidth[Mb/s]"] = np.prod(finnDriver.ishape_packed)*0.000001 / runtime
        res["DRAM_out_bandwidth[Mb/s]"] = np.prod(finnDriver.oshape_packed)*0.000001 / runtime
        if platform != "alveo":
            res["fclk[mhz]"] = Clocks.fclk0_mhz
        else:
            res["fclk[mhz]"] = finnDriver.fclk_mhz
        res["N"] = N
        file = open("nw_metrics.txt", "w")
        file.write(str(res))
        file.close()

    # if execution is selected unpack, unfold and save output to output npy file
    else:
        obuf_packed = np.empty_like(finnDriver.obuf_packed_device)
        finnDriver.copy_output_data_from_device(obuf_packed)
        obuf_folded = finnDriver.unpack_output(obuf_packed)
        obuf_normal = finnDriver.unfold_output(obuf_folded)
        np.save(outputfile, obuf_normal)


