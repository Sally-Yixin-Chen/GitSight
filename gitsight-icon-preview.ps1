Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap 512,512
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::FromArgb(37,99,235))
$bg = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(45,255,255,255))
$g.FillRoundedRectangle = $null
$pen = New-Object System.Drawing.Pen ([System.Drawing.Color]::White),34
$pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
$pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
$pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
$points = [System.Drawing.PointF[]]@([System.Drawing.PointF]::new(105,350),[System.Drawing.PointF]::new(210,234),[System.Drawing.PointF]::new(273,297),[System.Drawing.PointF]::new(407,139))
$g.DrawLines($pen,$points)
$g.DrawLine($pen,407,139,324,139)
$g.DrawLine($pen,407,139,407,222)
$bmp.Save('D:\GitPulse\gitsight-icon-preview.png',[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $pen.Dispose(); $bmp.Dispose()
