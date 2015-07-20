# py-adc

Python library for SPI-based Analog-to-digital converters.

## Usage

```python
from adc import ADC, MCP3208
adc = ADC(MCP3208, bus, device)
val = adc.measure(channel)
adc.close()
```
