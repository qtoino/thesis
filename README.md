# Audio Generation System with Variational Autoencoders

## Project Overview

This project implements a sound generation system using a two-layer Variational Autoencoder (VAE) architecture. The system converts audio samples into mel spectrograms, compresses them into a latent space, and enables generation of new audio samples by manipulating points in this 3D latent space.

## Architecture

The system utilizes a two-stage VAE architecture:

### Primary VAE
The first VAE compresses audio mel spectrograms into a 256-dimensional latent space:

- **Encoder:**
  - 4 convolutional layers with instance normalization and leaky ReLU activation
  - Downsampling with stride=2
  - Final fully connected layers producing mean and log variance for the latent space
  - Uses reparameterization trick for sampling

- **Decoder:**
  - Fully connected layers to reconstruct from latent space
  - 4 transposed convolutional layers with instance normalization and ReLU activation
  - Optional skip connections between encoder and decoder
  - Final sigmoid activation layer

### Secondary VAE
The secondary VAE further compresses the 256-dimensional latent space to a 3-dimensional space:

- **Encoder:**
  - Fully connected layers with normalization
  - Maps 256D vectors to 3D latent space

- **Decoder:**
  - Maps 3D vectors back to 256D vectors for audio generation
  - Enables intuitive navigation in a 3D coordinate system

## Features

- **Audio Generation:** Create new audio samples from coordinates in 3D space
- **Audio Interpolation:** Generate transitions between existing audio samples
- **Audio Visualization:** Display audio samples in a 3D interactive environment
- **Sound Organization:** Categorize and color-code audio samples by type
- **Favorites System:** Mark and save preferred generated sounds

## Technical Stack

- **Backend:**
  - Python 3.8
  - PyTorch 1.13.1 for deep learning models
  - Flask for RESTful API
  - torchaudio for audio processing

- **Database:**
  - SQLite for storing audio metadata and coordinates

- **Deployment:**
  - Docker for containerization
  - docker-compose for orchestration

## Getting Started

### Prerequisites
- Docker and docker-compose
- Python 3.8 (for local development)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd thesis-master
```

2. Start the application using Docker:
```bash
docker-compose up
```

This will:
- Build the backend and frontend containers
- Download the pre-trained model weights
- Initialize the database
- Start the Flask server on port 8000
- Start the frontend on port 3000

## API Endpoints

The system provides multiple REST API endpoints:

- `/addnew`: Generate a new sound from 3D coordinates
- `/interpole`: Create a sound by interpolating between two points
- `/all-audio-files`: Get all available audio files
- `/grab-generated-sounds`: Retrieve generated audio files
- `/favorite-audio-files`: Get favorite audio files
- `/health`: System health check

## Model Architecture Details

### Audio Processing Pipeline

1. Raw audio → Mel spectrogram conversion
2. Spectrogram normalization
3. VAE encoding to 256D latent space
4. Secondary VAE encoding to 3D space
5. 3D coordinates for interactive visualization

### Latent Space Properties

- 256-dimensional primary latent space captures audio characteristics
- 3-dimensional secondary latent space enables intuitive navigation
- KL divergence is used to regularize the latent space

## Future Work

- Implement more sophisticated audio generation techniques
- Add user accounts for personal sound collections
- Expand the training dataset for more diverse sound generation
