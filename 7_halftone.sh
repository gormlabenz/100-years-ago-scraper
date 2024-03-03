#!/bin/bash

# Eingabeparameter
DIR="images"
COLOR1="#FA461E"
COLOR2="#121212"

# Neuen Ordner erstellen
NEW_DIR="${DIR}_transformed"
cp -r "$DIR" "$NEW_DIR"

# In das neue Verzeichnis wechseln
cd "$NEW_DIR" || exit

# Logge den aktuellen Pfad
echo "Current path: $(pwd)"

# Skaliere alle Bilder auf 1080px Breite
mogrify -resize 1080x -format png *.{jpg,jpeg,png,gif,bmp,JPG,JPEG,PNG,GIF,BMP}

# Erstelle einen Farbverlauf
convert -size 1x100 gradient:"$COLOR1"-"$COLOR2" gradient.png

# Für jedes Bild im Ordner
for img in *.png; do
  # Überspringe die Farbverlaufsdatei und überprüfe, ob die Datei existiert
  if [[ "$img" == "gradient.png" ]] || ! [[ -e "$img" ]]; then
    continue
  fi
  
  # Erstelle Halftone Bild
  halftonecv "$img" --pitch 5 --scale 1.0 --mode cmyk --output cmyk --angles 0 15 30 45 --resample linear -m gray

  # Extrahiere den Basisnamen ohne Dateierweiterung
  base="${img%.*}"

  # Negiere das Halftone Bild
  convert "${base}-halftone.tiff" -negate -contrast -contrast -contrast -contrast -contrast -contrast -contrast -contrast "${base}-halftone-negate.png"

  # Wende Farbverlauf an
  convert "${base}-halftone-negate.png" gradient.png -clut "${base}-gradient.png"
  
  # Negiere das Bild
  convert "${base}-gradient.png" "$img"

  # Aufräumen
  rm "${base}-halftone.tiff" "${base}-gradient.png" "${base}-halftone-negate.png"
done

# Entferne die Farbverlaufsdatei
rm gradient.png

echo "Transformation completed."
