import time
import requests
import win32evtlog
import psutil
from datetime import datetime, timezone
import pywintypes

FORMSPREE_URL = "link do formspree"  # Substitua pelo seu endpoint do Formspree

NOME_DO_ARQUIVO_ALVO = "autoexplicativo..."

TEMPO_BLOQUEIO_SPAM = 30  
ultima_notificacao = 0    


def capturar_ips_conectados():
    """Rastreia conexões de rede ativas filtrando barulhos do Windows e conexões mortas."""
    conexoes_suspeitas = []
    
    PROGRAMAS_IGNORADOS = [
        'chrome.exe', 'steam.exe', 'robloxplayerbeta.exe', 
        'discord.exe', 'msedge.exe', 'firefox.exe', 'code.exe',
        'winword.exe', 'explorer.exe', 'svchost.exe', 'system idle process', 'system'
    ]
    
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.raddr and conn.raddr.ip not in ['127.0.0.1', '::1', '0.0.0.0']:
                if conn.status != 'ESTABLISHED':
                    continue
                    
                status = conn.status
                ip_externo = conn.raddr.ip
                porta_externa = conn.raddr.port

                try:
                    processo = psutil.Process(conn.pid)
                    nome_programa = processo.name()
                except:
                    nome_programa = "Desconhecido"
                if nome_programa.lower() not in PROGRAMAS_IGNORADOS:
                    info = f"IP: {ip_externo}:{porta_externa} | Programa: {nome_programa} | Status: {status}"
                    conexoes_suspeitas.append(info)
                    
    except Exception as e:
        return f"Erro ao escanear conexões de rede: {e}"

    if not conexoes_suspeitas:
        return "Nenhuma conexão externa suspeita detectada."

    return "\n".join(conexoes_suspeitas)

def vigiar_arquivos():
    global ultima_notificacao
    server = 'localhost'
    logtype = 'Security'
    
    try:
        hand = win32evtlog.OpenEventLog(server, logtype)
    except pywintypes.error as e:
        if e.winerror == 1314:
            print("[ERRO 1314] Privilegio insuficiente para ler o log 'Security'.")
            print("[DICA] Execute o VS Code ou o terminal como Administrador.")
        else:
            print(f"[ERRO] Falha ao abrir EventLog: {e}")
        return

    print(f"Vigilancia ativa. Monitorando {NOME_DO_ARQUIVO_ALVO}...")
    
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

    while True:
        try:
            events = win32evtlog.ReadEventLog(hand, flags, 0)
            if events:
                for event in events:
                    if event.EventID == 4663:
                        dados = event.StringInserts
                        if dados and len(dados) > 6:
                            nome_arquivo = str(dados[6]) 
                            usuario = str(dados[1])
                            processo = str(dados[11])
                            
                            if NOME_DO_ARQUIVO_ALVO.lower() in nome_arquivo.lower():
                                tempo_atual = time.time()
                                
                                if (tempo_atual - ultima_notificacao) > TEMPO_BLOQUEIO_SPAM:
                                    print(f"ALERTA: {NOME_DO_ARQUIVO_ALVO} foi acessado. Verificando conexoes...")
                                    
                                    ips_da_rede = capturar_ips_conectados()
                                    
                                    payload = {
                                        "Alerta": "ARQUIVO CONFIDENCIAL VIOLADO!",
                                        "Arquivo_Violado": nome_arquivo,
                                        "Usuario_no_PC": usuario,
                                        "Programa_Local_Usado": processo,
                                        "CONEXOES_DE_REDE_SUSPEITAS": ips_da_rede,
                                        "Data_Hora_UTC": datetime.now(timezone.utc).isoformat()
                                    }
                                    requests.post(FORMSPREE_URL, json=payload, timeout=5)
                                    print("Relatorio enviado com sucesso.")
                                    
                                    ultima_notificacao = tempo_atual

        except pywintypes.error as e:
            print(f"[ERRO] Falha na leitura do log de eventos: {e}")
            break
        except Exception as e:
            print(f"[ERRO INESPERADO] {e}")
        time.sleep(1)
   
if __name__ == "__main__":
    try:
      vigiar_arquivos()
    except KeyboardInterrupt:
     print("\n[INFO] Monitoramento encerrado pelo operador.")
