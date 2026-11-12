#!/usr/bin/env python3
"""Backup autenticado do Trabalho-Web-III: PostgreSQL + projeto + Telegram."""
from __future__ import annotations
import argparse, getpass, hashlib, io, json, os, re, shutil, subprocess, sys, tarfile, tempfile, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from argon2.low_level import Type, hash_secret_raw
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

MAGIC=b"TBW3BK1\n"; SALT=16; NONCE=12; TAG=16; BLOCK=1024*1024
PART=40*1024*1024
SKIP_DIRS={".git",".venv","__pycache__",".pytest_cache",".wrangler","node_modules","backups"}
TABLE=re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

def key_from(passphrase: str, salt: bytes) -> bytes:
    if len(passphrase)<16: raise ValueError("BACKUP_PASSPHRASE precisa ter ao menos 16 caracteres.")
    return hash_secret_raw(passphrase.encode(),salt,time_cost=3,memory_cost=65536,parallelism=2,hash_len=32,type=Type.ID)

def encrypt(src: Path,dst: Path,password: str):
    import secrets
    salt,nonce=secrets.token_bytes(SALT),secrets.token_bytes(NONCE)
    enc=Cipher(algorithms.AES(key_from(password,salt)),modes.GCM(nonce)).encryptor()
    with src.open("rb") as a,dst.open("wb") as b:
        b.write(MAGIC+salt+nonce)
        while chunk:=a.read(BLOCK): b.write(enc.update(chunk))
        b.write(enc.finalize()); b.write(enc.tag); b.flush(); os.fsync(b.fileno())

def decrypt(src: Path,dst: Path,password: str):
    header=len(MAGIC)+SALT+NONCE; size=src.stat().st_size
    if size<header+TAG: raise ValueError("Arquivo incompleto ou inválido.")
    with src.open("rb") as a:
        if a.read(len(MAGIC))!=MAGIC: raise ValueError("Formato de backup desconhecido.")
        salt,nonce=a.read(SALT),a.read(NONCE); a.seek(-TAG,os.SEEK_END); tag=a.read(TAG)
        left=size-header-TAG; a.seek(header)
        dec=Cipher(algorithms.AES(key_from(password,salt)),modes.GCM(nonce,tag)).decryptor()
        try:
            with dst.open("wb") as b:
                while left:
                    part=a.read(min(BLOCK,left))
                    if not part: raise ValueError("Arquivo truncado.")
                    left-=len(part); b.write(dec.update(part))
                b.write(dec.finalize())
        except InvalidTag as exc:
            dst.unlink(missing_ok=True)
            raise ValueError("Senha incorreta ou arquivo adulterado (autenticação GCM falhou).") from exc

def sha256(path: Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        while c:=f.read(BLOCK): h.update(c)
    return h.hexdigest()

def add_project(tar: tarfile.TarFile,root: Path):
    for base,dirs,files in os.walk(root):
        dirs[:]=[d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            p=Path(base)/name
            if p.is_symlink() or name.endswith((".pyc",".enc",".dump")): continue
            tar.add(p,arcname=(Path("project")/p.relative_to(root)).as_posix(),recursive=False)

def make_archive(root: Path,out: Path):
    with tempfile.TemporaryDirectory(prefix="tbw3-dump-") as td:
        dump=Path(td)/"database.dump"
        with dump.open("wb") as f:
            subprocess.run(["docker","compose","exec","-T","db","pg_dump","-U","estoque","-d","estoque","-Fc"],cwd=root,stdout=f,check=True)
        manifest={"format":"trabalho-web-iii","version":1,"created_at":datetime.now(timezone.utc).isoformat(),"database":"PostgreSQL 16 / estoque","includes":["project files","PostgreSQL custom dump"],"excludes":[".git",".venv","runtime caches","external VPS services"]}
        with tarfile.open(out,"w:gz") as tar:
            add_project(tar,root); tar.add(dump,arcname="database/database.dump")
            raw=json.dumps(manifest,ensure_ascii=False,indent=2).encode()
            info=tarfile.TarInfo("manifest.json"); info.size=len(raw); tar.addfile(info,io.BytesIO(raw))

def telegram_send(token: str,chat: str,file: Path,caption: str):
    boundary="----TBW3BackupBoundary"
    body=(f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{chat}\r\n"
          f"--{boundary}\r\nContent-Disposition: form-data; name=\"caption\"\r\n\r\n{caption[:900]}\r\n"
          f"--{boundary}\r\nContent-Disposition: form-data; name=\"document\"; filename=\"{file.name}\"\r\nContent-Type: application/octet-stream\r\n\r\n").encode()
    body+=file.read_bytes()+f"\r\n--{boundary}--\r\n".encode()
    req=urllib.request.Request(f"https://api.telegram.org/bot{token}/sendDocument",data=body,headers={"Content-Type":f"multipart/form-data; boundary={boundary}"})
    try:
        with urllib.request.urlopen(req,timeout=180) as response: result=json.loads(response.read())
    except urllib.error.URLError as exc: raise RuntimeError(f"Erro ao enviar ao Telegram: {exc}") from exc
    if not result.get("ok"): raise RuntimeError(f"Telegram recusou o arquivo: {result}")

def upload(path: Path,digest: str):
    token=os.getenv("TELEGRAM_BOT_TOKEN",""); chat=os.getenv("TELEGRAM_CHAT_ID","")
    if not token or not chat: raise ValueError("Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID.")
    if path.stat().st_size<=PART:
        telegram_send(token,chat,path,f"Backup Trabalho-Web-III\nSHA-256: {digest}"); return
    with tempfile.TemporaryDirectory(prefix="tbw3-parts-") as td:
        pieces=[]
        with path.open("rb") as src:
            i=1
            while chunk:=src.read(PART):
                p=Path(td)/f"{path.name}.part{i:04d}"; p.write_bytes(chunk); pieces.append(p); i+=1
        for i,p in enumerate(pieces,1):
            telegram_send(token,chat,p,f"Backup Trabalho-Web-III — parte {i}/{len(pieces)}\nArquivo: {path.name}\nSHA-256 completo: {digest}")

def create(root: Path):
    password=os.getenv("BACKUP_PASSPHRASE","")
    if len(password)<16: raise ValueError("Configure BACKUP_PASSPHRASE (mínimo 16 caracteres).")
    root=root.resolve()
    if not (root/"docker-compose.yml").is_file(): raise FileNotFoundError("docker-compose.yml não encontrado.")
    with tempfile.TemporaryDirectory(prefix="tbw3-backup-") as td:
        d=Path(td); archive=d/"backup.tar.gz"
        stamp=datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
        encrypted=d/f"trabalho-web-iii_{stamp}.tar.gz.enc"
        print("Exportando PostgreSQL e empacotando o projeto...")
        make_archive(root,archive)
        print("Criptografando com AES-256-GCM / Argon2id...")
        encrypt(archive,encrypted,password); digest=sha256(encrypted)
        print(f"Tamanho: {encrypted.stat().st_size} bytes | SHA-256: {digest}")
        upload(encrypted,digest)
        print("Telegram confirmou o recebimento do backup.")

def extract_project(tar: tarfile.TarFile,target: Path):
    target.mkdir(parents=True,exist_ok=True)
    if any(target.iterdir()): raise ValueError("O destino da recuperação completa precisa estar vazio.")
    members=[]
    for m in tar.getmembers():
        n=PurePosixPath(m.name)
        if n.is_absolute() or ".." in n.parts: raise ValueError(f"Caminho inseguro: {m.name}")
        if n.parts and n.parts[0]=="project":
            if m.issym() or m.islnk() or m.isdev(): raise ValueError(f"Tipo de arquivo não permitido: {m.name}")
            m.name=str(Path(*n.parts[1:]))
            if m.name!=".": members.append(m)
    tar.extractall(target,members=members)

def restore_db(dump: Path,project: Path,table: str|None):
    if table and not TABLE.fullmatch(table): raise ValueError("Nome de tabela inválido.")
    subprocess.run(["docker","compose","up","-d","db"],cwd=project,check=True)
    probe=["docker","compose","exec","-T","db","pg_isready","-U","estoque","-d","estoque"]
    for _ in range(30):
        if subprocess.run(probe,cwd=project,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0: break
        time.sleep(2)
    else: raise RuntimeError("PostgreSQL não ficou pronto em 60 segundos.")
    cmd=["docker","compose","exec","-T","db","pg_restore","-U","estoque","-d","estoque","--clean","--if-exists","--no-owner","--role=estoque"]
    if table: cmd += ["--table",f"public.{table}"]
    with dump.open("rb") as stream:
        proc=subprocess.run(cmd,cwd=project,stdin=stream)
    if proc.returncode: raise RuntimeError(f"pg_restore terminou com código {proc.returncode}.")
    print("Dump restaurado no PostgreSQL.")

def restore(args):
    password=os.getenv("BACKUP_PASSPHRASE") or getpass.getpass("Senha do backup: ")
    with tempfile.TemporaryDirectory(prefix="tbw3-restore-") as td:
        archive=Path(td)/"backup.tar.gz"
        print("Descriptografando e verificando autenticidade...")
        decrypt(args.input.resolve(),archive,password)
        with tarfile.open(archive,"r:gz") as tar:
            dumpinfo=tar.getmember("database/database.dump")
            dump=Path(td)/"database.dump"
            with tar.extractfile(dumpinfo) as src,dump.open("wb") as dst: shutil.copyfileobj(src,dst)
            if args.mode=="full":
                if not args.target: raise ValueError("Informe --target para recuperação completa.")
                target=args.target.resolve(); extract_project(tar,target)
                if not (target/"docker-compose.yml").is_file(): raise ValueError("docker-compose.yml ausente no backup.")
                restore_db(dump,target,None)
                subprocess.run(["docker","compose","up","-d","--build"],cwd=target,check=True)
                print("Recuperação completa concluída. Verifique containers e endpoint /saude.")
            else:
                if not args.confirm_overwrite: raise ValueError("A restauração sobrescreve dados; informe --confirm-overwrite.")
                if not args.project_dir: raise ValueError("Informe --project-dir para recuperação do banco.")
                restore_db(dump,args.project_dir.resolve(),args.table)

def main():
    p=argparse.ArgumentParser(description="Backup e recuperação do Trabalho-Web-III")
    sub=p.add_subparsers(dest="action",required=True)
    b=sub.add_parser("create"); b.add_argument("--project-dir",type=Path,default=Path.cwd())
    r=sub.add_parser("restore"); r.add_argument("--input",type=Path,required=True)
    r.add_argument("--mode",choices=("full","database"),required=True)
    r.add_argument("--project-dir",type=Path); r.add_argument("--target",type=Path)
    r.add_argument("--table"); r.add_argument("--confirm-overwrite",action="store_true")
    a=p.parse_args()
    try:
        if a.action=="create": create(a.project_dir)
        else: restore(a)
        return 0
    except Exception as exc:
        print(f"ERRO: {exc}",file=sys.stderr); return 1

if __name__=="__main__": raise SystemExit(main())
