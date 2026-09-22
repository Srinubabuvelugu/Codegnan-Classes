
# email templates
class EmailTemplates:
    @staticmethod
    def OTPEmailTemplate(username:str, otp:int):
        return f"""hello {username},

        Thanks for registering to SNS - mangement app
        your OTP:{otp}
        
        If you are not not register for app ignore this email and 
        don't OTP with any one.

        Regards
        SNS-management app
        """
    @staticmethod
    def ResetPasswordTemaplate(link:str, username:str="User"):
        template = f"""Dear {username},
        Thanks for using SNS app to manage your notes and files,

        Password Reset Link: {link}

        If your not doing thisone, simply ignore this email.


        Regards
        SNS App
        """
        return template