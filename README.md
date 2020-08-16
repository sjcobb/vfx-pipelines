# vfx-pipelines

## Overview

This repo consists of various pipelines that output the results of VFX experiments.

## Endpoints

### Effects

- GET /v1/effects
    - returns a list of all available effects

- POST /v1/effects/transform-image
    - initial endpoint to test basic transforms

- POST /v1/effects/image_layers
    - input is source image, customization params, and outputs 3d-photo-inpainting results
    - Body: jpeg
    - Response: npy depth map, rendered mesh/*.ply, mp4 videos with zoom-in / swing / circle / dolly-zoom-in motions
    - ? URL params: motion=zoom-in&motion=swing

- POST /v1/effects/melody_producer
    - input is source audio, either an mp4 file or a URL (YouTube video) 
    - outputs Mellotron .wav using various speakers (LJS, Sally)
        - https://github.com/NVIDIA/mellotron/blob/master/inference.ipynb
        - https://nv-adlr.github.io/Mellotron
    - 

- /v1/effects/midi_transformer

### Workflows

Workflow endpoints combine various effects and output videos ready for Compositing. 

- POST /v1/workflows/generate_song

## Notes

- https://pytorch.org/hub/research-models
- https://pytorch.org/hub/huggingface_pytorch-transformers/
-
- https://github.com/vt-vl-lab/3d-photo-inpainting/blob/master/DOCUMENTATION.md
- https://github.com/awslabs/amazon-sagemaker-examples/tree/master/sagemaker-experiments
-
- https://github.com/NVIDIA/mellotron

- transformer-config
- 