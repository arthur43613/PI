import csv
import random

idRio = 0 #Identificador do rio, servindo como nome
mediaVazao = 0 #Vazão media/padrão do rio mediada em m3/s
vazao = 0 #Vazão atual em m3/s
miliHora = 0 #mm/h de 2,5 a 10 medio, de 10 a 50 forte e acima violenta
miliDia = 0 #mm por dia, 50 medio, 50 a 100 forte, acima de 100 violenta
mili7 = 0 #mm nos ultimos sete dias
temp = 0 #Temperatura em
veloVen = 0 #Velociade do vento em
costa = False #Se o rio se encontra perto da costa
cidade = False #Se existe uma cidade perto do rio
vegetacao = False #Se existe vegetação suficiente para influenciar na absoção
montanha = False #Se existe montanhas perto do rio, ou se sua nascente vem de uma
solo = '' #Tipo de solo que o rio se encontra
nota = '' #Detalhes não expecificados nos outros topicos
alagou = False

ffT = [False,False,True]
ttF = [False,True,True]

solos = ['Arenoso','Argiloso','Humífero'] #Os tipos de solo com suas raridades

notas = ['Queimada Recente','Historicamente alagavel', 'Mare alta'] #Condições temporárias que favorecem os alagamentos

data = [['ID', 'Vazao Media', 'Vazao atual', 'Milimitro hora', 'Milimitro do dia', 'Milimitro em sete dias', 'Temperatura', 'Velocidade do Vento',
'Costa', 'Cidade', 'Vegetacao', 'Montanha', 'Solo', 'Notas','Alagou']] #Armazena os dados para serem passados para o csv

for idRio in range(10000):
    mediaVazao = round(random.triangular(2000, 200000, 5000)) #Gera a vazão media do rio

    vazao = round(random.triangular(mediaVazao/2, mediaVazao*2, mediaVazao)) #Gera a vazão atual do rio baseando na vazão media

    if random.random() < 0.5: #50 porcento de chance de estar chovendo
        miliHora = round(random.triangular(0, 65, 5))
    else:
        miliHora = 0

    miliDia = round(random.triangular(0, 100, 0))
    mili7= round(random.triangular(0, 500, 4))

    temp = round(random.triangular(-5, 40, 24))

    if miliHora >= 10: #Se estiver chovendo os ventos serão forte, caso contrario normais
        veloVen = round(random.triangular(20, 110, 20))
    else:
        veloVen = round(random.triangular(1, 40, 5))

    costa = random.choice(ffT)
    cidade = random.choice(ffT)
    vegetacao = random.choice(ttF)
    montanha = random.choice(ffT)

    if random.random() < 0.05: #Cinco porcento de chance de não gerar um solo
        solo = None
    else:
        solo = random.choice(solos)

    if random.random() < 0.15:
        nota = random.choice(notas)
    else:
        nota = None 
    
    if vazao > (mediaVazao*1.5): #Se a vazão estiver acima de 50% do normal
        alagou = True
    elif miliHora > 35 and miliDia > 70:
        alagou = True
    elif temp > 30 and montanha == True:
        alagou = True
    elif miliHora > 60 and veloVen < 15:
        alagou = True
    elif (solo == 'Arenoso' or 'ARENOSO' or 'arenoso') and vegetacao == False and miliHora > 40:
        alagou = True
    elif mili7 > 400 and cidade == True:
        alagou = True
    elif costa == True and nota == 'Mare alta':
        alagou = True
    else:
        alagou = False


    datatemp = [idRio,mediaVazao,vazao,miliHora,miliDia,mili7,temp,veloVen,costa,cidade,vegetacao,montanha,solo,nota,alagou]
    data.insert(idRio+1,datatemp)
    print(datatemp)

with open('dadosAlagamentoPI.csv', 'w', newline='') as csvfile:
    print('Escrito')
    writer = csv.writer(csvfile)
    writer.writerows(data)