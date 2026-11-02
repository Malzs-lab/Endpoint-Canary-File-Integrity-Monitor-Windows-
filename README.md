# Endpoint-Canary-File-Integrity-Monitor-Windows-
Script em Python voltado para monitoramento de seguranca defensiva (Blue Team). O script atua como um arquivo-isca (canary file): ele monitora o log de seguranca do Windows e, se o arquivo alvo for acessado, inspeciona conexoes de rede ativas no sistema e envia um alerta remoto via webhook.

---

Funcionalidades

- Auditoria de Acesso a Arquivos: Le o canal de eventos de seguranca do Windows (Security.evtx) buscando pelo Event ID 4663 (tentativa de acesso a objeto auditado).
- Inspecao de Rede em Tempo Real: Mapeia conexoes ativas com status ESTABLISHED usando a biblioteca psutil, filtrando processos comuns do sistema para destacar conexoes externas suspeitas.
- Alerta Remoto: Dispara um payload JSON via requisicao HTTP POST para um endpoint seguro (Formspree/Webhook) contendo usuario, processo responsavel e conexoes ativas.
- Anti-Spam de Notificacoes: Mecanismo simples de cooldown para evitar multiplos alertas repetidos em sequencia.

---

Tecnologias e Bibliotecas

- Python 3.10+
- pywin32: Acesso a API nativa do Windows para leitura de eventos (win32evtlog).
- psutil: Mapeamento de processos locais e sockets de rede abertos.
- requests: Envio de telemetria e disparo do alerta via HTTP.

---

Pre-Requisitos no Windows

Para que o Windows gere o evento 4663, a auditoria de acesso a objetos precisa estar habilitada:

1. Abra o Executar (Win + R), digite secpol.msc e pressione Enter.
2. Navegue ate:  
   Politicas Locais -> Politica de Auditoria -> Auditar acesso a objetos.
3. Marque a opcao Sucesso e clique em Aplicar.
4. No arquivo que servira de isca:
   - Clique com botao direito -> Propriedades -> aba Seguranca -> Avancadas.
   - Acesse a aba Auditoria, clique em Adicionar e defina o principal como Todos com permissao de leitura.

---

Instalacao e Uso

1. Clone o repositorio ou baixe o script:
   ```bash
   git clone https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git
   cd NOME_DO_REPOSITORIO
   ```

2. Crie e ative um ambiente virtual (recomendado):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Instale as dependencias:
   ```bash
   pip install pywin32 psutil requests
   ```

4. Configure as variaveis no inicio do script:
   - FORMSPREE_URL: URL do seu webhook ou endpoint de alerta.
   - NOME_DO_ARQUIVO_ALVO: Nome exato do arquivo que voce configurou a auditoria.

5. Execute como Administrador (necessario para ler o log Security):
   ```bash
   python main.py
   ```

---

## Exemplo de Dados no Alerta

```json
{
  "Alerta": "ARQUIVO CONFIDENCIAL VIOLADO!",
  "Arquivo_Violado": "C:\\Documentos\\senhas_confidenciais.txt",
  "Usuario_no_PC": "DESKTOP\\usuario",
  "Programa_Local_Usado": "notepad.exe",
  "CONEXOES_DE_REDE_SUSPEITAS": "IP: 198.51.100.23:4444 | Programa: powershell.exe | Status: ESTABLISHED",
  "Data_Hora": "2026-11-02T12:00:00Z"
