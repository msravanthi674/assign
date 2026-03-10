$session = Invoke-RestMethod http://localhost:8000/api/start-session
$uid = $session.user_id
Write-Host "Started session: $uid"

for ($i=0; $i -lt 10; $i++) {
    $q = Invoke-RestMethod http://localhost:8000/api/next-question/$uid
    $ans = $q.options[0]
    $qid = $q.question_id
    $encoded = [uri]::EscapeDataString($ans)
    
    $sub = Invoke-RestMethod -Method Post "http://localhost:8000/api/submit-answer?user_id=$uid&question_id=$qid&answer=$encoded"
    $newAbil = $sub.new_ability
    Write-Host "Answered Q$i, new ability: $newAbil"
}

Write-Host "Fetching report..."
$rep = Invoke-RestMethod http://localhost:8000/api/report/$uid
$rep | ConvertTo-Json -Depth 5
