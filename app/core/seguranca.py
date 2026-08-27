from pwdlib import PasswordHash

gerenciador_hash = PasswordHash(["bcrypt"])

def criar_hash(senha: str) -> str:

    return gerenciador_hash.hash(senha)

def verificar_senha(senha: str, senha_hash: str) -> bool:
    
    return gerenciador_hash.verify(senha, senha_hash)
    