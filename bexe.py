#!/usr/bin/env python3
import argparse, hashlib, json, os, struct, sys
MAGIC=b'BEXE'; VERSION=1

def pe_info(data):
    if data[:2] != b'MZ': return {'valid_pe':False,'arch':'unknown','reason':'Missing MZ header'}
    if len(data)<0x40: return {'valid_pe':False,'arch':'unknown','reason':'Truncated DOS header'}
    peoff=struct.unpack_from('<I',data,0x3c)[0]
    if peoff+6>len(data) or data[peoff:peoff+4]!=b'PE\0\0': return {'valid_pe':False,'arch':'unknown','reason':'Missing PE signature'}
    machine=struct.unpack_from('<H',data,peoff+4)[0]
    return {'valid_pe':True,'machine':f'0x{machine:04x}','arch':{0x014c:'x86',0x8664:'x64',0xaa64:'ARM64'}.get(machine,'unknown')}

def pack(src,dst):
    data=open(src,'rb').read(); info=pe_info(data)
    manifest={'format':'BEXE','version':VERSION,'filename':os.path.basename(src),'size':len(data),'sha256':hashlib.sha256(data).hexdigest(),'payload_offset':0,**info}
    raw=json.dumps(manifest,separators=(',',':')).encode()
    offset=10+len(raw)
    manifest['payload_offset']=offset; raw=json.dumps(manifest,separators=(',',':')).encode(); offset=10+len(raw)
    with open(dst,'wb') as f:
        f.write(MAGIC); f.write(bytes([VERSION,0])); f.write(struct.pack('<I',len(raw))); f.write(raw); f.write(data)
    return manifest

def read(path):
    with open(path,'rb') as f:
        h=f.read(10)
        if len(h)<10 or h[:4]!=MAGIC: raise ValueError('Not a BEXE file')
        n=struct.unpack('<I',h[6:10])[0]; m=json.loads(f.read(n)); payload=f.read()
    return m,payload

def main():
    p=argparse.ArgumentParser(); s=p.add_subparsers(dest='cmd',required=True)
    a=s.add_parser('pack'); a.add_argument('src'); a.add_argument('-o','--output',required=True)
    a=s.add_parser('inspect'); a.add_argument('bexe')
    a=s.add_parser('unpack'); a.add_argument('bexe'); a.add_argument('-o','--output',required=True)
    ns=p.parse_args()
    if ns.cmd=='pack': print(json.dumps(pack(ns.src,ns.output),indent=2))
    elif ns.cmd=='inspect':
        m,d=read(ns.bexe); print(json.dumps(m,indent=2)); print('payload_sha256:',hashlib.sha256(d).hexdigest())
    else:
        m,d=read(ns.bexe); open(ns.output,'wb').write(d); print('Wrote',ns.output)
if __name__=='__main__': main()
