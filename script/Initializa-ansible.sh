sudo dnf install python3-pip
pip install ansible
ssh-keygen -t rsa -b 4096 -f ~/.ssh/host_key -N ""
cd ../ansible
ansible-playbook --private-key ~/.ssh/comp0239_key -i inventory.yaml sshkeys-host.yaml
