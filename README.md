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
* [Usage](#usage)
  * [Function Descriptions](#functions-descriptions)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
<!--
* [Acknowledgements](#acknowledgements)
-->


<!-- ABOUT THE PROJECT -->
## Goal

The source code for the evaluation container for
SynthRAD2025, generated with
evalutils version 0.3.1.

<!-- GETTING STARTED -->
## Getting Started

### Dependencies

The user should have access to Docker [https://docs.docker.com/].
The requirements, specified in `requirements.txt` are:
* evalutils v0.3.1
* scikit-learn v0.24.2
* scipy v1.6.3
* scikit-image v0.19.3

### Installation

1. Clone the repo
```sh
git clone https://github.com/SynthRAD2025/evaluation.git
```
or
```sh
git clone git@github.com:SynthRAD2025/evaluation.git
```

<!-- USAGE EXAMPLES -->

## Usage

1. Data is to be organized so that the ground truth is in `ground-truth` folder. The ground truth folder should contain the subfolders `ct` and `masks`. All images are directly stored in these subfolders with the names `<patient_id>.nii.gz` or `<patient_id>.mha`. The predictions (synthetic CTs) should be stored in the `test/synthetic-ct` under the same names (i.e. `<patient_id>.nii.gz` or `<patient_id>.mha`).
2. Set some parameters at the bottom of the `evaluation.py` file. When running the docker locally, submission\_type shoud be set to 1 and number\_of\_cases should be equal to the number of test patients.
2. Run `test.sh`

### Functions Descriptions

**test.sh**

	description:
	create the docker and run the evaluations
	
	command line usage:
	./test.sh

<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/SynthRAD2025/evaluation/issues) for a list of proposed features (and known issues).

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

Distributed under the GNU General Public License v3.0. See `LICENSE` for more information.

<!-- CONTACT -->
## Contact

Suraj  - - mail here  
Matteo Maspero - [@matteomasperonl](https://twitter.com/matteomasperonl) - m.maspero@umcutrecht.nl

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
