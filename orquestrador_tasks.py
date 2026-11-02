import asyncio
from datetime import datetime, timedelta
import logging
import os
from pathlib import Path
import sys

home_dir = os.path.expanduser('~')
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("orquestrador.log", encoding="utf-8"),
        logging.StreamHandler()])

PYTHON_EXE = sys.executable

async def rodar_script_por_caminho(caminho_script: str):
    if not os.path.exists(caminho_script):
        logging.error(f"Arquivo não encontrado: {caminho_script}")
        return False

    nome_script = os.path.basename(caminho_script)
    pasta_script = os.path.dirname(caminho_script)

    logging.info(f"---> [INÍCIO] Executando script: {nome_script}")
    try:
        processo = await asyncio.create_subprocess_exec(
            PYTHON_EXE,
            caminho_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=pasta_script)
        
        stdout, stderr = await processo.communicate()

        if processo.returncode == 0:
            logging.info(f"---> [SUCESSO] Script {nome_script} finalizado com sucesso.")
            
            if stdout:
                logging.info(f"Saída do script:\n{stdout.decode('utf-8', errors='replace').strip()}")
            return True
        else:
            logging.error(f"---> [ERRO] O script {nome_script} falhou.")
            if stderr:
                logging.error(f"Erro detalhado:\n{stderr.decode('utf-8', errors='replace').strip()}")
            return False
    except Exception as e:
        logging.error(f"Erro ao tentar disparar o script {nome_script}: {e}", exc_info=True)
        return False

async def main():
    SCRIPT_JMJ = Path('extrair_relatorio_jmj.py').resolve()
    SCRIPT_QLIK = Path('extrair_relatorio_qlik.py').resolve()

    tasks = [
        asyncio.create_task(rodar_script_por_caminho(SCRIPT_JMJ)),
        asyncio.create_task(rodar_script_por_caminho(SCRIPT_QLIK))
        ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        logging.info("Orquestrador de Scripts iniciado!")
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Orquestrador finalizado pelo usuário.")