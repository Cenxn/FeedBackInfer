cd ../ansible
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml prepare-mount_filesystem.yaml
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml prepare-install_kaggle.yaml
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml prepare-download_kaggle_dataset.yaml
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml prepare-scn_ml_prerequest.yaml
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml ../debug/scn_code.yaml
