Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap 512,512
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$rect = New-Object System.Drawing.Rectangle 0,0,512,512
$gradient = New-Object System.Drawing.Drawing2D.LinearGradientBrush($rect,[System.Drawing.Color]::FromArgb(29,78,216),[System.Drawing.Color]::FromArgb(67,56,202),45)
$g.FillRectangle($gradient,$rect)
$ring = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(70,147,197,253)),12
$g.DrawEllipse($ring,72,72,368,368)
$font = New-Object System.Drawing.Font('Segoe UI',190,[System.Drawing.FontStyle]::Bold,[System.Drawing.GraphicsUnit]::Pixel)
$brush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::White)
$format = New-Object System.Drawing.StringFormat
$format.Alignment = [System.Drawing.StringAlignment]::Center
$format.LineAlignment = [System.Drawing.StringAlignment]::Center
$g.DrawString('GS',$font,$brush,(New-Object System.Drawing.RectangleF 0,40,512,300),$format)
$pen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(191,219,254)),18
$pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
$pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
$pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
$points = [System.Drawing.PointF[]]@([System.Drawing.PointF]::new(128,390),[System.Drawing.PointF]::new(220,390),[System.Drawing.PointF]::new(258,342),[System.Drawing.PointF]::new(293,367),[System.Drawing.PointF]::new(385,259))
$g.DrawLines($pen,$points)
$g.DrawLine($pen,349,259,385,259)
$g.DrawLine($pen,385,259,385,295)
$bmp.Save('D:\GitPulse\gitsight-gs-icon-preview.png',[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
