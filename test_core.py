import struct,unittest,wave,io
from wav_cue_map import analyze,example

def riff(chunks):
    body=b'WAVE'+b''.join(k+struct.pack('<I',len(v))+v+(b'\0'if len(v)%2 else b'')for k,v in chunks)
    return b'RIFF'+struct.pack('<I',len(body))+body
FMT=struct.pack('<HHIIHH',1,1,8000,16000,2,16)
def cue(i,s,chunk=b'data',start=0):return struct.pack('<I',1)+struct.pack('<II4sIII',i,0,chunk,start,0,s)

class Wav(unittest.TestCase):
    def test_real_example_against_stdlib_wave(self):
        b=example();r=analyze(b)
        with wave.open(io.BytesIO(b),'rb')as f:self.assertEqual((f.getnchannels(),f.getsampwidth(),f.getframerate(),f.getnframes()),(1,2,8000,8))
        data=next(c for c in r['chunks']if c['id_hex']=='64617461');self.assertEqual(r['cues'][0]['byte_offset'],data['value_offset']+6);self.assertEqual(r['labels'][0]['text_utf8_lossy'],'entry');self.assertEqual(r['findings'],[])
    def test_offset_boundary_duplicate_and_unsupported_cue(self):
        b=riff([(b'fmt ',FMT),(b'data',b'\0'*4),(b'cue ',cue(1,2)),(b'cue ',cue(1,0,b'wavl'))]);r=analyze(b)
        self.assertEqual({f['kind']for f in r['findings']},{'cue_outside_data','duplicate_cue_id','unsupported_cue_address'});self.assertIsNone(r['cues'][1]['byte_offset'])
    def test_odd_unknown_chunk_and_orphan_labels(self):
        label=b'labl'+struct.pack('<I',6)+struct.pack('<I',9)+b'x\0';r=analyze(riff([(b'JUNK',b'x'),(b'fmt ',FMT),(b'data',b'\0'*4),(b'LIST',b'adtl'+label)]))
        self.assertEqual(r['frames'],2);self.assertEqual(r['findings'],[{'kind':'orphan_label','id':9}]);self.assertEqual(r['chunks'][1]['offset'],22)
    def test_truncation_and_riff_mismatch_reject(self):
        b=example()
        for i in range(len(b)):
            with self.assertRaises(ValueError):analyze(b[:i])
        with self.assertRaises(ValueError):analyze(b+b'\0')
    def test_invalid_format_alignment_cue_and_missing_pad(self):
        cases=[[(b'fmt ',FMT),(b'data',b'\0')],[(b'fmt ',FMT),(b'fmt ',FMT),(b'data',b'')],[(b'fmt ',FMT),(b'data',b'\0'*4),(b'cue ',struct.pack('<I',2))],[(b'fmt ',struct.pack('<HHIIHH',1,1,8000,1,2,16)),(b'data',b'')]]
        for cs in cases:
            with self.assertRaises(ValueError):analyze(riff(cs))
        b=riff([(b'fmt ',FMT),(b'data',b''),(b'JUNK',b'x')])[:-1];b=b[:4]+struct.pack('<I',len(b)-8)+b[8:]
        with self.assertRaises(ValueError):analyze(b)
    def test_float_and_data_before_fmt(self):
        fmt=struct.pack('<HHIIHH',3,2,44100,352800,8,32);r=analyze(riff([(b'data',b'\0'*16),(b'fmt ',fmt)]));self.assertEqual(r['frames'],2)

if __name__=='__main__':unittest.main()
