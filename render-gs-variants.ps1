Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Drawing.Drawing2D
$out = 'D:\GitPulse'

function New-Canvas($path, $bg) {
  $bmp = New-Object System.Drawing.Bitmap 512,512
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $g.Clear($bg)
  return @($bmp,$g)
}
function Draw-Text($g,$text,$fontName,$size,$color,$rect) {
  $font = New-Object System.Drawing.Font($fontName,$size,[System.Drawing.FontStyle]::Regular,[System.Drawing.GraphicsUnit]::Pixel)
  $brush = New-Object System.Drawing.SolidBrush($color)
  $fmt = New-Object System.Drawing.StringFormat
  $fmt.Alignment = [System.Drawing.StringAlignment]::Center
  $fmt.LineAlignment = [System.Drawing.StringAlignment]::Center
  $g.DrawString($text,$font,$brush,$rect,$fmt)
  $font.Dispose(); $brush.Dispose(); $fmt.Dispose()
}
function Save-Canvas($bmp,$g,$path) { $bmp.Save($path,[System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose() }

# 1. Globe + editorial GS
$x = New-Canvas "$out\gs-variant-1.png" ([System.Drawing.Color]::FromArgb(247,245,239)); $bmp=$x[0];$g=$x[1]
$line = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(55,55,55)),3
$g.DrawEllipse($line,72,72,368,368); $g.DrawEllipse($line,170,72,172,368); $g.DrawEllipse($line,72,170,368,172)
Draw-Text $g 'GS' 'Bahnschrift SemiLight' 178 ([System.Drawing.Color]::FromArgb(31,31,31)) (New-Object System.Drawing.RectangleF 0,105,512,250)
Save-Canvas $bmp $g "$out\gs-variant-1.png"

# 2. Abstract cat-ear monogram
$x = New-Canvas "$out\gs-variant-2.png" ([System.Drawing.Color]::FromArgb(239,241,238)); $bmp=$x[0];$g=$x[1]
$dark = [System.Drawing.Color]::FromArgb(30,34,32); $thin = New-Object System.Drawing.Pen $dark,5
$g.DrawLine($thin,128,150,165,88); $g.DrawLine($thin,165,88,204,141); $g.DrawLine($thin,308,141,347,88); $g.DrawLine($thin,347,88,384,150)
Draw-Text $g 'GS' 'Century Gothic' 174 $dark (New-Object System.Drawing.RectangleF 0,125,512,250)
$g.DrawArc($thin,145,302,222,92,10,160)
Save-Canvas $bmp $g "$out\gs-variant-2.png"

# 3. Minimal globe seal
$x = New-Canvas "$out\gs-variant-3.png" ([System.Drawing.Color]::FromArgb(250,248,244)); $bmp=$x[0];$g=$x[1]
$ink = [System.Drawing.Color]::FromArgb(42,43,40); $gold = [System.Drawing.Color]::FromArgb(151,117,63)
$outer = New-Object System.Drawing.Pen $ink,8; $fine = New-Object System.Drawing.Pen $gold,3
$g.DrawEllipse($outer,65,65,382,382); $g.DrawArc($fine,95,160,322,190,195,150); $g.DrawArc($fine,160,95,190,322,105,150)
Draw-Text $g 'GS' 'Aptos Display' 166 $ink (New-Object System.Drawing.RectangleF 0,145,512,210)
Save-Canvas $bmp $g "$out\gs-variant-3.png"

# 4. Soft modern cat silhouette
$x = New-Canvas "$out\gs-variant-4.png" ([System.Drawing.Color]::FromArgb(232,235,232)); $bmp=$x[0];$g=$x[1]
$ink = [System.Drawing.Color]::FromArgb(35,38,36); $accent = [System.Drawing.Color]::FromArgb(185,142,82)
$cat = New-Object System.Drawing.Pen $accent,6
$g.DrawLine($cat,151,147,185,103); $g.DrawLine($cat,185,103,216,139); $g.DrawLine($cat,296,139,327,103); $g.DrawLine($cat,327,103,361,147)
Draw-Text $g 'GS' 'Gill Sans MT' 176 $ink (New-Object System.Drawing.RectangleF 0,130,512,220)
$g.DrawArc($cat,155,297,202,108,200,140)
Save-Canvas $bmp $g "$out\gs-variant-4.png"

# Contact sheet
$sheet = New-Object System.Drawing.Bitmap 1040,560
$sg = [System.Drawing.Graphics]::FromImage($sheet); $sg.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias; $sg.Clear([System.Drawing.Color]::White)
$files = @('gs-variant-1.png','gs-variant-2.png','gs-variant-3.png','gs-variant-4.png')
for($i=0;$i -lt 4;$i++){ $img=[System.Drawing.Image]::FromFile((Join-Path $out $files[$i])); $px=20+(($i%2)*510); $py=20+([math]::Floor($i/2)*270); $sg.DrawImage($img,$px,$py,250,250); $img.Dispose() }
$sheet.Save("$out\gs-variants-overview.png",[System.Drawing.Imaging.ImageFormat]::Png); $sg.Dispose();$sheet.Dispose()
