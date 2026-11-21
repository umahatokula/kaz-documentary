import re,subprocess,json
S="""How did the assassination of one man help plunge Europe into World War I?|On June 28, 1914, Archduke Franz Ferdinand, heir to the throne of Austria-Hungary, arrived in Sarajevo with his wife, Sophie.|By the end of the morning, both would be dead—and within weeks, Europe would be heading toward war.|But this wasn't simply a murder that automatically caused countries to start fighting.|It was the spark in a continent already filled with dangerous rivalries.|Austria-Hungary was a vast empire containing many different nationalities, and its leaders feared nationalist movements could tear it apart.|Some South Slav nationalists wanted territories under Habsburg rule to become part of a South Slav state.|Among them was Gavrilo Princip, a young Bosnian Serb who joined a plot to assassinate the archduke.|During the royal visit, one conspirator threw a bomb at Franz Ferdinand's car.|The attack failed to kill him, but it wounded people nearby.|The archduke continued to a reception at Sarajevo's town hall.|Later, he decided to visit the wounded in hospital.|During the journey, confusion about the route brought his car to a stop near Princip.|Princip stepped forward and fired, fatally wounding Franz Ferdinand and Sophie.|The assassination shocked Europe, but a wider war was still avoidable.|What happened next would be crucial.|Austrian-Hungarian leaders saw the attack as an opportunity to confront Serbia, which they viewed as a threat to their empire.|The plot had received assistance from individuals connected to Serbian military intelligence.""".split("|")
o=subprocess.run("ffmpeg -i vo.mp3 -af silencedetect=n=-35dB:d=0.2 -f null -",shell=True,capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',o)];en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',o)]
sil=list(zip(st,en));D=91.09
speech=[];t=0
for a,b in sil: speech.append((t,a)); t=b
speech.append((t,D))
tot=sum(b-a for a,b in speech)
def syl(w): return max(1,len(re.findall(r'[aeiouy]+',w.lower())))+ (3 if re.search(r'\d',w) else 0)
W=[sum(syl(w) for w in s.split()) for s in S];T=sum(W)
def m(frac):
  x=frac*tot
  for a,b in speech:
    if x<=b-a: return a+x
    x-=b-a
  return D
c=0;starts=[]
for w in W:
  t=m(c/T); 
  # snap to nearest silence end
  near=min(en+[0.0],key=lambda e:abs(e-t)); starts.append(round(near if abs(near-t)<1.2 else t,2)); c+=w
print(json.dumps(starts)); print(sil)
