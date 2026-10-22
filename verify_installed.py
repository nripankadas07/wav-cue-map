import json,pathlib,subprocess,sys,tempfile
ROOT=pathlib.Path(__file__).absolute().parent;REPO=ROOT.name;PY=pathlib.Path(sys.argv[1]).absolute();CMD=PY.parent/REPO
def run(args,exit,cwd):
    p=subprocess.run([str(CMD)]+[str(x)for x in args],cwd=cwd,text=True,capture_output=True,timeout=30)
    assert p.returncode==exit,(REPO,p.returncode,p.stdout,p.stderr)
    if exit==2:assert p.stderr and not p.stdout
    return json.loads(p.stdout)if p.stdout else None
with tempfile.TemporaryDirectory(prefix='installed-console-')as tmp:
    t=pathlib.Path(tmp)
    if REPO=='wav-cue-map':
        p=t/'demo.wav';run(['--make-example',p],0,t);raw=p.read_bytes();out=run([p],0,t)
        assert out['frames']==8 and out['cues'][0]['sample_offset']==3 and not out['findings']
        run(['--make-example',p],2,t);assert p.read_bytes()==raw
        bad=t/'bad.wav';bad.write_bytes(raw[:-1]);run([bad],2,t)
    elif REPO=='ber-boundary-tree':
        p=t/'demo.hex';p.write_bytes((ROOT/'example.hex').read_bytes());raw=p.read_bytes();out=run([p],0,t)
        assert len(out['nodes'])==4 and out['nodes'][3]['parent']==2
        bad=t/'bad.hex';bad.write_text('3003040201aa');run([bad],2,t)
        assert p.read_bytes()==raw
    else:
        p=t/'demo.json';p.write_bytes((ROOT/'example.json').read_bytes());raw=p.read_bytes();out=run([p],0,t)
        if REPO=='difference-bound-witness':assert not out['feasible']and out['sum_max']==-1
        elif REPO=='register-history-witness':assert out['linearization']==['read0','write1']
        else:assert out['area']==8 and out['holes']==1 and out['perimeter']==16
        bad=t/'bad.json';bad.write_text('{"size":[2,2],"counts":[3]}');run([bad],2,t)
        bad.write_text('{"duplicate":1,"duplicate":2}');run([bad],2,t)
        assert p.read_bytes()==raw
    run([t/'missing'],2,t)
print(json.dumps({'installed_console':True,'outside_checkout':True,'useful_example':True,'failure_case':True,'source_preserved':True}))
