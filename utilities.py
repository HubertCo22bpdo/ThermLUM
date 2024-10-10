# ThermLUM - luminescent thermometry data analysis application
# Copyright (C) 2024  Hubert Dzielak 

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
def quantization_to_resolution(value, resolution):
    if value % resolution == 0.0:
        quantized_value = value
    elif value % resolution >= 0.5 * resolution:
        quantized_value = ((value // resolution) * resolution) + resolution
    else:
        quantized_value = (value // resolution) * resolution
    return quantized_value
