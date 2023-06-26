#list.packages <- c("WaveletComp", "ggplot", "tidyverse",)

if (!require("pacman")) {
    install.packages("pacman")
    library("pacman")
    }
pacman::p_load("WaveletComp", "ggplot2", "tidyverse", "lubridate")

data_df <- read.csv("Dados/df_spi.csv", sep = ";") %>% t()
coords <- data_df[(1:2),] %>% as.data.frame()
spi_df <- data_df[(3:dim(data_df)[1]),] %>% as.data.frame()
spi_df <- cbind("Data" = seq(as.Date("1951/12/1"), as.Date("2020/12/1"), "month"), spi_df)
spi_df <- subset(spi_df, month(spi_df$Data) == 12)


b1_df <- c()
b2_df <- c()
b3_df <- c()

for (i in (2:ncol(spi_df))){
  data_wavelets <- data.frame(SPI12 = spi_df[,i])
  
  wavelets <- analyze.wavelet(
    data_wavelets, my.series = "SPI12",
    loess.span = 0.5, method = "white.noise",
    dt = 1, dj = 1 / 20,
    lowerPeriod = 2, upperPeriod = 64,
    make.pval = TRUE, n.sim = 100)
    
  band_1 <- reconstruct(
    wavelets, sel.lower = 2, sel.upper = 8,
    show.legend = FALSE, only.coi = F,
    rescale = FALSE, only.sig = F, plot.rec = F)
  
  band_2 <- reconstruct(
    wavelets, sel.lower = 9, sel.upper = 40,
    show.legend = FALSE, only.coi = F,
    rescale = FALSE, only.sig = F, plot.rec = F)
  
  b1_df <- cbind(b1_df, band_1$series$SPI12.r)
  b2_df <- cbind(b2_df, band_2$series$SPI12.r)
  b3_df <- cbind(b3_df, data_wavelets$SPI12 - band_1$series$SPI12.r - band_2$series$SPI12.r)
}
b1_df <- as.data.frame(b1_df)
b1_df <- rbind(coords, b1_df)
rownames(b1_df) <- c("lon", "lat", as.character(spi_df$Data))
write.table(b1_df, "Dados/Banda1.csv", row.names = T, col.names = F, sep = ";")

b2_df <- as.data.frame(b2_df)
b2_df <- rbind(coords, b2_df)
rownames(b2_df) <- c("lon", "lat", as.character(spi_df$Data))
write.table(b2_df, "Dados/Banda2.csv", row.names = T, col.names = F, sep = ";")

b3_df <- as.data.frame(b3_df)
b3_df <- rbind(coords, b3_df)
rownames(b3_df) <- c("lon", "lat", as.character(spi_df$Data))
write.table(b3_df, "Dados/Banda3.csv", row.names = T, col.names = F, sep = ";")

