library(filelock)

print("Entrando em Loop")
repeat {
  print("Loop")

  # Aguarda até o arquivo existir
  while (!file.exists("data/dadosAlagamentoPI.csv")) {
    print("Arquivo ainda não criado. Aguardando...")
    Sys.sleep(1)
  }

  # Tenta obter lock exclusivo
  lock_path <- "data/dadosAlagamentoPI.csv.lock"
  lock <- filelock::lock(lock_path, timeout = 5000)

  if (!is.null(lock)) {
    atual_mtime <- file.info("data/dadosAlagamentoPI.csv")$mtime

    if (!exists("last_mtime") || atual_mtime != last_mtime) {
      print("Dados divergentes, re-tratando")

      # Carrega e trata dados
      dados <- read.csv("data/dadosAlagamentoPI.csv", sep=",", na.strings = "", stringsAsFactors = T)
      
      # Tratamento temperatura
      medianaTemperatura <- median(dados[dados$Temperatura > -6 & dados$Temperatura < 41, ]$Temperatura, na.rm = TRUE)
      dados$Temperatura[dados$Temperatura < -6 | dados$Temperatura > 41] <- medianaTemperatura
      
      # Tratamento vazão
      dados <- subset(dados, Vazao.atual < Vazao.Media * 2)

      # Tratamento solo
      dados$Solo <- tolower(dados$Solo)
      dados$Solo[dados$Solo == "arenoso"] <- "Arenoso"
      dados$Solo[dados$Solo == "argiloso"] <- "Argiloso"
      dados$Solo[dados$Solo == "humifero"] <- "Humífero"
      dados$Solo[is.na(dados$Solo)] <- "Arenoso"
      dados$Solo <- factor(dados$Solo)

      # ID e index
      dados <- dados[, -1]
      row.names(dados) <- NULL

      # Renomeia colunas
      colnames(dados) <- c("vazaoMedia","vazaoAtual","milimitroHora","milimitroDia","milimitroSeteDias",
                           "temperatura","velocidadeVento","costa","cidade","vegetacao",
                           "montanha","solo","notas","alagou")

      write.csv(dados, "data/dadosCorretosPI.csv", row.names = TRUE)

      print("Dados divergentes tratados")
      last_mtime <- atual_mtime
    }

    # Libera o lock
    unlock(lock)
  } else {
    print("Arquivo está em uso por outro processo. Tentando novamente...")
  }

  Sys.sleep(5)
}