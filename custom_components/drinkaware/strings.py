{
    "title": "Drinkaware",
    "config": {
        "step": {
            "user": {
                "title": "Add Drinkaware Account",
                "description": "Enter a name for this Drinkaware account",
                "data": {
                    "account_name": "Account Name"
                }
            },
            "auth_method": {
                "title": "Choose Authentication Method",
                "description": "Select how you want to authenticate with Drinkaware",
                "data": {
                    "auth_method": "Authentication Method"
                }
            },
            "oauth_auth": {
                "title": "Authorize Drinkaware",
                "description": "{instructions}\n\n[Click here to authorize]({auth_url})\n\nAfter clicking this link, you'll be redirected to the Drinkaware login page. Enter your credentials and authorize the app. After authorization, you'll be redirected to a URL that starts with 'uk.co.drinkaware.drinkaware://'. Your browser might show an error like 'Can't open this page' - this is normal. Copy the ENTIRE URL from your browser's address bar and paste it in the next step."
            },
            "code": {
                "title": "Enter Redirect URL",
                "description": "Paste the entire URL from your browser's address bar after you were redirected. It should start with 'uk.co.drinkaware.drinkaware://' and contain a 'code=' parameter.\n\nIf you can't see the URL in your browser, use the developer tools (F12 → Network tab) to find the redirect URL, or check the browser console for navigation events.",
                "data": {
                    "redirect_url": "Redirect URL"
                }
            },
            "manual_token": {
                "title": "Enter Drinkaware Token",
                "description": "{instructions}",
                "data": {
                    "token": "Authentication Token"
                }
            }
        },
        "error": {
            "cannot_connect": "Failed to connect to Drinkaware API. Please check your internet connection.",
            "invalid_token": "The provided token is invalid or expired. Please provide a valid token.",
            "connection_error": "Could not connect to Drinkaware with the provided code.",
            "auth_error": "Authentication failed. Please try again.",
            "no_code_in_url": "Could not find authorization code in the URL. Please make sure you copy the complete URL. It should look like: uk.co.drinkaware.drinkaware://oauth/callback?state=XXXX&code=YYYY",
            "unknown": "An unexpected error occurred. Please check the logs for more information."
        },
        "abort": {
            "already_configured": "This Drinkaware account is already configured in Home Assistant."
        }
    }
}