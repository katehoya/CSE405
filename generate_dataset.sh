#!/bin/bash
export PYTHONPATH=$CONDA_PREFIX/lib/python3.10/site-packages

# COMFORT BALL
#python data_generation/generate_dataset.py --dataset_name comfort_ball --save_path ./data 1> /dev/null
~/바탕화면/Paper_code/COMFORT/blender-4.0.0-linux-x64/blender -b -P data_generation/generate_dataset_balls.py -- --dataset_name comfort_ball_noises --save_path ./data


# COMFORT CAR LEFT
#python data_generation/generate_dataset.py --dataset_name comfort_car_left --save_path ./data 1> /dev/null

# COMFORT CAR RIGHT
#python data_generation/generate_dataset.py --dataset_name comfort_car_right --save_path ./data 1> /dev/null
