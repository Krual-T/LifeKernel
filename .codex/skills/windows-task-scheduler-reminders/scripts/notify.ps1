param(
  [Parameter(Mandatory=$true)][string]$Title,
  [Parameter(Mandatory=$true)][string]$Body
)

$Message = "$Title`n$Body"
msg * $Message
