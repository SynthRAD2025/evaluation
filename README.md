<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GNU GPL-v3.0][license-shield]][license-url]


<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://synthrad2025.grand-challenge.org/">
    <img src="./SynthRAD_banner.png" alt="Logo" width="770" height="160">
  </a>


  <p align="center">
    Evaluation docker to asses the submissions in 
<a href="https://synthrad2025.grand-challenge.org/"><strong>SynthRAD2025 Grand Challenge</strong></a>
  <br />
    <a href="https://github.com/SynthRAD2025/evaluation"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/SynthRAD2025/evaluation">View Demo</a>
    ·
    <a href="https://github.com/SynthRAD2025/evaluation/issues">Report Bug</a>
    ·
    <a href="https://github.com/SynthRAD2025/evaluation/issues">Request Feature</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
## Table of Contents

* [Goal](#goal)
* [Getting Started](#getting-started)
  * [Dependencies](#prerequisites)
  * [Installation](#installation)
* [Ranking](#ranking)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
<!--
* [Acknowledgements](#acknowledgements)
-->


<!-- ABOUT THE PROJECT -->
## Goal

The source code for the evaluation container for
SynthRAD2025, generated using the [GrandChallenge Challenge Pack](https://github.com/DIAGNijmegen/demo-challenge-pack/tree/main)

<!-- GETTING STARTED -->
## Getting Started

### Dependencies

The user should have access to Docker [https://docs.docker.com/].
The requirements, specified in `requirements.txt` are:
* SimpleITK
* numpy
* scikit-image
* nibabel
* torch
* pandas
* p_tqdm
* requests
* acvl_utils
* dynamic_network_architectures
* dicom2nifti
* batchgeneratorsv2
* matplotlib
* seaborn
* monai
### Installation

1. Clone the repo
```sh
git clone https://github.com/SynthRAD2025/evaluation.git
```
or
```sh
git clone git@github.com:SynthRAD2025/evaluation.git
```

2. Download the segmentation models
```
sh download_totalsegmentator_models.sh
```

3. Prepare the input data
* In `ground_truth`, the file structure is separate directories for the `ct`, `mask`, and `segmentation` as generated by TotalSegmentator
* In each directory, there should be files with the structure `<patient_id>.mha`
* In the input, there should be matching files `<patient_id>.mha`
* With these files in place, run `input/generate_pred_json.py`

4. Build the Docker image
```
docker build -t synthrad2025_prelim_test_task1 .
```

5. Run the docker
```
docker run --gpus all -v /full/path/to/input:/input -v /full/path/to/output:/output synthrad2025_prelim_test_task1
```

The `--gpus all` is optional and can be passed when the machine the docker image runs on has a capable GPU (Nvidia, >= Ampere, >= 8GB VRAM)

<!-- RANKING -->
## Usage: Ranking

* Export the leaderboard of the to be ranked task to a `.csv` file.
* Change the path in `rank_teams.py` file to this file
* Run `rank_teams.py`


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create.
Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->
## License

Distributed under the MIT. See `LICENSE` for more information.

<!-- CONTACT -->
## Contact

Maarten Terpstra - m.l.terpstra-5@umcutrecht.nl  
Matteo Maspero - [@matteomasperonl](https://tw - m.maspero@umcutrecht.nl

Project Link: [https://github.com/SynthRAD2025/evaluation](https://github.com/SynthRAD2025/evaluation)


<!-- ACKNOWLEDGEMENTS 
## Acknowledgements

* []()
* []()
* []()
-->

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/
#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/SynthRAD2025/evaluation.svg?style=flat-square
[contributors-url]: https://github.com/SynthRAD2025/evaluation/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/SynthRAD2025/evaluation.svg?style=flat-square
[forks-url]: https://github.com/SynthRAD2025/evaluation/network/members
[stars-shield]: https://img.shields.io/github/stars/SynthRAD2025/evaluation.svg?style=flat-square
[stars-url]: https://github.com/SynthRAD2025/evaluation/stargazers
[issues-shield]: https://img.shields.io/github/issues/SynthRAD2025/evaluation.svg?style=flat-square
[issues-url]: https://github.com/SynthRAD2025/evaluation/issues
[license-shield]: https://img.shields.io/github/license/SynthRAD2025/evaluation.svg?style=flat-square
[license-url]: https://github.com/SynthRAD2025/evaluation/blob/master/LICENSE.txt
