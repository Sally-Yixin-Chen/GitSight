Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap 512,512
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::FromArgb(246,243,236))
$ink = [System.Drawing.Color]::FromArgb(40,39,37)
$globe = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(110,40,39,37)),7
$g.DrawEllipse($globe,79,79,354,354)
$g.DrawEllipse($globe,178,79,156,354)
$g.DrawEllipse($globe,79,188,354,136)
$g.DrawLine($globe,79,256,433,256)
$font = New-Object System.Drawing.Font('Bahnschrift',170,[System.Drawing.FontStyle]::Bold,[System.Drawing.GraphicsUnit]::Pixel)
$brush = New-Object System.Drawing.SolidBrush($ink)
$format = New-Object System.Drawing.StringFormat
$format.Alignment = [System.Drawing.StringAlignment]::Center
$format.LineAlignment = [System.Drawing.StringAlignment]::Center
$g.DrawString('GS',$font,$brush,(New-Object System.Drawing.RectangleF 0,95,512,230),$format)
$gold = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(183,146,85))
$g.FillEllipse($gold,396,97,18,18)
$bmp.Save('D:\GitPulse\gitsight-earth-gs-preview.png',[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
