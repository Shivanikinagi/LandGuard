<#
.SYNOPSIS
    Complete system integration test for LandGuard
.DESCRIPTION
    Tests all API endpoints including auth, upload, analysis, and blockchain
#>

param(
    [string]$BaseUrl = "http://localhost:8000",
    [string]$TestUsername = "testuser_$(Get-Random -Maximum 9999)",
    [string]$TestEmail = "test_$(Get-Random -Maximum 9999)@example.com",
    [string]$TestPassword = "SecurePass@123"
)

# Configuration
$script:Token = ""
$script:UploadedRecordId = $null
$script:AnalysisId = $null
$script:PassedTests = 0
$script:FailedTests = 0
$script:TotalTests = 0

# Helper function to make API calls
function Invoke-ApiTest {
    param(
        [string]$Method = "GET",
        [string]$Endpoint,
        [object]$Body = $null,
        [hashtable]$Headers = @{},
        [string]$ContentType = "application/json"
    )
    
    $uri = "$BaseUrl$Endpoint"
    
    try {
        $params = @{
            Uri = $uri
            Method = $Method
            Headers = $Headers
            ContentType = $ContentType
        }
        
        if ($Body) {
            if ($Body -is [string]) {
                $params.Body = $Body
            } else {
                $params.Body = ($Body | ConvertTo-Json -Depth 10)
            }
        }
        
        $response = Invoke-RestMethod @params
        return @{
            Success = $true
            Data = $response
        }
    }
    catch {
        return @{
            Success = $false
            Error = $_.Exception.Message
            Details = $_.ErrorDetails.Message
        }
    }
}

# Test function
function Test-Endpoint {
    param(
        [string]$TestName,
        [scriptblock]$TestScript
    )
    
    $script:TotalTests++
    Write-Host "`n[$script:TotalTests] Testing: $TestName" -ForegroundColor Cyan
    
    try {
        $result = & $TestScript
        if ($result) {
            Write-Host "   ✅ PASSED" -ForegroundColor Green
            $script:PassedTests++
            return $true
        } else {
            Write-Host "   ❌ FAILED" -ForegroundColor Red
            $script:FailedTests++
            return $false
        }
    }
    catch {
        Write-Host "   ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
        $script:FailedTests++
        return $false
    }
}

# Print header
Write-Host "`n========================================" -ForegroundColor Yellow
Write-Host "   LandGuard System Integration Test" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Yellow

# Test 1: Health Check
Test-Endpoint "Health Check Endpoint" {
    $result = Invoke-ApiTest -Endpoint "/api/v1/health"
    if ($result.Success) {
        Write-Host "   Server Status: $($result.Data.status)"
        return $result.Data.status -eq "healthy"
    }
    Write-Host "   ❌ FAILED: $($result.Error)" -ForegroundColor Red
    return $false
}

# Test 2: Public Dashboard
Test-Endpoint "Public Dashboard (No Auth)" {
    $result = Invoke-ApiTest -Endpoint "/api/v1/dashboard/public"
    if ($result.Success) {
        Write-Host "   Total Records: $($result.Data.total_records)"
        Write-Host "   Total Users: $($result.Data.total_users)"
        return $true
    }
    Write-Host "   ❌ FAILED: $($result.Error)" -ForegroundColor Red
    return $false
}

# Test 3: User Registration
Test-Endpoint "User Registration" {
    $registerData = @{
        username = $TestUsername
        email = $TestEmail
        password = $TestPassword
        full_name = "Test User"
        role = "user"
    }
    
    $result = Invoke-ApiTest -Method POST -Endpoint "/api/v1/auth/register" -Body $registerData
    
    if ($result.Success) {
        Write-Host "   User ID: $($result.Data.id)"
        Write-Host "   Username: $($result.Data.username)"
        return $true
    }
    Write-Host "   ❌ FAILED: $($result.Error)" -ForegroundColor Red
    if ($result.Details) {
        Write-Host "   Details: $($result.Details)" -ForegroundColor Yellow
    }
    return $false
}

# Test 4: User Login
Test-Endpoint "User Login & Token Generation" {
    $loginData = @{
        username = $TestUsername
        password = $TestPassword
    }
    
    $result = Invoke-ApiTest -Method POST -Endpoint "/api/v1/auth/login" -Body $loginData
    
    if ($result.Success -and $result.Data.access_token) {
        $script:Token = $result.Data.access_token
        Write-Host "   Token Type: $($result.Data.token_type)"
        Write-Host "   Token Length: $($script:Token.Length) chars"
        return $true
    }
    Write-Host "   ❌ FAILED: $($result.Error)" -ForegroundColor Red
    return $false
}

# Test 5: Get Current User
Test-Endpoint "Get Current User Info" {
    if (-not $script:Token) {
        Write-Host "   ❌ FAILED: No token available" -ForegroundColor Red
        return $false
    }
    
    $headers = @{
        Authorization = "Bearer $script:Token"
    }
    
    $result = Invoke-ApiTest -Endpoint "/api/v1/auth/me" -Headers $headers
    
    if ($result.Success) {
        Write-Host "   User: $($result.Data.username)"
        Write-Host "   Email: $($result.Data.email)"
        Write-Host "   Role: $($result.Data.role)"
        return $true
    }
    Write-Host "   ❌ FAILED: $($result.Error)" -ForegroundColor Red
    return $false
}

# Test 6: ML Models Check
Test-Endpoint "ML Models Availability" {
    if (-not $script:Token) {
        Write-Host "   ⚠️  Skipped: No token" -ForegroundColor Yellow
        return $false
    }
    
    $headers = @{
        Authorization = "Bearer $script:Token"
    }
    
    $result = Invoke-ApiTest -Endpoint "/api/v1/analysis/models" -Headers $headers
    
    if ($result.Success) {
        Write-Host "   Models Available: $($result.Data.available)"
        return $true
    }
    Write-Host "   ❌ FAILED: $($result.Error)" -ForegroundColor Red
    return $false
}

# Test 7: Blockchain Services Check
Test-Endpoint "Blockchain Services Availability" {
    $result = Invoke-ApiTest -Endpoint "/api/v1/blockchain/status"
    
    if ($result.Success) {
        Write-Host "   Blockchain Available: $($result.Data.available)"
        Write-Host "   Message: $($result.Data.message)"
        return $true
    }
    Write-Host "   ❌ FAILED: $($result.Error)" -ForegroundColor Red
    return $false
}

# Test 8: User Dashboard
Test-Endpoint "User-Specific Dashboard" {
    if (-not $script:Token) {
        Write-Host "   ⚠️  Skipped: No token" -ForegroundColor Yellow
        return $false
    }
    
    $headers = @{
        Authorization = "Bearer $script:Token"
    }
    
    $result = Invoke-ApiTest -Endpoint "/api/v1/dashboard/user" -Headers $headers
    
    if ($result.Success) {
        Write-Host "   User Records: $($result.Data.total_records)"
        return $true
    }
    Write-Host "   ❌ FAILED: $($result.Error)" -ForegroundColor Red
    return $false
}

# Test 9: Statistics
Test-Endpoint "Statistics Endpoint (Requires Auth)" {
    if (-not $script:Token) {
        Write-Host "   ⚠️  Skipped: No token" -ForegroundColor Yellow
        return $false
    }
    
    $headers = @{
        Authorization = "Bearer $script:Token"
    }
    
    $result = Invoke-ApiTest -Endpoint "/api/v1/statistics/overview" -Headers $headers
    
    if ($result.Success) {
        Write-Host "   Statistics Retrieved: Yes"
        return $true
    }
    Write-Host "   ❌ FAILED: $($result.Error)" -ForegroundColor Red
    return $false
}

# Test 10: Get Upload Records
Test-Endpoint "Get Upload Records" {
    if (-not $script:Token) {
        Write-Host "   ⚠️  Skipped: No token" -ForegroundColor Yellow
        return $false
    }
    
    $headers = @{
        Authorization = "Bearer $script:Token"
    }
    
    $result = Invoke-ApiTest -Endpoint "/api/v1/upload/records" -Headers $headers
    
    if ($result.Success) {
        Write-Host "   Total Records: $($result.Data.Count)"
        return $true
    }
    Write-Host "   ❌ FAILED: $($result.Error)" -ForegroundColor Red
    return $false
}

# Test 11: Document Upload
Test-Endpoint "Document Upload" {
    if (-not $script:Token) {
        Write-Host "   ⚠️  Skipped: No token" -ForegroundColor Yellow
        return $false
    }
    
    # Create a test file in the correct directory
    $testFile = Join-Path $PWD "test-document-$(Get-Random).txt"
    $testContent = "This is a test land document for fraud detection testing.`nProperty ID: TEST-$(Get-Random -Maximum 99999)`nOwner: Test Owner`nLocation: Test Location"
    Set-Content -Path $testFile -Value $testContent
    
    try {
        $headers = @{
            Authorization = "Bearer $script:Token"
        }
        
        $fileBytes = [System.IO.File]::ReadAllBytes($testFile)
        $fileContent = [System.Text.Encoding]::GetEncoding('iso-8859-1').GetString($fileBytes)
        
        $boundary = [System.Guid]::NewGuid().ToString()
        $LF = "`r`n"
        
        $bodyLines = (
            "--$boundary",
            "Content-Disposition: form-data; name=`"file`"; filename=`"$(Split-Path $testFile -Leaf)`"",
            "Content-Type: text/plain$LF",
            $fileContent,
            "--$boundary--$LF"
        ) -join $LF
        
        $result = Invoke-RestMethod -Uri "$BaseUrl/api/v1/upload" `
            -Method POST `
            -ContentType "multipart/form-data; boundary=$boundary" `
            -Body $bodyLines `
            -Headers $headers
        
        if ($result.id) {
            $script:UploadedRecordId = $result.id
            Write-Host "   Record ID: $($result.id)"
            Write-Host "   Status: $($result.status)"
            return $true
        }
        return $false
    }
    catch {
        Write-Host "   ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    finally {
        Remove-Item -Path $testFile -ErrorAction SilentlyContinue
    }
}
# Test 12: ML Analysis
Test-Endpoint "ML-Based Fraud Analysis" {
    if (-not $script:UploadedRecordId) {
        Write-Host "   ❌ FAILED: No uploaded record to analyze" -ForegroundColor Red
        return $false
    }
    
    $headers = @{
        Authorization = "Bearer $script:Token"
    }
    
    $result = Invoke-ApiTest -Method POST -Endpoint "/api/v1/analysis/analyze/$script:UploadedRecordId" -Headers $headers
    
    if ($result.Success) {
        $script:AnalysisId = $result.Data.id
        Write-Host "   Analysis ID: $($result.Data.id)"
        Write-Host "   Fraud Score: $($result.Data.fraud_score)"
        return $true
    }
    Write-Host "   ❌ FAILED: $($result.Error)" -ForegroundColor Red
    return $false
}

# Test 13: Get Analysis Result
Test-Endpoint "Retrieve Analysis Result" {
    if (-not $script:AnalysisId) {
        Write-Host "   ❌ FAILED: No analysis to retrieve" -ForegroundColor Red
        return $false
    }
    
    $headers = @{
        Authorization = "Bearer $script:Token"
    }
    
    $result = Invoke-ApiTest -Endpoint "/api/v1/analysis/result/$script:AnalysisId" -Headers $headers
    
    if ($result.Success) {
        Write-Host "   Fraud Detected: $($result.Data.fraud_detected)"
        return $true
    }
    Write-Host "   ❌ FAILED: $($result.Error)" -ForegroundColor Red
    return $false
}

# Test 14: Blockchain Verification
Test-Endpoint "Blockchain Verification" {
    if (-not $script:UploadedRecordId) {
        Write-Host "   ❌ FAILED: No uploaded record to verify" -ForegroundColor Red
        return $false
    }
    
    $headers = @{
        Authorization = "Bearer $script:Token"
    }
    
    $result = Invoke-ApiTest -Method POST -Endpoint "/api/v1/blockchain/verify/$script:UploadedRecordId" -Headers $headers
    
    if ($result.Success -or $result.Error -like "*not configured*") {
        Write-Host "   Blockchain: Not configured (expected)" -ForegroundColor Yellow
        return $true
    }
    return $false
}

# Test 15: Check Blockchain Status
Test-Endpoint "Check Blockchain Verification Status" {
    if (-not $script:UploadedRecordId) {
        Write-Host "   ❌ FAILED: No uploaded record to check" -ForegroundColor Red
        return $false
    }
    
    $headers = @{
        Authorization = "Bearer $script:Token"
    }
    
    $result = Invoke-ApiTest -Endpoint "/api/v1/blockchain/status/$script:UploadedRecordId" -Headers $headers
    
    if ($result.Success) {
        Write-Host "   Verified: $($result.Data.verified)"
        return $true
    }
    return $false
}

# Test 16: Get Record Details
Test-Endpoint "Get Uploaded Record Details" {
    if (-not $script:UploadedRecordId) {
        Write-Host "   ❌ FAILED: No uploaded record to retrieve" -ForegroundColor Red
        return $false
    }
    
    $headers = @{
        Authorization = "Bearer $script:Token"
    }
    
    $result = Invoke-ApiTest -Endpoint "/api/v1/upload/record/$script:UploadedRecordId" -Headers $headers
    
    if ($result.Success) {
        Write-Host "   Record Number: $($result.Data.record_number)"
        return $true
    }
    Write-Host "   ❌ FAILED: $($result.Error)" -ForegroundColor Red
    return $false
}

# Test 17: Cleanup - Delete Test Record
Test-Endpoint "Delete Test Record (Cleanup)" {
    if (-not $script:UploadedRecordId) {
        Write-Host "   ❌ FAILED: No uploaded record to delete" -ForegroundColor Red
        return $false
    }
    
    $headers = @{
        Authorization = "Bearer $script:Token"
    }
    
    $result = Invoke-ApiTest -Method DELETE -Endpoint "/api/v1/upload/record/$script:UploadedRecordId" -Headers $headers
    
    if ($result.Success) {
        Write-Host "   Cleanup: Successful"
        return $true
    }
    return $false
}

# Print Summary
Write-Host "`n`n========================================" -ForegroundColor Yellow
Write-Host "           TEST SUMMARY" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Yellow
Write-Host "Total Tests:  $script:TotalTests"
Write-Host "Passed:       $script:PassedTests" -ForegroundColor Green
Write-Host "Failed:       $script:FailedTests" -ForegroundColor Red

if ($script:FailedTests -eq 0) {
    Write-Host "`n✅ ALL TESTS PASSED!`n" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  SOME TESTS FAILED`n" -ForegroundColor Yellow
    Write-Host "Please review the errors above and fix issues.`n"
}

Write-Host "Test Token (save for manual testing):" -ForegroundColor Cyan
Write-Host "$script:Token`n"

# Exit with appropriate code
exit $script:FailedTests