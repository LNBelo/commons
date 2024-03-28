# -*- coding: utf-8  -*-

"""
    Script baseado em Pywikibot https://www.mediawiki.org/wiki/Manual:Pywikibot

    Faz o carregamento de arquivos no Wikimedia Commons com base em uma planilha do mesmo formato do Pattypan
    https://commons.wikimedia.org/wiki/Commons:Pattypan/Simple_manual#Fill_in_the_spreadsheet_with_file_descriptions

    Possui a opção de previsualização no Wikimedia Commons

    Aceita url ou local do arquivo a ser carregado no Wikimedia Commons
"""
import os
import re
import sys
import urllib.parse
import webbrowser
import pandas
import pywikibot
from tkinter import filedialog
from pywikibot.specialbots import UploadRobot


spreadsheet = filedialog.askopenfilenames()[0]
name_data = ['Data', 'data', 'DATA']
for name in name_data:
    try:
        data = pandas.read_excel(spreadsheet, name)
        colunas = data.columns
        break
    except ValueError:
        continue

name_template = ['Template', 'template', 'TEMPLATE']
for name in name_template:
    try:
        template = str(pandas.read_excel(spreadsheet, name).columns[0])
        template = re.sub('<#if categories.*', '${categories}', template, flags=re.DOTALL)
        break
    except ValueError:
        continue


# Faz a leitura de uma linha da planilha
def read_spreadsheet(line):
    body = template
    path = ''
    page_title = ''
    # Para cada coluna obtém o respectivo valor e o template com as informações
    for coluna in colunas:
        valor = str(data[coluna][line])
        if coluna == 'path':
            path = valor
        elif coluna == 'name':
            page_title = valor
        elif valor == 'nan':  # Trata células vazias
            body = body.replace('${' + coluna + '}', '')
        elif coluna == 'categories':
            try:
                categories = '[[Category:' + ']]\n[[Category:'.join(valor.split(';')) + ']]'
            except ValueError:
                categories = '[[Category:' + valor + ']]'
            body = body.replace('${' + coluna + '}', str(categories))
        else:
            body = body.replace('${' + coluna + '}', valor)

    extensao = os.path.splitext(path)[1]
    page_title = page_title + extensao

    return [path, page_title, body]


# Função para pré-visualização no Wikimedia Commons
def preview():
    read = read_spreadsheet(int(input('Qual é a linha do arquivo no planilha? ')) - 2)
    title = urllib.parse.quote_plus(read[1])
    text = urllib.parse.quote_plus(read[2])
    webbrowser.open(
        'https://commons.wikimedia.org/wiki/Special:ExpandTemplates?wpRemoveComments=true&wpInput=' + text + ' &wpContextTitle=' + title,
        new=2)


# Função Pywikibot
def complete_desc_and_upload(path, pagetitle, description, summary):
    url = path
    keepFilename = True  # True para não verificar o nome de cada arquivo
    verifyDescription = False  # False para não verificar a descrição de cada arquivo
    targetSite = pywikibot.DataSite('commons', 'commons')

    bot = UploadRobot(url, description=description, use_filename=pagetitle, keep_filename=keepFilename,
                      verify_description=verifyDescription, target_site=targetSite, summary=summary)
    bot.run()


# Função para carregamento de arquivos no Wikimedia Commons
def main(argv):
    first_line = int(input('Primeira linha com os dados a serem carregados: '))
    last_line = int(input('Última linha com os dados a serem carregados: '))
    summary = str(input('Digite o texto para o sumário:\nEx.: uploaded in the context of the GLAM-Partnership with Arquivo Nacional\n'))

    i = 1
    for line in range(first_line, last_line + 1):
        if first_line == last_line:
            total = 1
        else:
            total = last_line - first_line
        read = read_spreadsheet(line - 2)
        path = read[0]
        pagetitle = read[1]
        description = read[2]
        print('Loading ' + str(round(float(i / int(total)) * 100, 2)) + '%' + ' (' + str(i) + '/' + str(total) + ')')
        print(str("Estou na linha " + str(line) + ' de ' + str(last_line)))
        complete_desc_and_upload(path, pagetitle, description, summary)
        i += 1


# Preview dos arquivos no  Commons
answer = pywikibot.input_yn('Previsualização? ', default='', automatic_quit=False)
if answer is True:
    preview()
    while pywikibot.input_yn('Previsualização de outro arquivo? ', default='', automatic_quit=False) is True:
        preview()
    keep = pywikibot.input_yn('Continuar carregamento? ', default='', automatic_quit=False)
    if keep is False:
        exit()

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    finally:
        pywikibot.stopme()
