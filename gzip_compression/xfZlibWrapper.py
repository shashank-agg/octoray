from ctypes import *
import time
import os

class xfZlibWrapper:
    
    def __init__(self, xclbin_path, libzso_path):
        self.lib = cdll.LoadLibrary(libzso_path)
        xfZlib_constructor_wrapper = self.lib.xfZlib_constructor_wrapper
        xfZlib_constructor_wrapper.argtypes = [c_char_p, c_uint8, c_uint8, c_uint8, c_uint8, c_uint8]
        xfZlib_constructor_wrapper.restype = c_void_p

        self.xfZlibObject =  xfZlib_constructor_wrapper(
            c_char_p(xclbin_path),  #binaryFileName
            c_uint8(10),   #max_cr
            c_uint8(0),   #cd_flow
            c_uint8(0),   #device_id
            c_uint8(0),   #profile
            c_uint8(2)   #d_type
        )       

    def compress_file(self, inFilePath, outFilePath):
        inFilePath = inFilePath.encode('utf-8')
        outFilePath = outFilePath.encode('utf-8')
        compress_file_wrapper = self.lib.compress_file_wrapper
        compress_file_wrapper.argtypes = [c_void_p, c_char_p, c_char_p, c_uint64]
        return compress_file_wrapper(
            self.xfZlibObject, 
            inFilePath,
            outFilePath,
            os.path.getsize(inFilePath))
        # return 10
    
    def decompress_file(self, inFilePath, outFilePath):
        decompress_file_wrapper = self.lib.decompress_file_wrapper
        decompress_file_wrapper.argtypes = [c_void_p, c_char_p, c_char_p, c_uint64, c_int]
        return decompress_file_wrapper(
            self.xfZlibObject, 
            inFilePath,
            outFilePath,
            os.path.getsize(inFilePath),
            c_int(0))

    def compress_buffer(self, in_data, inputSize):
        compress_buffer_wrapper = self.lib.compress_buffer_wrapper
        compress_buffer_wrapper.argtypes = [c_void_p, c_char_p, c_void_p, POINTER(c_uint64)]
        compress_buffer_wrapper.restype = POINTER(c_char)

        output_size_ptr =  pointer(c_uint64(5))
        out_data = compress_buffer_wrapper(
            self.xfZlibObject,
            in_data,
            inputSize,
            output_size_ptr
        )
        size = output_size_ptr.contents.value
        return out_data[:size]

if __name__ == '__main__':
    XCLBIN_PATH = b'build/xclbin_xilinx_u50_gen3x16_xdma_201920_3_sw_emu/compress_decompress.xclbin'
    IN_FILE_PATH = 'sample.txt'
    OUT_FILE_PATH = 'sample.gz'
    
    xfZlib = xfZlibWrapper(XCLBIN_PATH)
    size = xfZlib.compress_file(IN_FILE_PATH, OUT_FILE_PATH)
    print(f'Compressed from {os.path.getsize(IN_FILE_PATH)} to {size} bytes')

