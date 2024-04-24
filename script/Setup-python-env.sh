cd ../ansible
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml prepare-install_kaggle.yaml
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml prepare-download_kaggle_dataset.yaml
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml prepare-install_vitural_env.yaml
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml prepare-install_redis.yaml