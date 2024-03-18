dd if=/dev/random of=../gadget/connauthfile bs=128 count=1
cd ../ansible
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml beegfs-packages.yaml
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml beegfs-host.yaml
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml beegfs-storage.yaml
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml beegfs-common.yaml
