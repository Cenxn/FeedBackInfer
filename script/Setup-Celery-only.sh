cd ../ansible
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml deploy-redis.yaml
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml deploy-celery_flower-NODjango.yaml