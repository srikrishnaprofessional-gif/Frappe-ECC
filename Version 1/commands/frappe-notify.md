---
description: Configure omnichannel alerts across WhatsApp, Twilio SMS, Slack, Email, and Microsoft Teams.
---

# /frappe:notify

Configure omnichannel alerts across WhatsApp, Twilio SMS, Slack, Email, and Microsoft Teams.

## Usage
```
/frappe:notify [channel] [event_trigger]
```

## Examples
```
/frappe:notify whatsapp 'Equipment Loan:on_submit'
```

## Description
Invokes `frappe-notification-omnichannel-agent` to execute the specialized workflow within the Frappe Framework and ERPNext runtime environment.
