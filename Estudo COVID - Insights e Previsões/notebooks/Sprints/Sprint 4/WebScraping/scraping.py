from bs4 import BeautifulSoup
import datetime as dt
from time import sleep
from random import randint, choice
import json

from requests_html import HTMLSession

# Intervalo a ser extraido
start_time = dt.datetime(2020, 1, 1) 
end_time = dt.datetime(2020, 12, 31)

vetor_datas = [start_time]
i = 1

# Formação do vetor com todas as datas do período a ser extraido
while vetor_datas[-1] < end_time:
    vetor_datas.append(start_time + dt.timedelta(days = i))
    i +=1 

for data in vetor_datas:
    date = data.strftime("%m/%d/%Y")
    date_json = data.strftime("%d-%m-%Y")
    dict_list = []

    # Diversas opções de User-Agent para o cabeçalho, rotacionar evita o bloqueio por parte do google
    UA = [  'Mozilla/5.0 (Linux; Android 6.0.1; SAMSUNG SM-N910F Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/4.0 Chrome/44.0.2403.133 Mobile Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3542.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
            'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36']
    
    user_agent = choice(UA)
    headers = {'User-Agent': user_agent}

    # Definição das search queries e geolocalização correspondente
    queries = [ 
                ('covid+argentina', 'ar'),
                ('covid+spain', 'es'),
                ('covid+ecuador', 'ec'),
                ('covid+mexico', 'mx'),
                ('covid+chile', 'cl')
                ]

    for query, geo in queries:
        # Os parametros importantes da URL de pesquisa do google são os seguintes:
        # q é o parametro resposavel pela search query, é o campo utilizado
        # gl é o parametro de geolocalização, define a região da pesquisa
        # tbs define o range de datas da busca
        # tbm realiza a pesquisa na aba de 'news'

        URL = f'https://www.google.com/search?q={query}&gl={geo}&tbs=cdr:1,cd_min:{date},cd_max:{date}&tbm=nws'

        with HTMLSession(browser_args=["--no-sandbox", "--user-agent='Testing'", '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36']) as session:

            # Carrega a URL numa sessão com suporte a JavaScript
            r = session.get(URL, headers=headers)

            # Metodo render executa o JavaScript presente na página.
            r.html.render(timeout=30)

            soup = BeautifulSoup(r.html.html, 'html.parser')

            print(soup)

            # Encontra a div que contém as noticias pelo atributo 'class'
            search_class = soup.find('div', attrs = {'class':'MjjYud'})
            
            if search_class:
                for item in search_class.find_all("div", attrs = {"class": "SoaBEf"}): # Dentro da div que contém as noticias, encontra as divs que contém cada noticia especifica
                    if item:
                        print(f'Titulo: {item.find("div", attrs = {"class": "mCBkyc ynAwRc MBeuO nDgy9d"}).text}') # Retorna o texto dentro da div
                        print(f'Data : {date_json}') # A janela de tempo definida
                        print(f'URL da noticia: {item.find("a", href = True)["href"]} \n') # Encontra o link da noticia

                        # Transforma as informações anteriores em um dicionario
                        dictionary = {
                        "Titulo": f'{item.find("div", attrs = {"class": "mCBkyc ynAwRc MBeuO nDgy9d"}).text}',
                        "Data": f"{date_json}",
                        "URL da noticia":  f'{item.find("a", href = True)["href"]}'
                        }

                        # Salva este dicionario em uma lista
                        dict_list.append(dictionary)
            
            else:
                # Caso a primeira div não exista, escreve valores padrão
                dictionary = {
                    "Titulo": f'não há dados',
                    "Data": f"{date_json}",
                    "URL da noticia":  f'não há dados'
                    }
                dict_list.append(dictionary)
                break
        
            # Salva a lista de dicionários em um JSON na camada de bronze.
            with open(fr"F:\Users\victo\Documents\GitHub\bootcamp_blue_Projeto2\Estudo COVID - Insights e Previsões\dados\Bronze\WebScraping - Google News\{query}\news_json{date_json}.json", "w", encoding="utf-8") as outfile:
                json.dump(dict_list, outfile, ensure_ascii=False, indent=4)

        # Necessário esperar entre 60 e 90 segundos entre cada request para evitar a detecção do google.
        sleep(randint(60,90))