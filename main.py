from urllib.request import urlopen, Request, urlretrieve
import json
from os import listdir
from os.path import isfile, join
import csv
from pymongo import MongoClient
from pandas import DataFrame
import numpy as np
#import matplotlib.pyplot as plt
import datetime

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


#baixa_dados()
#descompacta(): #roda na pasta: #unzip \*.zip
#sobe_bd()
conta_dias()
#conta_filiados_mes()
#conta_filiados_total()
#analisa_json()

