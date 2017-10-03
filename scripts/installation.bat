
REM python3 packages
pip3 install --upgrade pip
pip3 install ipython rpyc pygame Pillow
pip3 install --upgrade pyserial

REM change PATH to point to python 3.6
C:\Users\arad-lab\AppData\Local\Programs\Python\Python36\Scripts\;C:\Users\arad-lab\AppData\Local\Programs\Python\Python36\

REM change C:\python27 to C:\_python27

REM move all subfolder files to master folder
FOR /R "." %i IN (*.*) DO MOVE "%i" "C:\Users\User\Google Drive\Arad\Pictures\Conference"

REM power-shell reverse file names
gci -File -Recurse | %{$a = $_.BaseName -split "";[array]::Reverse($a);$s=$a -join "";ren $_.FullName ($s + $_.Extension)}
