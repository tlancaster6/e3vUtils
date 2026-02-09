This repo contains utilities for setting up WhiteMatter e3Vision Cameras.

Core Functionalities:
- aid in aperture adjustment
  - each camera has a manual aperture adjustment. Getting this setting consistent across cameras is difficult. I will connect two cameras at a time, one reference camera (with the desired setting) and one camera for adjustment. I will point both cameras at an evenly-lit white surface. You will calculate the mean pixel intensity near the center of the image for each and overlay the value onto a continuously updated side-by-side stream while I adjust the apterture on the second camera manually

Useful Resources: 
- API reference: https://docs.white-matter.com/docs/e3vision/api-reference/
- opencv streaming example: https://docs.white-matter.com/docs/e3vision/sample-scripts/opencv/

Assume that:
- e3vision watchtower has been launched
- cameras have been bound and connected
- cameras settings (codec, white balance, etc) have already been configured interactively
- we are running in local machine only mode (no api key needed)

Additional instructions
- keep this repo simple and streamlined. This is a small project with limited scope
- 