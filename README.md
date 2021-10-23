# DuBot-Slash
 A version of DuBot using slash commands
 
<h1>Guide</h1>
<h2>Requirements</h2>
<ul>
  <li>Python</li>
  <li>pip</li>
  <li>Computer</li>
</ul>

<h2>Setting everything up</h2>
<p1>First, you will need to open up CMD and run:<br>
<code>
cd directory/to/the/file/here
 </code><br>
Next, you will need to do:<br>
 <code>
pip install -r requirements.txt
 </code><br>
and wait until everything is installed.<br>
When everythings complete, close down cmd and create a new file called "config.json" in the directory.<br>
In this new file you will need to put this inside of it:<br>
<code>
{<br>
    "token": "",<br>
    "guildIDs": [],<br>
    "ownerID": <br>
}<br>
</code>
<br>
We will come back to this file later.
</p1>

<h2>Creating the bot</h2>
<p1>
 For this next part of the tutorial, I recommend you watch <a href="https://www.youtube.com/watch?v=ibtXXoMxaho">this</a> tutorial and come back.<br>
 </p1>
 
 <h2>Back inside the config file</h2>
 <p1>
 Inside of the empty quotes next to <code>"token":</code> paste your bots token inside.<br>
 Enable discord developer mode<br>
 <a href="https://www.youtube.com/watch?v=13LeA6m9kU8">tutorial</a><br>
 Now, get your id number and paste it next to the ownerID section of the config file.<br>
 Leave guildID blank.
 </p1>
 <h2>Final steps</h2>
 <p1>
 Now you simply run the .py file!
</p1>
