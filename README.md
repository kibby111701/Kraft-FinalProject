# GolfTrace: A Swing Measuring App
## Chris Kraft

### Introduction
Golf swings have a wide variety of measurables that contribute to what makes a “good” or “bad” swing. Examples of this include backswing tempo, head movement, and hip rotation. 
My objective in this project is to create an application that uses computer vision, specifically pose estimation, to measure and report these metrics when provided with a face-on video of a golf swing.

### Methodology
This project uses the MediaPipe BlazePose library to generate a wireframe image of the golfer for each frame of the video. 
From these images, the program extracts the positions of key body parts from the golfer, such as their head, shoulders, wrists, and hips.
Then, the program determines key frames of the video, including the swing start, backswing apex, impact, and followthrough. Initially, this was going to be achieved through [GolfDB](https://github.com/wmcnally/golfdb), an open source dataset and machine learning model for sequencing golf swings. However, GolfDB's model failed to correctly identify any phases for any of my test videos, seemingly as a result of overfitting. After some time trying to debug the model, I started to look into sequencing the swing algorithmically. I found out that the key phases of a golf swing correspond strongly with local minima and maxima of the y-position of the golfer's wrists. For example, the top of a backswing can be found using a local minima (where 0 is the top of the image), and the impact can be found using a local maxima. With this technique, the phases were correctly identified. Finally, metrics are produced by measuring and comparing body part positions between phases.
These results can also be accessed through this project's web app, which accepts .mov files and produces the metrics in a slightly more visually appealing format.

### Usage
- To run the basic Python script: `python3 main.py`
