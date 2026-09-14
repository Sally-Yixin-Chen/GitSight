Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap 512,512
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::White)
$blue = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(37,99,235)),7
$g.DrawEllipse($blue,79,79,354,354)
$g.DrawEllipse($blue,178,79,156,354)
$g.DrawEllipse($blue,79,188,354,136)
$g.DrawLine($blue,79,256,433,256)
$font = New-Object System.Drawing.Font('Bahnschrift',170,[System.Drawing.FontStyle]::Bold,[System.Drawing.GraphicsUnit]::Pixel)
$ink = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(23,23,23))
$fmt = New-Object System.Drawing.StringFormat
$fmt.Alignment = [System.Drawing.StringAlignment]::Center
$fmt.LineAlignment = [System.Drawing.StringAlignment]::Center
$g.DrawString('GS',$font,$ink,(New-Object System.Drawing.RectangleF 0,105,512,230),$fmt)
$bmp.Save('D:\GitPulse\gitsight-earth-gs-white-blue-preview.png',[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
