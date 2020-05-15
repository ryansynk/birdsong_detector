import numpy as np
import librosa
from scipy.fftpack import dct

#Based on http://practicalcryptography.com/miscellaneous/machine-learning/guide-mel-frequency-cepstral-coefficients-mfccs/

#Applying lifter to emphasize higher order coefficients
def lifter(L, num_ceps):
    n = np.arange(0,num_ceps)
    return 1 + (L/2)*np.sin(np.pi*n/L)

def log_mel_spectrum(DFT, mel_filters, Power, H):
    mel_spaced_spectrum = np.zeros((len(DFT),mel_filters))
    #Convolving filters and power spectrum
    for i in range(0,len(Power)):
        data = Power[i]
        for j in range(0,mel_filters):
            filter = H[j]
            mel_spaced_spectrum[i][j] += np.dot(filter,data)
    #Removing instances where value is zero and making it very small values
    mel_spaced_spectrum = np.where(mel_spaced_spectrum == 0,np.finfo(float).eps,mel_spaced_spectrum)
    #Log the spectrum
    return np.log(mel_spaced_spectrum)

#Framing sound file at 16kHz sampling rate into 25ms segments with 10ms steps (overlapping frames)
def get_frames(length_file, samples_p_frame, step, original):
    all_frames = []
    for i in range(0,length_file-samples_p_frame,step):
        frame = np.array([])
        for p in range(i, i + samples_p_frame):
            frame = np.append(frame,original[p])
        all_frames.append(frame)
    all_frames = np.array(all_frames)
    
    return all_frames

def mel_filterbank(sample_rate, mel_filters, fourier_points):
    #Computing the Mel-spaced Filterbank with 26 triangular filters. 
    Lower_freq = 0
    Upper_freq = sample_rate // 2
    Lower_mel = f_to_mel(Lower_freq)    
    Upper_mel = f_to_mel(Upper_freq)   
    length_H = fourier_points//2 + 1
    
    #Range of mel numbers in the range between lower and upper freq
    mel_range = np.linspace(Lower_mel, Upper_mel, mel_filters + 2)
    #Converting to Frequency Range
    freq_range = mel_to_f(mel_range)
    bins = np.floor((fourier_points + 1)*freq_range/sample_rate)
    
    #Getting Filters
    H = np.zeros((mel_filters,length_H))
    for m in range(1,mel_filters+1):
        for k in range(1, length_H + 1):
            if (k < bins[m-1]):
                H[m-1][k-1] = 0
            elif(bins[m-1] <= k and k <= bins[m]):
                H[m-1][k-1] = (k-bins[m-1])/(bins[m] - bins[m-1])
            elif(bins[m] <= k and k <= bins[m+1]):
                H[m-1][k-1] = (bins[m+1] - k)/(bins[m+1] - bins[m])
            elif(k > bins[m+1]):
                H[m-1][k-1] = 0
    H = np.roll(H,1)
    
    return H

#Frequency to Mel
def f_to_mel(f):
   return 1125*np.log(1+f/700)
    
#Mel to Frequency
def mel_to_f(mel):
    return 700*(np.exp(mel/1125)-1)

#Will return a (1000,13) feature vector 
def mfcc(wav_file, user=True ,sample_rate = 16000, frame_length = 0.025, frame_step = 0.01, num_ceps = 20, mel_filters = 40, fourier_points = 512, L = 22):  
    #Step size (16000Hz * frame_step = 160 examples)
    step = int(frame_step*sample_rate)
    #Samples per frame (16000Hz * 0.025 = 400 examples)
    samples_p_frame = int(frame_length*sample_rate)
    #Want feature vector of 1500 rows and 25 columns
    time = (1500*step+samples_p_frame)/sample_rate
    #Will be 15.025 seconds of recorded data
    standard_length = int(sample_rate*time)    

    #Setting Sample Rate 
    original,_ = librosa.load(wav_file, sr=sample_rate)
    if (len(original) < standard_length):
        return None
    
    #Saving first 15.025 seconds of recording to standardize length
    original = original[0:standard_length]
    
    if (user == False):
        return librosa.feature.mfcc(y=original,sr=sample_rate,n_mfcc=num_ceps).T
    
    length_file = len(original)
    #Adding zeros to audio so frames work out nicely
    add_zeros = int(((int(np.ceil((length_file - samples_p_frame)/(frame_step*1000))))*(frame_step*1000)) + 400 - length_file)
    original = np.pad(original, (0, add_zeros), 'constant')
    
    #Framing sound file at 16kHz sampling rate into 25ms segments with 10ms steps (overlapping frames)
    frames = get_frames(length_file, samples_p_frame, step, original)
    
    #Doing Discrete Fourier Transform 
    DFT = np.abs(np.fft.rfft(frames, fourier_points))
    
    #Getting the Power Spectrum of DFT
    Power = 1.0 / fourier_points * np.square(DFT)
    
    #Mel Filterbank
    H = mel_filterbank(sample_rate, mel_filters, fourier_points)
    
    #Getting the mel spaced spectrum for each frame in log (more like human auditory)
    log_mel_spaced_spectrum = log_mel_spectrum(DFT, mel_filters, Power, H)
    
    #Discrete Cosine Transform
    MFCC_no_lifter = dct(log_mel_spaced_spectrum, type=2, axis=1, norm='ortho')[:,:num_ceps]
    
    #Getting Lifter
    lift = lifter(L, num_ceps)
    
    #Applying a Lifter
    return lift*MFCC_no_lifter

if __name__ == "__main__":
    """
    wave_file = "Zenaida-macroura-139840.wav"
    wav_file = "Baeolophus-bicolor-15185.wav"
    wav_file = "Turdus-migratorius-5864.wav"
    result = mfcc(wave_file,user=False).T
    print(result)
    print(result.shape)
    print("")
    result = mfcc(wave_file,user=True)
    print(result)
    print(result.shape)
    """