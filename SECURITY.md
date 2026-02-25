# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of CodexAI seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. Email your report to **[INSERT SECURITY EMAIL]**
3. Include the following details:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: We will acknowledge your report within **48 hours**
- **Assessment**: We will assess the vulnerability within **5 business days**
- **Resolution**: We aim to release a fix within **14 days** for critical issues
- **Credit**: We will credit you in the release notes (unless you prefer anonymity)

---

## Security Best Practices

### Credential Management

#### ⚠️ CRITICAL: Never Commit Secrets

```bash
# WRONG - Never do this
AZURE_OPENAI_KEY=sk-abc123...  # Hardcoded in source code

# CORRECT - Always use environment variables
AZURE_OPENAI_KEY=${AZURE_OPENAI_KEY}  # Read from environment
```

#### Required Practices

1. **Use `.env` files locally** — Never commit them to Git
   ```bash
   cp .env.template .env
   # Edit .env with your actual credentials
   ```

2. **Use Azure Key Vault in production**
   ```bash
   az keyvault secret set --vault-name codexai-vault \
     --name "AZURE-OPENAI-KEY" --value "your-key"
   ```

3. **Rotate API keys every 90 days**
   ```bash
   # Regenerate keys in Azure Portal
   # Update .env and Key Vault
   # Restart affected services
   ```

4. **Use Azure Managed Identities** to eliminate keys entirely
   ```python
   from azure.identity import DefaultAzureCredential
   credential = DefaultAzureCredential()
   # No API key needed!
   ```

### Pre-Commit Checklist

Before every commit, verify:

- [ ] No `.env` files are staged (`git status`)
- [ ] No API keys or connection strings in code (`git diff --cached | grep -i "key\|secret\|password"`)
- [ ] `.gitignore` includes all sensitive file patterns
- [ ] No hardcoded URLs with credentials

### Recommended Tools

- **git-secrets**: Prevents committing secrets
  ```bash
  brew install git-secrets
  git secrets --install
  git secrets --register-aws  # or custom patterns
  ```

- **GitHub Secret Scanning**: Enable in repository settings

- **Azure Security Center**: Monitor for misconfigurations

---

## Architecture Security

### Data in Transit

- All API communication uses **HTTPS/TLS 1.3**
- Azure Functions enforce HTTPS-only
- Frontend served over HTTPS via Azure App Service

### Data at Rest

- Azure Blob Storage: **AES-256 encryption** (default)
- Cosmos DB: **Encryption at rest** (default)
- Azure Cognitive Search: **Encrypted storage** (default)

### Access Control

- **Principle of Least Privilege**: Each service has minimum required permissions
- **Azure RBAC**: Role-based access control for all resources
- **Network Security**: Consider VNet integration for production

### Input Validation

- File size limits enforced (max 100MB per upload)
- File type validation (code files only)
- API request validation and sanitization
- Rate limiting on all endpoints

---

## Incident Response

In case of a security incident:

1. **Contain**: Revoke compromised credentials immediately
2. **Assess**: Determine scope and impact
3. **Remediate**: Patch vulnerability, rotate all affected keys
4. **Notify**: Inform affected users if data was accessed
5. **Review**: Conduct post-incident review and update procedures

---

## Contact

For security-related inquiries, contact: **[INSERT SECURITY EMAIL]**