# Guia de Deploy Automático - Flask no cPanel

Este guia explica como configurar o deploy automático da aplicação Flask para o servidor cPanel (hvacsolution81.com) usando GitHub Actions.

## ⚠️ ALERTA DE SEGURANÇA CRÍTICO

**A password do cPanel foi exposta publicamente. Por favor, altere IMEDIATAMENTE a password do cPanel antes de continuar com qualquer configuração:**

1. Aceda ao cPanel: https://hvacsolution81.com:2083/
2. Vá a "Password & Security"
3. Altere a password para uma nova e segura
4. Guarde a nova password num gestor de passwords

## Visão Geral

O sistema de deploy automático funciona da seguinte forma:

1. Quando faz `git push` para a branch `main`, o GitHub Actions é acionado
2. O workflow conecta-se ao servidor via SSH usando uma chave privada
3. Sincroniza os ficheiros do repositório para o servidor usando `rsync`
4. Instala as dependências Python listadas em `requirements.txt`
5. Recarrega a aplicação tocando o ficheiro `passenger_wsgi.py`

## Pré-requisitos

- Acesso ao cPanel do servidor hvacsolution81.com
- Acesso de administrador ao repositório GitHub (para configurar Secrets)
- Cliente SSH instalado localmente (Linux/Mac incluído por defeito, Windows usar Git Bash ou WSL)

## Passo 1: Gerar Par de Chaves SSH

As chaves SSH permitem que o GitHub Actions se conecte ao servidor de forma segura sem password.

### No Linux/Mac/Git Bash:

```bash
# Gerar par de chaves SSH (pressione Enter para aceitar localização padrão)
ssh-keygen -t ed25519 -f ~/.ssh/deploy_key_hvacsolution -C "deploy@github-actions"

# Ver a chave pública (para copiar)
cat ~/.ssh/deploy_key_hvacsolution.pub

# Ver a chave privada (para copiar)
cat ~/.ssh/deploy_key_hvacsolution
```

**Importante:** 
- A chave **pública** (`.pub`) vai para o servidor
- A chave **privada** (sem `.pub`) vai para os GitHub Secrets

### No Windows (PowerShell):

```powershell
# Gerar par de chaves
ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\deploy_key_hvacsolution -C "deploy@github-actions"

# Ver a chave pública
Get-Content $env:USERPROFILE\.ssh\deploy_key_hvacsolution.pub

# Ver a chave privada
Get-Content $env:USERPROFILE\.ssh\deploy_key_hvacsolution
```

## Passo 2: Instalar Chave Pública no Servidor

Existem duas formas de adicionar a chave pública ao servidor:

### Opção A: Via SSH (mais rápido)

```bash
# Copiar chave pública para o servidor
ssh-copy-id -i ~/.ssh/deploy_key_hvacsolution.pub -p 22 hvacsolution81@142.132.146.190
```

### Opção B: Via File Manager do cPanel (alternativa)

1. Aceda ao cPanel: https://hvacsolution81.com:2083/
2. Abra **File Manager**
3. Navegue para a pasta home (normalmente `/home2/hvacsolution81/`)
4. Mostre ficheiros ocultos: **Settings** → ☑ **Show Hidden Files**
5. Crie a pasta `.ssh` se não existir (clique direito → Create New Folder)
6. Entre na pasta `.ssh`
7. Crie/edite o ficheiro `authorized_keys`:
   - Se o ficheiro já existe: clique direito → **Edit**
   - Se não existe: **New File** → nome: `authorized_keys`
8. Cole o conteúdo da chave **pública** (ficheiro `.pub`) numa nova linha
9. Guarde o ficheiro
10. Defina permissões corretas (essencial!):
    - Pasta `.ssh`: **700** (rwx------)
    - Ficheiro `authorized_keys`: **600** (rw-------)

### Opção C: Via SSH Terminal no cPanel

1. Aceda ao cPanel
2. Abra **Terminal**
3. Execute:

```bash
# Criar pasta .ssh se não existir
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Adicionar a chave pública
echo "COLE_AQUI_O_CONTEUDO_DA_CHAVE_PUBLICA" >> ~/.ssh/authorized_keys

# Definir permissões corretas
chmod 600 ~/.ssh/authorized_keys
```

## Passo 3: Testar Conexão SSH

Antes de configurar o GitHub, teste se a chave SSH funciona:

```bash
# Testar conexão SSH com a chave
ssh -i ~/.ssh/deploy_key_hvacsolution -p 22 hvacsolution81@142.132.146.190

# Se funcionar, deverá ver o prompt do servidor
# Digite 'exit' para sair
```

## Passo 4: Configurar GitHub Secrets

Os GitHub Secrets guardam informações sensíveis (chave privada, credenciais) de forma segura.

1. Vá ao repositório no GitHub: https://github.com/TR2008/TJR_TEST
2. Clique em **Settings** (⚙️)
3. No menu lateral esquerdo: **Secrets and variables** → **Actions**
4. Clique em **New repository secret** e adicione os seguintes secrets:

### Secret 1: SSH_HOST
- **Name:** `SSH_HOST`
- **Value:** `142.132.146.190`

### Secret 2: SSH_PORT
- **Name:** `SSH_PORT`
- **Value:** `22`

### Secret 3: SSH_USER
- **Name:** `SSH_USER`
- **Value:** `hvacsolution81`

### Secret 4: SSH_KEY
- **Name:** `SSH_KEY`
- **Value:** Conteúdo COMPLETO da chave **privada** (ficheiro sem `.pub`)

**Importante para SSH_KEY:**
- Copie TODO o conteúdo do ficheiro de chave privada, incluindo:
  ```
  -----BEGIN OPENSSH PRIVATE KEY-----
  ... (todo o conteúdo) ...
  -----END OPENSSH PRIVATE KEY-----
  ```
- Inclua a linha inicial e final
- Não adicione espaços ou quebras de linha extra

### Secret 5: DEPLOY_PATH
- **Name:** `DEPLOY_PATH`
- **Value:** `/home2/hvacsolution81/myflaskapp`

**Nota:** Ajuste o caminho `DEPLOY_PATH` se a sua aplicação estiver noutro local no servidor.

## Passo 5: Configurar Virtualenv no cPanel (Opcional mas Recomendado)

O virtualenv isola as dependências Python da aplicação.

1. Aceda ao cPanel
2. Vá a **Setup Python App**
3. Clique em **Create Application**
4. Configure:
   - **Python version:** 3.9 ou superior (escolha a versão mais recente disponível)
   - **Application root:** `/home2/hvacsolution81/myflaskapp` (mesmo caminho do DEPLOY_PATH)
   - **Application URL:** (deixe vazio se usar domínio próprio)
   - **Application startup file:** `passenger_wsgi.py`
   - **Application Entry point:** `application`
5. Clique em **Create**

O cPanel criará automaticamente:
- Um virtualenv em `~/virtualenv/myflaskapp/[versão]/`
- Um ficheiro `.htaccess` configurado
- Links simbólicos necessários

## Passo 6: Testar o Deploy Automático

Agora que tudo está configurado, teste o deploy:

1. Faça uma pequena alteração no código (por exemplo, adicione um comentário)
2. Faça commit e push para a branch `main`:

```bash
git add .
git commit -m "Teste de deploy automático"
git push origin main
```

3. Vá ao GitHub e verifique o progresso:
   - Aceda a: https://github.com/TR2008/TJR_TEST/actions
   - Deverá ver o workflow "Deploy Flask to cPanel" a correr
   - Clique no workflow para ver os logs detalhados

4. Se o workflow completar com sucesso (✓ verde):
   - A aplicação foi sincronizada para o servidor
   - As dependências foram instaladas
   - O Passenger foi recarregado
   - A aplicação deve estar disponível em: https://hvacsolution81.com/

## Resolução de Problemas

### Erro: "Permission denied (publickey)"

**Causa:** A chave SSH não está corretamente instalada no servidor.

**Solução:**
1. Verifique as permissões da pasta `.ssh` (700) e ficheiro `authorized_keys` (600)
2. Confirme que copiou a chave **pública** (.pub) para o servidor
3. Teste a conexão SSH localmente antes de tentar via GitHub Actions

### Erro: "Host key verification failed"

**Causa:** O servidor não está nos known_hosts.

**Solução:** O workflow já trata disto automaticamente com `ssh-keyscan`. Se persistir, limpe o ficheiro known_hosts local e tente novamente.

### Erro: "No such file or directory" no rsync

**Causa:** O caminho DEPLOY_PATH está incorreto.

**Solução:**
1. Verifique o caminho correto no servidor usando o Terminal do cPanel: `pwd`
2. Atualize o secret `DEPLOY_PATH` no GitHub com o caminho correto

### Aplicação não carrega (Erro 500)

**Causa:** Problemas com as dependências ou configuração do Passenger.

**Solução:**
1. Aceda ao Terminal do cPanel
2. Veja os logs de erro:
   ```bash
   cd ~/myflaskapp
   tail -f ~/logs/myflaskapp-error_log
   ```
3. Verifique se todas as dependências estão instaladas:
   ```bash
   source ~/virtualenv/myflaskapp/[versão]/bin/activate
   pip list
   ```
4. Teste a aplicação manualmente:
   ```bash
   python3 app.py
   ```

### Virtualenv não encontrado no workflow

**Causa:** O virtualenv não foi criado no cPanel ou está noutro caminho.

**Solução:** O workflow já tem fallback para `python3 -m pip --user`. Se preferir usar o virtualenv:
1. Crie a aplicação Python no cPanel (Passo 5)
2. Anote o caminho exato do virtualenv
3. Se necessário, ajuste o workflow para usar o caminho correto

## Estrutura de Ficheiros no Servidor

Após o deploy, a estrutura no servidor deverá ser:

```
/home2/hvacsolution81/myflaskapp/
├── .htaccess                 (criado pelo cPanel)
├── passenger_wsgi.py         (ponto de entrada Passenger)
├── app.py                    (aplicação Flask principal)
├── config.py
├── requirements.txt
├── auth.py
├── basket.py
├── ... (outros ficheiros da aplicação)
├── .gitignore
└── README_DEPLOY.md
```

## Manutenção

### Fazer Deploy de Novas Alterações

Basta fazer push para `main`:

```bash
git add .
git commit -m "Descrição das alterações"
git push origin main
```

O deploy é automático!

### Adicionar Novas Dependências

1. Adicione ao ficheiro `requirements.txt`
2. Commit e push
3. O workflow instala automaticamente

### Recarregar Manualmente a Aplicação

Se precisar recarregar manualmente no servidor:

```bash
ssh -p 22 hvacsolution81@142.132.146.190
cd ~/myflaskapp
touch passenger_wsgi.py
```

### Ver Logs da Aplicação

No Terminal do cPanel:

```bash
# Logs de erro
tail -f ~/logs/myflaskapp-error_log

# Logs de acesso
tail -f ~/logs/myflaskapp-access_log
```

## Segurança

### Boas Práticas

1. ✅ **Nunca** commite a chave privada SSH para o repositório (já está no .gitignore)
2. ✅ **Nunca** commite ficheiros `.env` com credenciais (já está no .gitignore)
3. ✅ Altere a password do cPanel regularmente
4. ✅ Use variáveis de ambiente para secrets na aplicação
5. ✅ Mantenha as dependências atualizadas (`pip list --outdated`)
6. ✅ Reveja os logs de deploy regularmente

### Revogar Acesso

Se precisar revogar o acesso de deploy:

1. Vá aos Secrets do GitHub e delete `SSH_KEY`
2. No servidor, remova a linha correspondente de `~/.ssh/authorized_keys`
3. Gere um novo par de chaves se necessário

## Suporte

Se encontrar problemas:

1. Verifique os logs do workflow no GitHub Actions
2. Verifique os logs da aplicação no servidor
3. Consulte a documentação do Passenger: https://www.phusionpassenger.com/
4. Documentação cPanel Python Apps: https://docs.cpanel.net/cpanel/software/python-selector/

---

**Última atualização:** Dezembro 2024  
**Repositório:** https://github.com/TR2008/TJR_TEST
