# -*- coding: utf-8 -*-
"""Pytorch_backend.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FplETlCgg-NhcHjAJDdKB4B2UE93sXfS
"""

import torch
import torch.nn as nn
import torchaudio
import torchaudio.functional as F
import torchaudio.transforms as T

import os

#import lmdb
import pickle

from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import numpy as np

from scipy.io import wavfile

print(torch.__version__)

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"
print(f"Using device {device}")

# LMDB_DIR = "./content/drive/MyDrive/tese/ESC50/lmdb/spec"
PATH_BEST = "./audio/model/best_model.pt"
MODEL_PATH = PATH_BEST

PATH_BEST_S = "./audio/model_s/best_model.pt"
MODEL_PATH_S = PATH_BEST_S

truncate = True

SAMPLE_RATE = 44100
NUM_SAMPLES = 2**15-1 ##2**16-1 - aproximadamente 4 segundos ou 5*16000
n_fft = 1024
n_mel = 128            ##128
cached = False

n_layers_vae = 4
n_dimensions = 128
x_latent = int(n_mel/(2**n_layers_vae))
y_latent = int((2*(NUM_SAMPLES+1)/n_fft)/(2**n_layers_vae))
unflatten_size = (n_dimensions, x_latent, y_latent) ##(32, 16, 16)

latent_dims = 256

batch_size = 64

normalize_dataset_db = False
ref_level_db = 20
min_level_db = -100

skip_connections = False

generated_i = 0

class VariationalEncoder(nn.Module):
    def __init__(self, latent_dims, min_val, max_val):
        super(VariationalEncoder, self).__init__()
        self.conv1 = nn.Conv2d(1, 16, 3, stride=2, padding=1)
        self.inorm1 = nn.InstanceNorm2d(16)
        self.conv2 = nn.Conv2d(16, 32, 3, stride=2, padding=1)
        self.inorm2 = nn.InstanceNorm2d(32)
        self.conv3 = nn.Conv2d(32, 64, 3, stride=2, padding=1)
        self.inorm3 = nn.InstanceNorm2d(64)
        self.conv4 = nn.Conv2d(64, 128, 3, stride=2, padding=1)
        self.inorm4 = nn.InstanceNorm2d(128)

        self.linear1 = nn.Linear(n_dimensions * x_latent * y_latent, 1024)
        self.linear2 = nn.Linear(1024, latent_dims)
        self.linear3 = nn.Linear(1024, latent_dims)
        self.relu = nn.ReLU()

        self.N = torch.distributions.Normal(0, 1)
        self.kl = 0

        self.min_val = min_val
        self.max_val = max_val


    def normalize_function(self, spec):
        mean = (self.min_val + self.max_val) / 2
        scale = self.max_val - self.min_val
        return (spec - mean) / scale + 0.5

    def forward(self, x):
        x = x.to(device)
        x = self.normalize_function(x)
        #print("x " + str(x.size()), flush = True)
        x1 = nn.functional.leaky_relu(self.inorm1(self.conv1(x)))
        #print("leaky_relu(conv1) " + str(x1.size()), flush = True)
        x2 = nn.functional.leaky_relu(self.inorm2(self.conv2(x1)))
        #print("leaky_relu(conv2) " + str(x2.size()), flush = True)
        x3 = nn.functional.leaky_relu(self.inorm3(self.conv3(x2)))
        #print("leaky_relu(conv3) " + str(x3.size()), flush = True)
        x4 = nn.functional.leaky_relu(self.inorm4(self.conv4(x3)))
        #print("leaky_relu(conv4) " + str(x4.size()), flush = True)
        x = torch.flatten(x4, start_dim=1)
        #print("flatten " + str(x.size()), flush = True)
        x = nn.functional.leaky_relu(self.linear1(x))

        mu = self.linear2(x)
        log_var = self.linear3(x)

        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        z = mu + eps * std
        #print("z " + str(z.size()), flush = True)
        self.kl = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
        return z, (x1, x2, x3, x4)

class Decoder(nn.Module):
    def __init__(self, latent_dims, min_val, max_val):
        super().__init__()

        self.decoder_lin = nn.Sequential(
            nn.Linear(latent_dims, 1024),
            nn.ReLU(True),
            nn.Linear(1024, n_dimensions * x_latent * y_latent),
            nn.ReLU(True)
        )

        self.unflatten = nn.Unflatten(dim=1, unflattened_size=unflatten_size)
        

        self.decoder_conv1 = nn.Sequential(
                nn.ConvTranspose2d(128, 64, 3, stride=2, padding=1, output_padding=1),
                nn.InstanceNorm2d(64),
                nn.ReLU(True)
        )
        self.decoder_conv2 = nn.Sequential(
                nn.ConvTranspose2d(64, 32, 3, stride=2, padding=1, output_padding=1),
                nn.InstanceNorm2d(32),
                nn.ReLU(True)
        )
        self.decoder_conv3 = nn.Sequential(
                nn.ConvTranspose2d(32, 16, 3, stride=2, padding=1, output_padding=1),
                nn.InstanceNorm2d(16),
                nn.ReLU(True)
        )
        self.decoder_conv4 = nn.Sequential(
                nn.ConvTranspose2d(16, 1, 3, stride=2, padding=1, output_padding=1),
                nn.Sigmoid()
        )

        self.min_val = min_val
        self.max_val = max_val

    def denormalize_function(self, spec):
        mean = (self.min_val + self.max_val) / 2
        scale = self.max_val - self.min_val
        return (spec - 0.5) * scale + mean
        
    def forward(self, x, layer_outputs):
        x1, x2, x3, x4 = layer_outputs
        x = self.decoder_lin(x)
        #print("decoder_lin " + str(x.size()), flush = True)
        x = self.unflatten(x)
        #print("unflatten " + str(x.size()), flush = True)
        if skip_connections:
            x = torch.cat((x, x4), 1)  # Concatenate skip connection
        x = self.decoder_conv1(x)
        if skip_connections:
            x = torch.cat((x, x3), 1)  # Concatenate skip connection
        x = self.decoder_conv2(x)
        if skip_connections:
            x = torch.cat((x, x2), 1)  # Concatenate skip connection
        x = self.decoder_conv3(x)
        if skip_connections:
            x = torch.cat((x, x1), 1)  # Concatenate skip connection
        x = self.decoder_conv4(x)
        x = self.denormalize_function(x)
        return x

class VariationalAutoencoder(nn.Module):
    def __init__(self, latent_dims, min_val, max_val):
        super(VariationalAutoencoder, self).__init__()
        self.encoder = VariationalEncoder(latent_dims, min_val, max_val)
        self.decoder = Decoder(latent_dims, min_val, max_val)

    def forward(self, x):
        x = x.to(device)
        z = self.encoder(x)
        return self.decoder(z)

def read_value_lmdb(index, lmdb_name):
    # Open the LMDB environment
    env = lmdb.open(lmdb_name, readonly=True)

    with env.begin() as txn:
        lmdblength = txn.get(f"{index:08}".encode("ascii"))
        # Remember it's a Spec_Image object that is loaded
        spec_image = pickle.loads(lmdblength)
        len = int(spec_image) if lmdblength is not None else 0
    return env, len

def calculate_picel(stft, sr, times=None, freqs=None):
    if freqs is None:
        freqs = np.linspace(0, sr / 2, stft.shape[0])

    if times is None:
        times = np.arange(stft.shape[1])

    X, Y = np.meshgrid(times, freqs)
    stft_aux = stft
    if torch.is_tensor(stft):
        if(stft.is_cuda):
            stft_aux = stft.cpu()
        stft_aux = stft_aux.detach().numpy()

    return X, Y, stft_aux

def plot_stft(stft, sr, ax=None, fig=None, times=None, freqs=None, label=None):

    def add_colorbar(fig, ax, im):
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        fig.colorbar(im, cax=cax, orientation="vertical")

    if fig is None:
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))

    X, Y, stft_aux = calculate_picel(stft, sr, times, freqs)

    im0 = ax.pcolor(X, Y, stft_aux, cmap="magma")
    add_colorbar(fig, ax, im0)
    ax.set_title(label)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")

    return fig

def show_spec_batch(sample_batched, sr, samples):
    """Show image for a batch of samples."""
    #print(sample_batched[0].size())
    #TUDO BURRO NESTE LOOP
    #print(sample_batched)
    dims = []
    try:
        dims = list(sample_batched.size())
        #print(f'try {dims[0]}')
    except:
        dims = sample_batched.shape
        sample_batched = torch.tensor(sample_batched)
        #print(f'except {sample_batched.shape}')

    for i in range(dims[0]): 
        #image = torch.tensor(sample_batched[i])
        #print(type(sample_batched))
        #print(image)
        image_sq = torch.squeeze(sample_batched[i])
        #print(f'image_sq {image_sq.shape}')
        f = plot_stft(image_sq, sr)
        if samples > 0:
            if samples-1 <= i:
                break

def normalize(S):
    return torch.clamp((((S - min_level_db) / -min_level_db)*2.)-1., -1, 1)

def denormalize(S):
    return (((torch.clamp(S, -1, 1)+1.)/2.) * -min_level_db) + min_level_db

class Mel2Audio(torch.nn.Module):
    def __init__(
        self,
        sample_freq,
        n_fft,
        n_mel,
        normalize
    ):  
        super().__init__()

        self.sample_freq=sample_freq
        self.n_fft=n_fft
        self.n_mel=n_mel
        self.normalize = normalize

        self.inv_mel_scale = torchaudio.transforms.InverseMelScale(n_stft = n_fft//2+1, n_mels=n_mel, sample_rate=sample_freq)

        #default: 
        #  win_length = n_fft
        #  hop_length = win_length // 2
        self.grif_lim = torchaudio.transforms.GriffinLim(n_fft=n_fft) 
        

    def forward(self, melspec) -> np.array:

        melspec = torch.tensor(melspec).to(device)

        if self.normalize:
            melspec = denormalize(melspec)+ref_level_db

        melspec = torchaudio.functional.DB_to_amplitude(melspec, 1, 1)

        # Convert to power spectrogram
        spec = self.inv_mel_scale(melspec)

        # Convert to mel-scale
        wav = self.grif_lim(spec)

        return wav


class Audio2Mel(torch.nn.Module):
    def __init__(
        self,
        resample_freq,
        truncate,
        n_signal,
        n_fft,
        n_mel,
        device,
        ref_level_db,
        normalize,
    ):  
        super().__init__()

        self.resample_freq=resample_freq
        self.truncate=truncate
        self.n_signal=n_signal
        self.n_fft=n_fft
        self.n_mel=n_mel
        self.device=device
        self.ref_level_db=ref_level_db
        self.normalize = normalize

        #default: 
        #  win_length = n_fft
        #  hop_length = win_length // 2

        self.spec = torchaudio.transforms.Spectrogram(n_fft=n_fft, power=2) 

        self.mel_scale = torchaudio.transforms.MelScale(n_mels=n_mel, sample_rate=resample_freq, n_stft=n_fft // 2 + 1)

        self.power2dB = torchaudio.transforms.AmplitudeToDB(stype="power", top_db=70)

        #F.interpolate(input_tensor, size=(572, 572), mode='bilinear')

    def _audio_truncate(self, audio):
        if self.truncate:
            # truncate the audio signal at n_signal
            if audio.shape[-1] > self.n_signal:
                x = audio[:, :self.n_signal]
            else:
                pad = self.n_signal - audio.shape[-1]
                x = torch.nn.functional.pad(audio, (0, pad))
        else:
            # pad and separate the audio signal into chunks of length n_signal
            pad = self.n_signal - (audio.shape[-1] % self.n_signal)
            x = torch.nn.functional.pad(audio, (0, pad))
            x = x.reshape(-1, self.n_signal)

        return x

    def forward(self, wav) -> torch.Tensor:
        
        audio, sr = torchaudio.load(wav)
        audio = audio.to(self.device)

        # check if the first dimension is 2
        if audio.size(0) == 2:
            # convert stereo audio to mono audio by taking the average of the two channels
            mono_audio = torch.mean(audio, dim=0)

            # reshape the tensor to have size [1, 137813]
            audio = mono_audio.unsqueeze(0)
            
        resample = torchaudio.transforms.Resample(orig_freq=sr, new_freq=self.resample_freq).to(self.device)
        resampled = resample(audio)

        # Truncate audio
        truncated = self._audio_truncate( resampled)

        # Convert to power spectrogram
        spec = self.spec(truncated)

        # Convert to mel-scale
        mel = self.mel_scale(spec)
        
        # Convert to dB
        mel_db = self.power2dB(mel)

        if self.normalize:
            mel_db = mel_db-self.ref_level_db

            #Normalize
            mel_db = normalize(mel_db)

        return mel_db

# Instantiate a pipeline
pppipeline = Audio2Mel(SAMPLE_RATE, truncate, NUM_SAMPLES, n_fft, n_mel, device, ref_level_db, normalize_dataset_db )

# Move the computation graph to CUDA
pppipeline.to(device=torch.device(device), dtype=torch.float32)

### Set the random seed for reproducible results
torch.manual_seed(0)

min_val = -53.07412
max_val = 48.4
#env_test, min_val = read_value_lmdb(-2, LMDB_DIR) 
#env_test, max_val = read_value_lmdb(-3, LMDB_DIR) 
#env_test.close()
def load_model():
    vae = VariationalAutoencoder(latent_dims=latent_dims, min_val=min_val, max_val=max_val)

    globaliter = 0
    beta = 0.1
    warmup=10000

    try:
        #vae.load_state_dict(torch.load(PATH))
        checkpoint = torch.load(MODEL_PATH, map_location=device)
        vae.load_state_dict(checkpoint['model_state_dict'])
        #optim.load_state_dict(checkpoint['optimizer_state_dict'], map_location=device) 
        n_epoch = checkpoint['epoch']
        val_loss = checkpoint['loss']
        vae.eval()
        print("Loaded model from " + MODEL_PATH)
        print(f'Number of epochs trained on: {n_epoch}')
        print(f'Validation loss: {val_loss}')
    except:
        n_epoch = 0
        print("Training from scratch!")

    print(f'Selected device: {device}')


    vae.to(device)

    vae.eval()

    return vae






class VAE(nn.Module):
    def __init__(self, input_dim, hidden_dim, latent_dim):
        super(VAE, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim
        
        # Encoder layers
        self.encoder_fc1 = nn.Linear(input_dim, hidden_dim)
        self.encoder_fc2 = nn.Linear(hidden_dim, int(hidden_dim/2))
        self.bn1 = nn.LayerNorm(hidden_dim)
        self.bn2 = nn.LayerNorm(int(hidden_dim/2))
        self.fc_mean = nn.Linear(int(hidden_dim/2), latent_dim)
        self.fc_logvar = nn.Linear(int(hidden_dim/2), latent_dim)
        
        # Decoder layers
        self.decoder_fc1 = nn.Linear(latent_dim, int(hidden_dim/2))
        self.decoder_fc2 = nn.Linear(int(hidden_dim/2), hidden_dim)
        self.decoder_fc3 = nn.Linear(hidden_dim, input_dim)
        
    def encode(self, x):
        x = nn.functional.relu(self.bn1(self.encoder_fc1(x)))
        x = nn.functional.relu(self.bn2(self.encoder_fc2(x)))
        mean = self.fc_mean(x)
        logvar = self.fc_logvar(x)
        return mean, logvar
    
    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        z = mu + eps * std
        return z
    
    def decode(self, z):
        z = nn.functional.relu(self.bn2(self.decoder_fc1(z)))
        z = nn.functional.relu(self.bn1(self.decoder_fc2(z)))
        x_hat = torch.sigmoid(self.decoder_fc3(z))
        return x_hat
    
    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        x_hat = self.decode(z)
        return x_hat, mu, logvar
    
def load_model_s():
    input_dim = latent_dims
    hidden_dim = 128
    latent_dim = 3

    model = VAE(input_dim, hidden_dim, latent_dim)


    try:
        #vae.load_state_dict(torch.load(PATH))
        checkpoint = torch.load(MODEL_PATH_S, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        #optim.load_state_dict(checkpoint['optimizer_state_dict'], map_location=device) 
        n_epoch_s = checkpoint['epoch']
        val_loss = checkpoint['loss']
        model.eval()
        print("Loaded model from " + MODEL_PATH_S)
        print(f'Number of epochs trained on: {n_epoch_s}')
        print(f'Validation loss: {val_loss}')
    except:
        n_epoch_s = 0
        print("Training from scratch!")

    print(f'Selected device: {device}')

    model.to(device)

    model.eval()

    return model


class GenerativeF():
    def __init__(self, model, model_s):  
        super(GenerativeF, self).__init__()
        self.generated_i = 0
        self.vae = model
        self.model_s = model_s

    def latent2coor(self, latent):
        mu, logvar = self.model_s.encode(latent)
        z = self.model_s.reparameterize(mu, logvar)
        z = z.detach().cpu().numpy()[0]
        coor = [z[0]*100, z[1]*100, z[2]*100]
        return coor

    def spec2audio(self, img_recon, prefix):

        # Instantiate a pipeline
        rpipeline = Mel2Audio(SAMPLE_RATE, n_fft, n_mel, normalize_dataset_db)

        # Move the computation graph to CUDA
        rpipeline.to(device=torch.device(device), dtype=torch.float32)

        audio = rpipeline(img_recon)

        wav_sq = torch.squeeze(audio)
        wave_audio = wav_sq.cpu().numpy()
        # Set the filename and sampling rate
        self.generated_i += 1
        filename = f"./audio/generated/{prefix}_{str(self.generated_i)}.wav"
        #filename =  os.path.join(os.path.dirname(__file__), "audio/generated", f"GS_{str(self.generated_i)}.wav")
        sampling_rate = 44100 # For example
        wavfile.write(filename, sampling_rate, wave_audio)
        return filename
    

    def audioAsInput(self, x):  
        x_encoded, conn = self.vae.encoder(x)
        # print(x_encoded.shape)
        img_recon = self.vae.decoder(x_encoded, conn)
        # print(img_recon.shape)

        # show_spec_batch(img_recon, SAMPLE_RATE, -1)

        filename = self.spec2audio(img_recon, "MIC")
        
        return filename, self.generated_i


    def latentAsInput(self, x):

        img_recon = self.vae.decoder(x, "none")
        #print(img_recon.shape)

        return self.spec2audio(img_recon, "AB")


    def coorAsInput(self, coor):
        
        input = [[coor["x"], coor["y"], coor["z"]]]

        x = self.model_s.decode(torch.tensor(input).to(device))

        return self.latentAsInput(x)
        
    def interpolation(self, audio_a, audio_b, influence_a, influence_b):
        
        if audio_a[0].startswith('INT_'):
            mel_a = pppipeline(f"./audio/generated/{audio_a[0]}")
        elif audio_a[0].startswith('AB_'):
            mel_a = pppipeline(f"./audio/generated/{audio_a[0]}")
        else:
            mel_a = pppipeline(f"./static/VENGEWAV/{audio_a[0]}")
        mel_a = mel_a.unsqueeze(0)
        
        if audio_b[0].startswith('INT_'):
            mel_b = pppipeline(f"./audio/generated/{audio_b[0]}")
        elif audio_b[0].startswith('AB_'):
            mel_a = pppipeline(f"./audio/generated/{audio_b[0]}")
        else:    
            mel_b = pppipeline(f"./static/VENGEWAV/{audio_b[0]}")
        mel_b = mel_b.unsqueeze(0)
        
        a_encoded, coon_a = self.vae.encoder(mel_a)
        b_encoded, conn_b = self.vae.encoder(mel_b)
        
        conv_comb = influence_a*a_encoded +  influence_b*b_encoded
        
        img_recon = self.vae.decoder(conv_comb, coon_a)
        
        filename = self.spec2audio(img_recon, "INT")
        
        return filename, self.generated_i
        
        
        

