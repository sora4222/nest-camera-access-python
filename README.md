# googlenestcam

Get pictures and sound from your Google Nest Cameras in a few lines of Python, ready for PyTorch, TensorFlow or OpenCV.

The package handles Google login, the Nest WebRTC live stream, and turning video into NumPy arrays.

- [Login](docs/login.md): Google setup and logging in
- Notebooks (`pip install "googlenestcam[notebooks]"`): [Quick start](notebooks/01-quick-start.ipynb), [Live view](notebooks/02-live-view.ipynb), [OpenCV, PyTorch and TensorFlow](notebooks/03-machine-learning.ipynb), [Server login](notebooks/04-server-login.ipynb)
- [Design](docs/design.md): what version 1 does and how it is used
- [Glossary](GLOSSARY.md): the words used in code and docs
- [Decisions](docs/adr/): why some choices were made

Development: `make check`, `make test`, `make coverage`, and `make build` (puts the wheel in `dist/` for other projects to install). Pull request checks: [docs/ci.md](docs/ci.md).
