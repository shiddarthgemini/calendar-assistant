# Google OAuth Verification Checklist

## Pre-Verification Requirements

### ✅ 1. Complete OAuth Consent Screen
- [ ] App name: "Calendar Assistant"
- [ ] User support email: [Your Email]
- [ ] Developer contact information: [Your Email]
- [ ] App description: Detailed description of functionality
- [ ] App logo: Upload a professional logo (recommended)
- [ ] App domain: [Your Domain]
- [ ] Authorized domains: Add your domain
- [ ] Privacy policy URL: [Your Privacy Policy URL]
- [ ] Terms of service URL: [Your Terms of Service URL]

### ✅ 2. Configure Scopes
- [ ] `https://www.googleapis.com/auth/calendar`
- [ ] `https://www.googleapis.com/auth/calendar.events`
- [ ] Remove any unnecessary scopes

### ✅ 3. Create OAuth 2.0 Credentials
- [ ] Web application client ID created
- [ ] Authorized redirect URIs configured:
  - `https://yourdomain.com/oauth2callback`
  - `http://localhost:5000/oauth2callback` (for development)
- [ ] Download credentials.json file

## Legal Documentation Requirements

### ✅ 4. Privacy Policy
- [ ] Create comprehensive privacy policy (see `privacy_policy.md`)
- [ ] Host on your domain: `https://yourdomain.com/privacy`
- [ ] Include all required sections:
  - Data collection practices
  - How data is used
  - Data sharing policies
  - User rights and choices
  - Contact information
  - Compliance statements

### ✅ 5. Terms of Service
- [ ] Create comprehensive terms of service (see `terms_of_service.md`)
- [ ] Host on your domain: `https://yourdomain.com/terms`
- [ ] Include all required sections:
  - Service description
  - User responsibilities
  - Acceptable use policies
  - Liability limitations
  - Termination clauses
  - Contact information

## Technical Requirements

### ✅ 6. Application Security
- [ ] HTTPS enabled for all pages
- [ ] Secure session management
- [ ] OAuth state parameter validation
- [ ] CSRF protection implemented
- [ ] Input validation and sanitization
- [ ] Error handling without sensitive data exposure

### ✅ 7. Data Handling
- [ ] Minimal data collection (only what's necessary)
- [ ] Secure data transmission (HTTPS)
- [ ] Proper data retention policies
- [ ] User data deletion capabilities
- [ ] No unnecessary data storage

### ✅ 8. User Experience
- [ ] Clear consent flow
- [ ] Easy account deletion
- [ ] Data export functionality
- [ ] Clear error messages
- [ ] Responsive design
- [ ] Accessibility compliance

## Verification Application Process

### ✅ 9. Prepare Verification Application
- [ ] Complete Google Cloud Console verification form
- [ ] Provide detailed app description
- [ ] Explain data usage and security measures
- [ ] Describe user benefits and use cases
- [ ] Provide testing instructions
- [ ] Include screenshots of key features

### ✅ 10. Required Information for Verification
- [ ] **App Purpose**: Clear explanation of what your app does
- [ ] **Target Users**: Who will use your app
- [ ] **Data Usage**: How you use Google Calendar data
- [ ] **Security Measures**: How you protect user data
- [ ] **Testing Instructions**: How Google can test your app
- [ ] **Contact Information**: Multiple ways to reach you

### ✅ 11. Supporting Documentation
- [ ] Privacy Policy URL
- [ ] Terms of Service URL
- [ ] Support contact information
- [ ] Business registration (if applicable)
- [ ] Domain ownership verification
- [ ] SSL certificate verification

## Post-Submission Requirements

### ✅ 12. Response to Google's Questions
- [ ] Respond promptly to any Google inquiries
- [ ] Provide additional documentation if requested
- [ ] Make any requested changes to your app
- [ ] Update privacy policy or terms if needed
- [ ] Address any security concerns

### ✅ 13. Testing and Validation
- [ ] Ensure app works correctly for Google's testing
- [ ] Test all OAuth flows thoroughly
- [ ] Verify error handling works properly
- [ ] Test with different user scenarios
- [ ] Ensure compliance with all requirements

## Timeline and Expectations

### ✅ 14. Verification Timeline
- [ ] **Week 1-2**: Initial review by Google
- [ ] **Week 3-4**: Additional questions or requests
- [ ] **Week 5-6**: Final review and approval
- [ ] **Total Time**: 4-6 weeks (can be longer)

### ✅ 15. Common Issues to Avoid
- [ ] Incomplete privacy policy
- [ ] Missing terms of service
- [ ] Insufficient app description
- [ ] Poor security practices
- [ ] Unclear data usage explanation
- [ ] Missing contact information

## Production Deployment Checklist

### ✅ 16. Before Going Live
- [ ] Complete verification process
- [ ] Deploy to production server
- [ ] Configure production OAuth credentials
- [ ] Update redirect URIs for production
- [ ] Test all functionality in production
- [ ] Monitor for any issues

### ✅ 17. Ongoing Compliance
- [ ] Keep privacy policy updated
- [ ] Maintain terms of service
- [ ] Monitor app usage and security
- [ ] Respond to user feedback
- [ ] Regular security audits
- [ ] Update dependencies regularly

## Contact Information Template

```
App Name: Calendar Assistant
Developer Email: [your-email@domain.com]
Support Email: [support@yourdomain.com]
Privacy Policy: https://yourdomain.com/privacy
Terms of Service: https://yourdomain.com/terms
App URL: https://yourdomain.com
Support URL: https://yourdomain.com/support
```

## Verification Form Tips

1. **Be Specific**: Provide detailed, specific answers
2. **Be Honest**: Don't overstate your app's capabilities
3. **Be Professional**: Use clear, professional language
4. **Be Complete**: Answer all questions thoroughly
5. **Be Responsive**: Respond quickly to any follow-up questions

## Success Metrics

- [ ] Verification approved by Google
- [ ] App available to all users (not just test users)
- [ ] No verification warnings or errors
- [ ] Smooth OAuth flow for all users
- [ ] Positive user feedback
- [ ] Stable app performance

---

**Note**: This checklist should be completed before submitting your verification application. Missing items may delay or prevent approval. 