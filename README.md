<!--
 * @Date: 2023-01-07 22:59:34
 * @LastEditors: ThetisEliza wxf199601@gmail.com
 * @LastEditTime: 2023-03-13 21:13:04
 * @FilePath: /outlier/README.md
-->
# ⚔️ OUTLIER

## Instruction

Are you mad or bothered by wanna

* Chat with your friends but your boss standing behind you?
* Tell some secret about boss or company you serve but your computer and network is under survellience?
* Make some import decisions with nobody finding out?

Try this ⚔️ outlier chat room !

⚔️ Outlier, known as the famous movie, standing for the people who act out of laws, is a simple tool for you to communicate with your friends. You could build a server really simply and quickly with it. And invite your friends to setup clients on it. It's designed to use your own "Symmetic Encryption Algorithm" and setup a secret key to make your communication hardly to decryped.

## Setup

Install with pip
```shell
pip install outlierchat
```

## Quick Tour

After setup. You can start a server just start the module outlier.server as
```shell
python -m outlier -s [-i ip_addr] [-p port]
```

Then you and your friends can easily connect to the server by
```shell
python -m outlier -n name -i ip_addr [-p port]
```

After connected, it's easy to regard it as an online game system. The client firstly is 
at the server hall where one can type `$info` to check what rooms there exist and
how many people are in it. Then type `$room [room name]` to choose one room or build a new one to enter it and you can easily send and receive messages with your friends.

## Note

You should check you network configuration carefully and thus some knowledge about internet technology shoule be used, such as `NAT`. The ipv4 address and the port of the server should be correctly configured to find the server.

## Feature

We currently use a rolling dynamic asymmetric encrpytion algorithm to keep the channel untracked. The server rolls a pair of public key and private key with RSA algorithm to transmit secret key for a symmetic encryption channel, then the encryped secret key can be safe once the key pair rolls. Only if the network traffic was completely recorded, the encrypting key pais of secret would be lost forever. This means once the channel is disconnected, NO ONE could recover the secret key. However, this design keeps no RSA certificated public key, so anyone could mock a fake one, thus, it's very vulnerable to a fake server or MIIT attack.


## Disclaimers

This program is only for temporary secret communication channel and definitely CANNOT escape from decryption by professional security team especially when the source code is open. Thus before you 
use this tool, you should know that we DO NOT take ANY responsiblility for any behaviours you take and the consequences that would come.


## Development log

See [DEVLOG.md](https://github.com/ThetisEliza/outlier/blob/main/DEVLOG.md)


## Copyright and License Information

Copyright Phoenix Wang, Micca shi, 2023-2024

Distributed under the term of [Apache 2.0 license](https://github.com/ThetisEliza/outlier/blob/main/LICENSE)
