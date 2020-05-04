# 2Rays3DTracking

Blender addon to track 3D position by two videos

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Plugin depends on mathutils which is included in Blender, and also [csaps](https://github.com/espdev/csaps), [NumPy](https://numpy.org/), [SciPy](https://www.scipy.org/) (dependency of csaps)

Installing. Run CMD from BlenderDir/*version*/python/bin

```
python -m pip install csaps numpy scipy
```

### Installing

Open Blender. *Edit->Preferences->Addons->Install* and select *addon.py* file. Enable addon.
Check that addon was successfully installed: In Properties window go to Object Properties tab, find 2Rays3DTracking tab.

## Usage

### General overview

If you want to track 3D position of real object using this addon, you need:

* Capture video of this object from 2 static cameras. Cameras have too be located in different positions, with angle 30-60 degree, be close as posible to object and contain object for all moving time.
* Measure real position and rotation of cameras
* Process vide footage, increase contrast and sharpness
* Track 2D motion of object on 2 videos using Blender Movie tracking
* Recreate 3D scene with 2 cameras using measured data
* Setup addons parameters, Field of View cameras, Frames Per Second
* Process addon tracking. Position animation will be applied to object

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
Special thanks to Igor Orlovsky for the calculation algorithms
