import re
path = r'c:\Users\danie\AppData\Roaming\Code\User\workspaceStorage\54268263e3c45ae3be8b9c20bb73aa69\GitHub.copilot-chat\transcripts\576734da-0d92-45d6-ad12-68c755105b79.jsonl'
with open(path, encoding='utf-8') as f:
    content = f.read()
hits = re.findall(r'a_pics/[^\s"\\]{10,200}', content)
unique = sorted(set(hits))
for h in unique:
    print(h)
