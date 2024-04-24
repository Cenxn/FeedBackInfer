# FeedBackInfer
This project is for COMP0239 Coursework, implemented a distributed message passing system for machine learning code (The original deep learning code is from https://www.kaggle.com/code/debarshichanda/feedback-inference).
The model aims to classify argumentative elements in student writing as "effective," "adequate," or "ineffective."
The Django project at [feedback_infer_dj](./feedback_infer_dj/) have two main functions:
1. type_essay/ page, allow the user to type a single essay, and tag each discourse with a discourse tag. Upload the essay and the model will generate analysis results.
2. upload_csv/ page, allows the user to upload a single CSV file, but include a limited number of essays (no more than 20), and generate the analysis results.

To avoid waiting too long for large statistics using web services, it is recommended that larger CSV files be run directly using celery. 

This system based on 5 AWS machines (Not including the host, it only sends commands.) is capable of training more than 60,000 essay records (the maximum capacity test guarantees that the system can run continuously for more than 24 hours). 

## Project Initialization
Please configure your [inventory.yaml](./ansible/inventory_old.yaml) first.
``` bash
git clone https://github.com/Cenxn/FeedBackInfer.git
cd FeedBackInfer/script/
./Initialize-ansible.sh
./Setup-Beegfs.sh
./Setup-python-env.sh
./Setup_Celery-with-Django.yaml
# or 
# Setup-Celery-only.yaml
```

- [`Initialize-ansible.sh`](script/Initializa-ansible.sh) Install ansible on the host, and automatically configure the ssh security key.
- [`Setup-Beegfs.sh`](script/Setup-Beegfs.sh) Configure BeeGFS and build firewall settings.
- [`Setup-python-env.sh`](script/Setup-python-env.sh) Install the Python virtual environment and download the datasets required for Kaggle. Please prepare your own [kaggle.json](https://www.kaggle.com/docs/api) file, and put it in the gadget/kaggle.json.
**(For the version that was submitted to moodle, I've attached my own kaggle.json that can be used directly.)**
- [`Setup_Celery-with-Django.sh`](script/Setup_Celery-with-Django.sh) If you only need to see the Django web, run this script and it will automatically deploy and start django on port 8000 (port-forwarding to 80) on your machine. 
It can be accessed at `http://your_clicent01_external_ip`.
- [`Setup-Celery-only.sh`](script/Setup_Celery-with-Django.sh) If you want to analysis larger files, do it directly on celery by modifying the path file of [`main.py`](celery_code/main.py) to introduce your CSV file. 

You can visit `http://your_work01_external_ip` to check the Flower interface, the monitoring and management tool that accompanies Celery.

How to use `main.py`:
``` bash
source /beegfs_data/virtualenv/FeedBackInfer/bin/activate
cd /beegfs-FeedBackInfer/
/beegfs_data/virtualenv/FeedBackInfer/bin/python celery_code/main.py
```

## HIGHLIGHT ##
The example to test the system, could edit in [`main.py`](celery_code/main.py) and execute based on the above commands (The [dataset](https://www.kaggle.com/competitions/feedback-prize-effectiveness/data) is already downloaded via [`prepare-download_kaggle_dataset.yaml`](ansibleprepare-download_kaggle_dataset.yaml):
``` python
# Example_1
df_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/test.csv'
essay_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/test'
```
The train.csv was originally used to train this model but is used here **only** as a test function. This file contains 36,765 records and will take more than 4 hours to execute.
``` python
# Example_2
df_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/train.csv'
essay_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/train'
```
The CSV file used to test that the model has the ability to execute for more than 24 hours is composed of multiple randomly generated train.csv files.

The test.csv can also be used to test the upload_csv/ web page.

To test type_essay/ web page, you could simply type the essay content.
