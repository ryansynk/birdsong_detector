library(tuneR)
library(warbleR)
library(dplyr)

# function to convert mp3 files to wav files and store them back
convert_to_wav <- function(speciesName){
  print("Converting to wav...")
  parent <- getwd()
  subdir <- speciesName
  source_directory <- file.path(parent, subdir)
  dir.create(source_directory)
  setwd(source_directory)
  dest_directory <- file.path(source_directory, "wav")
  dir.create(dest_directory)
  
  files <- list.files(path=".", pattern="*.mp3", full.names=FALSE, recursive=FALSE)
  for(file in files){
    out <- tryCatch( {
    
    wav <- gsub(".mp3", ".wav", file)
    mp3 <- readMP3(file)
    writeWave(mp3, file.path(dest_directory, wav), extensible = FALSE)
    },
    error=function(e){
      message(paste("File error:", file))
      return(NA)
    }, warning=function(w){
      message(paste("File Warning:", file))
    }
    )
  }
}

# uses WarbleR to hit the xeno-canto API and download audio and metadata
fetch_data <- function(speciesName){
  parent <- getwd()
  subdir <- speciesName
  directory <- file.path(parent, subdir)
  dir.create(directory)
  setwd(directory)
  all_file <- paste(speciesName, "_all_samples", sep="")
  A_file <- paste(speciesName, "_A_samples", sep="")
  
  samples <- querxc(qword = speciesName, download = FALSE)
  
  samples.song <- samples[grep("song", samples$Vocalization_type, ignore.case = TRUE), ]
  samples.song.A <- samples.song[samples.song$Quality == "A",]
  samples.song.LQ <- samples.song[samples.song$Quality != "A",]
  
  n_songs <- nrow(samples.song)
  n_HQ <- nrow(samples.song.A)
  ratio <- n_HQ / n_songs
  if (n_songs >=100 && ratio >= .2){
    if(n_songs > 800) {
      samples.song.A <- sample_n(samples.song.A, size = 200)
      tmp.samples.song <- sample_n(samples.song.LQ, size = 600)
      samples.song <- distinct(rbind(samples.song.A, tmp.samples.song))  
    }
    out <- tryCatch( {
      querxc(X = samples.song)
      write.csv(samples.song, all_file)
    
      
    },
    error=function(e){
      message(paste("File error:"))
      
    }, warning=function(w){
      message(paste("File Warning:"))
    }
    )
    
  }
}


# Set the root directory that contains the scripts and
# data directories.
working_directory <- "D:/Document-HDD/UMD/Senior 2/498/"


# loop through all of the species, fetch the data, then convert it all to WAV
for(name in c("Parus major", "Phylloscopus collybita", "Baeolophus bicolor", "Melospiza melodia", "Cardinalis cardinalis", "Hirundo rustica", "Zenaida macroura", 
              "Spinus tristis", "Icterus galbula", "Sturnella magna", "Thryothorus ludovicianus", "Passer domesticus", "Poecile atricapillus", 
              "Turdus migratorius", "Cyanistes caeruleus", "Loxia curvirostra", "Passer montanus", "Sylvia atricapilla", "Sylvia communis")){
  setwd(working_directory)
  fetch_data(name)
  setwd(working_directory)
  convert_to_wav(name)
}

