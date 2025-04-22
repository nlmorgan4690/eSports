<!-----



Conversion time: 0.472 seconds.


Using this Markdown file:

1. Paste this output into your source file.
2. See the notes and action items below regarding this conversion run.
3. Check the rendered output (headings, lists, code blocks, tables) for proper
   formatting and use a linkchecker before you publish this page.

Conversion notes:

* Docs to Markdown version 1.0β44
* Thu Apr 17 2025 05:43:43 GMT-0700 (PDT)
* Source doc: Untitled document
* Tables are currently converted to HTML tables.
----->

# __Allowed Firewall Rules for Esports__
As new consoles or games come online the DCSD IT Infrastructure team researches necisary ports to allow for firewall rules. 

## __1. Overall Ruleset for allowed games and platforms__ 

<table>
  <tr>
   <td>FW Rule
   </td>
   <td> ( Allowed )
   </td>
  </tr>
  <tr>
   <td>TCP
   </td>
   <td>53, 80, 443, 465, 983, 1119, 1120, 1935, 2099, 3074, 3478-3480, 3724, 4000, 5222-5223, 6112-6120, 8088, 8393-8400, 10000-20000 27014-27050
   </td>
  </tr>
  <tr>
   <td>UDP
   </td>
   <td>53, 88, 500, 1024-65535
   </td>
  </tr>
</table>

## __2. Games and Platforms broken out__
References to sources linked below.

<table>
  <tr>
   <td>
   </td>
   <td>TCP
   </td>
   <td>UDP
   </td>
  </tr>
  <tr>
   <td>Nintendo Switch
   </td>
   <td>
   </td>
   <td>1024-65535
   </td>
  </tr>
  <tr>
   <td>Xbox Windows App
   </td>
   <td>3074
   </td>
   <td>88, 500, 3074, 3544, 4500
   </td>
  </tr>
  <tr>
   <td>Xbox One
   </td>
   <td>53, 80, 3074
   </td>
   <td>53, 88, 500, 3074, 3544, 4500
   </td>
  </tr>
  <tr>
   <td>Xbox Series X/Series S
   </td>
   <td>3074
   </td>
   <td>88, 500, 3074, 3544, 4500
   </td>
  </tr>
  <tr>
   <td>Playstation 4
   </td>
   <td>80, 443, 1935, 3478-3480 (inclusive)
   </td>
   <td>3478, 3479
   </td>
  </tr>
  <tr>
   <td>Playstation 5
   </td>
   <td>1935,3478-3480
   </td>
   <td>3074,3478-3479
   </td>
  </tr>
  <tr>
   <td> <strong>Games</strong>
   </td>
   <td>
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>League of Legends
   </td>
   <td>2099, 5222-5223, 8088, 8393-8400
   </td>
   <td>5000-5500, 8088
   </td>
  </tr>
  <tr>
   <td>Madden NFL EA Online
   </td>
   <td>80, 443, 9988, 10000-20000, 17503, 17504, 42120, 42210, 42230, 44125, 44225, 44325
   </td>
   <td>3659, 17503, 17504, 10000-20000
   </td>
  </tr>
  <tr>
   <td>Madden NFL
   </td>
   <td>3478-3480, 3074, 465, 983, 1935, 3478-3480, 5223, 10070-10080
   </td>
   <td>3074, 3478-3479, 3658, 10070, 88, 500, 3074, 3544, 4500
   </td>
  </tr>
  <tr>
   <td>Rocket League PC
   </td>
   <td>80 (HTTP) 443(TCP)
   </td>
   <td>7000-9000
   </td>
  </tr>
  <tr>
   <td>Rocket League PS4
   </td>
   <td>1935, 3478-3480 (inclusive)
   </td>
   <td>3074, 3478-3479 (inclusive)
   </td>
  </tr>
  <tr>
   <td>NBA 2k23 PC
   </td>
   <td>27015, 27036
   </td>
   <td>27015, 27031-27036
   </td>
  </tr>
  <tr>
   <td>NBA 2k23 PS
   </td>
   <td>3478-3480
   </td>
   <td>3074, 3478-3479
   </td>
  </tr>
  <tr>
   <td>NBA 2k23 XB
   </td>
   <td>3074
   </td>
   <td>88, 500, 3074, 3544, 4500
   </td>
  </tr>
  <tr>
   <td>Hearthstone PC
   </td>
   <td>1119, 3724
   </td>
   <td>1119, 3724
   </td>
  </tr>
  <tr>
   <td>Blizzard
   </td>
   <td>80, 443, 1119, 1120, 3074, 3724, 4000, 6112-6120, 27014-27050
   </td>
   <td>80, 443, 1119, 1120, 3478-3479, 3724, 4000, 4379-4380, 5060, 5062, 6112-6119, 6250, 27000-27031, 27036, 12000-64000
   </td>
  </tr>
  <tr>
   <td>Epic Games
   </td>
   <td>80, 443, 3478, 3479, 5060, 5062, 5222, 6250, 12000-65000
   </td>
   <td>80, 443, 3478, 3479, 5060, 5062, 5222, 6250, 12000-65000
   </td>
  </tr>
  <tr>
   <td>Riot Games
   </td>
   <td>80, 443, 5060, 5062, 12000-65000
   </td>
   <td>80, 443, 5060, 5062, 12000-65000
   </td>
  </tr>
  <tr>
   <td>Steam
   </td>
   <td>80, 443, 27015-27050
   </td>
   <td>27000-27100, 3478, 4379, 4380, 27014-27030
   </td>
  </tr>
</table>

## __3. Resources__ 
<a href="https://help.generationesports.com/hc/en-us/articles/360061115811-Networking-Whitelist-Ports-and-Services-to-Open">https://help.generationesports.com/hc/en-us/articles/360061115811-Networking-Whitelist-Ports-and-Services-to-Open</a>
<a href="https://portforward.com/hearthstone/">https://portforward.com/hearthstone/</a>
<a href="https://en-americas-support.nintendo.com/app/answers/detail/a_id/22272/~/how-to-set-up-a-routers-port-forwarding-for-a-nintendo-switch-console#:~:text=select%20OK.-,On%20a%20PC%20or%20smart%20device,-Access%20your%20router%27s">https://en-americas-support.nintendo.com/app/answers/detail/a_id/22272/~/how-to-set-up-a-routers-port-forwarding-for-a-nintendo-switch-console#:~:text=select%20OK.-,On%20a%20PC%20or%20smart%20device,-Access%20your%20router%27s</a>
<a href="https://docs.google.com/document/d/1FZ0gGquDX3x-sFcRmYuX-opfSVk0qRwB52nuq9fAE20/edit">eSports PlayVS Firewall and Content Filter Requirements</a>
<a href="https://help.playvs.com/en/articles/4919231-hardware-network-specifications-inclusion-lists">https://help.playvs.com/en/articles/4919231-hardware-network-specifications-inclusion-lists</a>

