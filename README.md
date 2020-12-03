# vfx-pipelines (TBD)

## Overview

This repo consists of various in-development pipelines that output the results of VFX experiments from my YouTube channel: https://www.youtube.com/channel/UCo_IXLTK8dtF2qOUCt4l47Q

## Plugins / Addons

### Blender

https://docs.blender.org/api/current/index.html

### DaVinci Resolve

OpenFX plugin guide: https://github.com/MrKepzie/Natron/wiki/OpenFX-plugin-programming-guide-(Basic-introduction)

## Future Endpoints

Will make use of AWS Lambda and Step Functions.

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

### Parallel Dimensions Contest

I participated in this 3D modeling challenge:
https://www.pny.com/promo/professional/parallel-dimensions

See /parallel-dimensions-contest/snowmen_battle_portal.mp4 and following link for my animation: https://youtu.be/EwZ8MXwUj-8

3D render was built in Blender and DaVinci Resolve / Fusion.

See final montage video: https://www.youtube.com/watch?v=EdCvwmebWN0&feature=youtu.be&t=178

### Learning Links
- https://pytorch.org/hub/research-models
- https://pytorch.org/hub/huggingface_pytorch-transformers/
-
- https://github.com/vt-vl-lab/3d-photo-inpainting/blob/master/DOCUMENTATION.md
- https://github.com/awslabs/amazon-sagemaker-examples/tree/master/sagemaker-experiments
-
- https://github.com/NVIDIA/mellotron

- transformer-config
- https://github.com/macio97/Real-Snow