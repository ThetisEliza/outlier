<!--
 * @Date: 2023-01-07 22:59:34
 * @LastEditors: ThetisEliza wxf199601@gmail.com
 * @LastEditTime: 2023-01-10 18:10:35
 * @FilePath: /outlier/README.md
-->
# OUTLIER

## Instruction

This is a simple chat-room for you to communicate with your friends.

Are you mad or bothered by wanna

* Chatting with your friends but your boss standing behind you?
* Tell some secret about boss or company you serve but your computer and network is under survellience?
* Make some import decisions with nobody finding out?

Try this outlier tool !

Outlier, known as the famous movie, standing for the people that are active out of meaning "laws", with this tool,
You can build a secret server really simply and quickly. And setup a client to connect to it. It's designed to use
your own "Symmetic Encryption Algorithm" and setup a secret key to make your communication hardly to decryped.

## Setup

Install with pip
```bash
pip install outlierchat
```

## Quick tour

After setup. You can start a server just start the module outlier.server as
```python
python -m outlier.server [-a addr]
```

Then you and your friends cat easily connect to the server. Just type
```python
python -m outlier.client -n name [-a addr]
```

After connected, it's easy to regard it as an online game system. The client firstly is 
at the server hall where one can type $info to check what rooms there exist and
how many people are in it. Then type $room [room name] to choose one room or build a new one to enter it and you can easily send and receive messages with your friends.

## Development log

See [DEVLOG.md](https://github.com/ThetisEliza/outlier/DEVLOG.md)



