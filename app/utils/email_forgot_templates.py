def get_otp_forgot_password_html(otp_code: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset OTP</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #ffffff; color: #333333; margin: 0; padding: 0; line-height: 1.6;">
        <!-- Preheader Text (Hidden in email body, visible in client lists like Gmail) -->
        <span style="display: none; max-height: 0px; overflow: hidden; opacity: 0; font-size: 0px; mso-hide: all;">
            Your password reset code is {otp_code}. Use this to reset your account password.
            &nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
        </span>
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="padding: 40px 0; background-color: #f9f9f9;">
            <tr>
                <td align="center">
                    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 500px; background-color: #ffffff; border: 1px solid #eaeaea; border-radius: 8px; overflow: hidden;">
                        <tr>
                            <td style="padding: 30px 40px; text-align: center; border-bottom: 1px solid #eaeaea;">
                                <h1 style="color: #111111; margin: 0; font-size: 20px; font-weight: 600;">Trash Bin API</h1>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 40px;">
                                <p style="margin-top: 0; font-size: 16px; color: #555555;">Hello,</p>
                                <p style="font-size: 16px; color: #555555; margin-bottom: 30px;">We received a request to reset the password for your account. Please use the following One-Time Password (OTP) to proceed:</p>
                                
                                <div style="text-align: center; margin-bottom: 30px;">
                                    <div style="display: inline-block; font-size: 32px; font-weight: 700; letter-spacing: 6px; color: #111111; background-color: #f9f9f9; padding: 15px 30px; border-radius: 6px; border: 1px solid #eeeeee;">
                                        {otp_code}
                                    </div>
                                </div>
                                
                                <p style="font-size: 15px; color: #555555;">This code is valid for <strong>5 minutes</strong>. Please do not share this code with anyone.</p>
                                <p style="font-size: 13px; color: #999999; margin-top: 30px; margin-bottom: 0;">If you did not request a password reset, you can safely ignore this email. Your password will not be changed.</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="background-color: #fcfcfc; padding: 20px 40px; text-align: center; border-top: 1px solid #eaeaea;">
                                <p style="margin: 0; font-size: 12px; color: #888888;">&copy; 2026 Trash Bin API. All rights reserved.</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
