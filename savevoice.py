import pyaudio
import struct
import datetime
import wave
import os
import numpy as np

def savevoice(file_sample):

    global THRESHOLD 
    global WIDTH
    global CHANNELS
    global RATE
    global BLOCKSIZE
    global DURATION
    THRESHOLD = 20   # Threshold to start writing to wave file
    WIDTH = 2           # bytes per sample
    CHANNELS = 1
    RATE = 16000        # Sampling rate (samples/second)
    BLOCKSIZE = 1024
    DURATION = 60       # Duration in seconds

    NumBlocks = int( DURATION * RATE / BLOCKSIZE )

    print('  ** Waiting ** ...')

    # Open audio device:
    p = pyaudio.PyAudio()
    PA_FORMAT = p.get_format_from_width(WIDTH)
    stream = p.open(format = PA_FORMAT,
                    channels = 1,
                    rate = RATE,
                    input = True,
                    output = True)
    i = 0
    endTime = 0

    wait = True
    sample_recorded = 0
    avg_fft = [0 for n in range(3)]


    while True:
        fft_sum = 0
        input_string = stream.read(BLOCKSIZE)                     # Read audio input stream

        input_tuple = struct.unpack('h'*BLOCKSIZE, input_string)  # Convert
        output_block = np.array(input_tuple)
        X = np.fft.fft(input_tuple)
        fft_sum += sum(abs(X))

        if wait is True:
            m = max(abs(output_block))
            if m >= THRESHOLD:
                wait = False
                print "Recording..."
                endTime = datetime.datetime.now() + datetime.timedelta(seconds=1)

        process_fft(file_sample, wait, endTime, sample_recorded, stream, avg_fft)

        if(sample_recorded == 1):
            return "{:.6f}".format(avg_fft[file_sample])
        

def process_fft(num, wait, endTime, sample_recorded, stream, avg_fft):
    fft_sum = 0
    num += 1
    output_wavefile = "sample" + str(num) + ".wav"
    # if not os.path.isdir(output_wavefile):
    #     os.mkdir(output_wavefile)
    # os.makedirs(os.path.dirname(output_wavefile), exist_ok=True)
    wf = wave.open(output_wavefile, 'wb')      # wave file
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(WIDTH)
    wf.setframerate(RATE)
    while (wait is False):
        input_string = stream.read(BLOCKSIZE)                     # Read audio input stream
        input_tuple = struct.unpack('h'*BLOCKSIZE, input_string)  # Convert
        output_block = np.array(input_tuple)
        X = np.fft.fft(input_tuple)
        fft_sum += sum(abs(X))
        # Convert values to binary string
        output_string = struct.pack('h' * BLOCKSIZE, *output_block)
        # Write to wave file
        wf.writeframes(output_string)
        if datetime.datetime.now() >= endTime:
            sample_recorded = 1
            wait = True
            print "Finished recording sample " + str(num) 
            avg_fft[num] = fft_sum/(DURATION * RATE)
            print "The average is for the sample " + str(num) + " is ", avg_fft[num]
            break
