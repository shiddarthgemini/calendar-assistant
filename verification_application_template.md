# Google OAuth Verification Application Template

## Application Information

**App Name**: Calendar Assistant  
**Developer Email**: [your-email@domain.com]  
**Support Email**: [support@yourdomain.com]  
**App URL**: https://yourdomain.com  
**Privacy Policy URL**: https://yourdomain.com/privacy  
**Terms of Service URL**: https://yourdomain.com/terms  

## Detailed App Description

**What does your app do?**
Calendar Assistant is a web-based productivity application that helps users create and manage Google Calendar events using natural language input. The app uses AI-powered natural language processing to understand user intent and automatically create calendar events with appropriate titles, dates, times, and durations.

**Key Features:**
- Natural language event creation (e.g., "team meeting tomorrow at 3pm for 1 hour")
- AI-powered parsing of complex date/time expressions
- Integration with Google Calendar through OAuth 2.0
- Real-time event listing and management
- User-friendly web interface with confirmation modals
- Multi-user support with individual authentication

**Target Users:**
- Professionals who need to quickly schedule meetings and appointments
- Teams and organizations requiring efficient calendar management
- Individuals who prefer natural language input over traditional calendar interfaces
- Users who want to reduce the time spent on manual calendar entry

## Data Usage and Security

**What Google Calendar data does your app access?**
Our app accesses the following Google Calendar data:
- **Calendar Events**: Read existing events and create new events
- **Calendar Metadata**: Basic calendar information to identify the user's primary calendar
- **User Profile**: Email address and display name for authentication and personalization

**How do you use this data?**
- **Event Creation**: Parse natural language input and create corresponding calendar events
- **Event Display**: Show users their upcoming events for reference and management
- **User Authentication**: Verify user identity and maintain secure sessions
- **Personalization**: Display user-specific information and preferences

**What security measures do you implement?**
- **OAuth 2.0 Authentication**: Secure authentication through Google's OAuth system
- **HTTPS Encryption**: All data transmission is encrypted using SSL/TLS
- **Token Security**: OAuth tokens are stored securely and can be revoked by users
- **Session Management**: Secure session handling with automatic timeout
- **Input Validation**: All user inputs are validated and sanitized
- **Error Handling**: Secure error handling without exposing sensitive information
- **Minimal Data Storage**: We only store necessary OAuth tokens, no calendar data is permanently stored

## User Benefits and Use Cases

**What problems does your app solve?**
- **Time Efficiency**: Reduces time spent manually entering calendar events
- **Natural Interaction**: Allows users to create events using everyday language
- **Reduced Errors**: Minimizes mistakes in date/time entry through AI parsing
- **Improved Productivity**: Streamlines calendar management workflow
- **Accessibility**: Makes calendar management more accessible to users who prefer natural language

**Primary Use Cases:**
1. **Quick Meeting Scheduling**: "Schedule a team meeting tomorrow at 2pm for 1 hour"
2. **Appointment Booking**: "Book a doctor appointment on Friday at 3:30pm for 30 minutes"
3. **Event Planning**: "Create a lunch meeting with John next Monday at noon"
4. **Reminder Setting**: "Set a reminder to call the client in 2 hours"

## Testing Instructions

**How can Google test your app?**
1. **Visit the app URL**: https://yourdomain.com
2. **Click "Login with Google"** to authenticate
3. **Grant calendar permissions** when prompted
4. **Try creating events** using natural language:
   - "team meeting tomorrow at 3pm"
   - "doctor appointment on Friday 2pm for 30 minutes"
   - "call with John in 2 hours"
5. **View created events** in the events list
6. **Test the confirmation flow** for events requiring duration input

**Test Account Information:**
- **Test Email**: [test-email@domain.com]
- **Test Password**: [if applicable]
- **Expected Behavior**: Users should be able to create calendar events using natural language and see them appear in their Google Calendar

## Technical Implementation

**OAuth Flow:**
1. User clicks "Login with Google"
2. Redirected to Google OAuth consent screen
3. User grants calendar permissions
4. Redirected back to app with authorization code
5. App exchanges code for access token
6. User can now create and manage calendar events

**Data Flow:**
1. User enters natural language prompt
2. App uses OpenAI API to parse the input
3. App creates calendar event via Google Calendar API
4. Event appears in user's Google Calendar
5. App displays confirmation and event details

**Security Implementation:**
- OAuth state parameter validation
- CSRF protection
- Secure session management
- Input sanitization
- Error handling without data exposure

## Compliance and Legal

**Privacy Policy**: Our comprehensive privacy policy covers:
- Data collection and usage practices
- User rights and choices
- Data security measures
- Third-party service usage
- Contact information

**Terms of Service**: Our terms of service include:
- Service description and usage terms
- User responsibilities and acceptable use
- Liability limitations
- Termination clauses
- Contact information

**Data Retention**: We implement minimal data retention:
- OAuth tokens: Stored until user revokes access
- Session data: Cleared on logout
- No permanent storage of calendar data

## Contact Information

**Primary Contact**: [Your Name]  
**Email**: [your-email@domain.com]  
**Phone**: [your-phone-number]  
**Address**: [your-business-address]  

**Support Contact**:  
**Email**: [support@yourdomain.com]  
**Support URL**: https://yourdomain.com/support  

## Additional Information

**Business Information**: [If applicable]
- Business registration number
- Legal entity information
- Business address and contact details

**Domain Ownership**: 
- Domain: yourdomain.com
- SSL Certificate: Valid and properly configured
- Domain verification: Completed in Google Cloud Console

**Previous Issues**: [If any]
- Describe any previous verification attempts
- Explain how issues have been resolved
- Provide documentation of improvements made

---

**Note**: Customize this template with your specific information before submitting to Google. Ensure all URLs, contact information, and technical details are accurate and up-to-date. 