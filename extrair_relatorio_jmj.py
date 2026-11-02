import os
import pandas as pd
import xlrd
import openpyxl
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging as log

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
load_dotenv()

# Config LOGs
home_dir = os.path.expanduser("~")

url = os.getenv("JMJ_URL")
usuario = os.getenv("JMJ_USER")
senha = os.getenv("JMJ_PASS")

pasta_protocolos = os.path.join(home_dir, "Downloads", "Protocolos JMJ")
if not os.path.exists(pasta_protocolos):
    os.makedirs(pasta_protocolos)
    print(f'Dataset JMJ criada com sucesso!')
else:
    arquivos_existentes = os.listdir(pasta_protocolos)
    for a in arquivos_existentes:
        if a.lower().endswith((".xls", ".xlsx")):
            caminho_arq_exists = os.path.join(pasta_protocolos, a)
            os.remove(caminho_arq_exists)

def driver_config():
    caminho_downloads = pasta_protocolos
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    ##configurações de download
    chrome_options.add_experimental_option("prefs",{
        "download.default_directory": str(caminho_downloads),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    driver = webdriver.Chrome(options=chrome_options)
    return driver

driver = driver_config()
wait = WebDriverWait(driver=driver, timeout= 30)
actions = ActionChains(driver)

def extrair_relatorio_beneficiarios():
    try:
        driver.get(url=url)
        if wait.until(EC.url_to_be(url)):
            print('URL acessada com sucesso, iniciando processo de coleta de dados!')
            # Pagina de login inicial
            input_user = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "body > ui-view > div > div > div > div > div > ui-view > form > div > div.login__form > div:nth-child(1) > input")))
            input_password = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/ui-view/div/div/div/div/div/ui-view/form/div/div[2]/div[2]/jmj-input-password-login/input")))
            input_user.clear(), input_password.clear()
            input_user.send_keys(usuario), input_password.send_keys(senha)
            btn_entrar = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "login__submit")))
            btn_entrar.click()
            print('sistema acessado, credenciais validas.')

            # Pagina inicial
            ## Sidebar
            btn_sidebar = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/ui-view/div[2]/header/nav/a")))
            btn_sidebar.click()

            ## Selecionar a aba de protocolos no Sidebar
            btn_protocolos = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "body > ui-view > div.wrapper.ng-scope > aside > section > ul > li:nth-child(3) > a")))
            btn_protocolos.click()
            protoc_benef = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/ui-view/div[2]/aside/section/ul/li[3]/ul/li[1]/a")))
            protoc_benef.click()

            # Relatório de Beneficiários
            ## Filtros
            filtro_status = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="status"]/div/div/input')))
            filtro_status.clear()
            filtro_status.send_keys("Finalizado")

            opcao_finalizado = wait.until(EC.visibility_of_element_located((By.XPATH, '//ul[contains(@class, "k-list")]//li[contains(., "Finalizado")]')))
            opcao_finalizado.click()

            data_extracao_inicio_dt = datetime.strptime("01/01/2026", "%d/%m/%Y")

            data_atual = datetime.today()

            filtro_date_abertura = driver.find_element(By.XPATH, '//*[@id="dataAberturaInicial"]')
            filtro_date_abertura_final = driver.find_element(By.XPATH, '//*[@id="dataAberturaFinal"]')

            while data_extracao_inicio_dt <= data_atual:
                data_extracao_fim_dt = min(data_extracao_inicio_dt + timedelta(days=5), data_atual) # Soma 5 dias

                data_extracao_inicio_str = data_extracao_inicio_dt.strftime("%d/%m/%Y")
                data_extracao_fim_str = data_extracao_fim_dt.strftime("%d/%m/%Y")
                try:
                    actions.move_to_element(filtro_date_abertura).click().perform()
                    for _ in range(10):
                        actions.send_keys(Keys.BACKSPACE)
                    actions.send_keys(data_extracao_inicio_str).perform()
                    actions.reset_actions()

                    actions.move_to_element(filtro_date_abertura_final).click().perform()
                    for _ in range(10):
                        actions.send_keys(Keys.BACKSPACE)
                    actions.send_keys(data_extracao_fim_str).perform()
                    actions.reset_actions()
                    print("=" * 85)
                    print('\nParametros de pesquisa aplicados, iniciando pesquisa.')

                    btn_pesquisa = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'body > ui-view > div.wrapper.ng-scope > div > div > ui-view > div > div:nth-child(3) > form > div.panel-body.with-border.ng-scope > div > div:nth-child(2) > button')))
                    actions.move_to_element(btn_pesquisa).perform()
                    btn_pesquisa.click()

                    ## Carregamento de tela
                    wait.until(EC.invisibility_of_element((By.CSS_SELECTOR, ".grid-loading-backgroud")))
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".grid-loading-backgroud.ng-hide")))

                    ## Verificar retorno de dados
                    mensagens_vazio = driver.find_elements(By.CSS_SELECTOR, ".grid-watermark")
                    tabela_vazia = any(msg.is_displayed() and "Nenhum registro encontrado" in msg.text for msg in mensagens_vazio)

                    if not tabela_vazia:
                        print(f"Registros encontrados! Exportando dados do periodo de {data_extracao_inicio_str} até {data_extracao_fim_str}")
                        btn_extracao = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="table"]/div[1]/div[1]')))
                        btn_extracao.click()

                        format_extracao = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="menuitem-1"]/button')))
                        format_extracao.click()
                        wait.until(EC.invisibility_of_element((By.XPATH, "/html/body/ui-view/div[1]/div[2]")))
                        time.sleep(10)

                        relatorios_baixados = [arq for arq in os.listdir(pasta_protocolos) if arq.lower().endswith(".xls") and not arq.lower().endswith(".crdownload")]
                        if relatorios_baixados:
                            ult_relatorio_baixado = sorted(relatorios_baixados, key=lambda arq: os.path.getmtime(os.path.join(pasta_protocolos, arq)), reverse=True)

                            caminho_antigo = os.path.join(pasta_protocolos, ult_relatorio_baixado)
                            extensao = os.path.splitext(caminho_antigo)[1]

                            novo_nome = f"relatorio de beneficiarios {data_extracao_inicio_str} - {data_extracao_fim_str}{extensao}".replace("/", ".")
                            caminho_novo = os.path.join(pasta_protocolos, novo_nome)
                            os.rename(caminho_antigo, caminho_novo)

                        else:
                            log.info(f"Sem dados no período {data_extracao_inicio_str} a {data_extracao_fim_str}.")

                except Exception as erro_lote:
                    log.warning(f"Falha ao processar lote de {data_extracao_inicio_str} a {data_extracao_fim_str}: {erro_lote}")

                data_extracao_inicio_dt = data_extracao_fim_dt + timedelta(days=1)
            return print(f"Extração JMJ bem sucedida, processo concluído!")
    
    except Exception as e:
        print(f"Erro na extração com o seguinte erro: {e}")

    except ValueError as error:
        print(f"Erro na extração com o seguinte erro: {error}")

    finally:
        driver.quit()

def estruturar_dataset(pasta_origem: str):
    pasta_destino = r"A:\Relatorios BI\Painel de SAC\dataset"
    os.makedirs(pasta_destino, exist_ok=True)

    arquivos_existentes = os.listdir(pasta_destino)
    for a in arquivos_existentes:
        if a.lower().endswith((".xls", ".xlsx")):
            caminho_arq_exists = os.path.join(pasta_destino, a)
            os.remove(caminho_arq_exists)

    arquivos = [arq for arq in os.listdir(pasta_origem) if arq.lower().endswith((".xls", ".xlsx"))]
    for arquivo in arquivos:
        caminho_completo_origem = os.path.join(pasta_origem, arquivo)
        df = pd.read_excel(caminho_completo_origem, engine="xlrd", skiprows=9)

        nome_sem_extensao = os.path.splitext(arquivo)[0]
        caminho_completo_destino = os.path.join(pasta_destino, f"{nome_sem_extensao}.xlsx")

        df.to_excel(caminho_completo_destino, index=False, engine="openpyxl")
        os.remove(caminho_completo_origem)
    print("Dataset estruturado e salvo em .xlsx com sucesso!")

def main():
    i = 1
    sucesso = False

    while i < 3:
        try:
            log.info("-" * 96)
            log.info(f"Iniciando extração tentativa {i}".center(96))
            log.info("-" * 96)

            extrair_relatorio_beneficiarios()
            estruturar_dataset(pasta_protocolos)

            log.info("-" * 96)
            log.info(f"Rotina concluída com sucesso!".center(96))
            log.info("-" * 96)

            sucesso = True
            break
            
        except Exception as e:
            log.error(f"Erro na extração tentativa {i}: {e}")
            i += 1
            if i <= 3:
                print("Aguardando 10 segundos antes de tentar novamente...")
                time.sleep(10)
        except ValueError as e:
            log.error(f"Erro na extração tentativa {i}: {e}")
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