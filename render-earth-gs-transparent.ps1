Add-Type -AssemblyName System.Drawing
$bmp = [System.Drawing.Bitmap]::new(512,512,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::Transparent)
$dark = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(53,53,53))
$g.FillEllipse($dark,66,66,380,380)
$g.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
$clear = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::Transparent)
$cutouts = @(
  [System.Drawing.PointF]::new(119,178),[System.Drawing.PointF]::new(230,110),[System.Drawing.PointF]::new(218,148),[System.Drawing.PointF]::new(184,166),[System.Drawing.PointF]::new(176,201),[System.Drawing.PointF]::new(132,219)
)
$g.FillPolygon($clear,$cutouts)
$g.FillEllipse($clear,100,220,88,116)
$g.FillEllipse($clear,285,126,72,51)
$g.FillEllipse($clear,292,190,104,72)
$g.FillEllipse($clear,285,260,86,92)
$g.FillEllipse($clear,195,310,85,90)
$g.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceOver
$font = New-Object System.Drawing.Font('Bahnschrift',142,[System.Drawing.FontStyle]::Bold,[System.Drawing.GraphicsUnit]::Pixel)
$cream = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(244,241,234))
$fmt = New-Object System.Drawing.StringFormat
$fmt.Alignment = [System.Drawing.StringAlignment]::Center
$fmt.LineAlignment = [System.Drawing.StringAlignment]::Center
$g.DrawString('GS',$font,$cream,(New-Object System.Drawing.RectangleF 0,120,512,210),$fmt)
$bmp.Save('D:\GitPulse\gitsight-earth-gs-transparent-preview.png',[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
