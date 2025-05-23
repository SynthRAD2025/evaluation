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

The user should have access to [Docker](https://docs.docker.com/). This repository contains the (modified)implementations of [nnUNet](https://github.com/MIC-DKFZ/nnUNet) and [TotalSegmentator](https://github.com/wasserth/TotalSegmentator), and the weights of the TotalSegmentator model used for evaluation. All these assets are originally published under the Apache License and redistributed here. 

### Installation

**1. Clone the repo**
```sh
git clone https://github.com/SynthRAD2025/evaluation.git
```
or
```sh
git clone git@github.com:SynthRAD2025/evaluation.git
```

**2. Prepare the input data**
* In `ground_truth`, the file structure is separate directories for the `ct`, `mask`, and `segmentation`. Then `ct/<patient_id>.mha` is the ground-truth CT, `mask/<patient_id>.mha` is the corresponding mask that is 1 where there is anatomy, 0 otherwise, and `segmentation/<patient_id>.mha` contains the segmentation as generated by TotalSegmentator. This segmentation contains the class label for every voxel.
* In the input, there should be matching files `<patient_id>.mha`. These are the Synthetic CTs generated from the CBCT or MR images by your algorithm. These sCTs must be generated by you beforehand, evaluation of algorithms is NOT part of this evaluation container. 
* With these files in place, run `input/generate_pred_json.py`. This command generated the JSON file to simulate a submission to Grand-Challenge. When `CREATE_FOLDERS_AND_FILES=True`, the script will also generate the file structure. 

**3. Build the Docker image**
```
docker build -t synthrad2025_eval_docker .
```

**4. Run the docker**
```
docker run -e NPROCS=1 -e DEBUG=0 -v /full/path/to/input:/input -v /full/path/to/groundtruth:/opt/ml/input/data/ground_truth -v /full/path/to/output:/output synthrad2025_eval_docker
```

By default, the Docker image performs parallel evaluation of the cases. By setting `NPROCS=1`, it will perform serial evaluation (one at a time). Increasing NPROCS can decrease the computation time of the evaluation, but also increases computation costs. Setting `DEBUG=1` will generate additional output and intermediate metrics while the model is running.

The output is written to `/output/metrics.json` and contains the computed [SynthRAD2025 metrics](https://github.com/SynthRAD2025/metrics/) per case, as well as the aggregate metrics over the entire dataset (per metric, the mean, maximum, median, minimum, standard deviation, 25th percentile, and 75th percentile).



<!-- RANKING -->
## Ranking

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
Matteo Maspero - [@matteomasperonl](https://bsky.app/profile/matteomaspero.bsky.social) - m.maspero@umcutrecht.nl

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
