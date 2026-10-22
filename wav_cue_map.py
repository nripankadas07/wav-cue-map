"""Inspect PCM/IEEE-float RIFF-WAVE chunks and direct-data cue/label references."""
import argparse,json,struct,sys

def analyze(b):
    if not isinstance(b,bytes)or len(b)>16777216:raise ValueError('WAV bytes exceed16MiB')
    if len(b)<12 or b[:4]!=b'RIFF' or b[8:12]!=b'WAVE':raise ValueError('little-endian RIFF WAVE required')
    if struct.unpack_from('<I',b,4)[0]+8!=len(b):raise ValueError('RIFF length differs from file length')
    def chunks(start,end):
        out=[];p=start
        while p<end:
            if len(out)>=5000 or p+8>end:raise ValueError('chunk count or truncated header at '+str(p))
            name=b[p:p+4];n=struct.unpack_from('<I',b,p+4)[0];stop=p+8+n
            if stop+(n%2)>end:raise ValueError('chunk crosses parent or lacks pad at '+str(p))
            out.append((name,p,p+8,stop));p=stop+(n%2)
        return out
    cs=chunks(12,len(b));formats=[c for c in cs if c[0]==b'fmt '];datas=[c for c in cs if c[0]==b'data']
    if len(formats)!=1 or len(datas)!=1:raise ValueError('exactly one fmt and data chunk required')
    _,_,p,end=formats[0]
    if end-p not in (16,18)or end-p==18 and b[p+16:end]!=b'\0\0':raise ValueError('only conventional16/18-byte fmt supported')
    code,channels,rate,byte_rate,align,bits=struct.unpack_from('<HHIIHH',b,p)
    if code not in (1,3)or not 1<=channels<=64 or not rate or bits not in ((8,16,24,32)if code==1 else(32,64)):raise ValueError('unsupported PCM/IEEE float format')
    if align!=channels*(bits//8)or byte_rate!=rate*align:raise ValueError('inconsistent alignment or byte rate')
    data=datas[0];length=data[3]-data[2]
    if length%align:raise ValueError('data contains incomplete frame')
    frames=length//align;cues=[];labels=[];findings=[];ids=set()
    def finding(kind,**x):findings.append({'kind':kind,**x})
    for name,off,p,end in cs:
        if name==b'cue ':
            if end-p<4:raise ValueError('truncated cue count')
            count=struct.unpack_from('<I',b,p)[0]
            if count>5000 or end-p!=4+24*count:raise ValueError('cue count/length mismatch')
            for i in range(count):
                ident,position,chunk,chunkstart,blockstart,sample=struct.unpack_from('<II4sIII',b,p+4+24*i)
                supported=chunk==b'data' and chunkstart==blockstart==0
                row={'id':ident,'position':position,'chunk_id_hex':chunk.hex(),'chunk_start':chunkstart,'block_start':blockstart,'sample_offset':sample,'supported_direct_data':supported,'byte_offset':data[2]+sample*align if supported and sample<frames else None}
                cues.append(row)
                if len(cues)>5000:raise ValueError('more than5000 cue points unsupported')
                if ident in ids:finding('duplicate_cue_id',id=ident)
                ids.add(ident)
                if not supported:finding('unsupported_cue_address',id=ident)
                elif sample>=frames:finding('cue_outside_data',id=ident,sample_offset=sample)
        elif name==b'LIST':
            if end-p<4:raise ValueError('LIST type missing')
            if b[p:p+4]!=b'adtl':continue
            for sub,suboff,q,stop in chunks(p+4,end):
                if sub!=b'labl':continue
                if stop-q<5 or b[stop-1]!=0:raise ValueError('labl needs ID and NUL-terminated text')
                ident=struct.unpack_from('<I',b,q)[0];raw=b[q+4:stop-1]
                labels.append({'id':ident,'text_utf8_lossy':raw.decode('utf8',errors='replace'),'text_hex':raw.hex()})
                if len(labels)>5000:raise ValueError('more than5000 labels unsupported')
    labelids=set()
    for l in labels:
        if l['id']not in ids:finding('orphan_label',id=l['id'])
        if l['id']in labelids:finding('duplicate_label',id=l['id'])
        labelids.add(l['id'])
    return {'format':{'code':code,'channels':channels,'sample_rate':rate,'bits':bits,'block_align':align},'frames':frames,
            'duration_fraction':str(frames)+'/'+str(rate),'chunks':[{'id_hex':n.hex(),'offset':o,'value_offset':p,'length':e-p}for n,o,p,e in cs],
            'cues':cues,'labels':labels,'findings':findings,'limitation':'No playlist/wavl/RF64/RIFX/extensible/compressed addressing, audio decoding or playback. Cue position is reported separately; sample offsets resolve only against one direct data chunk.'}

def example():
    def chunk(k,v):return k+struct.pack('<I',len(v))+v+(b'\0'if len(v)%2 else b'')
    fmt=struct.pack('<HHIIHH',1,1,8000,16000,2,16)
    cue=struct.pack('<I',1)+struct.pack('<II4sIII',1,0,b'data',0,0,3)
    label=chunk(b'labl',struct.pack('<I',1)+b'entry\0')
    body=b'WAVE'+chunk(b'fmt ',fmt)+chunk(b'cue ',cue)+chunk(b'LIST',b'adtl'+label)+chunk(b'data',b'\0'*16)
    return b'RIFF'+struct.pack('<I',len(body))+body

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('--make-example',action='store_true');a=p.parse_args()
    try:
        if a.make_example:
            with open(a.input,'xb')as f:f.write(example())
            print(json.dumps({'created':a.input}));return 0
        with open(a.input,'rb')as f:b=f.read(16777217)
        print(json.dumps(analyze(b),indent=2));return 0
    except (ValueError,OSError,UnicodeError,struct.error)as e:print(json.dumps({'error':str(e)}),file=sys.stderr);return 2

if __name__=="__main__": raise SystemExit(main())
