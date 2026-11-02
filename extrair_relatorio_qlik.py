import pandas as pd
import numpy as np
from datetime import datetime as dt
import time
import os
from dotenv import load_dotenv
import shutil

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
load_dotenv()


dir_user = os.path.expanduser('~')

PASTA_PROJETO = os.path.join(dir_user, "Desktop", "paineis", "Processamento de Contas Medicas")
DATASET_XML = os.path.join(PASTA_PROJETO, "Dataset XMLs")
DATASET_PRODUCAO = os.path.join(PASTA_PROJETO, "Dataset producao medica")

def verificar_pasta(caminho: str):
    if not os.path.exists(caminho):
        os.makedirs(caminho)
        print(f"Pasta {os.path.basename(caminho)} criada")

url = os.getenv('QLIK_URL')
usuario_qlik = os.getenv('QLIK_USER')
senha_qlik = os.getenv('QLIK_PASS')

def driver_config(url: str, pasta_download: str):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    ##configurações de download
    chrome_options.add_experimental_option("prefs",{
        "download.default_directory": str(pasta_download),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    return driver

def extrair_relatorio_xml():
    driver = driver_config(url=url, pasta_download=DATASET_XML)
    wait = WebDriverWait(driver, timeout=30)
    actions = ActionChains(driver)
    print("Página acessada com sucesso")

    input_user = wait.until(EC.presence_of_element_located((By.ID, "username-input")))
    input_password = wait.until(EC.presence_of_element_located((By.ID, "password-input")))
    login_btn = wait.until(EC.element_to_be_clickable((By.ID, "loginbtn")))
    print("Usuario e senha localizado")

    input_user.clear()
    input_password.clear()
    input_user.send_keys(usuario_qlik)
    input_password.send_keys(senha_qlik)
    login_btn.click()
    print("Credenciais enviadas!")

    time.sleep(5)
    folder_xml = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="q-route-area"]/div/div[1]/div/div/div/div/ul/li[2]/div/div[3]/div[1]/div/div')))
    try:
        folder_xml.click()
    except Exception:
        driver.execute_script("arguments[0].click();", folder_xml)
    print("Pasta do relatorio XML acessada")

    pages_open = driver.window_handles
    driver.switch_to.window(pages_open[-1])

    relatorio_xml = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="approved-sheet-section"]/li[2]/div/div/div/div[1]/div/div[2]')))
    try:
        relatorio_xml.click()
    except Exception:
        driver.execute_script("arguments[0].click();", relatorio_xml)
    print("Relatório acessado, começando a extração")

    table_relatorio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="grid"]/div[15]/div[1]/div/div[1]/article/div[1]')))
    actions.move_to_element(table_relatorio).perform()
    actions.context_click().perform()

    btn_baixar = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[8]/div/div/div/ng-transclude/ul/li[7]')))
    btn_baixar.click()

    btn_dados = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="export"]')))
    btn_dados.click()

    btn_exportar = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="data-export-settings-dialog"]/div[3]/button[2]')))
    btn_exportar.click()

    wait.until(EC.invisibility_of_element((By.XPATH, '//*[@id="export-dialog"]/div/div[2]/div')))
    url_extract = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "export-url")))
    url_extract.click()
    print("Relatório de XML extraído com sucesso!")
    driver.quit()

def estruturar_dataset(caminho: str) -> str:
    print(f"Iniciando estruturação do {os.path.basename(caminho)}")
    pasta_backup = os.path.join(caminho, "backup")
    os.makedirs(pasta_backup, exist_ok=True)

    arquivos = os.listdir(caminho)
    tem_crdownload = any(f.endswith(".crdownload") for f in arquivos)

    if arquivos and not tem_crdownload:
        apenas_arquivos = [f for f in arquivos if os.path.isfile(os.path.join(caminho, f))]

        if not apenas_arquivos:
            return None

        arquivos_ordenados = sorted(apenas_arquivos, key=lambda f: os.path.getmtime(os.path.join(caminho, f)), reverse=True)

        mais_recente = arquivos_ordenados[0]
        mais_recente_renomeado = os.rename(os.path.join(caminho, mais_recente), os.path.join(caminho, f"ft_xml - {dt.today().strftime(format= "%d-%m-%Y")}.xlsx"))
        arquivos_antigos = arquivos_ordenados[1:]

        for arq in arquivos_antigos:
            origem = os.path.join(caminho, arq)
            destino = os.path.join(pasta_backup, arq)
            shutil.move(origem, destino)
        print(f"Estruturação do {os.path.basename(caminho)} finalizada!")
        return mais_recente_renomeado
    return None

def main():
    i = 1
    sucesso = False
    while i < 3:
        print("-" * 96)
        print(f"Iniciando extração tentativa {i}".center(96))
        print("-" * 96)
        try:
            verificar_pasta(PASTA_PROJETO)
            verificar_pasta(DATASET_XML)
            verificar_pasta(DATASET_PRODUCAO)

            extrair_relatorio_xml()
            estruturar_dataset(DATASET_XML)

            print("-" * 96)
            print("Extração finalizada com sucesso".center(96))
            print("-" * 96)
            sucesso = True
            break

        except Exception as e:
            print(f"Erro na extração (tentativa {i}): {e}")
            i += 1
            if i <= 3:
                print("Aguardando 10 segundos antes de tentar novamente...")
                time.sleep(10)
        except ValueError as e:
                print(f"Erro na extração (tentativa {i}): {e}")
                i += 1
                if i <= 3:
                    print("Aguardando 10 segundos antes de tentar novamente...")
                    time.sleep(10)

    if not sucesso:
        print("-" * 96)
        print("Falha na extração após atingir o limite de tentativas.".center(96))
        print("-" * 96)

if __name__ == "__main__":
    main()
