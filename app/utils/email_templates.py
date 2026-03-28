# noinspection SpellCheckingInspection
def get_otp_registration_html(otp_code: str) -> str:
    """
    Returns a professional, industry-standard HTML email template for OTP registration.
    """
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OTP Verification</title>
    </head>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6; color: #333333; margin: 0; padding: 0; line-height: 1.6;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f3f4f6; padding: 40px 0;">
            <tr>
                <td align="center">
                    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                        
                        <!-- Header -->
                        <tr>
                            <td style="background-color: #16a34a; padding: 30px; text-align: center;">
                                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">Trash Bin API</h1>
                            </td>
                        </tr>

                        <!-- Body -->
                        <tr>
                            <td style="padding: 40px 30px;">
                                <p style="margin-top: 0; font-size: 16px; color: #4b5563;">Hello,</p>
                                <p style="font-size: 16px; color: #4b5563;">Thank you for registering. To complete your account verification, please enter the following One-Time Password (OTP):</p>
                                
                                <div style="margin: 35px 0; text-align: center;">
                                    <span style="display: inline-block; font-size: 40px; font-weight: bold; letter-spacing: 8px; color: #16a34a; background-color: #f0fdf4; padding: 15px 30px; border-radius: 8px; border: 2px dashed #86efac; margin-left: 8px;">
                                        {otp_code}
                                    </span>
                                </div>
                                
                                <p style="font-size: 16px; color: #4b5563;">This code is valid for <strong>5 minutes</strong>. Please do not share this code with anyone.</p>
                                <p style="font-size: 14px; color: #9ca3af; margin-bottom: 0;">If you did not request this verification, please ignore this email. Your account is completely secure.</p>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f9fafb; padding: 20px 30px; text-align: center; border-top: 1px solid #f3f4f6;">
                                <p style="margin: 0; font-size: 13px; color: #6b7280;">&copy; 2026 Trash Bin API. All rights reserved.</p>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
