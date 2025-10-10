#!/bin/bash

# Stop and disable service
sudo systemctl stop ollama
sudo systemctl disable ollama

# Remove files
sudo rm -f /usr/bin/ollama /usr/local/bin/ollama
sudo rm -rf /usr/lib/ollama /var/lib/ollama /run/ollama
sudo rm -f /etc/systemd/system/ollama.service /etc/ld.so.conf.d/ollama.conf
sudo ldconfig

# Remove user/group
sudo userdel -r ollama 2>/dev/null || true
sudo groupdel ollama 2>/dev/null || true

# Clean environment
#sed -i '/OLLAMA_/d' ~/.bashrc ~/.bash_profile ~/.zshrc 2>/dev/null

echo "Ollama 已完全卸载"
