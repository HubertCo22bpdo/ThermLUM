def quantization_to_resolution(value, resolution):
    if value % resolution == 0.0:
        quantized_value = value
    elif value % resolution >= 0.5 * resolution:
        quantized_value = ((value // resolution) * resolution) + resolution
    else:
        quantized_value = (value // resolution) * resolution
    return quantized_value