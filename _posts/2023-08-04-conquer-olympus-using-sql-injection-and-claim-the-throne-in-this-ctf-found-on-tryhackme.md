---
title: "Conquer Olympus Using SQL Injection and Claim the Throne in this CTF Found on TryHackMe"
slug: olympus
layout: post
excerpt_separator:  <!--more-->
categories:
  - ctfs
---

This walkthrough covers the [Olympus](https://tryhackme.com/room/olympusroom) CTF found on [TryHackMe](https://tryhackme.com/). The goal of this challenge is to exploit an SQLi vulnerability in a CMS, use sqlmap to acquire user credentials by extracting a database, identify a subdomain hosting a chat application, upload a reverse shell to establish a foothold on the system and take advantage of a poorly managed SUID binary to escalate privileges.

### Step 1: What's Out There?

```bash
nmap -sS -sV -sC -p 22,80 olympus.thm --min-rate=1000
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135195190/4f9965b8-825d-42ef-9211-c24ecfd32696.webp){: .center-image }

### Step 2: FFUF

```bash
ffuf -w /usr/share/wordlists/SecLists/Discovery/Web-Content/common.txt:FUZZ -u http://olympus.thm/FUZZ -fc 403
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135218898/f1601161-af87-4569-8bec-af42899fc8e0.webp){: .center-image }

We discovered a directory named `~webmaster`, which is where the CMS is located.

### Step 3: SQLi

Testing the Victor CMS search field feature reveals an SQLi:

```sql
'SELECT * FROM users WHERE username='' and password='' OR 1=1;
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135249671/7a5a0911-850b-4022-8390-f5132fe2c69f.webp){: .center-image }

Let's capture this with `Burp Suite` and plug it into `sqlmap` to automate our injection attack.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135258695/bc797866-ff1c-4232-a7df-47350afc8f02.webp){: .center-image }

Copy this over to a text editor and run it through `sqlmap`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135267192/06a8ef5f-d0ff-4373-ad80-84b2bdf0edb2.webp){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135274129/7dcdf2db-1f04-4e90-8bd4-79b752237fc1.webp){: .center-image }

We discovered a flag in olympus, let's dump it.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135284186/255dad89-c893-4faa-a7f8-79aa62c608b7.webp){: .center-image }

Let's obtain our first flag.

```bash
sqlmap -r req.txt --batch --dump -T flag -D olympus
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135304775/1f9277f9-a4db-4a22-842c-a59309af7a2b.jpeg){: .center-image }

Now let's see what that user's table can offer us.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135315500/d0fe3ef4-d4f8-4aa6-83c2-95d9d74ab2cc.jpeg){: .center-image }

Juicy credentials, we can crack the password hash to *prometheus* and use it to log in to the chat application.

### Step 4: Enumerate Subdomain

We discovered three users: *root*, *zeus*, and *prometheus*. Additionally, we discovered a subdomain called `chat` that can be added to our `/etc/hosts` list.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135339781/9f65783f-2537-4336-bcdb-8d556637c10e.webp){: .center-image }

Let's enumerate the newly discovered subdomain.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135354579/a14f5d24-a480-4ca3-a718-d93c9f4b3308.webp){: .center-image }

I'm sure the uploads directory will play an important role later, in the meantime let's see if we can log in with these credentials.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135363114/4f647e65-7e79-4401-a1bc-67e6e1329080.webp){: .center-image }

And we're in. There looks to be an upload feature, let's see if we can upload a reverse shell.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135371739/99d49d50-44ff-49ae-aa77-8634ee42d4a3.webp){: .center-image }

It looks to have been uploaded somewhere, but not sure where. Let's go back to `sqlmap` and dump the chats table to see if the file name was changed upon uploading.

```bash
sqlmap -r req.txt --batch --dump -T chats -D olympus
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135388161/79fa1af1-215a-4c87-9ce9-87b7daa747ae.webp){: .center-image }

Looks like it did. Let's copy this and see if we can visit and go to it using the `/uploads/` directory we found earlier.

Going to the path drops us into a shell. Searching for SUID binaries reveals `cputils`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135397019/2a652788-32b6-4cf5-93f2-6daa330e48df.webp){: .center-image }

We can copy over *zeus* `id_rsa key` and then ssh in with it.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135403791/bb79bcd0-4905-4d25-a28a-faca1fe4aacb.webp){: .center-image }

Crack it using `ssh2john` and `john-the-ripper`.

### Step 5: Privesc and Root

After looking around the file system for a while we discovered this:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135428251/53529f09-b0a5-4e7b-a46b-194d8143c831.webp){: .center-image }

Inside the PHP file seems to be a backdoor.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135434883/16fa8740-ccc0-4415-be08-737d6bbbf9fd.webp){: .center-image }

Running `uname -a; w; /lib/defended/libc.so.99` drops us into a root shell.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135443964/fd401057-3d13-4b48-a153-67b44dde8add.jpeg){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691135446720/6ce4f8c5-2dd4-4245-b58c-75aeb82aa8ef.jpeg){: .center-image }

This box was very difficult for me. I don't consider myself to be that knowledgeable on SQLi attacks, so I had to resort to a lot of googling to help me through. I will definitely give this box several more runs as I need to sharpen my command injection skills. As always, Happy Hacking!