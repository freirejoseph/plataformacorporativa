param(
  [switch]$Watch,
  [int]$Interval = 60,
  [switch]$Push,
  [string]$Message = "Auto sync plataformacorporativa",
  [string]$RemoteRoot = "/home/plataformacorporativa"
)

$script = Join-Path $PSScriptRoot 'sync_and_publish.py'
$args = @($script)
if ($Watch) { $args += '--watch' }
$args += '--interval'; $args += $Interval.ToString()
if ($Push) { $args += '--push' }
$args += '--message'; $args += $Message
$args += '--remote-root'; $args += $RemoteRoot

python @args
