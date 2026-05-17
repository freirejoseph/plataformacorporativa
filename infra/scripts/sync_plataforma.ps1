param(
    [ValidateSet('both', 'push', 'pull')]
    [string]$Direction = 'both',
    [string]$RemoteRoot = '/home/plataformacorporativa',
    [switch]$DryRun,
    [switch]$Watch,
    [int]$Interval = 60
)

$scriptPath = Join-Path $PSScriptRoot 'sync_plataforma.py'
$args = @('--direction', $Direction, '--remote-root', $RemoteRoot)
if ($DryRun) { $args += '--dry-run' }
if ($Watch) {
    $args += '--watch'
    $args += '--interval'
    $args += [string]$Interval
}

python $scriptPath @args
