dados = read.csv("dadosAlagamentoPI.csv", sep=",", na.strings = "", stringsAsFactors = T)

#Tratamento temperatura
medianaTemperatura = median(dados[dados$Temperatura>-6|dados$Temperatura<41,]$Temperatura)
dados[dados$Temperatura< (-6)|dados$Temperatura>41,]$Temperatura = medianaTemperatura

#Tratamento vazão
dados <- subset(dados,Vazao.atual < Vazao.Media*2)

#Tratamento solo
dados$Solo[dados$Solo == "arenoso" | dados$Solo == "ARENOSO"] = "Arenoso"
dados$Solo[dados$Solo == "argiloso" | dados$Solo =="ARGILOSO"] = "Argiloso"
dados$Solo[dados$Solo=="humifero"] = "Humífero"
dados$Solo[is.na(dados$Solo)]="Arenoso"
dados$Solo = factor(dados$Solo)

#Tratamento ID e index
dados <- dados[,-1]
row.names(dados) <- NULL

#Tratamento Colunas
colnames(dados) = c("vazaoMedia","vazaoAtual","milimitroHora","milimitroDia","milimitroSeteDias","temperatura","velocidadeVento","costa","cidade","vegetacao","montanha","solo","notas","alagou")

#Cria csv com dados tratados
write.csv(dados,"dadosCorretosPI.csv",row.names = TRUE)




last_mtime <- file.info("dadosAlagamentoPI.csv")$mtime
print("Entrando em Loop")
repeat {
  print("Loop")
  atual_mtime <- file.info("dadosAlagamentoPI.csv")$mtime
  
  if (atual_mtime != last_mtime) {
    print("Dados divergentes, re-tratando")
    # Recarrega o arquivo inteiro ou parte dele
    dados = read.csv("dadosAlagamentoPI.csv", sep=",", na.strings = "", stringsAsFactors = T)
    
    #Tratamento temperatura
    medianaTemperatura = median(dados[dados$Temperatura>-6|dados$Temperatura<41,]$Temperatura)
    dados[dados$Temperatura< (-6)|dados$Temperatura>41,]$Temperatura = medianaTemperatura
    
    #Tratamento vazão
    dados <- subset(dados,Vazao.atual < Vazao.Media*2)
    
    #Tratamento solo
    dados$Solo[dados$Solo == "arenoso" | dados$Solo == "ARENOSO"] = "Arenoso"
    dados$Solo[dados$Solo == "argiloso" | dados$Solo =="ARGILOSO"] = "Argiloso"
    dados$Solo[dados$Solo=="humifero"] = "Humífero"
    dados$Solo[is.na(dados$Solo)]="Arenoso"
    dados$Solo = factor(dados$Solo)
    
    #Tratamento ID e index
    dados <- dados[,-1]
    row.names(dados) <- NULL
    
    #Tratamento Colunas
    colnames(dados) = c("vazaoMedia","vazaoAtual","milimitroHora","milimitroDia","milimitroSeteDias","temperatura","velocidadeVento","costa","cidade","vegetacao","montanha","solo","notas","alagou")
    
    #Cria csv com dados tratados
    write.csv(dados,"dadosCorretosPI.csv",row.names = TRUE)
    print("Dados divergentes tratados")
    
    # Atualiza o tempo da última modificação
    last_mtime <- atual_mtime
  }
  
  Sys.sleep(15)  # Checa a cada 10 segundos
}