בשביל להריץ את הפרוייקט:
הרימו את השרת בעזרת python main.py

שלחו בקשה לhttp://localhost:8080/path עם הbody הבא:
{"code": "print('hello world')"}
תקבלו בחזרה path ותשמרו אותו

לאחר מכון יש להתחבר בעזרת web socket לניתוב ws://localhost:8080/ws/debug

ולשלוח את ההודעות הבאות לפי הסדר הבא:
1. init
   {
   "seq": 1,
   "type": "request",
   "command": "initialize",
   "arguments": {
      "clientID": "monaco-client",
      "pathFormat": "path",
   }
   }

2. luanch
   
{
  "seq": 2,
  "type": "request",
  "command": "launch",
  "arguments": {
    "noDebug": false,
"stopOnEntry": true,
"program": <הpath שקיבלת>
    "cwd": <הpath שקיבלת ללא השם של הקובץ עצמו (מתחיל במילה script)>
  }
}

3. configurtionDone

{
  "seq": 3,
  "type": "request",
  "command": "configurationDone"
}
