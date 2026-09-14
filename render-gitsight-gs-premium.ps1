Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap 512,512
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::FromArgb(23,23,23))
$font = New-Object System.Drawing.Font('Segoe UI',178,[System.Drawing.FontStyle]::Regular,[System.Drawing.GraphicsUnit]::Pixel)
$brush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(244,240,232))
$format = New-Object System.Drawing.StringFormat
$format.Alignment = [System.Drawing.StringAlignment]::Center
$format.LineAlignment = [System.Drawing.StringAlignment]::Center
$g.DrawString('GS',$font,$brush,(New-Object System.Drawing.RectangleF 0,28,512,280),$format)
$pen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(200,169,107)),14
$pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
$pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
$pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
$points = [System.Drawing.PointF[]]@([System.Drawing.PointF]::new(118,365),[System.Drawing.PointF]::new(194,365),[System.Drawing.PointF]::new(229,322),[System.Drawing.PointF]::new(263,347),[System.Drawing.PointF]::new(354,239))
$g.DrawLines($pen,$points)
$g.DrawLine($pen,323,239,354,239)
$g.DrawLine($pen,354,239,354,270)
$bmp.Save('D:\GitPulse\gitsight-gs-premium-preview.png',[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
