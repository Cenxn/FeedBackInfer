# FeedBackInfer
This project is for COMP0239 Coursework, implemented a distributed message passing system for machine learning code (The original deep learning code is from https://www.kaggle.com/code/debarshichanda/feedback-inference).
The model aims to classify argumentative elements in student writing as "effective," "adequate," or "ineffective."
The Django project at [feedback_infer_dj](./feedback_infer_dj/) have two main functions:
1. type_essay/ page, allow user type a single essay, tag each discourse with discourse tag. Upload the essay and the model will generate analysis reuslt.
2. upload_csv/ page, allow user upload a single csv file, but inclueded limited essay (no more than 20), and generate the analysis results.

In order to avoid waiting too long for large statistics using web services, it is recommended that larger csv files be run directly using celery. 

This system based on 5 AWS machines (exclusive the host machine) is capable of training more than 60,000 essay records (the maximum capacity test guarantees that the system can run continuously for more than 24 hours). 

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

- [`Initialize-ansible.sh`](.script/Initializa-ansible.sh) Install ansible on the host, and automatically configure the ssh security key.
- [`Setup-Beegfs.sh`](.script/Setup-Beegfs.sh) Configure BeeGFS and build firewall settings.
- [`Setup-python-env.sh`](.script/Setup-python-env.sh) Install the python virtual environment and download the datasets required for kaggle. Please prepare your own [kaggle.json](https://www.kaggle.com/docs/api) file, and put it in the gadget/kaggle.json.
- [`Setup_Celery-with-Django.yaml`](.script/Setup_Celery-with-Django.yaml) If you only need to see the django web, run this script and it will automatically deploy and start django on port 8000 (port-forwarding to 80) on your machine. 
It can be accessed at `http://your_clicent01_external_ip`.
- [`Setup-Celery-only.yaml`](.script/Setup_Celery-with-Django.yaml) If you want to analyse larger files, do it directly on celery by modifying the path file of [`main.py`](celery_code
/main.py) to introduce your csv file. 

You can visit `http://your_work01_external_ip` to check Flower inferface, the monitoring and management tool that accompanies Celery.

How to use `main.py`:
``` bash
source /beegfs_data/virtualenv/FeedBackInfer/bin/activate
cd /beegfs-FeedBackInfer/
/beegfs_data/virtualenv/FeedBackInfer/bin/python celery_code/main.py
```

Hint: 
