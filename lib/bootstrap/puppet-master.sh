#!/bin/bash -v

apt update
apt install -y cowsay

/usr/games/cowsay "__teststring__" > /tmp/moo
