sudo dd if=/dev/random of=../gadget/connauthfile bs=128 count=1
sudo chmod 400 ../gadget/connauthfile
sudo cp ../gadget/connauthfile /etc/beegfs/connauthfile
cd ../ansible
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml beegfs-packages.yaml
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml beegfs-host.yaml
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml beegfs-storage.yaml
ansible-playbook --private-key ~/.ssh/host_key -i inventory.yaml beegfs-common.yaml
