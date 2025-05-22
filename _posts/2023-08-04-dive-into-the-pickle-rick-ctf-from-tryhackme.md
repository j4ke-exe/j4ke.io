---
title: "Dive Into the Pickle Rick CTF from TryHackMe"
slug: pickle-rick
layout: post
excerpt_separator:  <!--more-->
categories:
  - ctfs
---

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2F1CvUxwwsd7XLubzuHhA5%2Fimage.png?alt=media&token=5a8f16c6-1611-4a19-b7b2-e7c0095e8b33){: .center-image }

This walkthrough will go over the [Pickle Rick](https://tryhackme.com/room/picklerick) CTF found on [TryHackMe](https://tryhackme.com). The focus behind this box is to teach the importance of cleaning up developer comments in files, improper storage, and input validation for web applications.

### Step 1: What's Out There?

My methodology might be different than yours when it comes to recon and trying to identify what type of technologies exist on my target. To avoid being loud, we're going to take a less intrusive approach and enumerate the web server to see what we can find. First, let's take a look at the home page.

![Homepage](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2FftA84GzfrRnJuSYwEC4M%2Fimage.png?alt=media&token=9b4c9032-d9f3-45b3-ac7d-7f231d500b1c){: .center-image }

Right off the bat, we can tell that there is no functionality for this page. It's a static display of an image and text. No indication of a way for us to try an injection attack. However, after taking a peek at the source code, we discovered a username `R1ckRul3s`.

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2FPMPIqlGyt9kIpK57kXqG%2Fimage.png?alt=media&token=cf485b17-9cf8-417a-ac7c-14eb46a3c4bd){: .center-image }

In addition to gaining a username due to the developer having poor cybersecurity hygiene, we can see that there is a directory called `assets`. Let's take a look at this and see if there's anything that can help us get a foothold on the box.

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2FmLE1xi1peeEQXiffaZAi%2Fimage.png?alt=media&token=b9187289-8f4a-4f90-b162-849029ec66a0){: .center-image }

The only thing that stands out to me here is `Apache/2.4.18`, this lets me know that we're dealing with a Linux-based system, which will come in handy later. The version is vulnerable to a privilege escalation attack, but this doesn't do us much good as it is a Local Privilege Escalation and will require us to get a shell on the box. But something to take note of, nonetheless. So, where to from here? Well, before we start using tools to further enumerate directories, let's see if we can access `robots.txt`, perhaps there's something useful there.

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2FnvyKC6Cx1HMOPSqhvlbL%2Fimage.png?alt=media&token=246b70be-5e3e-4607-ac49-dfa797be0639){: .center-image }

Not really sure what `Wubbalubbadubdub` is, but let's put it in our back pocket along with `R1ckRul3s`, I'm sure there's some importance to it. Now, let's dig deeper and see what type of content we can pull out of this site. For this, we will be using `dirb`. This tool essentially runs a dictionary attack against a website to help us find web objects. There are other tools out there that can achieve the same or similar results, like `ffuf` and `gobuster`, but I like this one.

> Syntax: `dirb` [`http://website.thm`](http://website.thm)

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2FW4ccFONbIWfORWtCdK4C%2Fimage.png?alt=media&token=05d956a7-18ab-4264-b839-4463d02d33eb){: .center-image }

Well, this doesn't tell us anything more than what we already know. But there has to be something out there just purely based on the fact that a username exists, there are images in `assets` that are being used other than on the home page, so perhaps there's a filter that is blocking us from discovering more. At this point, we know there's a login page for an admin because the description on the home page hints at it. So, let's manually look for login pages and see what we come up with.

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2F9Ursm8EPcRriXl7crnHd%2Fimage.png?alt=media&token=097f5f00-29c4-44f9-b043-a0f3156d7348){: .center-image }

I found this page after trying `login.php`. Now, let's try using `R1ckRul3s` as our username and `Wubbalubbadubdub` as our password.

### Step 2: Finding the Ingredients

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2FppWIFNLXdrw5h26dJbo2%2Fimage.png?alt=media&token=66695589-955a-4c44-b615-a702a119b493){: .center-image }

We're in! And what's this? A command panel...very interesting. Considering how we identified the operating system to be Linux earlier when we took a peek at the `assets` directory, we might be able to run some commands here to find the ingredients.

First, we will check and see who we are by typing `whoami`.

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2FB1zzx2lxIyN1Gvtl9JgY%2Fimage.png?alt=media&token=958699a9-071b-415a-8496-15c9c8de6b45){: .center-image }

Just as I expected, we're logged in as a non-privileged user `www-data`. We should still be able to view some documents and maneuver around. Let's see if we can execute the looksee command to view content in our current directory. We'll follow it with `pwd` to print our working directory.

```bash
ls -lah; pwd
```

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2FXDiCsnKUlb4u6AIv9cqa%2Fimage.png?alt=media&token=9149dea8-1153-45ee-8819-ec6e281f2c81){: .center-image }

A lot of goodies in the base `/var/www/html` directory. I bet `Sup3rS3cretPickl3Ingred.txt` contains one of our ingredients, let's see what's inside.

```bash
cat Sup3rS3cretPickl3Ingred.txt
```

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2FYbYoh5NA8v2ALjO0UOkI%2Fimage.png?alt=media&token=53295cff-12b7-400f-a6be-b30e0cc11def){: .center-image }

Well, looks like we are not allowed to use `cat`, but we can use another command like `less` to see the content of the file.

```bash
less Sup3rS3cretPickl3Ingred.txt
```

When a hacker has a will, a hacker will find a way. We found our first ingredient, `*** ******* ****`. Now, let's see what this `clue.txt` has for us.

```bash
less clue.txt
```

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2FzKtJ3lxVkJi6fVo5CTLI%2Fimage.png?alt=media&token=6ca53b9a-fc45-4627-87f6-b6e352ce2612){: .center-image }

Alright, looks like we need to do some more digging for the other ingredients. Taking into consideration that we're in `/var/www/html` on Linux, we need to take three steps back for us to get to the base for our directory traversal.

```bash
cd ../../../; ls -lah; pwd
```

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2FkIYrs4vxhcmimsr6oDua%2Fimage.png?alt=media&token=14601966-f6b5-4c48-9ad1-70898aa32973){: .center-image }

Let's start by looking in `/home` for our next ingredient. Just like Windows OS, this directory houses folders like Documents, Downloads, and Pictures. I don't know about you, but this is where I would store something important.

```bash
cd /home; ls -lah; pwd
```

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2F6OqJs0kznRaX4r3GbYKO%2Fimage.png?alt=media&token=d9c5c7da-fa5d-47a5-90f9-5bf2cee81db8){: .center-image }

We found two folders, `rick` and `ubuntu`. We'll start with `rick` since it's owned by `root`.

```bash
cd /home/rick; ls -lah; pwd
```

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2F2imsShc06xLGteqEYwsN%2Fimage.png?alt=media&token=ad636c17-a719-4b6a-b570-e23dcde54322){: .center-image }

Nice, we found our second ingredient. One thing to note about this is that it is a file and not a directory. We know this by looking at the permissions `-rwxrwxrwx` which allow us to read, write, and execute; however, if it were a directory then it would look like `drwxrwxrwx`. Because of this, we will need to put quotes around the file name to ensure it runs due to there being a space between the words. If we don't, then it will escape and not give us any results.

```bash
less /home/rick/"second ingredients"
```

`* ***** ****` for our second ingredient. No idea what this is either, perhaps I should watch this show? I might just have to watch an episode and see if I like it. Anyways, back to hacking and getting that prize root folder we saw after our first looksee into the base directory. The first thing we should do in this scenario is see what we can run as `sudo`.

```bash
sudo -l
```

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2FTs1cpvzoT2ycYhHF8sG3%2Fimage.png?alt=media&token=d433a7ae-207a-4ca7-850c-98bf1095d07c){: .center-image }

Well, this is good and bad. Good for us as we can literally run anything as `sudo` since we don't need a password to authenticate us. Bad for the owner of this box because we can look into the `root` directory without much effort.

```bash
sudo ls -lah ../../../root
```

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2F8xpqpD8QSqjsmfKzpaKH%2Fimage.png?alt=media&token=952a4749-2efd-46fe-af51-b2c9aa49d609){: .center-image }

With a bit of "Linux Fu", we are able to see the contents of `root`. From here we should be able to get our last ingredient and complete this box.

```bash
sudo less ../../../root/3rd.txt
```

We obtained our third ingredient, `***** *****`and are ready to submit all three and pwn this box.

### Step 3: Pwned

![](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FnxJHllso3wpDcEpkQXO3%2Fuploads%2Fobb8DGjSdqnW9M9kcguv%2F2023_06_28_06_40_55_spaces_nxJHllso3wpDcEpkQXO3_uploads_c84Mzpv5BS8Vpy96rbRL_image.png_1230_770_an.jpg?alt=media&token=75157b5f-3a2c-4d24-8af6-49c0a0156a60){: .center-image }

I hope you enjoyed this walkthrough of the [Pickle Rick](https://tryhackme.com/room/picklerick) CTF built by [TryHackMe](https://tryhackme.com) and [ar33zy](https://tryhackme.com/p/ar33zy). Keep on hacking.