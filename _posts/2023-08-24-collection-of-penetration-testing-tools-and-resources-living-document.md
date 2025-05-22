---
title: "Collection of Penetration Testing Tools and Resources [Living Document]"
slug: pentest-tools
layout: post
excerpt_separator:  <!--more-->
categories:
  - infosec
---

This article serves as a living document, which I will continually update with the penetration testing tools and resources that I regularly use.

{% include important.html content="Under no circumstances should you utilize any tool against a target without obtaining prior written consent. I am not responsible for your actions." %}

### 🌐 Network Scanners

`nmap:` [https://nmap.org/download](https://nmap.org/download)

`rustscan:` [https://github.com/RustScan/RustScan](https://github.com/RustScan/RustScan)

`autorecon:` [https://github.com/Tib3rius/AutoRecon](https://github.com/Tib3rius/AutoRecon)

### 🖥 Enumerate Samba

`enum4linux:` [https://github.com/CiscoCXSecurity/enum4linux](https://github.com/CiscoCXSecurity/enum4linux)

`smbclient:` [https://www.samba.org/samba/docs/current/man-html/smbclient.1.html](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html)

`smbmap:` [https://github.com/ShawnDEvans/smbmap](https://github.com/ShawnDEvans/smbmap)

`rpcclient:` [https://www.samba.org/samba/docs/current/man-html/rpcclient.1.html](https://www.samba.org/samba/docs/current/man-html/rpcclient.1.html)

### 🗄 Enumerate DNS Records

`dnsrecon:` [https://github.com/darkoperator/dnsrecon](https://github.com/darkoperator/dnsrecon)

`dnsenum:` [https://github.com/fwaeytens/dnsenum](https://github.com/fwaeytens/dnsenum)

`fierce:` [https://github.com/mschwager/fierce](https://github.com/mschwager/fierce)

`dns dumpster:` [https://dnsdumpster.com/](https://dnsdumpster.com/)

### 🔎 Web Fuzzers

`dirb:` [https://github.com/v0re/dirb](https://github.com/v0re/dirb)

`dirbuster:` [https://github.com/KajanM/DirBuster](https://github.com/KajanM/DirBuster)

`ffuf:` [https://github.com/ffuf/ffuf](https://github.com/ffuf/ffuf)

`gobuster:` [https://github.com/OJ/gobuster](https://github.com/OJ/gobuster)

### 📝 WordPress Vulnerability Scanner

`wpscan:` [https://github.com/wpscanteam/wpscan](https://github.com/wpscanteam/wpscan)

### 💉 SQL Vulnerability Scanner

`sqlmap:` [https://github.com/sqlmapproject/sqlmap](https://github.com/sqlmapproject/sqlmap)

### 🔑 Cracking

`john-the-ripper:` [https://github.com/openwall/john](https://github.com/openwall/john)

`hashcat:` [https://github.com/hashcat/hashcat](https://github.com/hashcat/hashcat)

`aircrack-ng:` [https://www.aircrack-ng.org/](https://www.aircrack-ng.org/)

`cyberchef:` [https://gchq.github.io/CyberChef/](https://gchq.github.io/CyberChef/)

`crackstation:` [https://crackstation.net/](https://crackstation.net/)

`anycript:` [https://anycript.com/](https://anycript.com/)

`hashid:` [https://hashes.com/en/tools/hash\_identifier](https://hashes.com/en/tools/hash_identifier)

`hashcat hashes:` [https://hashcat.net/wiki/doku.php?id=example\_hashes](https://hashcat.net/wiki/doku.php?id=example_hashes)

### 🦾 Brute Force

`hydra:` [https://github.com/vanhauser-thc/thc-hydra](https://github.com/vanhauser-thc/thc-hydra)

### 🧱 Pivoting

`sshuttle:` [https://github.com/sshuttle/sshuttle](https://github.com/sshuttle/sshuttle)

`chisel:` [https://github.com/jpillora/chisel](https://github.com/jpillora/chisel)

`socat:` [http://www.dest-unreach.org/socat/](http://www.dest-unreach.org/socat/)

### 🛡 Vulnerability Scanners

`nikto:` [https://github.com/sullo/nikto](https://github.com/sullo/nikto)

`nessus:` [https://www.tenable.com/products/nessus](https://www.tenable.com/products/nessus)

### 🏴‍☠️ Penetration Testing Framework

`metasploit:` [https://www.metasploit.com/](https://www.metasploit.com/)

### 🐚 Shells

`pentestmonkey:`[https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php](https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php)

`payloadsallthethings:`[https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md)

### 📈 Privilege Escalation

`deepce:` [https://github.com/stealthcopter/deepce](https://github.com/stealthcopter/deepce)

`gtfobins:` [https://gtfobins.github.io/](https://gtfobins.github.io/)

`winpeas:` [https://github.com/carlospolop/PEASS-ng/tree/master/winPEAS](https://github.com/carlospolop/PEASS-ng/tree/master/winPEAS)

`linpeas:` [https://github.com/carlospolop/PEASS-ng/tree/master/linPEAS](https://github.com/carlospolop/PEASS-ng/tree/master/linPEAS)

`windows exploit suggester:` [https://github.com/bitsadmin/wesng](https://github.com/bitsadmin/wesng)

`linenum:` [https://github.com/rebootuser/LinEnum](https://github.com/rebootuser/LinEnum)

`pspy64:` [https://github.com/DominicBreuker/pspy](https://github.com/DominicBreuker/pspy)

`priv2admin:` [https://github.com/gtworek/Priv2Admin](https://github.com/gtworek/Priv2Admin)

`linux privesc:` [https://exploit-notes.hdks.org/exploit/linux/privilege-escalation/](https://exploit-notes.hdks.org/exploit/linux/privilege-escalation/)

### 🕸 Web Application Proxy

`burpsuite:` [https://portswigger.net/burp/communitydownload](https://portswigger.net/burp/communitydownload)

`caido:` [https://caido.io/](https://caido.io/)

`owasp zap:` [https://www.zaproxy.org/](https://www.zaproxy.org/)

### 💊 Packet Analyzer

`wireshark:` [https://www.wireshark.org/](https://www.wireshark.org/)

### 🪟 Active Directory

`bloodhound:` [https://github.com/BloodHoundAD/BloodHound](https://github.com/BloodHoundAD/BloodHound)

`sharphound:` [https://github.com/BloodHoundAD/SharpHound](https://github.com/BloodHoundAD/SharpHound)

`adpeas:` [https://github.com/61106960/adPEAS](https://github.com/61106960/adPEAS)

`powersploit:` [https://github.com/PowerShellMafia/PowerSploit](https://github.com/PowerShellMafia/PowerSploit)

`psmapexec:` [https://github.com/The-Viper-One/PsMapExec](https://github.com/The-Viper-One/PsMapExec)

`crackmapexec:` [https://github.com/mpgn/CrackMapExec](https://github.com/mpgn/CrackMapExec)

`kerbrute:` [https://github.com/ropnop/kerbrute](https://github.com/ropnop/kerbrute)

`rubeus:` [https://github.com/GhostPack/Rubeus](https://github.com/GhostPack/Rubeus)

`impacket:` [https://github.com/fortra/impacket](https://github.com/fortra/impacket)

`mimikatz:` [https://github.com/ParrotSec/mimikatz](https://github.com/ParrotSec/mimikatz)

`evil-winrm:` [https://github.com/Hackplayers/evil-winrm](https://github.com/Hackplayers/evil-winrm)

### 📡 C2 Frameworks

`powershell empire/starkiller:` [https://github.com/BC-SECURITY/Starkiller](https://github.com/BC-SECURITY/Starkiller)

`armitage:` [https://github.com/r00t0v3rr1d3/armitage](https://github.com/r00t0v3rr1d3/armitage)

`covenant:` [https://github.com/cobbr/Covenant](https://github.com/cobbr/Covenant)

### 🕵️‍♂️ OSINT

`social-engineering toolkit:` [https://github.com/trustedsec/social-engineer-toolkit](https://github.com/trustedsec/social-engineer-toolkit)

`whatweb:` [https://github.com/urbanadventurer/WhatWeb](https://github.com/urbanadventurer/WhatWeb)

`osint framework:` [https://osintframework.com/](https://osintframework.com/)

`netcraft:` [https://sitereport.netcraft.com/](https://sitereport.netcraft.com/)

`osint.sh:` [https://osint.sh/](http://OSINT.SH)

`melissa lookups:` [https://lookups.melissa.com/home/](https://lookups.melissa.com/home/)

`whatsmyname:` [https://whatsmyname.app](https://whatsmyname.app)

`credential hunting:` [https://dehashed.com/](https://dehashed.com/)

`haveibeenpwned:` [https://haveibeenpwned.com/](https://haveibeenpwned.com/)

### 🧩 Browser Extensions

`builtwith:`[https://addons.mozilla.org/en-US/firefox/addon/builtwith/?utm\_source=addons.mozilla.org&utm\_medium=referral&utm\_content=search](https://addons.mozilla.org/en-US/firefox/addon/builtwith/?utm_source=addons.mozilla.org&utm_medium=referral&utm_content=search)

`cookie-editor:`[https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/?utm\_source=addons.mozilla.org&utm\_medium=referral&utm\_content=search](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/?utm_source=addons.mozilla.org&utm_medium=referral&utm_content=search)

`dotgit:`[https://addons.mozilla.org/en-US/firefox/addon/dotgit/?utm\_source=addons.mozilla.org&utm\_medium=referral&utm\_content=search](https://addons.mozilla.org/en-US/firefox/addon/dotgit/?utm_source=addons.mozilla.org&utm_medium=referral&utm_content=search)

`foxyproxy:`[https://addons.mozilla.org/en-US/firefox/addon/foxyproxy-standard/?utm\_source=addons.mozilla.org&utm\_medium=referral&utm\_content=search](https://addons.mozilla.org/en-US/firefox/addon/foxyproxy-standard/?utm_source=addons.mozilla.org&utm_medium=referral&utm_content=search)

`hack-tools:`[https://addons.mozilla.org/en-US/firefox/addon/hacktools/?utm\_source=addons.mozilla.org&utm\_medium=referral&utm\_content=search](https://addons.mozilla.org/en-US/firefox/addon/hacktools/?utm_source=addons.mozilla.org&utm_medium=referral&utm_content=search)

`wappalyzer:`[https://addons.mozilla.org/en-US/firefox/addon/wappalyzer/](https://addons.mozilla.org/en-US/firefox/addon/wappalyzer/)

> *Current as of 22 May 2025*