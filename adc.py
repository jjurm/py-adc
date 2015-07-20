#!/usr/bin/python
#
# Library for SPI-based Analog-to-digital converters.
#
# Author : JJurM
#
# uses spidev to communicate with the chip through SPI interface
#

import spidev

class ADC:

	SINGLE = 1
	DIFF = 0

	def __init__(self, model_class, bus=0, device=0, speed=None):
		self.spi = spidev.SpiDev()
		self.spi.open(bus, device)
		self.model = model_class(self.spi)
		self.spi.max_speed_hz = speed or self.model.max_speed

	def close(self):
		self.spi.close()

	def measure(self, channel, sgl_diff=self.SINGLE):
		''' Measures vallue on given channel with SINGLE or DIFF mode; returns integer value '''
		val = self.model.measure(channel, sgl_diff)
		return val


class AbstractModel:
	''' Abstract model class for MCP series ADCs '''
	
	name = ''
	channels = 8
	resolution = 12  # 4096
	max_speed = 1000000  # 1MHz

	def __init__(self, spi):
		self.spi = spi

	def getBits(self, channel, sgl_diff):
		''' Returns bits to send to ADC for reading '''
		bits = 0b1                                                  # Start bit
		bits = (bits << 1) | sgl_diff                               # SINGLE/DIFF
		bits = (bits << (self.channels-1).bit_length()) | channel   # Data bits (channel select)
		bits = bits << 1                                            # 'don't care' bit for sampling
		bits = bits << 1                                            # null bit
		bits = bits << self.resolution                              # reading value
		return bits

	def bitsToBytes(self, bits):
		''' Converts number to array of bytes after right-padding the bit sequence '''
		bits = bits << (8 - (bits.bit_length() % 8))
		bytes = []
		while bits > 0:
			bytes.insert(0, bits & 0xff)
			bits = bits >> 8
		return bytes

	def process(self, resp):
		''' Processes response (array of bytes) from SPI communication and returns extracted value '''
		dontcare = 0
		dontcare += 1                                # Start bit
		dontcare += 1                                # SINGLE/DIFF
		dontcare += (self.channels-1).bit_length()   # Data bits (channel select)
		dontcare += 1                                # 'don't care' bit for sampling
		dontcare += 1                                # null bit

		# put all bits to string
		bits = self.bytesToBits(resp)
		value = int(bits[dontcare:(dontcare+self.resolution)], 2)
		return value

	def bytesToBits(self, bytes):
		''' Converts array of bytes to string of bits '''
		return "".join(map(lambda x: bin(x)[2:].zfill(8), resp))

	def measure(self, channel, sgl_diff):
		''' Measures value on given channel with SINGLE or DIFF mode; returns integer between 0 and (2^resolution) '''
		bits = self.getBits(channel, sgl_diff)
		data = self.bitsToBytes(bits)
		resp = self.spi.xfer2(data)
		return self.process(resp)


class MCP3208(AbstractModel):

	name = 'MCP3208'
	channels = 8
	resolution = 12  # 4096
	max_speed = 1000000  # 1MHz


if __name__ == '__main__':

    adc = ADC(MCP3208)
    print(adc.measure(0))
