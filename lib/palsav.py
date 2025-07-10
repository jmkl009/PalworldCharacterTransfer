import zlib
import struct

def decompress_sav_to_gvas(data):
    """
    Decompress a Palworld .sav file into a GVAS file.
    
    Args:
        data: The raw bytes of the .sav file.
        
    Returns:
        Tuple of (decompressed_data, save_type, chunk_header)
    """
    # Palworld save files start with a header of 12 bytes.
    # The first 8 bytes are the compressed length, the next 4 bytes are the save type.
    if len(data) < 12:
        raise Exception(f"save file too small: {len(data)}")

    # Extract compressed length and save type from header
    compressed_len = struct.unpack("<Q", data[:8])[0]
    save_type = data[8:12]
    
    # Handle both PlZ (original) and PlM (new format in 0.6 update) formats
    if save_type == b'PlZ':
        # Original format (PlZ)
        uncompressed_data = zlib.decompress(data[12:])
        return uncompressed_data, save_type, data[:12]
    elif save_type == b'PlM':
        # New format introduced in 0.6 update (PlM)
        uncompressed_data = zlib.decompress(data[12:])
        return uncompressed_data, save_type, data[:12]
    else:
        # Unknown format
        raise Exception(f"not a compressed Palworld save, found {save_type} instead of b'PlZ' or b'PlM'")

def compress_gvas_to_sav(gvas_data, save_type, cnk_header=None):
    """
    Compress a GVAS file into a Palworld .sav file.
    
    Args:
        gvas_data: The raw bytes of the GVAS file.
        save_type: The save type, typically b'PlZ' or b'PlM'
        cnk_header: Optional header data to use instead of generating a new one.
        
    Returns:
        The compressed .sav file as bytes.
    """
    compressed_data = zlib.compress(gvas_data)
    
    # If no header is provided, generate one using the current compression length and save type
    if cnk_header is None:
        header = struct.pack("<Q", len(compressed_data)) + save_type
    else:
        # Otherwise use the provided header but update the compressed length
        header = struct.pack("<Q", len(compressed_data)) + cnk_header[8:12]
    
    return header + compressed_data
