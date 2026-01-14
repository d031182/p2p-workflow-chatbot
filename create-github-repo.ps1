# Create GitHub repository
# Note: Set your GitHub token as an environment variable: $env:GITHUB_TOKEN = "your_token_here"
$token = $env:GITHUB_TOKEN
if (-not $token) {
    Write-Error "GitHub token not found. Please set the GITHUB_TOKEN environment variable."
    exit 1
}

$headers = @{
    'Authorization' = "token $token"
    'Content-Type' = 'application/json'
}

$body = @{
    name = 'p2p-workflow-chatbot'
    description = 'Purchase-to-Pay Workflow Application with AI-powered Chatbot for procurement process automation'
    private = $false
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri 'https://api.github.com/user/repos' -Method Post -Headers $headers -Body $body
Write-Output "Repository created successfully!"
Write-Output "Repository URL: $($response.html_url)"
Write-Output "Clone URL: $($response.clone_url)"
