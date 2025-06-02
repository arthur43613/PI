import os
import csv
import random
import time
from tempfile import NamedTemporaryFile
import shutil

LOCKFILE = 'data/dadosAlagamentoPI.lock'

def acquire_lock():
    while os.path.exists(LOCKFILE):
        print('Lock encontrado, aguardando...')
        time.sleep(1)
    with open(LOCKFILE, 'w') as f:
        f.write(str(os.getpid()))

def release_lock():
    if os.path.exists(LOCKFILE):
        os.remove(LOCKFILE)

def atomic_write_csv(data, filename):
    dir_name = os.path.dirname(filename)
    with NamedTemporaryFile(mode='w', delete=False, dir=dir_name, newline='') as tmpfile:
        writer = csv.writer(tmpfile)
        writer.writerows(data)
        temp_name = tmpfile.name
    shutil.move(temp_name, filename)
    print('Escrito (atomic)')

idRio = 0
mediaVazao = 0
vazao = 0
miliHora = 0
miliDia = 0
mili7 = 0
temp = 0
veloVen = 0
costa = False
cidade = False
vegetacao = False
montanha = False
solo = ''
nota = ''
alagou = False

ffT = [False, False, True]
ttF = [False, True, True]

solos = ['Arenoso','Arenoso','Arenoso','Argiloso','Argiloso','Humífero','arenoso','ARENOSO','arenoso','argiloso','ARGILOSO','humifero']
notas = ['Queimada Recente','Historicamente alagavel', 'Mare alta']

data = [['ID', 'Vazao Media', 'Vazao atual', 'Milimitro hora', 'Milimitro do dia', 'Milimitro em sete dias', 'Temperatura', 'Velocidade do Vento',
         'Costa', 'Cidade', 'Vegetacao', 'Montanha', 'Solo', 'Notas','Alagou']]

# Primeira geração
for idRio in range(100):
    mediaVazao = round(random.triangular(2000, 200000, 5000))
    if random.random() < 0.05:
        vazao = round(random.triangular(mediaVazao*50, mediaVazao*200, mediaVazao*100))
    else:
        vazao = round(random.triangular(mediaVazao/2, mediaVazao*2, mediaVazao))

    miliHora = round(random.triangular(0, 65, 5)) if random.random() < 0.5 else 0
    miliDia = round(random.triangular(0, 100, 0))
    mili7 = round(random.triangular(0, 500, 4))
    temp = round(random.triangular(70, 500, 300)) if random.random() < 0.05 else round(random.triangular(-5, 40, 24))
    veloVen = round(random.triangular(20, 110, 20)) if miliHora >= 10 else round(random.triangular(1, 40, 5))
    costa = random.choice(ffT)
    cidade = random.choice(ffT)
    vegetacao = random.choice(ttF)
    montanha = random.choice(ffT)
    solo = None if random.random() < 0.05 else random.choice(solos)
    nota = random.choice(notas) if random.random() < 0.15 else None

    if vazao > mediaVazao*1.5:
        alagou = True
        print('0')
    elif miliHora > 35 and miliDia > 70:
        alagou = True
        print('1')
    elif temp > 30 and montanha:
        alagou = True
        print('2')
    elif miliHora > 60 and veloVen < 15:
        alagou = True
        print('3')
    elif solo and solo.lower() == 'arenoso' and not vegetacao and miliHora > 40:
        alagou = True
        print('4')
    elif mili7 > 400 and cidade:
        alagou = True
        print('5')
    elif costa and nota == 'Mare alta':
        alagou = True
        print('6')
    else:
        alagou = False

    datatemp = [idRio, mediaVazao, vazao, miliHora, miliDia, mili7, temp, veloVen, costa, cidade, vegetacao, montanha, solo, nota, alagou]
    data.append(datatemp)
    print(datatemp)

acquire_lock()
atomic_write_csv(data, 'data/dadosAlagamentoPI.csv')
release_lock()

# Loop infinito
while True:
    print('Dormindo (zzz)')
    time.sleep(10)

    acquire_lock()
    #data = data[:1]  # Mantém apenas o cabeçalho

    for idRio in range(100):
        mediaVazao = round(random.triangular(2000, 200000, 5000))
        if random.random() < 0.05:
            vazao = round(random.triangular(mediaVazao*50, mediaVazao*200, mediaVazao*100))
        else:
            vazao = round(random.triangular(mediaVazao/2, mediaVazao*2, mediaVazao))

        miliHora = round(random.triangular(0, 65, 5)) if random.random() < 0.5 else 0
        miliDia = round(random.triangular(0, 100, 0))
        mili7 = round(random.triangular(0, 500, 4))
        temp = round(random.triangular(70, 500, 300)) if random.random() < 0.05 else round(random.triangular(-5, 40, 24))
        veloVen = round(random.triangular(20, 110, 20)) if miliHora >= 10 else round(random.triangular(1, 40, 5))
        costa = random.choice(ffT)
        cidade = random.choice(ffT)
        vegetacao = random.choice(ttF)
        montanha = random.choice(ffT)
        solo = None if random.random() < 0.05 else random.choice(solos)
        nota = random.choice(notas) if random.random() < 0.15 else None

        if vazao > mediaVazao*1.5:
            alagou = True
            print('0')
        elif miliHora > 35 and miliDia > 70:
            alagou = True
            print('1')
        elif temp > 30 and montanha:
            alagou = True
            print('2')
        elif miliHora > 60 and veloVen < 15:
            alagou = True
            print('3')
        elif solo and solo.lower() == 'arenoso' and not vegetacao and miliHora > 40:
            alagou = True
            print('4')
        elif mili7 > 400 and cidade:
            alagou = True
            print('5')
        elif costa and nota == 'Mare alta':
            alagou = True
            print('6')
        else:
            alagou = False

        datatemp = [idRio, mediaVazao, vazao, miliHora, miliDia, mili7, temp, veloVen, costa, cidade, vegetacao, montanha, solo, nota, alagou]
        data.append(datatemp)
        print(datatemp)

    atomic_write_csv(data, 'data/dadosAlagamentoPI.csv')
    release_lock()