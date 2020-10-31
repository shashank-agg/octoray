extern "C" 
{
    void * xfZlib_constructor_wrapper( char * xclbin_path, uint8_t max_cr, uint8_t cd_flow, uint8_t device_id, uint8_t profile, uint8_t d_type )
    {
        return new xfZlib(xclbin_path, max_cr, cd_flow, device_id, profile, d_type);
    }

    void xfZlib_destructor_wrapper (void *ptr)
    {
         delete ptr; 
    }

    uint64_t compress_file_wrapper(void* ptr, char* inFile_name, char* outFile_name, uint64_t input_size)
    {
        try
        {
            xfZlib * ref = reinterpret_cast<xfZlib *>(ptr);
            std::string str1(inFile_name);
            std::string str2(outFile_name);
            return ref->compress_file(str1, str2, input_size);
        }
        catch(...)
        {
           return -1; //assuming -1 is an error condition. 
        }
    }

    uint64_t decompress_file_wrapper(void* ptr, char* inFile_name, char* outFile_name, uint64_t input_size, int cu_run)
    {
        try
        {
            xfZlib * ref = reinterpret_cast<xfZlib *>(ptr);
            std::string str1(inFile_name);
            std::string str2(outFile_name);
            return ref->decompress_file(str1, str2, input_size, cu_run);
        }
        catch(...)
        {
           return -1; //assuming -1 is an error condition. 
        }
    }
}