<!--
 * @Date: 2023-01-07 22:59:34
 * @LastEditors: ThetisEliza wxf199601@gmail.com
 * @LastEditTime: 2023-03-13 11:09:01
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

## Quick tour

After setup. You can start a server just start the module outlier.server as
```shell
python -m outlier.server [-i ip_addr] [-p port]
```

Then you and your friends cat easily connect to the server
```shell
python -m outlier.client -n name -i ip_addr [-p port]
```

After connected, it's easy to regard it as an online game system. The client firstly is 
at the server hall where one can type `$info` to check what rooms there exist and
how many people are in it. Then type `$room [room name]` to choose one room or build a new one to enter it and you can easily send and receive messages with your friends.

## Note

You should check you network configuration carefully and thus some knowledge about internet technology shoule be used, such as `NAT`. The ipv4 address and the port of the server should be correctly configured to find the server.


## Development log

See [DEVLOG.md](https://github.com/ThetisEliza/outlier/blob/main/DEVLOG.md)
