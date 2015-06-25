from urllib.request import urlopen, Request, urlretrieve
import json
from os import listdir
from os.path import isfile, join
import csv
#from pymongo import MongoClient
from pandas import DataFrame
import numpy as np
#import matplotlib.pyplot as plt
import datetime
import shapefile


def le_arquivos(mypath):
    return [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]

def conecta(db):
    client = MongoClient()
    my_db = client["filiados"]
    my_collection = my_db[db]
    return my_collection

def baixa_dados():
    siglas = {
        "dem",
        "pen",
        "pc_do_b",
        "pcb",
        "pco",
        "pdt",
        "phs",
        "pmdb",
        "pmn",
        "pp",
        "ppl",
        "pps",
        "pr",
        "prb",
        "pros",
        "prp",
        "prtb",
        "psb",
        "psc",
        "psd",
        "psdb",
        "psdc",
        "psl",
        "psol",
        "pstu",
        "pt",
        "pt_do_b",
        "ptb",
        "ptc",
        "ptn",
        "pv",
        "sd"
    }
    ufs = {
        "ac",
        "al",
        "am",
        "ap",
        "ba",
        "ce",
        "df",
        "es",
        "go",
        "ma",
        "mg",
        "ms",
        "mt",
        "pa",
        "pb",
        "pe",
        "pi",
        "pr",
        "rj",
        "rn",
        "ro",
        "rr",
        "rs",
        "sc",
        "se",
        "sp",
        "to"
    }

    ja_temos = le_arquivos("dados/")
    for sigla in siglas:
        for uf in ufs:
            if sigla+"_"+uf+".zip" not in ja_temos:
                print("FALTA "+sigla.upper()+"-"+uf.upper())
                url = "http://agencia.tse.jus.br/estatistica/sead/eleitorado/filiados/uf/filiados_"+sigla+"_"+uf+".zip"
                #baixa arquivo
                urlretrieve(url, "dados/"+sigla+"_"+uf+".zip")

def sobe_bd():
    path = "dados/aplic/sead/lista_filiados/uf/"
    arquivos = le_arquivos(path)
    conexao = conecta("filiados")

    for a in arquivos:
        if a.startswith("filiados"):
            file = csv.DictReader(open(path+a,encoding="iso-8859-1"),delimiter=";")
            print(a)
            for row in file:
                conexao.insert(row)

def conta_filiados_mes():
    conexao = conecta("filiados")
    dados = conexao.find()
    saida = {}
    i = 0
    meses = [1,2,3,4]
    for d in dados:
        try:
            sigla = d["SIGLA DO PARTIDO"]
            data = [int(a) for a in d["DATA DA FILIACAO"].split("/")]
            dia = data[0]
            mes = data[1]
            ano = data[2]
            #if 1979 < ano < 2016:
            if ano == 2015:
                #if mes in meses:
                #if not (mes == 4 and dia > 14):
                #if ano not in saida:
                #    saida[ano] = {}
                if mes not in saida:
                    saida[mes] = {}
                if dia not in saida[mes]:

                    saida[mes][dia] = 0
                #if sigla not in saida[mes]:
                #    saida[mes][sigla] = 0
                saida[mes][dia] += 1
        except:
            print("Errinho! continuando")
            continue
        i += 1
        if i % 50000 == 0:
            print("ESTAMOS NA LINHA "+str(i))

    print(saida)
    with open('filiados_2015_dia.txt', 'w') as outfile:
        json.dump(saida, outfile)

def conta_estoque_ano():
    arquivos = le_arquivos(".")
    #if "partido_ano_filiados.json" in arquivos and "partido_ano_desfiliados.json" in arquivos:
    if "partido_ano_filiados2011.json" in arquivos and "partido_ano_filiados2011.json" in arquivos:
        print("Arquivos preparatórios foram encontrados! Vamos direto fazer o cálculo")
        termina_contagem_estoque()
    else:
        print("Não temos os arquivos preparatórios. Vamos montá-los do zero")
        prepara_contagem_estoque()
        termina_contagem_estoque()

def prepara_contagem_estoque():
    conexao = conecta("filiados")
    dados = conexao.find({"SIGLA DO PARTIDO":{"$in": ["PT","PMDB","PSDB","PSOL"]}},{'DATA DA FILIACAO':1,'SITUACAO DO REGISTRO':1,"_id":0,"SIGLA DO PARTIDO":1,"DATA DA DESFILIACAO":1,"DATA DO CANCELAMENTO":1,"UF":1,"NOME DO MUNICIPIO":1})

    filiados = {}
    desfiliados = {}
    saida = {}
    anos = range(1979,2016)
    for a in anos:
        filiados[a] = {}
        desfiliados[a] = {}
        saida[a] = {}

    i = 0
    for d in dados:
        i += 1
        if i % 50000 == 0:
            print("ESTAMOS NA LINHA "+str(i))

        data = [int(a) for a in d["DATA DA FILIACAO"].split("/")]
        dia_filiacao = data[0]
        mes_filiacao = data[1]
        ano_filiacao = data[2]

        if d["DATA DA DESFILIACAO"]:
            data = [int(a) for a in d["DATA DA DESFILIACAO"].split("/")]
            ano_desfiliacao = data[2]
        else:
            if d["DATA DO CANCELAMENTO"]:
                data = [int(a) for a in d["DATA DO CANCELAMENTO"].split("/")]
                ano_desfiliacao = data[2]
            else:
                ano_desfiliacao = False

        if (1979 < ano_filiacao < 2016 and (not ano_desfiliacao or 1979 < ano_desfiliacao < 2016)):
            cidade_uf = d["NOME DO MUNICIPIO"]+"/"+d["UF"]
            if not d["SIGLA DO PARTIDO"] in filiados[ano_filiacao]:
                filiados[ano_filiacao][d["SIGLA DO PARTIDO"]] = {}
            if cidade_uf not in filiados[ano_filiacao][d["SIGLA DO PARTIDO"]]:
                filiados[ano_filiacao][d["SIGLA DO PARTIDO"]][cidade_uf] = 0
            filiados[ano_filiacao][d["SIGLA DO PARTIDO"]][cidade_uf] += 1

            if ano_desfiliacao:
                if not d["SIGLA DO PARTIDO"] in desfiliados[ano_desfiliacao]:
                    desfiliados[ano_desfiliacao][d["SIGLA DO PARTIDO"]] = {}
                if cidade_uf not in desfiliados[ano_desfiliacao][d["SIGLA DO PARTIDO"]]:
                    desfiliados[ano_desfiliacao][d["SIGLA DO PARTIDO"]][cidade_uf] = 0
                desfiliados[ano_desfiliacao][d["SIGLA DO PARTIDO"]][cidade_uf] += 1

    #with open('partido_ano_filiados.json', 'w') as outfile:
    with open('partido_ano_filiados_cidade.json', 'w') as outfile:
        json.dump(filiados, outfile)

    #with open('partido_ano_desfiliados.json', 'w') as outfile:
    with open('partido_ano_desfiliados_cidade.json', 'w') as outfile:
        json.dump(desfiliados, outfile)


def termina_contagem_estoque():
    #with open('partido_ano_filiados.json', 'r') as jsonfile:
    with open('partido_ano_filiados_cidade.json', 'r') as jsonfile:
        filiados = json.load(jsonfile)

    #with open('partido_ano_desfiliados.json', 'r') as jsonfile:
    with open('partido_ano_desfiliados_cidade.json', 'r') as jsonfile:
        desfiliados = json.load(jsonfile)

    #primeiro, colocamos 0 filiados para os partidos que não tiveram filiados em um determinado ano
    partidos = []
    for ano in filiados:
        for sigla in filiados[ano]:
            if sigla not in partidos:
                partidos.append(sigla)

    for p in partidos:
        for ano in filiados:
            if p not in filiados[ano]:
                filiados[ano][p] = []

    #e aqui criamos uma lista de cidades para iterar por elas
    cidades = []

    #agora calculamos o saldo ano a ano
    saldo = {}
    for ano in filiados:
        if ano not in saldo:
            saldo[ano] = {}
        for sigla in filiados[ano]:
            saldo[ano][sigla] = {}
            for cidade_uf in filiados[ano][sigla]:
                if cidade_uf not in cidades:
                    cidades.append(cidade_uf)
                if sigla in desfiliados[ano]:
                    if cidade_uf in desfiliados[ano][sigla]:
                        saldo[ano][sigla][cidade_uf] = filiados[ano][sigla][cidade_uf] - desfiliados[ano][sigla][cidade_uf]
                    else:
                        saldo[ano][sigla][cidade_uf] = filiados[ano][sigla][cidade_uf]
                else:
                    saldo[ano][sigla][cidade_uf] = filiados[ano][sigla][cidade_uf]

    #e depois do saldo, o estoque
    estoque = {"sigla":[],"ano":[],"cidade":[],"estoque":[]}
    for ano in saldo:
        for sigla in saldo[ano]:
            for cidade_uf in cidades:
                estoque["sigla"].append(sigla)
                estoque["ano"].append(ano)
                estoque["cidade"].append(cidade_uf)
                estoque["estoque"].append(soma_anos_anteriores(saldo,ano,sigla,cidade_uf))

    with open ("estoque_partidos_ano_cidade.json","w") as outfile:
        json.dump(estoque,outfile)

    df = DataFrame(estoque)
    print(df)

    df = df.fillna(0)
    df.to_csv("estoque_partidos_ano_cidade.csv")

def soma_anos_anteriores(dados,ano,sigla,cidade_uf):
    anos = [int(k) for k in dados.keys()]
    primeiro = min(anos)
    saida = 0

    for a in range(primeiro,int(ano)+1):
        ano_atual = str(a)
        if sigla in dados[ano_atual]:
            if cidade_uf in dados[ano_atual][sigla]:
                saida += dados[ano_atual][sigla][cidade_uf]
    return saida

def conta_filiados_total():
    conexao = conecta("filiados")
    dados = conexao.find()
    saida = {}
    i = 0
    for d in dados:
        try:
            sigla = d["SIGLA DO PARTIDO"]
            data = [int(a) for a in d["DATA DA FILIACAO"].split("/")]
            mes = data[1]
            ano = data[2]
            if 1979 < ano < 2016:
                if ano not in saida:
                    saida[ano] = {}
                if mes not in saida[ano]:
                    saida[ano][mes] = {}
                if sigla not in saida[ano][mes]:
                    saida[ano][mes][sigla] = 0
                saida[ano][mes][sigla] += 1
        except:
            print("Errinho! continuando")
            continue
        i += 1
        if i % 50000 == 0:
            print("ESTAMOS NA LINHA "+str(i))

    print(saida)
    with open('partido_total.txt', 'w') as outfile:
        json.dump(saida, outfile)

def conta_dias():
    with open("filiados_2015_dia.txt",'r') as json_file:
        data = json.load(json_file)

    for dia in data["4"]:

        print(dia+": "+str(data["4"][dia]))

def analisa_json():
    with open("partido_mes.txt") as json_file:
    #with open('partido_total.txt') as json_file:
        data = json.load(json_file)
        dados = []
        for ano in data:
            if 1979 < int(ano) < 2016:
                for mes in data[ano]:
                    for sigla in data[ano][mes]:
                        item = {"ano":ano,"mes":mes,"sigla":sigla,"filiados":data[ano][mes][sigla]}
                        dados.append(item)

        dados = DataFrame(dados)
        dados.to_csv("partido_mes.csv",index=False)
        #dados.to_csv("partido_total.csv",index=False)
        print(dados)

def prepara_geojson():
    from pandas import read_csv
    dados = read_csv("estoque_partidos_ano_cidade.csv")

    dados["variavel"] = dados.apply(lambda t:t["sigla"]+"_"+str(t["ano"]),axis=1)
    for coluna in dados.columns:
        if coluna not in ["estoque","variavel","cidade"]:
            del dados[coluna]

    dados = dados.to_dict(orient="records")

    saida = {}

    i = 0
    for dado in dados:
        i+=1
        if i % 5000 == 0:
            print(i)
        nome = tira_acento(dado["cidade"])
        if nome not in saida:
            saida[nome] = {}
        saida[nome][dado["variavel"]] = dado["estoque"]

    with open("prep_geojson.json","w") as outfile:
        json.dump(saida,outfile)

    return saida

def tira_acento(s):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def cria_geojson_cidades(arquivo):
    #pegamos o json de dados que vamos usar aqui
    try:
        with open("prep_geojson.json","r") as jsonfile:
            dados = json.load(jsonfile)
            print("Carregamos o arquivo de prepração! Agora vamos mudar o shp")
    except:
        print("Não há arquivo pré-preparado. Vamos criá-lo")
        dados = prepara_geojson()

    import shapefile, copy
    #abrimos o shape
    reader = shapefile.Reader(arquivo)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []
    for sr in reader.shapeRecords():
       atr = dict(zip(field_names, sr.record))
       geom = sr.shape.__geo_interface__
       buffer.append(dict(type="Feature", \
        geometry=geom, properties=atr))

    #agora mudamos o que queremos mudar nas propriedades
    saida = []
    resta = ["cod_ibge","nome_ibge_","estado"]
    for a in buffer:
        linha = copy.deepcopy(a)
        for property in a["properties"]:
            if property not in resta:
                linha["properties"].pop(property, None)
        nome = tira_acento(linha["properties"]["nome_ibge_"].upper()+"/"+linha["properties"]["estado"])
        try:
            for partido_data in dados[nome]:
                linha["properties"][partido_data] = dados[nome][partido_data]
        except KeyError:
            pass
        saida.append(linha)

    # write the GeoJSON file
    from json import dumps
    geojson = open(arquivo+".json", "w")
    geojson.write(dumps({"type": "FeatureCollection",\
    "features": saida}, indent=2) + "\n")
    geojson.close()


#baixa_dados()
#descompacta(): #roda na pasta: #unzip \*.zip
#sobe_bd()
#conta_dias()
#conta_filiados_mes()
#conta_filiados_total()
#analisa_json()
#conta_estoque_ano()
#prepara_contagem_estoque()
#termina_contagem_estoque()

#conta_filiados_cidade()
cria_geojson_cidades("mapa/municipios_tse")
