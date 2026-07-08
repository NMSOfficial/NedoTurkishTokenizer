from pathlib import Path
p=Path('nedo_turkish_tokenizer/segmentation.py')
t=p.read_text(encoding='utf-8')
if '# NEDO_V21_FIX4_VERB_STEM' not in t:
    t += '''\n\n# NEDO_V21_FIX4_VERB_STEM\ndef _v21_variants(s):\n    out=[(s,None)]\n    if len(s)>=2:\n        out.append((s+"mak", "verb_mak"))\n        out.append((s+"mek", "verb_mek"))\n    if len(s)>=3:\n        m={"b":"p","c":"ç","d":"t","ğ":"k"}\n        if s[-1] in m:\n            base=s[:-1]+m[s[-1]]\n            out.append((base, s[-1]+">"+m[s[-1]]))\n            out.append((base+"mak", s[-1]+">"+m[s[-1]]+"+mak"))\n            out.append((base+"mek", s[-1]+">"+m[s[-1]]+"+mek"))\n        if s[-1]=="y" and len(s)>=4:\n            base=s[:-1]\n            out.append((base, "buffer_y"))\n            out.append((base+"mak", "buffer_y+mak"))\n            out.append((base+"mek", "buffer_y+mek"))\n    seen=set(); ans=[]\n    for a,b in out:\n        if a not in seen:\n            seen.add(a); ans.append((a,b))\n    return ans\n'''
    p.write_text(t,encoding='utf-8')
