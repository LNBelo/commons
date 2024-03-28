# -*- coding: utf-8  -*-

"""
    Script baseado em Pywikibot https://www.mediawiki.org/wiki/Manual:Pywikibot

    Faz o carregamento de arquivos no Wikimedia Commons com base em uma planilha do mesmo formato para o Open Refine

    Possui a opção de previsualização no Wikimedia Commons

    Aceita url ou local do arquivo a ser carregado no Wikimedia Commons
"""
import urllib.parse
import webbrowser
import pandas
import pywikibot
from tkinter import filedialog
from pywikibot.specialbots import UploadRobot


def read_spreadsheet(ss, line):
    wikitext = ''
    path = ''
    name = ''

    for coluna in colunas:
        valor = str(ss[coluna][line])
        if coluna == 'path':
            path = valor
        elif coluna == 'name':
            name = valor
        elif coluna == 'wikitext':
            wikitext = valor

    return [path, name, wikitext]


def preview(ss):
    line = int(input('Qual é a linha do arquivo no planilha? ')) - 2
    read = read_spreadsheet(ss, line)
    name = urllib.parse.quote_plus(read[1])
    wikitext = urllib.parse.quote_plus(read[2])
    webbrowser.open(
        'https://commons.wikimedia.org/wiki/Special:ExpandTemplates?wpRemoveComments=true&wpInput='
        + wikitext + ' &wpContextTitle=' + name, new=2)


# Pywikibot
def complete_desc_and_upload(path, pagetitle, description, summary):
    url = path
    keepFilename = True  # True para não pedir para o usuário verificar o nome de cada arquivo
    verifyDescription = False  # False para não pedir para o usuário verificar a descrição de cada arquivo
    targetSite = pywikibot.DataSite('commons', 'commons')

    bot = UploadRobot(url, description=description, use_filename=pagetitle, keep_filename=keepFilename,
                      verify_description=verifyDescription, target_site=targetSite, summary=summary,
                      chunk_size=1024 * 1024)  # 1024 * 1024 convertendo bytes para megabytes
    bot.run()


def main(ss):
    first_line = int(input('Primeira linha com os dados a serem carregados: '))
    last_line = int(input('Última linha com os dados a serem carregados: '))
    summary = str(input('Digite o texto para o sumário:\n'
                        'Ex.: uploaded in the context of the GLAM-Partnership with Arquivo Nacional\n'))

    i = 1
    for line in range(first_line, last_line + 1):
        if first_line == last_line:
            total = 1
        else:
            total = last_line - first_line
        read = read_spreadsheet(ss, line - 2)
        path = read[0]
        pagetitle = read[1]
        description = read[2]
        print('Loading ' + str(round(float(i / int(total)) * 100, 2)) + '%' + ' (' + str(i) + '/' + str(total) + ')')
        print(str("Estou na linha " + str(line) + ' de ' + str(last_line)))
        complete_desc_and_upload(path, pagetitle, description, summary)
        i += 1


if __name__ == "__main__":
    ss = filedialog.askopenfilenames()[0]
    ss = pandas.read_excel(ss)
    colunas = ss.columns

    # Preview dos arquivos no  Commons
    answer = pywikibot.input_yn('Previsualização? ', default='', automatic_quit=False)
    if answer is True:
        preview(ss)
        while pywikibot.input_yn('Previsualização de outro arquivo? ', default='', automatic_quit=False) is True:
            preview(ss)
        keep = pywikibot.input_yn('Continuar carregamento? ', default='', automatic_quit=False)
        if keep is False:
            exit()

    try:
        main(ss)
    finally:
        pywikibot.stopme()
